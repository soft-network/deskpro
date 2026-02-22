"""
camelCase Pydantic schemas for the Tickets API.

Frontend expects camelCase field names (e.g. customerName, createdAt).
We use alias_generator so Django snake_case model fields map automatically.
"""
from datetime import datetime
from typing import Optional
from pydantic import ConfigDict

from ninja import Schema


def to_camel(s: str) -> str:
    """Convert snake_case to camelCase."""
    parts = s.split("_")
    return parts[0] + "".join(p.title() for p in parts[1:])


class CamelSchema(Schema):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class TicketMessageOut(CamelSchema):
    id: str
    sender: str
    body: str
    timestamp: datetime


class TicketOut(CamelSchema):
    id: int
    subject: str
    customer_name: str
    customer_email: str
    status: str
    priority: str
    channel: str
    assignee: str
    tags: list[str]
    created_at: datetime
    updated_at: datetime
    messages: list[TicketMessageOut] = []
