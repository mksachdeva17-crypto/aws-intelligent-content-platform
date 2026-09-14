"""DynamoDB adapter with atomic pointer + immutable version writes."""

from __future__ import annotations

import json
import os

from .service import Conflict, Scope


def _key(scope: Scope, entry_id: str) -> str:
    # Length-prefixed components avoid delimiter collisions in caller-provided IDs.
    parts = (scope.tenant_id, scope.site_id, entry_id)
    return "".join(f"{len(part)}:{part}" for part in parts)


class DynamoContentRepository:
    def __init__(self, table_name: str, client=None):
        import boto3

        self.client = client or boto3.client("dynamodb", endpoint_url=os.environ.get("AWS_ENDPOINT_URL"))
        self.table_name = table_name

    @staticmethod
    def _item(entry: dict, sort_key: str) -> dict:
        scope = Scope(entry["tenantId"], entry["siteId"])
        return {
            "pk": {"S": _key(scope, entry["id"])},
            "sk": {"S": sort_key},
            "entry": {"S": json.dumps(entry, separators=(",", ":"))},
            "version": {"N": str(entry["version"])},
        }

    def create(self, entry: dict) -> None:
        from botocore.exceptions import ClientError

        try:
            self.client.transact_write_items(TransactItems=[
                {"Put": {"TableName": self.table_name, "Item": self._item(entry, "CURRENT"),
                         "ConditionExpression": "attribute_not_exists(pk)"}},
                {"Put": {"TableName": self.table_name, "Item": self._item(entry, "VERSION#00000001"),
                         "ConditionExpression": "attribute_not_exists(pk)"}},
            ])
        except ClientError as error:
            if error.response.get("Error", {}).get("Code") == "TransactionCanceledException":
                raise Conflict("content already exists") from error
            raise

    def get(self, scope: Scope, entry_id: str) -> dict | None:
        result = self.client.get_item(
            TableName=self.table_name,
            Key={"pk": {"S": _key(scope, entry_id)}, "sk": {"S": "CURRENT"}},
            ConsistentRead=True,
        )
        item = result.get("Item")
        return json.loads(item["entry"]["S"]) if item else None

    def update(self, entry: dict, expected_version: int) -> None:
        from botocore.exceptions import ClientError

        try:
            self.client.transact_write_items(TransactItems=[
                {"Put": {"TableName": self.table_name, "Item": self._item(entry, "CURRENT"),
                         "ConditionExpression": "#v = :expected",
                         "ExpressionAttributeNames": {"#v": "version"},
                         "ExpressionAttributeValues": {":expected": {"N": str(expected_version)}}}},
                {"Put": {"TableName": self.table_name,
                         "Item": self._item(entry, f"VERSION#{entry['version']:08d}"),
                         "ConditionExpression": "attribute_not_exists(pk)"}},
            ])
        except ClientError as error:
            if error.response.get("Error", {}).get("Code") == "TransactionCanceledException":
                raise Conflict("stale version") from error
            raise
