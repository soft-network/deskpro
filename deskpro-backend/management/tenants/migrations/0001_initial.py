import uuid

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Tenant",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=255)),
                ("slug", models.SlugField(max_length=50, unique=True)),
                ("neon_database_name", models.CharField(blank=True, max_length=255)),
                ("neon_db_host", models.CharField(blank=True, max_length=255)),
                ("neon_db_user", models.CharField(blank=True, max_length=255)),
                ("neon_db_password", models.CharField(blank=True, max_length=255)),
                ("neon_db_port", models.PositiveIntegerField(default=5432)),
                ("is_active", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "app_label": "tenants",
            },
        ),
    ]
