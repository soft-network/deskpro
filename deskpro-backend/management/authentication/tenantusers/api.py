"""
Accounts API.

POST /api/auth/login   — authenticate and set httpOnly JWT cookies
POST /api/auth/logout  — clear JWT cookies
"""
import json
import logging

from django.http import HttpResponse
from ninja import Router
from ninja.errors import HttpError

from management.authentication.tenantusers.schemas import LoginIn
from management.authentication.tenantusers.tokens import TenantRefreshToken

logger = logging.getLogger(__name__)

router = Router(tags=["Auth"])

# Cookie settings — httpOnly so JavaScript cannot read the token
_COOKIE = dict(httponly=True, samesite="Lax", path="/")


@router.post("/login", auth=None)
def login(request, payload: LoginIn):
    """
    Authenticate an Agent and return user info.
    Access and refresh JWTs are stored in httpOnly cookies (not in the response body).
    """
    from django.conf import settings

    db_alias = f"tenant_{payload.tenant_slug}"

    if db_alias not in settings.DATABASES:
        _try_load_tenant_db(payload.tenant_slug, db_alias)

    if db_alias not in settings.DATABASES:
        raise HttpError(404, f"Tenant '{payload.tenant_slug}' not found.")

    from management.authentication.tenantusers.models import Agent

    try:
        agent = Agent.objects.using(db_alias).get(email=payload.email)
    except Agent.DoesNotExist:
        raise HttpError(401, "Invalid credentials.")

    if not agent.check_password(payload.password):
        raise HttpError(401, "Invalid credentials.")

    if not agent.is_active:
        raise HttpError(403, "Account is inactive.")

    refresh = TenantRefreshToken.for_agent(agent)
    access = refresh.access_token

    response = HttpResponse(
        json.dumps({"email": agent.email, "full_name": agent.full_name}),
        content_type="application/json",
        status=200,
    )
    response.set_cookie("access_token", str(access), max_age=3600, **_COOKIE)
    response.set_cookie("refresh_token", str(refresh), max_age=7 * 24 * 3600, **_COOKIE)
    return response


@router.get("/me")
def me(request):
    """Return the current user's info from the JWT cookie."""
    token = request.COOKIES.get("access_token")
    if not token:
        from ninja.errors import HttpError
        raise HttpError(401, "Not authenticated.")
    try:
        from rest_framework_simplejwt.tokens import AccessToken
        payload = dict(AccessToken(token).payload)
    except Exception:
        from ninja.errors import HttpError
        raise HttpError(401, "Invalid or expired token.")
    return {"email": payload.get("email", ""), "full_name": payload.get("full_name", "")}


@router.post("/logout", auth=None)
def logout(request):
    """Clear the JWT cookies."""
    response = HttpResponse(
        json.dumps({"detail": "Logged out."}),
        content_type="application/json",
        status=200,
    )
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/")
    return response


def _try_load_tenant_db(tenant_slug: str, db_alias: str) -> None:
    try:
        from management.tenants.models import Tenant
        from core.db_router import register_tenant_db

        tenant = Tenant.objects.using("default").get(
            slug=tenant_slug, is_active=True
        )
        register_tenant_db(tenant)
    except Exception as exc:
        logger.warning("Could not load tenant DB '%s': %s", tenant_slug, exc)
