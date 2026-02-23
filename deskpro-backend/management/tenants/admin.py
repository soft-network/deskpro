import logging

from django import forms
from django.conf import settings
from django.contrib import admin, messages

from management.tenants.models import Tenant, TenantMember
from core.neon_client import NeonClient

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Tenant creation form (shown only when adding a new tenant)
# ---------------------------------------------------------------------------

class TenantCreationForm(forms.ModelForm):
    """
    Extends the standard Tenant form with admin credentials so that saving
    from the admin panel triggers the full provisioning flow:
    Neon DB → migrations → Agent → TenantMember → activate.
    """
    admin_full_name = forms.CharField(
        max_length=255,
        required=True,
        label="Admin full name",
        help_text="Full name of the first admin agent for this tenant.",
    )
    admin_password = forms.CharField(
        widget=forms.PasswordInput(render_value=False),
        required=True,
        label="Admin password",
        help_text="Initial password for the tenant admin account. Not stored here.",
    )

    class Meta:
        model = Tenant
        fields = ("name", "slug", "admin_email")


# ---------------------------------------------------------------------------
# Inline: members belonging to a tenant
# ---------------------------------------------------------------------------

class TenantMemberInline(admin.TabularInline):
    model = TenantMember
    extra = 0
    can_delete = False
    show_change_link = False
    fields = ("email", "full_name", "role", "created_at")
    readonly_fields = ("email", "full_name", "role", "created_at")

    def has_add_permission(self, request, obj=None):
        return False


# ---------------------------------------------------------------------------
# Tenant admin
# ---------------------------------------------------------------------------

@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "admin_email", "member_count", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "slug", "admin_email")

    # neon_db_password is intentionally excluded — encrypted at rest, never shown.
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

    def get_form(self, request, obj=None, **kwargs):
        # Show the extended creation form only when adding a new tenant
        if obj is None:
            return TenantCreationForm
        return super().get_form(request, obj, **kwargs)

    def save_model(self, request, obj: Tenant, form, change: bool) -> None:
        if not change:
            # New tenant: run full provisioning after the initial save
            from management.tenants.provisioning import provision_tenant

            obj.is_active = False
            obj.save(using="default")

            try:
                provision_tenant(
                    tenant=obj,
                    admin_password=form.cleaned_data["admin_password"],
                    admin_full_name=form.cleaned_data["admin_full_name"],
                )
                messages.success(
                    request,
                    f"Tenant '{obj.slug}' provisioned successfully — "
                    f"DB, schema, and admin agent created.",
                )
            except Exception as exc:
                # Roll back the reserved record so the slug is freed
                try:
                    obj.delete(using="default")
                except Exception:
                    pass
                messages.error(request, f"Provisioning failed: {exc}")
                logger.error("Admin provisioning failed for '%s': %s", obj.slug, exc)
        else:
            super().save_model(request, obj, form, change)

    def delete_model(self, request, obj: Tenant) -> None:
        _cleanup_tenant(obj)
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset) -> None:
        for tenant in queryset:
            _cleanup_tenant(tenant)
        super().delete_queryset(request, queryset)


# ---------------------------------------------------------------------------
# TenantMember admin (read-only directory)
# ---------------------------------------------------------------------------

@admin.register(TenantMember)
class TenantMemberAdmin(admin.ModelAdmin):
    list_display = ("email", "full_name", "tenant", "role", "created_at")
    list_filter = ("role", "tenant")
    search_fields = ("email", "full_name", "tenant__slug")
    readonly_fields = ("tenant", "email", "full_name", "role", "created_at")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _cleanup_tenant(tenant: Tenant) -> None:
    """Delete Neon DB (prod only) and unregister from settings.DATABASES."""
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
