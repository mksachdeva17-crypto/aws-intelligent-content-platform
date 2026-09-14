import { ConflictError } from "./service.js";

function scopedKey(scope, entryId) {
  return [scope.tenantId, scope.siteId, entryId]
    .map((part) => `${part.length}:${part}`)
    .join("");
}

export class DynamoContentRepository {
  constructor(tableName, client = null) {
    this.tableName = tableName;
    this.client = client;
    this.sdkPromise = null;
  }

  static item(entry, sortKey) {
    return {
      pk: { S: scopedKey(entry, entry.id) },
      sk: { S: sortKey },
      entry: { S: JSON.stringify(entry) },
      version: { N: String(entry.version) },
    };
  }

  async sdk() {
    this.sdkPromise ??= import("@aws-sdk/client-dynamodb");
    const sdk = await this.sdkPromise;
    this.client ??= new sdk.DynamoDBClient({
      endpoint: process.env.AWS_ENDPOINT_URL || undefined,
    });
    return sdk;
  }

  async create(entry) {
    const { TransactWriteItemsCommand } = await this.sdk();
    try {
      await this.client.send(new TransactWriteItemsCommand({
        TransactItems: [
          { Put: { TableName: this.tableName, Item: DynamoContentRepository.item(entry, "CURRENT"),
            ConditionExpression: "attribute_not_exists(pk)" } },
          { Put: { TableName: this.tableName, Item: DynamoContentRepository.item(entry, "VERSION#00000001"),
            ConditionExpression: "attribute_not_exists(pk)" } },
        ],
      }));
    } catch (error) {
      if (error?.name === "TransactionCanceledException") {
        throw new ConflictError("content already exists");
      }
      throw error;
    }
  }

  async get(scope, entryId) {
    const { GetItemCommand } = await this.sdk();
    const result = await this.client.send(new GetItemCommand({
      TableName: this.tableName,
      Key: { pk: { S: scopedKey(scope, entryId) }, sk: { S: "CURRENT" } },
      ConsistentRead: true,
    }));
    return result.Item ? JSON.parse(result.Item.entry.S) : null;
  }

  async update(entry, expectedVersion) {
    const { TransactWriteItemsCommand } = await this.sdk();
    try {
      await this.client.send(new TransactWriteItemsCommand({
        TransactItems: [
          { Put: { TableName: this.tableName, Item: DynamoContentRepository.item(entry, "CURRENT"),
            ConditionExpression: "#v = :expected",
            ExpressionAttributeNames: { "#v": "version" },
            ExpressionAttributeValues: { ":expected": { N: String(expectedVersion) } } } },
          { Put: { TableName: this.tableName,
            Item: DynamoContentRepository.item(entry, `VERSION#${String(entry.version).padStart(8, "0")}`),
            ConditionExpression: "attribute_not_exists(pk)" } },
        ],
      }));
    } catch (error) {
      if (error?.name === "TransactionCanceledException") {
        throw new ConflictError("stale version");
      }
      throw error;
    }
  }
}

export { scopedKey };
