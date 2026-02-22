"""
Custom JWT token that injects tenant_slug, email, and full_name into claims.

Uses manual token construction because Agent is no longer AUTH_USER_MODEL
(SaasAdmin is), so for_user() would fail or reference the wrong model.
"""
from rest_framework_simplejwt.tokens import RefreshToken


class TenantRefreshToken(RefreshToken):
    """Refresh token with tenant-aware custom claims."""

    @classmethod
    def for_agent(cls, agent) -> "TenantRefreshToken":
        token = cls()
        token["user_id"] = agent.pk
        token["tenant_slug"] = agent.tenant_slug
        token["email"] = agent.email
        token["full_name"] = agent.full_name
        return token
