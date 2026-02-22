"""
Development settings — DEBUG mode, permissive CORS.
"""
from .base import *  # noqa: F401, F403

DEBUG = True

# CORS_ALLOW_ALL_ORIGINS cannot be used together with CORS_ALLOW_CREDENTIALS.
# In dev we explicitly allow the frontend origin so cookies are forwarded.
CORS_ALLOWED_ORIGINS = ["http://localhost:3000"]
CORS_ALLOW_CREDENTIALS = True

# In dev, allow all hosts
ALLOWED_HOSTS = ["*"]

# Django Debug Toolbar (optional, uncomment to use)
# INSTALLED_APPS += ["debug_toolbar"]
# MIDDLEWARE = ["debug_toolbar.middleware.DebugToolbarMiddleware"] + MIDDLEWARE
