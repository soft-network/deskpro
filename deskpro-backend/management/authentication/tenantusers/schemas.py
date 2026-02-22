"""Pydantic schemas for accounts API."""
from ninja import Schema


class LoginIn(Schema):
    email: str
    tenant_slug: str
    password: str


class LoginOut(Schema):
    email: str
    full_name: str
