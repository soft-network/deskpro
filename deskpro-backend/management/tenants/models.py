"""
Tenant model — lives on the Control Plane ('default') DB.

Each row represents a provisioned tenant with their Neon DB credentials.
"""
import uuid

from django.db import models


class Tenant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=50, unique=True)

    # Neon DB credentials for this tenant
    neon_database_name = models.CharField(max_length=255, blank=True)
    neon_db_host = models.CharField(max_length=255, blank=True)
    neon_db_user = models.CharField(max_length=255, blank=True)
    neon_db_password = models.CharField(max_length=255, blank=True)  # Encrypt in prod
    neon_db_port = models.PositiveIntegerField(default=5432)

    admin_email = models.EmailField(blank=True, help_text="Email of the tenant registrant (admin)")
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "tenants"

    def __str__(self):
        return f"{self.name} ({self.slug})"

    def get_db_alias(self) -> str:
        return f"tenant_{self.slug}"

    def get_db_config(self) -> dict:
        return {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": self.neon_database_name,
            "USER": self.neon_db_user,
            "PASSWORD": self.neon_db_password,
            "HOST": self.neon_db_host,
            "PORT": str(self.neon_db_port),
            # Django 5 requires these keys when a DB config is registered dynamically
            "TIME_ZONE": None,
            "CONN_HEALTH_CHECKS": False,
            "CONN_MAX_AGE": 0,
            "AUTOCOMMIT": True,
            "ATOMIC_REQUESTS": False,
            "OPTIONS": {
                "sslmode": "require",
            },
            "TEST": {},
        }
