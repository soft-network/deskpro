"""
SaasAdmin — the Control Plane superuser model.

Lives on the default DB, is AUTH_USER_MODEL, and powers Django Admin.
"""
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class SaasAdminManager(BaseUserManager):
    def create_user(self, email, password=None, **extra):
        email = self.normalize_email(email)
        user = self.model(email=email, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        extra.setdefault("is_active", True)
        return self.create_user(email, password, **extra)


class SaasAdmin(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255, blank=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = SaasAdminManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        app_label = "staff"

    def __str__(self):
        return self.email
