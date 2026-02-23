"""
TenantUser model — custom AbstractBaseUser that lives on Tenant DBs.

The USERNAME_FIELD is email. tenant_slug is stored denormalized so
a JWT payload can be fully reconstructed from the TenantUser record alone.

is_admin means "tenant admin" (not Django admin access).
"""
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models


class TenantUserManager(BaseUserManager):
    def create_user(self, email: str, password: str | None = None, **extra):
        if not email:
            raise ValueError("Email is required.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user


class TenantUser(AbstractBaseUser):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255, blank=True)
    tenant_slug = models.CharField(max_length=50)
    is_admin = models.BooleanField(default=False)   # True = tenant admin role
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = TenantUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["tenant_slug"]

    class Meta:
        app_label = "accounts"

    def __str__(self):
        return f"{self.email} ({self.tenant_slug})"

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return self.is_admin
