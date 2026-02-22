import uuid

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Ticket",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("subject", models.CharField(max_length=500)),
                ("customer_name", models.CharField(max_length=255)),
                ("customer_email", models.EmailField(max_length=254)),
                ("status", models.CharField(
                    choices=[("open", "Open"), ("pending", "Pending"), ("resolved", "Resolved"), ("closed", "Closed")],
                    default="open", max_length=20
                )),
                ("priority", models.CharField(
                    choices=[("low", "Low"), ("medium", "Medium"), ("high", "High"), ("urgent", "Urgent")],
                    default="medium", max_length=20
                )),
                ("channel", models.CharField(
                    choices=[("email", "Email"), ("chat", "Chat"), ("phone", "Phone"), ("web", "Web")],
                    default="email", max_length=20
                )),
                ("assignee", models.CharField(blank=True, max_length=255)),
                ("tags", django.contrib.postgres.fields.ArrayField(
                    base_field=models.CharField(max_length=100),
                    blank=True,
                    default=list,
                    size=None,
                )),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "app_label": "tickets",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="TicketMessage",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("sender", models.CharField(max_length=255)),
                ("body", models.TextField()),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                ("ticket", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="messages",
                    to="tickets.ticket",
                )),
            ],
            options={
                "app_label": "tickets",
                "ordering": ["timestamp"],
            },
        ),
    ]
