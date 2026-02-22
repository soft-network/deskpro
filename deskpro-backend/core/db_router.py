"""
TenantDatabaseRouter — routes ORM queries to the correct Neon DB.

Control-plane apps (tenants, admin, auth, contenttypes, sessions) always
use the 'default' (Control Plane) DB.

All other apps (tenant related apps) are routed to the tenant DB alias
stored in thread-local storage for the current request.
"""
from django.conf import settings

from core.thread_local import get_current_tenant_db

# Apps that live exclusively on the Control Plane DB
CONTROL_PLANE_APPS = frozenset(
    {"tenants", "admin", "auth", "contenttypes", "sessions", "staff"}
)

# Apps that live exclusively on Tenant DBs
TENANT_APPS = frozenset({"accounts", "tickets"})


class TenantDatabaseRouter:
    """Route reads and writes to the appropriate database."""

    def _is_control_plane(self, app_label: str) -> bool:
        return app_label in CONTROL_PLANE_APPS

    def db_for_read(self, model, **hints):
        if self._is_control_plane(model._meta.app_label):
            return "default"
        tenant_db = get_current_tenant_db()
        if tenant_db is None:
            raise RuntimeError(
                f"No tenant context set — cannot route '{model._meta.app_label}' query. "
                "Ensure TenantMiddleware ran and the request carries a valid tenant slug."
            )
        return tenant_db

    def db_for_write(self, model, **hints):
        if self._is_control_plane(model._meta.app_label):
            return "default"
        tenant_db = get_current_tenant_db()
        if tenant_db is None:
            raise RuntimeError(
                f"No tenant context set — cannot route '{model._meta.app_label}' write. "
                "Ensure TenantMiddleware ran and the request carries a valid tenant slug."
            )
        return tenant_db

    def allow_relation(self, obj1, obj2, **hints):
        # Allow relations within the same DB domain
        db1 = obj1._state.db
        db2 = obj2._state.db
        if db1 == db2:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if db == "default":
            # Only migrate control-plane apps on default DB
            return app_label in CONTROL_PLANE_APPS
        if db.startswith("tenant_"):
            # Only migrate tenant apps on tenant DBs
            return app_label in TENANT_APPS
        return None


def register_tenant_db(tenant) -> None:
    """
    Dynamically add a tenant's DB configuration to settings.DATABASES.

    Called during signup (after provisioning) and lazily per-request
    by TenantMiddleware when a tenant alias is not yet registered.
    """
    alias = tenant.get_db_alias()
    if alias not in settings.DATABASES:
        settings.DATABASES[alias] = tenant.get_db_config()
