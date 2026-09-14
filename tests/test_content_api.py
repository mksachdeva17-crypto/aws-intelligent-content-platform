"""Dependency-free Day 1 contract tests."""

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from content_api.handler import lambda_handler
from content_api.repository import DynamoContentRepository
from content_api.service import Conflict, ContentError, ContentService, Scope


class MemoryRepository:
    def __init__(self):
        self.current = {}
        self.versions = {}

    @staticmethod
    def key(scope, entry_id):
        return scope.tenant_id, scope.site_id, entry_id

    def create(self, entry):
        key = self.key(Scope(entry["tenantId"], entry["siteId"]), entry["id"])
        if key in self.current:
            raise Conflict("content already exists")
        self.current[key] = dict(entry)
        self.versions[key, 1] = dict(entry)

    def get(self, scope, entry_id):
        value = self.current.get(self.key(scope, entry_id))
        return dict(value) if value else None

    def update(self, entry, expected_version):
        key = self.key(Scope(entry["tenantId"], entry["siteId"]), entry["id"])
        if self.current[key]["version"] != expected_version:
            raise Conflict("stale version")
        self.current[key] = dict(entry)
        self.versions[key, entry["version"]] = dict(entry)


def payload(content_type="product", fields=None):
    return {"tenantId": "demo", "siteId": "demo-site", "contentType": content_type,
            "locale": "en-CA", "status": "DRAFT", "fields": fields or {"name": "Example"}}


class ContentServiceTests(unittest.TestCase):
    def setUp(self):
        self.repository = MemoryRepository()
        self.service = ContentService(self.repository)

    def test_two_types_use_same_crud_path_and_versions_are_immutable(self):
        product = self.service.create(payload("product", {"price": 129.99}))
        article = self.service.create(payload("article", {"headline": "News"}))
        self.assertEqual(self.service.get(product["id"], "demo", "demo-site")["fields"], {"price": 129.99})
        self.assertEqual(self.service.get(article["id"], "demo", "demo-site")["fields"], {"headline": "News"})
        updated = self.service.update(product["id"], "demo", "demo-site",
                                      {**payload("product", {"price": 109.99}), "version": 1})
        self.assertEqual(updated["version"], 2)
        key = self.repository.key(Scope("demo", "demo-site"), product["id"])
        self.assertEqual(self.repository.versions[key, 1]["fields"], {"price": 129.99})
        with self.assertRaises(Conflict):
            self.service.update(product["id"], "demo", "demo-site",
                                {**payload("product", {"price": 99}), "version": 1})

    def test_scope_and_envelope_validation(self):
        entry = self.service.create(payload())
        with self.assertRaises(ContentError):
            self.service.create({**payload(), "fields": []})
        with self.assertRaises(ContentError):
            self.service.create({**payload(), "tenantId": ""})
        with self.assertRaises(ContentError):
            self.service.update(entry["id"], "demo", "demo-site",
                                {**payload(), "siteId": "other", "version": 1})
        with self.assertRaises(ContentError):
            self.service.update(entry["id"], "demo", "demo-site",
                                {**payload(), "contentType": "article", "version": 1})
        with self.assertRaises(ContentError):
            self.service.create({**payload(), "status": "PUBLISHED"})
        with self.assertRaises(ContentError):
            self.service.create({**payload(), "version": True})
        with self.assertRaises(ContentError):
            self.service.create({**payload(), "id": "client-chosen"})

    def test_read_cannot_cross_scope(self):
        entry = self.service.create(payload())
        with self.assertRaises(ContentError) as error:
            self.service.get(entry["id"], "other", "demo-site")
        self.assertEqual(error.exception.status_code, 404)


class HandlerTests(unittest.TestCase):
    def setUp(self):
        self.service = ContentService(MemoryRepository())

    def call(self, method, route, body=None, query=None, entry_id=None):
        event = {"requestContext": {"http": {"method": method}}, "routeKey": route,
                 "queryStringParameters": query, "pathParameters": {"id": entry_id} if entry_id else None}
        if body is not None:
            event["body"] = json.dumps(body)
        response = lambda_handler(event, None, self.service)
        return response["statusCode"], json.loads(response["body"])

    def test_create_get_update(self):
        status, created = self.call("POST", "POST /content", payload())
        self.assertEqual(status, 201)
        query = {"tenantId": "demo", "siteId": "demo-site"}
        status, found = self.call("GET", "GET /content/{id}", query=query, entry_id=created["id"])
        self.assertEqual((status, found), (200, created))
        status, updated = self.call("PUT", "PUT /content/{id}",
                                    {**payload(), "version": 1}, query, created["id"])
        self.assertEqual((status, updated["version"]), (200, 2))
        status, _ = self.call("PUT", "PUT /content/{id}",
                              {**payload(), "version": 1}, query, created["id"])
        self.assertEqual(status, 409)

    def test_bad_json_missing_scope_and_missing_entry(self):
        self.assertEqual(self.call("GET", "GET /content/{id}", entry_id="x")[0], 400)
        self.assertEqual(self.call("GET", "GET /content/{id}",
                                   query={"tenantId": "demo", "siteId": "demo-site"}, entry_id="x")[0], 404)
        event = {"requestContext": {"http": {"method": "POST"}},
                 "routeKey": "POST /content", "body": "not-json"}
        self.assertEqual(lambda_handler(event, None, self.service)["statusCode"], 400)


class DynamoShapeTests(unittest.TestCase):
    def test_entry_snapshot_serializes_generic_fields_and_scoped_key(self):
        entry = {**payload("product", {"price": 129.99}), "id": "entry-1", "version": 1}
        item = DynamoContentRepository._item(entry, "CURRENT")
        self.assertEqual(item["pk"]["S"], "4:demo9:demo-site7:entry-1")
        self.assertEqual(item["sk"]["S"], "CURRENT")
        self.assertEqual(json.loads(item["entry"]["S"]), entry)


if __name__ == "__main__":
    unittest.main()
