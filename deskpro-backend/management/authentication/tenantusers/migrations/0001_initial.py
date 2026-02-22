import django.utils.timezone
from django.db import migrations, models
import management.authentication.tenantusers.models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Agent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                ("last_login", models.DateTimeField(blank=True, null=True, verbose_name="last login")),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("full_name", models.CharField(blank=True, max_length=255)),
                ("tenant_slug", models.CharField(max_length=50)),
                ("is_staff", models.BooleanField(default=False)),
                ("is_active", models.BooleanField(default=True)),
                ("date_joined", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "app_label": "accounts",
            },
            managers=[
                ("objects", management.authentication.tenantusers.models.AgentManager()),
            ],
        ),
    ]
