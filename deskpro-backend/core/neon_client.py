"""
Neon Management API v2 wrapper.

Docs: https://api-docs.neon.tech/reference/getting-started-with-neon-api

Each call uses the NEON_API_KEY and NEON_PROJECT_ID from Django settings.
All Tenant DBs share the same Neon role (NEON_ROLE_NAME); isolation is
achieved via distinct database names.
"""
import logging
from dataclasses import dataclass

import httpx
from django.conf import settings

logger = logging.getLogger(__name__)

NEON_API_BASE = "https://console.neon.tech/api/v2"


@dataclass
class TenantDBCredentials:
    host: str
    user: str
    password: str
    database_name: str
    port: int = 5432


class NeonClient:
    """Thin wrapper around the Neon Management API v2."""

    def __init__(self):
        self.api_key: str = settings.NEON_API_KEY
        self.project_id: str = settings.NEON_PROJECT_ID
        self.role_name: str = settings.NEON_ROLE_NAME

    @property
    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def _get(self, path: str) -> dict:
        url = f"{NEON_API_BASE}{path}"
        response = httpx.get(url, headers=self._headers, timeout=30)
        response.raise_for_status()
        return response.json()

    def _post(self, path: str, json: dict) -> dict:
        url = f"{NEON_API_BASE}{path}"
        response = httpx.post(url, headers=self._headers, json=json, timeout=30)
        response.raise_for_status()
        return response.json()

    def _delete(self, path: str) -> dict:
        url = f"{NEON_API_BASE}{path}"
        response = httpx.delete(url, headers=self._headers, timeout=30)
        response.raise_for_status()
        return response.json()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_primary_branch_id(self) -> str:
        """Return the project's primary branch ID."""
        data = self._get(f"/projects/{self.project_id}/branches")
        for branch in data.get("branches", []):
            if branch.get("primary"):
                return branch["id"]
        raise RuntimeError(
            f"No primary branch found for project {self.project_id}"
        )

    def _get_read_write_host(self) -> str:
        """Return the read-write endpoint host for the project."""
        data = self._get(f"/projects/{self.project_id}/endpoints")
        for endpoint in data.get("endpoints", []):
            if endpoint.get("type") == "read_write":
                return endpoint["host"]
        raise RuntimeError(
            f"No read-write endpoint found for project {self.project_id}"
        )

    def _reveal_password(self, branch_id: str) -> str:
        """Reveal the plaintext password for the Neon role."""
        data = self._get(
            f"/projects/{self.project_id}/branches/{branch_id}"
            f"/roles/{self.role_name}/reveal_password"
        )
        return data["password"]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def create_database(self, database_name: str) -> TenantDBCredentials:
        """
        Create a new database on the primary branch and return DB credentials.

        Steps:
          1. Resolve primary branch ID
          2. Create database on that branch
          3. Resolve read-write host
          4. Reveal role password
        """
        logger.info("Creating Neon database: %s", database_name)

        branch_id = self._get_primary_branch_id()

        self._post(
            f"/projects/{self.project_id}/branches/{branch_id}/databases",
            {"database": {"name": database_name, "owner_name": self.role_name}},
        )

        host = self._get_read_write_host()
        password = self._reveal_password(branch_id)

        logger.info("Successfully created database '%s' on host '%s'", database_name, host)

        return TenantDBCredentials(
            host=host,
            user=self.role_name,
            password=password,
            database_name=database_name,
            port=5432,
        )

    def delete_database(self, database_name: str) -> dict:
        """
        Delete a database from the primary branch (for tenant offboarding).
        """
        logger.info("Deleting Neon database: %s", database_name)
        branch_id = self._get_primary_branch_id()
        result = self._delete(
            f"/projects/{self.project_id}/branches/{branch_id}"
            f"/databases/{database_name}"
        )
        logger.info("Deleted database '%s'", database_name)
        return result

    def list_databases(self) -> list[dict]:
        """ (for debugging)."""
        branch_id = self._get_primary_branch_id()
        data = self._get(
            f"/projects/{self.project_id}/branches/{branch_id}/databases"
        )
        return data.get("databases", [])
