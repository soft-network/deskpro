"""
Auth classes for the Tenants API.
"""
from ninja.security import APIKeyHeader
from django.conf import settings


class AdminKeyAuth(APIKeyHeader):
    """
    Requires the X-Admin-Key header to match settings.ADMIN_API_KEY.
    Used for privileged control-plane operations (e.g. deleting tenants).
    """
    param_name = "X-Admin-Key"

    def authenticate(self, request, key: str):
        if key == settings.ADMIN_API_KEY:
            return key
        return None
