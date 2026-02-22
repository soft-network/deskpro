"""
Agent model — custom AbstractBaseUser that lives on Tenant DBs.

The USERNAME_FIELD is email. tenant_slug is stored denormalized so
a JWT payload can be fully reconstructed from the Agent record alone.
"""
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models


class AgentManager(BaseUserManager):
    def create_user(self, email: str, password: str | None = None, **extra):
        if not email:
            raise ValueError("Email is required.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user


class Agent(AbstractBaseUser):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255, blank=True)
    tenant_slug = models.CharField(max_length=50)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = AgentManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["tenant_slug"]

    class Meta:
        app_label = "accounts"

    def __str__(self):
        return f"{self.email} ({self.tenant_slug})"

    def has_perm(self, perm, obj=None):
        return self.is_staff

    def has_module_perms(self, app_label):
        return self.is_staff
