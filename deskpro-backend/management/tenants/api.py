"""
Tenant API.

POST   /api/tenants/signup        — provision a new tenant (public)
DELETE /api/tenants/{slug}        — delete a tenant (requires X-Admin-Key)
"""
import logging

from django.conf import settings
from django.core.management import call_command
from ninja import Router
from ninja.errors import HttpError

from management.tenants.auth import AdminKeyAuth
from management.tenants.models import Tenant
from management.tenants.schemas import TenantSignupIn, TenantSignupOut, TenantDeleteOut
from core.db_router import register_tenant_db
from core.neon_client import NeonClient

logger = logging.getLogger(__name__)

router = Router(tags=["Tenants"])


@router.post("/signup", response=TenantSignupOut, auth=None)
def signup(request, payload: TenantSignupIn):
    """
    Create a new tenant:
      1. Validate slug uniqueness
      2. Reserve Tenant record (is_active=False)
      3. Provision Neon DB
      4. Register DB + run migrations
      5. Create first admin Agent
      6. Activate tenant
    """
    # 1. Slug uniqueness
    if Tenant.objects.using("default").filter(slug=payload.slug).exists():
        from ninja.errors import HttpError
        raise HttpError(409, f"Slug '{payload.slug}' is already taken.")

    tenant = None
    try:
        # 2. Reserve tenant record
        tenant = Tenant.objects.using("default").create(
            name=payload.name,
            slug=payload.slug,
            admin_email=payload.admin_email,
            is_active=False,
        )

        # 3. Provision Neon DB
        db_name = f"tenant_{payload.slug}"
        client = NeonClient()
        creds = client.create_database(db_name)

        # 4. Persist credentials
        tenant.neon_database_name = creds.database_name
        tenant.neon_db_host = creds.host
        tenant.neon_db_user = creds.user
        tenant.neon_db_password = creds.password
        tenant.neon_db_port = creds.port
        tenant.save(using="default")

        # Register DB so Django can use it immediately
        register_tenant_db(tenant)
        db_alias = tenant.get_db_alias()

        # 5. Run migrations on the new tenant DB
        _run_tenant_migrations(db_alias)

        # 6. Create the first admin Agent
        _create_admin_agent(
            db_alias=db_alias,
            tenant_slug=payload.slug,
            email=payload.admin_email,
            password=payload.admin_password,
            full_name=payload.admin_full_name,
        )

        # 7. Activate
        tenant.is_active = True
        tenant.save(using="default")

        logger.info("Tenant '%s' provisioned successfully.", payload.slug)

    except Exception as exc:
        logger.error("Tenant provisioning failed for '%s': %s", payload.slug, exc)
        # Rollback: delete reserved record so slug is freed
        if tenant is not None:
            try:
                tenant.delete(using="default")
            except Exception:
                pass
        from ninja.errors import HttpError
        raise HttpError(500, f"Provisioning failed: {exc}") from exc

    return TenantSignupOut(
        id=str(tenant.id),
        name=tenant.name,
        slug=tenant.slug,
        message="Tenant provisioned successfully.",
    )


@router.delete("/{slug}", response=TenantDeleteOut, auth=AdminKeyAuth())
def delete_tenant(request, slug: str):
    """
    Delete a tenant:
      1. Look up the tenant record
      2. Delete the Neon database
      3. Remove from settings.DATABASES (if loaded)
      4. Delete the control-plane Tenant record
    """
    try:
        tenant = Tenant.objects.using("default").get(slug=slug)
    except Tenant.DoesNotExist:
        raise HttpError(404, f"Tenant '{slug}' not found.")

    db_alias = tenant.get_db_alias()

    # 1. Delete Neon DB
    try:
        client = NeonClient()
        client.delete_database(tenant.neon_database_name)
        logger.info("Deleted Neon DB for tenant '%s'", slug)
    except Exception as exc:
        logger.warning("Could not delete Neon DB for '%s': %s", slug, exc)

    # 2. Unregister from settings.DATABASES
    if db_alias in settings.DATABASES:
        del settings.DATABASES[db_alias]
        logger.info("Unregistered DB alias '%s'", db_alias)

    # 3. Delete control-plane record
    
    tenant.delete(using="default")
    logger.info("Tenant '%s' deleted from control plane.", slug)

    return TenantDeleteOut(slug=slug, message=f"Tenant '{slug}' deleted successfully.")


def _run_tenant_migrations(db_alias: str) -> None:
    """Run Django migrations for tenant apps on the given DB alias."""
    # accounts and tickets are the tenant-scoped apps
    call_command("migrate", "--database", db_alias, verbosity=0)


def _create_admin_agent(
    db_alias: str,
    tenant_slug: str,
    email: str,
    password: str,
    full_name: str,
) -> None:
    """Create the first admin Agent on the tenant DB."""
    from management.authentication.tenantusers.models import Agent
    from core.thread_local import set_current_tenant_db, clear_current_tenant_db

    set_current_tenant_db(db_alias)
    try:
        agent = Agent(
            email=email,
            tenant_slug=tenant_slug,
            is_staff=True,
            is_active=True,
            full_name=full_name,
        )
        agent.set_password(password)
        agent.save(using=db_alias)
    finally:
        clear_current_tenant_db()
