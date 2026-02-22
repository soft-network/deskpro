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
      3. Provision DB
           Dev  (TENANT_DEV_MODE=True)  → use fixed softflow_tenant_dev, no Neon API call
           Prod (TENANT_DEV_MODE=False) → call NeonClient.create_database()
      4. Persist credentials + register DB alias
      5. Apply template schema (Django migrations) to tenant DB
      6. Create first admin Agent
      7. Activate tenant
    """
    # 1. Slug uniqueness
    if Tenant.objects.using("default").filter(slug=payload.slug).exists():
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

        # 3. Provision DB — dev uses fixed credentials, prod calls Neon API
        if settings.TENANT_DEV_MODE:
            creds = _get_dev_tenant_db_creds()
            logger.info(
                "[DEV] Using fixed dev DB '%s' for tenant '%s' (no Neon API call).",
                creds.database_name,
                payload.slug,
            )
        else:
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

        # Register DB alias so Django can route queries immediately
        register_tenant_db(tenant)
        db_alias = tenant.get_db_alias()

        # 5. Apply template schema: run Django migrations on the tenant DB.
        #    The migration files (accounts + tickets) define the canonical
        #    tenant schema — applying them IS the template-schema step.
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
        # Rollback: free the slug so the client can retry
        if tenant is not None:
            try:
                tenant.delete(using="default")
            except Exception:
                pass
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

    # 1. Delete Neon DB — skip in dev mode (shared fixed DB must not be dropped)
    if settings.TENANT_DEV_MODE:
        logger.info("[DEV] Skipping Neon DB deletion for tenant '%s' (dev mode).", slug)
    else:
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


def _get_dev_tenant_db_creds():
    """
    Return fixed dev DB credentials from settings (no Neon API call).

    In dev mode all tenants share a single pre-existing Neon database
    (softflow_tenant_dev). Each tenant gets a distinct Django DB alias
    (tenant_<slug>) but they all point to the same physical database —
    which is fine for local development where only one tenant is active
    at a time.
    """
    from core.neon_client import TenantDBCredentials

    dev = settings.DEV_TENANT_DB
    return TenantDBCredentials(
        host=dev["HOST"],
        user=dev["USER"],
        password=dev["PASSWORD"],
        database_name=dev["NAME"],
        port=int(dev["PORT"]),
    )


def _run_tenant_migrations(db_alias: str) -> None:
    """
    Apply the tenant template schema to the given DB alias.

    Django migrations for the tenant-scoped apps (accounts, tickets) define
    the canonical schema. Running them here is the "apply template schema"
    step — idempotent, so safe to run against the shared dev DB on every
    signup.
    """
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
