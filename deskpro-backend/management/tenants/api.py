"""
Tenant API.

POST   /api/tenants/signup        — provision a new tenant (public)
DELETE /api/tenants/{slug}        — delete a tenant (requires X-Admin-Key)
"""
import logging

from django.conf import settings
from ninja import Router
from ninja.errors import HttpError

from management.tenants.auth import AdminKeyAuth
from management.tenants.models import Tenant
from management.tenants.provisioning import provision_tenant
from management.tenants.schemas import TenantSignupIn, TenantSignupOut, TenantDeleteOut
from core.neon_client import NeonClient

logger = logging.getLogger(__name__)

router = Router(tags=["Tenants"])


@router.post("/signup", response=TenantSignupOut, auth=None)
def signup(request, payload: TenantSignupIn):
    """
    Create a new tenant:
      1. Validate slug uniqueness
      2. Reserve Tenant record (is_active=False)
      3-9. Delegate to provision_tenant()
    """
    if Tenant.objects.using("default").filter(slug=payload.slug).exists():
        raise HttpError(409, f"Slug '{payload.slug}' is already taken.")

    tenant = None
    try:
        tenant = Tenant.objects.using("default").create(
            name=payload.name,
            slug=payload.slug,
            admin_email=payload.admin_email,
            is_active=False,
        )
        provision_tenant(
            tenant=tenant,
            admin_password=payload.admin_password,
            admin_full_name=payload.admin_full_name,
        )
    except Exception as exc:
        logger.error("Tenant provisioning failed for '%s': %s", payload.slug, exc)
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
      2. Delete the Neon database (skipped in dev mode)
      3. Remove from settings.DATABASES
      4. Delete the control-plane Tenant record
    """
    try:
        tenant = Tenant.objects.using("default").get(slug=slug)
    except Tenant.DoesNotExist:
        raise HttpError(404, f"Tenant '{slug}' not found.")

    db_alias = tenant.get_db_alias()

    # Skip Neon deletion in dev mode (shared fixed DB must not be dropped)
    if settings.TENANT_DEV_MODE:
        logger.info("[DEV] Skipping Neon DB deletion for tenant '%s' (dev mode).", slug)
    else:
        try:
            NeonClient().delete_database(tenant.neon_database_name)
            logger.info("Deleted Neon DB for tenant '%s'", slug)
        except Exception as exc:
            logger.warning("Could not delete Neon DB for '%s': %s", slug, exc)

    if db_alias in settings.DATABASES:
        del settings.DATABASES[db_alias]
        logger.info("Unregistered DB alias '%s'", db_alias)

    tenant.delete(using="default")
    logger.info("Tenant '%s' deleted from control plane.", slug)

    return TenantDeleteOut(slug=slug, message=f"Tenant '{slug}' deleted successfully.")
