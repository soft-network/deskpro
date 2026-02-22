"""
Management command: create_saas_admin

Creates or updates the SaaS superuser on the control-plane DB.
Credentials are read from settings (SAAS_ADMIN_EMAIL, SAAS_ADMIN_PASSWORD)
and can be overridden via CLI arguments.

Usage:
  # Use credentials from .env
  python manage.py create_saas_admin

  # Override credentials
  python manage.py create_saas_admin --email admin@example.com --password secret
"""
from django.conf import settings
from django.core.management.base import BaseCommand

from management.authentication.centralusers.models import SaasAdmin


class Command(BaseCommand):
    help = "Create or update the SaaS superuser (reads from .env by default)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--email",
            default=None,
            help="E-mail address (default: SAAS_ADMIN_EMAIL from .env)",
        )
        parser.add_argument(
            "--password",
            default=None,
            help="Password (default: SAAS_ADMIN_PASSWORD from .env)",
        )
        parser.add_argument(
            "--full-name",
            default=None,
            dest="full_name",
            help="Full name (default: SAAS_ADMIN_FULL_NAME from .env)",
        )

    def handle(self, *args, **options):
        email = options["email"] or settings.SAAS_ADMIN_EMAIL
        password = options["password"] or settings.SAAS_ADMIN_PASSWORD
        full_name = options["full_name"] or settings.SAAS_ADMIN_FULL_NAME

        admin, created = SaasAdmin.objects.using("default").get_or_create(
            email=email,
            defaults={"full_name": full_name, "is_staff": True, "is_superuser": True, "is_active": True},
        )

        admin.set_password(password)
        admin.is_staff = True
        admin.is_superuser = True
        admin.is_active = True

        if full_name:
            admin.full_name = full_name

        admin.save(using="default")

        action = "Created" if created else "Updated"
        self.stdout.write(self.style.SUCCESS(f"{action} SaaS admin: {email}"))
