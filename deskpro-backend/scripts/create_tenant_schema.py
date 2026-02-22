#!/usr/bin/env python
"""
Run Django migrations on a specific tenant DB alias.

Usage:
    python scripts/create_tenant_schema.py <tenant_slug>

Example:
    python scripts/create_tenant_schema.py acme
"""
import os
import sys
from pathlib import Path

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

os.environ.setdefault("DJANGO_ENV", "dev")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"config.settings.{os.environ['DJANGO_ENV']}")

import django  # noqa: E402

django.setup()

from django.core.management import call_command  # noqa: E402

from management.tenants.models import Tenant  # noqa: E402
from core.db_router import register_tenant_db  # noqa: E402


def create_tenant_schema(tenant_slug: str) -> None:
    try:
        tenant = Tenant.objects.using("default").get(slug=tenant_slug)
    except Tenant.DoesNotExist:
        print(f"ERROR: Tenant '{tenant_slug}' not found in Control Plane DB.")
        sys.exit(1)

    db_alias = tenant.get_db_alias()
    register_tenant_db(tenant)

    print(f"Running migrations on '{db_alias}'...")
    call_command("migrate", "--database", db_alias, verbosity=1)
    print("Done.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/create_tenant_schema.py <tenant_slug>")
        sys.exit(1)

    create_tenant_schema(sys.argv[1])
