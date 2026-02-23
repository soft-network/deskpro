"""
Tenant provisioning logic — shared between the REST API and Django Admin.

provision_tenant() is the single entry point for steps 3-9 of tenant setup:
  3. Create a dedicated Neon database for the tenant
  4. Persist credentials on the Tenant record
  5. Register DB alias in settings.DATABASES
  6. Apply template schema (Django migrations)
  7. Create the first admin Agent on the tenant DB
  8. Mirror the admin in the control-plane TenantMember directory
  9. Activate the tenant
"""
import logging

from django.core.management import call_command

from core.db_router import register_tenant_db
from core.neon_client import NeonClient
from management.tenants.models import Tenant, TenantMember

logger = logging.getLogger(__name__)


def provision_tenant(tenant: Tenant, admin_password: str, admin_full_name: str) -> None:
    """
    Provision a pre-created (is_active=False) Tenant record end-to-end.

    Caller is responsible for rolling back (deleting the Tenant record)
    if this function raises.
    """
    # 3. Create a dedicated Neon database for this tenant
    creds = NeonClient().create_database(f"tenant_{tenant.slug}")

    # 4. Persist credentials
    tenant.neon_database_name = creds.database_name
    tenant.neon_db_host = creds.host
    tenant.neon_db_user = creds.user
    tenant.neon_db_password = creds.password
    tenant.neon_db_port = creds.port
    tenant.save(using="default")

    # 5. Register DB alias so Django can route queries immediately
    register_tenant_db(tenant)
    db_alias = tenant.get_db_alias()

    # 6. Apply template schema
    _run_tenant_migrations(db_alias)

    # 7. Create first admin TenantUser on tenant DB
    _create_admin_agent(
        db_alias=db_alias,
        tenant_slug=tenant.slug,
        email=tenant.admin_email,
        password=admin_password,
        full_name=admin_full_name,
    )

    # 8. Mirror in control-plane TenantMember directory (no password stored)
    _sync_tenant_member(
        tenant=tenant,
        email=tenant.admin_email,
        full_name=admin_full_name,
        role=TenantMember.ROLE_ADMIN,
    )

    # 9. Activate
    tenant.is_active = True
    tenant.save(using="default")

    logger.info("Tenant '%s' provisioned successfully.", tenant.slug)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _run_tenant_migrations(db_alias: str) -> None:
    """
    Apply the tenant template schema to the given DB alias.

    Django migrations for tenant-scoped apps (accounts, tickets) define
    the canonical schema — applying them is the template-schema step.
    Idempotent: safe to run against the shared dev DB on every signup.
    """
    call_command("migrate", "--database", db_alias, verbosity=0)


def _create_admin_agent(
    db_alias: str,
    tenant_slug: str,
    email: str,
    password: str,
    full_name: str,
) -> None:
    """Create the first admin TenantUser on the tenant DB."""
    from management.authentication.tenantusers.models import TenantUser
    from core.thread_local import set_current_tenant_db, clear_current_tenant_db

    set_current_tenant_db(db_alias)
    try:
        user = TenantUser(
            email=email,
            tenant_slug=tenant_slug,
            is_admin=True,
            is_active=True,
            full_name=full_name,
        )
        user.set_password(password)
        user.save(using=db_alias)
    finally:
        clear_current_tenant_db()


def _sync_tenant_member(
    tenant: Tenant,
    email: str,
    full_name: str,
    role: str,
) -> None:
    """
    Mirror an Agent into the control-plane TenantMember directory.
    No password is stored here — this is a read-only directory record.
    """
    TenantMember.objects.using("default").update_or_create(
        tenant=tenant,
        email=email,
        defaults={"full_name": full_name, "role": role},
    )
