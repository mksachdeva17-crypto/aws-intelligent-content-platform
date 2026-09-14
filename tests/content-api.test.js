import assert from "node:assert/strict";
import test from "node:test";

import { createHandler } from "../src/content-api/handler.js";
import { DynamoContentRepository } from "../src/content-api/repository.js";
import { ConflictError, ContentError, ContentService } from "../src/content-api/service.js";

class MemoryRepository {
  constructor() {
    this.current = new Map();
    this.versions = new Map();
  }

  key(scope, entryId) {
    return `${scope.tenantId}\u0000${scope.siteId}\u0000${entryId}`;
  }

  async create(entry) {
    const key = this.key(entry, entry.id);
    if (this.current.has(key)) throw new ConflictError("content already exists");
    this.current.set(key, structuredClone(entry));
    this.versions.set(`${key}\u00001`, structuredClone(entry));
  }

  async get(scope, entryId) {
    const entry = this.current.get(this.key(scope, entryId));
    return entry ? structuredClone(entry) : null;
  }

  async update(entry, expectedVersion) {
    const key = this.key(entry, entry.id);
    if (this.current.get(key).version !== expectedVersion) throw new ConflictError("stale version");
    this.current.set(key, structuredClone(entry));
    this.versions.set(`${key}\u0000${entry.version}`, structuredClone(entry));
  }
}

function payload(contentType = "product", fields = { name: "Example" }) {
  return {
    tenantId: "demo",
    siteId: "demo-site",
    contentType,
    locale: "en-CA",
    status: "DRAFT",
    fields,
  };
}

function apiEvent(method, routeKey, { body, query, entryId } = {}) {
  return {
    requestContext: { http: { method } },
    routeKey,
    queryStringParameters: query,
    pathParameters: entryId ? { id: entryId } : undefined,
    ...(body === undefined ? {} : { body: JSON.stringify(body) }),
  };
}

async function call(service, method, routeKey, options) {
  const result = await createHandler(service)(apiEvent(method, routeKey, options));
  return [result.statusCode, JSON.parse(result.body)];
}

test("two content types use the same CRUD path and versions remain immutable", async () => {
  const repository = new MemoryRepository();
  const service = new ContentService(repository);
  const product = await service.create(payload("product", { price: 129.99 }));
  const article = await service.create(payload("article", { headline: "News" }));

  assert.deepEqual((await service.get(product.id, "demo", "demo-site")).fields, { price: 129.99 });
  assert.deepEqual((await service.get(article.id, "demo", "demo-site")).fields, { headline: "News" });
  const updated = await service.update(product.id, "demo", "demo-site", {
    ...payload("product", { price: 109.99 }), version: 1,
  });
  assert.equal(updated.version, 2);
  const key = repository.key(product, product.id);
  assert.deepEqual(repository.versions.get(`${key}\u00001`).fields, { price: 129.99 });
  await assert.rejects(
    service.update(product.id, "demo", "demo-site", {
      ...payload("product", { price: 99 }), version: 1,
    }),
    ConflictError,
  );
});

test("scope and generic envelope validation reject invalid data", async () => {
  const service = new ContentService(new MemoryRepository());
  const entry = await service.create(payload());
  await assert.rejects(service.create({ ...payload(), fields: [] }), ContentError);
  await assert.rejects(service.create({ ...payload(), tenantId: "" }), ContentError);
  await assert.rejects(service.update(entry.id, "demo", "demo-site", {
    ...payload(), siteId: "other", version: 1,
  }), ContentError);
  await assert.rejects(service.update(entry.id, "demo", "demo-site", {
    ...payload("article"), version: 1,
  }), ContentError);
  await assert.rejects(service.create({ ...payload(), status: "PUBLISHED" }), ContentError);
  await assert.rejects(service.create({ ...payload(), version: true }), ContentError);
  await assert.rejects(service.create({ ...payload(), id: "client-chosen" }), ContentError);
});

test("reads cannot cross tenant or site scope", async () => {
  const service = new ContentService(new MemoryRepository());
  const entry = await service.create(payload());
  await assert.rejects(
    service.get(entry.id, "other", "demo-site"),
    (error) => error instanceof ContentError && error.statusCode === 404,
  );
});

test("handler creates, reads, updates, and returns expected failures", async () => {
  const service = new ContentService(new MemoryRepository());
  const [createStatus, created] = await call(service, "POST", "POST /content", { body: payload() });
  assert.equal(createStatus, 201);
  const query = { tenantId: "demo", siteId: "demo-site" };
  const [getStatus, found] = await call(service, "GET", "GET /content/{id}", {
    query, entryId: created.id,
  });
  assert.equal(getStatus, 200);
  assert.deepEqual(found, created);
  const [updateStatus, updated] = await call(service, "PUT", "PUT /content/{id}", {
    body: { ...payload(), version: 1 }, query, entryId: created.id,
  });
  assert.equal(updateStatus, 200);
  assert.equal(updated.version, 2);
  assert.equal((await call(service, "PUT", "PUT /content/{id}", {
    body: { ...payload(), version: 1 }, query, entryId: created.id,
  }))[0], 409);
  assert.equal((await call(service, "GET", "GET /content/{id}", { entryId: "x" }))[0], 400);
  assert.equal((await call(service, "GET", "GET /content/{id}", { query, entryId: "x" }))[0], 404);
  const invalid = await createHandler(service)({
    requestContext: { http: { method: "POST" } }, routeKey: "POST /content", body: "not-json",
  });
  assert.equal(invalid.statusCode, 400);
});

test("DynamoDB item shape uses a collision-safe scoped key", () => {
  const entry = { ...payload("product", { price: 129.99 }), id: "entry-1", version: 1 };
  const item = DynamoContentRepository.item(entry, "CURRENT");
  assert.equal(item.pk.S, "4:demo9:demo-site7:entry-1");
  assert.equal(item.sk.S, "CURRENT");
  assert.deepEqual(JSON.parse(item.entry.S), entry);
});
