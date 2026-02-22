"""Pydantic schemas for the tenants API."""
import re

from ninja import Schema
from pydantic import field_validator


SLUG_RE = re.compile(r"^[a-z0-9-]{3,50}$")


class TenantSignupIn(Schema):
    name: str
    slug: str
    admin_email: str
    admin_password: str
    admin_full_name: str = ""

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v: str) -> str:
        if not SLUG_RE.match(v):
            raise ValueError(
                "Slug must be 3-50 characters and contain only lowercase "
                "letters, digits, and hyphens."
            )
        return v


class TenantSignupOut(Schema):
    id: str
    name: str
    slug: str
    message: str


class TenantDeleteOut(Schema):
    slug: str
    message: str
