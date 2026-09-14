"""Run the IAM-signed Day 1 management API smoke test after deployment."""

import argparse
import json
import subprocess
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import boto3
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest


def call(session, region, method, url, body=None):
    encoded = json.dumps(body).encode("utf-8") if body is not None else None
    headers = {"Content-Type": "application/json"} if encoded is not None else {}
    signed = AWSRequest(method=method, url=url, data=encoded, headers=headers)
    credentials = session.get_credentials()
    if credentials is None:
        raise RuntimeError("AWS credentials are required")
    SigV4Auth(credentials.get_frozen_credentials(), "execute-api", region).add_auth(signed)
    request = Request(url, data=encoded, method=method, headers=dict(signed.headers.items()))
    try:
        with urlopen(request, timeout=20) as response:
            return response.status, json.load(response)
    except HTTPError as error:
        return error.code, json.loads(error.read())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True, help="terraform output management_api_url")
    parser.add_argument("--region", required=True)
    parser.add_argument("--profile", help="AWS CLI profile (otherwise use default credential chain)")
    args = parser.parse_args()
    if args.profile:
        result = subprocess.run(
            ["aws", "configure", "export-credentials", "--profile", args.profile, "--format", "process"],
            check=True,
            capture_output=True,
            text=True,
        )
        credentials = json.loads(result.stdout)
        session = boto3.Session(
            aws_access_key_id=credentials["AccessKeyId"],
            aws_secret_access_key=credentials["SecretAccessKey"],
            aws_session_token=credentials.get("SessionToken"),
            region_name=args.region,
        )
    else:
        session = boto3.Session(region_name=args.region)
    base = args.url.rstrip("/")
    scope = {"tenantId": "demo", "siteId": "demo-site"}
    product = {**scope, "contentType": "product", "locale": "en-CA", "status": "DRAFT",
               "fields": {"name": "Day 1 smoke", "price": 12.5}}
    article = {**scope, "contentType": "article", "locale": "en-CA", "status": "DRAFT",
               "fields": {"headline": "Same generic API"}}
    status, created_product = call(session, args.region, "POST", f"{base}/content", product)
    assert status == 201, (status, created_product)
    status, created_article = call(session, args.region, "POST", f"{base}/content", article)
    assert status == 201, (status, created_article)
    product_url = f"{base}/content/{created_product['id']}?{urlencode(scope)}"
    article_url = f"{base}/content/{created_article['id']}?{urlencode(scope)}"
    status, fetched_product = call(session, args.region, "GET", product_url)
    assert status == 200 and fetched_product == created_product, (status, fetched_product)
    status, fetched_article = call(session, args.region, "GET", article_url)
    assert status == 200 and fetched_article == created_article, (status, fetched_article)
    status, updated = call(session, args.region, "PUT", product_url, {**product, "version": 1,
                                                                       "fields": {"name": "Updated", "price": 10.5}})
    assert status == 200 and updated["version"] == 2, (status, updated)
    status, conflict = call(session, args.region, "PUT", product_url, {**product, "version": 1})
    assert status == 409, (status, conflict)
    print(json.dumps({"result": "PASS", "productId": created_product["id"],
                      "articleId": created_article["id"], "version": updated["version"]}))


if __name__ == "__main__":
    main()
