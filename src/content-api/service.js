import { randomUUID } from "node:crypto";

export class ContentError extends Error {
  constructor(message, statusCode = 400) {
    super(message);
    this.name = this.constructor.name;
    this.statusCode = statusCode;
  }
}

export class NotFoundError extends ContentError {
  constructor(message) {
    super(message, 404);
  }
}

export class ConflictError extends ContentError {
  constructor(message) {
    super(message, 409);
  }
}

function requiredString(value, name) {
  if (typeof value !== "string" || value.trim() === "") {
    throw new ContentError(`${name} must be a non-empty string`);
  }
  return value.trim();
}

function scope(data) {
  return {
    tenantId: requiredString(data?.tenantId, "tenantId"),
    siteId: requiredString(data?.siteId, "siteId"),
  };
}

function fields(data) {
  const value = data?.fields;
  if (value === null || typeof value !== "object" || Array.isArray(value)) {
    throw new ContentError("fields must be an object");
  }
  return value;
}

function taxonomy(data) {
  const value = data?.taxonomy ?? [];
  if (!Array.isArray(value) || value.some((item) => typeof item !== "string" || item.trim() === "")) {
    throw new ContentError("taxonomy must be an array of non-empty strings");
  }
  return value;
}

export class ContentService {
  constructor(repository) {
    this.repository = repository;
  }

  async create(data) {
    if (data === null || typeof data !== "object" || Array.isArray(data)) {
      throw new ContentError("body must be an object");
    }
    const contentScope = scope(data);
    if (Object.hasOwn(data, "id")) {
      throw new ContentError("id is server-generated on create");
    }
    if ((data.status ?? "DRAFT") !== "DRAFT") {
      throw new ContentError("Day 1 only supports DRAFT status");
    }
    if (Object.hasOwn(data, "version") && data.version !== 1) {
      throw new ContentError("create version must be 1");
    }
    const entry = {
      id: randomUUID(),
      ...contentScope,
      contentType: requiredString(data.contentType, "contentType"),
      locale: requiredString(data.locale, "locale"),
      status: "DRAFT",
      version: 1,
      fields: fields(data),
      taxonomy: taxonomy(data),
    };
    await this.repository.create(entry);
    return entry;
  }

  async get(entryId, tenantId, siteId) {
    const contentScope = {
      tenantId: requiredString(tenantId, "tenantId"),
      siteId: requiredString(siteId, "siteId"),
    };
    const entry = await this.repository.get(contentScope, requiredString(entryId, "id"));
    if (!entry) {
      throw new NotFoundError("content not found");
    }
    return entry;
  }

  async update(entryId, tenantId, siteId, data) {
    if (data === null || typeof data !== "object" || Array.isArray(data)) {
      throw new ContentError("body must be an object");
    }
    const requestScope = {
      tenantId: requiredString(tenantId, "tenantId"),
      siteId: requiredString(siteId, "siteId"),
    };
    const bodyScope = scope(data);
    if (bodyScope.tenantId !== requestScope.tenantId || bodyScope.siteId !== requestScope.siteId) {
      throw new ContentError("body scope must match request scope");
    }
    if (Object.hasOwn(data, "id") && data.id !== entryId) {
      throw new ContentError("body id must match URL id");
    }
    if (!Number.isInteger(data.version) || data.version < 1) {
      throw new ContentError("version must be a positive integer");
    }
    if ((data.status ?? "DRAFT") !== "DRAFT") {
      throw new ContentError("Day 1 only supports DRAFT status");
    }
    const current = await this.get(entryId, tenantId, siteId);
    const contentType = requiredString(data.contentType, "contentType");
    if (contentType !== current.contentType) {
      throw new ContentError("contentType cannot change");
    }
    const updated = {
      ...current,
      locale: requiredString(data.locale, "locale"),
      fields: fields(data),
      taxonomy: taxonomy(data),
      version: data.version + 1,
    };
    await this.repository.update(updated, data.version);
    return updated;
  }
}
