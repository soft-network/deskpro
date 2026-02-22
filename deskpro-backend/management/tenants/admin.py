import logging

from django.conf import settings
from django.contrib import admin

from management.tenants.models import Tenant, TenantMember
from core.neon_client import NeonClient

logger = logging.getLogger(__name__)


def _cleanup_tenant(tenant: Tenant) -> None:
    """Delete Neon DB and unregister from settings.DATABASES."""
    if settings.TENANT_DEV_MODE:
        logger.info("[DEV] Skipping Neon DB deletion for '%s' (dev mode).", tenant.slug)
    elif tenant.neon_database_name:
        try:
            NeonClient().delete_database(tenant.neon_database_name)
            logger.info("Deleted Neon DB '%s'", tenant.neon_database_name)
        except Exception as exc:
            logger.warning("Could not delete Neon DB for '%s': %s", tenant.slug, exc)

    db_alias = tenant.get_db_alias()
    if db_alias in settings.DATABASES:
        del settings.DATABASES[db_alias]
        logger.info("Unregistered DB alias '%s'", db_alias)


class TenantMemberInline(admin.TabularInline):
    """Read-only list of all agents belonging to this tenant."""

    model = TenantMember
    extra = 0
    can_delete = False
    show_change_link = False
    fields = ("email", "full_name", "role", "created_at")
    readonly_fields = ("email", "full_name", "role", "created_at")

    def has_add_permission(self, request, obj=None):
        # Members are managed by the provisioning API, not manually
        return False


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "admin_email", "member_count", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "slug", "admin_email")

    # neon_db_password is intentionally excluded from fields — it is
    # encrypted at rest and must never be visible in the admin UI.
    readonly_fields = ("id", "admin_email", "created_at", "neon_database_name",
                       "neon_db_host", "neon_db_user", "neon_db_port")
    fields = (
        "id", "name", "slug", "admin_email", "is_active", "created_at",
        "neon_database_name", "neon_db_host", "neon_db_user", "neon_db_port",
    )

    inlines = [TenantMemberInline]

    @admin.display(description="Members")
    def member_count(self, obj):
        return obj.members.count()

    def delete_model(self, request, obj: Tenant) -> None:
        _cleanup_tenant(obj)
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset) -> None:
        for tenant in queryset:
            _cleanup_tenant(tenant)
        super().delete_queryset(request, queryset)


@admin.register(TenantMember)
class TenantMemberAdmin(admin.ModelAdmin):
    list_display = ("email", "full_name", "tenant", "role", "created_at")
    list_filter = ("role", "tenant")
    search_fields = ("email", "full_name", "tenant__slug")
    readonly_fields = ("tenant", "email", "full_name", "role", "created_at")

    # No passwords ever stored or shown here — this is a directory record only
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
