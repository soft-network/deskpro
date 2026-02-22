from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from management.authentication.centralusers.models import SaasAdmin


class SaasAdminCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = SaasAdmin
        fields = ("email", "full_name")


class SaasAdminChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = SaasAdmin
        fields = ("email", "full_name", "is_staff", "is_superuser", "is_active")


@admin.register(SaasAdmin)
class SaasAdminAdmin(UserAdmin):
    form = SaasAdminChangeForm
    add_form = SaasAdminCreationForm
    model = SaasAdmin

    list_display = ("email", "full_name", "is_staff", "is_superuser", "is_active")
    ordering = ("email",)
    search_fields = ("email", "full_name")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal", {"fields": ("full_name",)}),
        ("Permissions", {"fields": ("is_staff", "is_superuser", "is_active", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {"fields": ("email", "full_name", "password1", "password2", "is_staff", "is_superuser")}),
    )
