#!/usr/bin/env python
"""
Run Django migrations on all active tenant DBs.

Usage:
    python scripts/migrate_all_tenants.py

Useful after adding a new migration to accounts or tickets apps.
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

os.environ.setdefault("DJANGO_ENV", "dev")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"config.settings.{os.environ['DJANGO_ENV']}")

import django  # noqa: E402

django.setup()

from django.core.management import call_command  # noqa: E402

from management.tenants.models import Tenant  # noqa: E402
from core.db_router import register_tenant_db  # noqa: E402


def migrate_all_tenants() -> None:
    tenants = Tenant.objects.using("default").filter(is_active=True)
    count = tenants.count()

    if count == 0:
        print("No active tenants found.")
        return

    print(f"Migrating {count} active tenant(s)...")

    for tenant in tenants:
        db_alias = tenant.get_db_alias()
        register_tenant_db(tenant)
        print(f"  → {db_alias} ({tenant.name})...")
        try:
            call_command("migrate", "--database", db_alias, verbosity=0)
            print(f"     ✓ Done.")
        except Exception as exc:
            print(f"     ✗ FAILED: {exc}")

    print("All tenant migrations complete.")


if __name__ == "__main__":
    migrate_all_tenants()
