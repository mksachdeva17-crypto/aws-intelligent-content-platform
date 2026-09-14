"""Exercise the real DynamoDB adapter against LocalStack Hobby's DynamoDB API."""

import argparse
import sys
from pathlib import Path

import boto3
from botocore.exceptions import ClientError

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from content_api.repository import DynamoContentRepository
from content_api.service import Conflict, ContentService


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--endpoint", default="http://127.0.0.1:4566")
    parser.add_argument("--region", default="ca-central-1")
    args = parser.parse_args()
    client = boto3.client("dynamodb", endpoint_url=args.endpoint, region_name=args.region,
                          aws_access_key_id="test", aws_secret_access_key="test")
    table_name = "intelligent-cms-local-content"
    try:
        client.create_table(
            TableName=table_name,
            AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"},
                                  {"AttributeName": "sk", "AttributeType": "S"}],
            KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"},
                       {"AttributeName": "sk", "KeyType": "RANGE"}],
            BillingMode="PAY_PER_REQUEST",
        )
    except ClientError as error:
        if error.response.get("Error", {}).get("Code") != "ResourceInUseException":
            raise
    service = ContentService(DynamoContentRepository(table_name, client=client))
    scope = {"tenantId": "demo", "siteId": "demo-site"}
    product = service.create({**scope, "contentType": "product", "locale": "en-CA",
                              "fields": {"price": 12.5}})
    article = service.create({**scope, "contentType": "article", "locale": "en-CA",
                              "fields": {"headline": "LocalStack"}})
    assert service.get(product["id"], **{"tenant_id": "demo", "site_id": "demo-site"}) == product
    assert service.get(article["id"], "demo", "demo-site") == article
    updated = service.update(product["id"], "demo", "demo-site",
                             {**scope, "contentType": "product", "locale": "en-CA",
                              "fields": {"price": 10.5}, "version": 1})
    assert updated["version"] == 2
    try:
        service.update(product["id"], "demo", "demo-site",
                       {**scope, "contentType": "product", "locale": "en-CA",
                        "fields": {"price": 9.5}, "version": 1})
    except Conflict:
        pass
    else:
        raise AssertionError("stale update was accepted")
    print("PASS: LocalStack DynamoDB adapter handled two types and a stale-write conflict")


if __name__ == "__main__":
    main()
