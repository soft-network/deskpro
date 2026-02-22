"""
TenantMiddleware — extracts tenant_slug from JWT cookie and sets thread-local DB alias.

Flow per request:
  1. Clear any leftover thread-local state
  2. Skip public paths (no auth required)
  3. Read JWT from httpOnly cookie "access_token"
  4. Extract tenant_slug from JWT payload
  5. Ensure tenant DB is registered in settings.DATABASES
  6. Set thread-local DB alias to f"tenant_{slug}"
  7. Execute the view
  8. Clean up thread-local state
"""
import logging

from django.conf import settings
from django.http import HttpRequest, JsonResponse

from core.thread_local import clear_current_tenant_db, set_current_tenant_db

logger = logging.getLogger(__name__)

# Paths accessible without a valid tenant JWT cookie
PUBLIC_PATHS = {
    "/api/tenants/",   # signup + delete — each endpoint handles its own auth
    "/api/auth/login",
    "/api/auth/logout",
    "/api/auth/me",    # reads JWT directly, no tenant DB needed
    "/api/docs",
    "/api/openapi.json",
    "/admin/",
    "/admin",
    "/favicon.ico",
}


def _is_public(path: str) -> bool:
    return any(path.startswith(p) for p in PUBLIC_PATHS)


def _decode_token(token: str) -> dict | None:
    """Decode a JWT access token and return its payload, or None on failure."""
    try:
        from rest_framework_simplejwt.tokens import AccessToken

        decoded = AccessToken(token)
        return dict(decoded.payload)
    except Exception:
        return None


class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        clear_current_tenant_db()

        try:
            if not _is_public(request.path):
                token = request.COOKIES.get("access_token")
                if not token:
                    return JsonResponse(
                        {"detail": "Not authenticated."},
                        status=401,
                    )

                payload = _decode_token(token)

                if payload is None:
                    return JsonResponse(
                        {"detail": "Invalid or expired token."},
                        status=401,
                    )

                tenant_slug = payload.get("tenant_slug")
                if not tenant_slug:
                    return JsonResponse(
                        {"detail": "Token missing tenant_slug claim."},
                        status=401,
                    )

                db_alias = f"tenant_{tenant_slug}"

                # Lazily register tenant DB if not already loaded
                if db_alias not in settings.DATABASES:
                    self._load_tenant_db(tenant_slug, db_alias)
                    if db_alias not in settings.DATABASES:
                        return JsonResponse(
                            {"detail": f"Tenant '{tenant_slug}' not found or inactive."},
                            status=404,
                        )

                set_current_tenant_db(db_alias)

            response = self.get_response(request)
        finally:
            clear_current_tenant_db()

        return response

    @staticmethod
    def _load_tenant_db(tenant_slug: str, db_alias: str) -> None:
        """Load a single tenant's DB config from the Control Plane DB."""
        try:
            from management.tenants.models import Tenant
            from core.db_router import register_tenant_db

            tenant = Tenant.objects.using("default").get(
                slug=tenant_slug, is_active=True
            )
            register_tenant_db(tenant)
        except Exception as exc:
            logger.warning("Could not load tenant DB for '%s': %s", tenant_slug, exc)
