"""Pure content rules; AWS-specific persistence lives in repository.py."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4


class ContentError(Exception):
    status_code = 400


class NotFound(ContentError):
    status_code = 404


class Conflict(ContentError):
    status_code = 409


@dataclass(frozen=True)
class Scope:
    tenant_id: str
    site_id: str


def _required_string(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContentError(f"{name} must be a non-empty string")
    return value.strip()


def _scope(data: dict) -> Scope:
    return Scope(
        _required_string(data.get("tenantId"), "tenantId"),
        _required_string(data.get("siteId"), "siteId"),
    )


def _fields(data: dict) -> dict:
    value = data.get("fields")
    if not isinstance(value, dict):
        raise ContentError("fields must be an object")
    return value


def _taxonomy(data: dict) -> list[str]:
    value = data.get("taxonomy", [])
    if not isinstance(value, list) or any(not isinstance(x, str) or not x.strip() for x in value):
        raise ContentError("taxonomy must be an array of non-empty strings")
    return value


class ContentService:
    def __init__(self, repository):
        self.repository = repository

    def create(self, data: dict) -> dict:
        if not isinstance(data, dict):
            raise ContentError("body must be an object")
        scope = _scope(data)
        if "id" in data:
            raise ContentError("id is server-generated on create")
        if data.get("status", "DRAFT") != "DRAFT":
            raise ContentError("Day 1 only supports DRAFT status")
        if "version" in data and (type(data["version"]) is not int or data["version"] != 1):
            raise ContentError("create version must be 1")
        entry = {
            "id": str(uuid4()),
            "tenantId": scope.tenant_id,
            "siteId": scope.site_id,
            "contentType": _required_string(data.get("contentType"), "contentType"),
            "locale": _required_string(data.get("locale"), "locale"),
            "status": "DRAFT",
            "version": 1,
            "fields": _fields(data),
            "taxonomy": _taxonomy(data),
        }
        self.repository.create(entry)
        return entry

    def get(self, entry_id: str, tenant_id: str, site_id: str) -> dict:
        scope = Scope(_required_string(tenant_id, "tenantId"), _required_string(site_id, "siteId"))
        entry = self.repository.get(scope, _required_string(entry_id, "id"))
        if entry is None:
            raise NotFound("content not found")
        return entry

    def update(self, entry_id: str, tenant_id: str, site_id: str, data: dict) -> dict:
        if not isinstance(data, dict):
            raise ContentError("body must be an object")
        scope = Scope(_required_string(tenant_id, "tenantId"), _required_string(site_id, "siteId"))
        if _scope(data) != scope:
            raise ContentError("body scope must match request scope")
        if "id" in data and data["id"] != entry_id:
            raise ContentError("body id must match URL id")
        expected = data.get("version")
        if isinstance(expected, bool) or not isinstance(expected, int) or expected < 1:
            raise ContentError("version must be a positive integer")
        if data.get("status", "DRAFT") != "DRAFT":
            raise ContentError("Day 1 only supports DRAFT status")
        current = self.get(entry_id, tenant_id, site_id)
        content_type = _required_string(data.get("contentType"), "contentType")
        if content_type != current["contentType"]:
            raise ContentError("contentType cannot change")
        updated = {
            **current,
            "locale": _required_string(data.get("locale"), "locale"),
            "fields": _fields(data),
            "taxonomy": _taxonomy(data),
            "version": expected + 1,
        }
        self.repository.update(updated, expected)
        return updated
