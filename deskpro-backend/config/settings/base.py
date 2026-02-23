"""
Base settings shared across all environments.
"""
import os
from datetime import timedelta
from pathlib import Path

from decouple import Config, RepositoryEnv

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load the correct .env file based on DJANGO_ENV
_django_env = os.environ.get("DJANGO_ENV", "dev")
_env_file = BASE_DIR / f".env.{_django_env}"
config = Config(RepositoryEnv(str(_env_file)))

# Security
SECRET_KEY = config("DJANGO_SECRET_KEY")
JWT_SECRET_KEY = config("JWT_SECRET_KEY")

DEBUG = False

ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="localhost,127.0.0.1").split(",")

# ---------------------------------------------------------------------------
# Installed Apps
# ---------------------------------------------------------------------------

# Django built-ins — framework infrastructure, always on 'default' DB
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
]

# Third-party packages
THIRD_PARTY_APPS = [
    "corsheaders",
    "ninja",
]

# Control-plane apps — shared, live on the central 'default' DB
# Migrations run only on 'default' (see TenantDatabaseRouter.allow_migrate)
CONTROL_PLANE_APPS = [
    "management.authentication.centralusers",   # SaasAdmin — must be first (defines AUTH_USER_MODEL)
    "management.tenants",                        # Tenant registry + provisioning API
]

# Tenant-scoped apps — isolated, each tenant gets its own DB
# Migrations run only on 'tenant_*' aliases (see TenantDatabaseRouter.allow_migrate)
TENANT_SCOPED_APPS = [
    "management.authentication.tenantusers",    # Agent (per-tenant user accounts)
    "apps.tickets",                              # Helpdesk tickets + messages
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + CONTROL_PLANE_APPS + TENANT_SCOPED_APPS

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "core.middleware.TenantMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# Control Plane Database (Neon default DB)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("CONTROL_DB_NAME", default="neondb"),
        "USER": config("CONTROL_DB_USER", default="neondb_owner"),
        "PASSWORD": config("CONTROL_DB_PASSWORD"),
        "HOST": config("CONTROL_DB_HOST"),
        "PORT": config("CONTROL_DB_PORT", default="5432"),
        "OPTIONS": {
            "sslmode": "require",
        },
    }
}

DATABASE_ROUTERS = ["core.db_router.TenantDatabaseRouter"]

# Custom User Model
AUTH_USER_MODEL = "staff.SaasAdmin"

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# JWT Settings
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "SIGNING_KEY": JWT_SECRET_KEY,
    "ALGORITHM": "HS256",
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}

# Neon API
NEON_API_KEY = config("NEON_API_KEY")
NEON_PROJECT_ID = config("NEON_PROJECT_ID")
NEON_ROLE_NAME = config("NEON_ROLE_NAME", default="neondb_owner")

# Admin API key — protects internal management endpoints (e.g. DELETE /api/tenants/{slug})
ADMIN_API_KEY = config("ADMIN_API_KEY")

# Field-level encryption key for sensitive DB columns (e.g. Tenant.neon_db_password).
# Generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
FIELD_ENCRYPTION_KEY = config("FIELD_ENCRYPTION_KEY")

# SaaS Admin superuser — used by the create_saas_admin management command
SAAS_ADMIN_EMAIL = config("SAAS_ADMIN_EMAIL", default="admin@deskpro.dev")
SAAS_ADMIN_PASSWORD = config("SAAS_ADMIN_PASSWORD")
SAAS_ADMIN_FULL_NAME = config("SAAS_ADMIN_FULL_NAME", default="")

