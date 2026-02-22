"""
CookieAuth — Ninja cookie authentication class.

Reads the access_token from the httpOnly cookie set at login.
The decoded payload is available as `request.auth` in protected endpoints.
"""
from ninja.security import APIKeyCookie


class CookieAuth(APIKeyCookie):
    param_name = "access_token"

    def authenticate(self, request, key: str) -> dict | None:
        try:
            from rest_framework_simplejwt.tokens import AccessToken

            decoded = AccessToken(key)
            return dict(decoded.payload)
        except Exception:
            return None
