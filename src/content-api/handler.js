import { DynamoContentRepository } from "./repository.js";
import { ContentError, ContentService } from "./service.js";

let defaultService;

function response(statusCode, body) {
  return {
    statusCode,
    headers: { "content-type": "application/json" },
    body: JSON.stringify(body),
  };
}

function body(event) {
  if (event.body === undefined || event.body === null) {
    throw new ContentError("JSON body is required");
  }
  let raw = event.body;
  if (event.isBase64Encoded) {
    try {
      raw = Buffer.from(raw, "base64").toString("utf8");
    } catch {
      throw new ContentError("body must be valid base64-encoded UTF-8");
    }
  }
  try {
    const parsed = JSON.parse(raw);
    if (parsed === null || typeof parsed !== "object" || Array.isArray(parsed)) {
      throw new ContentError("body must be an object");
    }
    return parsed;
  } catch (error) {
    if (error instanceof ContentError) throw error;
    throw new ContentError("body must be valid JSON");
  }
}

function service() {
  defaultService ??= new ContentService(new DynamoContentRepository(process.env.TABLE_NAME));
  return defaultService;
}

export function createHandler(injectedService = null) {
  return async function contentApiHandler(event) {
    try {
      const method = event.requestContext?.http?.method;
      const route = event.routeKey;
      if (!["POST /content", "GET /content/{id}", "PUT /content/{id}"].includes(route)) {
        return response(404, { error: "route not found" });
      }
      const contentService = injectedService ?? service();
      if (method === "POST" && route === "POST /content") {
        return response(201, await contentService.create(body(event)));
      }
      const entryId = event.pathParameters?.id;
      const tenantId = event.queryStringParameters?.tenantId;
      const siteId = event.queryStringParameters?.siteId;
      if (method === "GET" && route === "GET /content/{id}") {
        return response(200, await contentService.get(entryId, tenantId, siteId));
      }
      if (method === "PUT" && route === "PUT /content/{id}") {
        return response(200, await contentService.update(entryId, tenantId, siteId, body(event)));
      }
      return response(404, { error: "route not found" });
    } catch (error) {
      if (error instanceof ContentError) {
        return response(error.statusCode, { error: error.message });
      }
      throw error;
    }
  };
}

export const handler = createHandler();
