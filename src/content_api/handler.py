"""API Gateway HTTP API v2 Lambda entry point."""

from __future__ import annotations

import base64
import binascii
import json
import os

from .repository import DynamoContentRepository
from .service import ContentError, ContentService


def _response(status: int, body: dict) -> dict:
    return {"statusCode": status, "headers": {"content-type": "application/json"},
            "body": json.dumps(body, separators=(",", ":"))}


def _body(event: dict) -> dict:
    raw = event.get("body")
    if raw is None:
        raise ContentError("JSON body is required")
    if event.get("isBase64Encoded"):
        try:
            raw = base64.b64decode(raw, validate=True).decode("utf-8")
        except (ValueError, UnicodeError, binascii.Error) as error:
            raise ContentError("body must be valid base64-encoded UTF-8") from error
    try:
        value = json.loads(raw)
    except (ValueError, TypeError) as error:
        raise ContentError("body must be valid JSON") from error
    if not isinstance(value, dict):
        raise ContentError("body must be an object")
    return value


def lambda_handler(event: dict, _context, service: ContentService | None = None) -> dict:
    try:
        method = event.get("requestContext", {}).get("http", {}).get("method")
        route = event.get("routeKey")
        if route not in {"POST /content", "GET /content/{id}", "PUT /content/{id}"}:
            return _response(404, {"error": "route not found"})
        if service is None:
            service = ContentService(DynamoContentRepository(os.environ["TABLE_NAME"]))
        if method == "POST" and route == "POST /content":
            return _response(201, service.create(_body(event)))
        params = event.get("pathParameters") or {}
        query = event.get("queryStringParameters") or {}
        entry_id = params.get("id")
        tenant_id, site_id = query.get("tenantId"), query.get("siteId")
        if method == "GET" and route == "GET /content/{id}":
            return _response(200, service.get(entry_id, tenant_id, site_id))
        if method == "PUT" and route == "PUT /content/{id}":
            return _response(200, service.update(entry_id, tenant_id, site_id, _body(event)))
        return _response(404, {"error": "route not found"})
    except ContentError as error:
        return _response(error.status_code, {"error": str(error)})
