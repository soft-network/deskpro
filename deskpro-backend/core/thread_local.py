"""
Thread-local storage for the current tenant's database alias.

Each request sets a tenant DB alias at the start and clears it after
(handled by TenantMiddleware). This ensures ORM queries are routed to
the correct Neon database for the authenticated tenant.
"""
import threading

_thread_locals = threading.local()


def set_current_tenant_db(alias: str) -> None:
    """Set the DB alias for the current thread."""
    _thread_locals.tenant_db = alias


def get_current_tenant_db() -> str | None:
    """Return the DB alias for the current thread, or None if not set."""
    return getattr(_thread_locals, "tenant_db", None)


def clear_current_tenant_db() -> None:
    """Clear the tenant DB alias from the current thread."""
    if hasattr(_thread_locals, "tenant_db"):
        del _thread_locals.tenant_db
