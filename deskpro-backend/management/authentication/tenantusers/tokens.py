"""
Custom JWT token that injects tenant_slug, email, and full_name into claims.

Uses manual token construction because TenantUser is no longer AUTH_USER_MODEL
(SaasAdmin is), so for_user() would fail or reference the wrong model.
"""
from rest_framework_simplejwt.tokens import RefreshToken


class TenantRefreshToken(RefreshToken):
    """Refresh token with tenant-aware custom claims."""

    @classmethod
    def for_user(cls, user) -> "TenantRefreshToken":
        token = cls()
        token["user_id"] = user.pk
        token["tenant_slug"] = user.tenant_slug
        token["email"] = user.email
        token["full_name"] = user.full_name
        return token
