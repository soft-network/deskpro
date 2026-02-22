"""
Tenant and TenantMember models — live on the Control Plane ('default') DB.

Tenant        — one row per provisioned tenant; holds Neon DB credentials.
TenantMember  — mirror of every Agent across all tenants so SaaS admins
                 can see who belongs where without querying tenant DBs.
"""
import uuid

from django.db import models


class EncryptedCharField(models.CharField):
    """
    CharField that transparently encrypts values at rest using Fernet.

    The Python-side value is always plaintext; encryption/decryption
    happens only when reading from or writing to the database.
    """

    def from_db_value(self, value, expression, connection):
        if not value:
            return value
        from core.encryption import decrypt
        try:
            return decrypt(value)
        except Exception:
            # Fallback: return as-is for any unencrypted legacy values
            return value

    def get_prep_value(self, value):
        if not value:
            return value
        from core.encryption import encrypt
        return encrypt(value)


class Tenant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=50, unique=True)

    # Neon DB credentials — password is encrypted at rest via EncryptedCharField
    neon_database_name = models.CharField(max_length=255, blank=True)
    neon_db_host = models.CharField(max_length=255, blank=True)
    neon_db_user = models.CharField(max_length=255, blank=True)
    neon_db_password = EncryptedCharField(max_length=500, blank=True)
    neon_db_port = models.PositiveIntegerField(default=5432)

    admin_email = models.EmailField(blank=True, help_text="Email of the tenant registrant")
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
            "PASSWORD": self.neon_db_password,   # decrypted transparently by EncryptedCharField
            "HOST": self.neon_db_host,
            "PORT": str(self.neon_db_port),
            "TIME_ZONE": None,
            "CONN_HEALTH_CHECKS": False,
            "CONN_MAX_AGE": 0,
            "AUTOCOMMIT": True,
            "ATOMIC_REQUESTS": False,
            "OPTIONS": {"sslmode": "require"},
            "TEST": {},
        }


class TenantMember(models.Model):
    """
    Control-plane directory of every Agent across all tenants.

    Created/updated automatically by the provisioning API whenever an Agent
    is added to a tenant DB. Gives SaaS admins a unified view of all users
    without needing to query individual tenant databases.

    Passwords are never stored here — this is a read-only directory record.
    """

    ROLE_AGENT = "agent"
    ROLE_ADMIN = "admin"
    ROLE_CHOICES = [
        (ROLE_AGENT, "Agent"),
        (ROLE_ADMIN, "Admin"),
    ]

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="members",
    )
    email = models.EmailField()
    full_name = models.CharField(max_length=255, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_AGENT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "tenants"
        unique_together = [("tenant", "email")]
        ordering = ["tenant__slug", "email"]

    def __str__(self):
        return f"{self.email} @ {self.tenant.slug} ({self.role})"
