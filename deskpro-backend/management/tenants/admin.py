import logging

from django.conf import settings
from django.contrib import admin

from management.tenants.models import Tenant
from core.neon_client import NeonClient

logger = logging.getLogger(__name__)


def _cleanup_tenant(tenant: Tenant) -> None:
    """Delete Neon DB and unregister from settings.DATABASES."""
    if tenant.neon_database_name:
        try:
            NeonClient().delete_database(tenant.neon_database_name)
            logger.info("Deleted Neon DB '%s'", tenant.neon_database_name)
        except Exception as exc:
            logger.warning("Could not delete Neon DB for '%s': %s", tenant.slug, exc)

    db_alias = tenant.get_db_alias()
    if db_alias in settings.DATABASES:
        del settings.DATABASES[db_alias]
        logger.info("Unregistered DB alias '%s'", db_alias)


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "admin_email", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "slug", "admin_email")
    readonly_fields = ("id", "admin_email", "created_at")

    def delete_model(self, request, obj: Tenant) -> None:
        """Called when a single tenant is deleted from the detail view."""
        _cleanup_tenant(obj)
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset) -> None:
        """Called when tenants are deleted via the list-view bulk action."""
        for tenant in queryset:
            _cleanup_tenant(tenant)
        super().delete_queryset(request, queryset)
