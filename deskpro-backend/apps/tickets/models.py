"""
Ticket and TicketMessage models — live on Tenant DBs.

Tags are stored as a comma-separated text field for broad DB compatibility.
Use a JSONField or ArrayField if you know all Tenant DBs will be PostgreSQL
(Neon is Postgres, so ArrayField works — but requires django.contrib.postgres).
"""
import uuid

from django.contrib.postgres.fields import ArrayField
from django.db import models


class Ticket(models.Model):
    STATUS_CHOICES = [
        ("open", "Open"),
        ("pending", "Pending"),
        ("resolved", "Resolved"),
        ("closed", "Closed"),
    ]
    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("urgent", "Urgent"),
    ]
    CHANNEL_CHOICES = [
        ("email", "Email"),
        ("chat", "Chat"),
        ("phone", "Phone"),
        ("web", "Web"),
    ]

    subject = models.CharField(max_length=500)
    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="open")
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default="medium")
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES, default="email")
    assignee = models.CharField(max_length=255, blank=True)
    tags = ArrayField(models.CharField(max_length=100), default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "tickets"
        ordering = ["-created_at"]

    def __str__(self):
        return f"#{self.pk} — {self.subject}"


class TicketMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket = models.ForeignKey(
        Ticket, on_delete=models.CASCADE, related_name="messages"
    )
    sender = models.CharField(max_length=255)
    body = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "tickets"
        ordering = ["timestamp"]

    def __str__(self):
        return f"Message {self.id} on Ticket #{self.ticket_id}"
