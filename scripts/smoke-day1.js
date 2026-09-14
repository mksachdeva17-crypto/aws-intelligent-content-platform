import { createHash, createHmac } from "node:crypto";
import { execFileSync } from "node:child_process";

function argument(name) {
  const index = process.argv.indexOf(`--${name}`);
  return index >= 0 ? process.argv[index + 1] : undefined;
}

const region = argument("region");
const profile = argument("profile");
const baseUrl = argument("url")?.replace(/\/$/, "");
if (!region || !profile || !baseUrl) {
  throw new Error("Usage: node scripts/smoke-day1.js --url <url> --region <region> --profile <profile>");
}

const credentials = JSON.parse(execFileSync("aws", [
  "configure", "export-credentials", "--profile", profile, "--format", "process",
], { encoding: "utf8" }));

const hash = (value) => createHash("sha256").update(value).digest("hex");
const hmac = (key, value, encoding) => createHmac("sha256", key).update(value).digest(encoding);
const encode = (value) => encodeURIComponent(value).replace(/[!'()*]/g, (character) =>
  `%${character.charCodeAt(0).toString(16).toUpperCase()}`);

async function call(method, rawUrl, requestBody) {
  const url = new URL(rawUrl);
  const payload = requestBody === undefined ? "" : JSON.stringify(requestBody);
  const now = new Date();
  const amzDate = now.toISOString().replace(/[:-]|\.\d{3}/g, "");
  const date = amzDate.slice(0, 8);
  const canonicalQuery = [...url.searchParams.entries()]
    .map(([key, value]) => [encode(key), encode(value)])
    .sort(([leftKey, leftValue], [rightKey, rightValue]) =>
      leftKey.localeCompare(rightKey) || leftValue.localeCompare(rightValue))
    .map(([key, value]) => `${key}=${value}`)
    .join("&");
  const headers = {
    host: url.host,
    "x-amz-date": amzDate,
    ...(credentials.SessionToken ? { "x-amz-security-token": credentials.SessionToken } : {}),
    ...(requestBody === undefined ? {} : { "content-type": "application/json" }),
  };
  const headerNames = Object.keys(headers).sort();
  const canonicalHeaders = headerNames.map((name) => `${name}:${headers[name].trim()}\n`).join("");
  const canonicalPath = url.pathname.split("/").map(encode).join("/");
  const canonicalRequest = [method, canonicalPath, canonicalQuery, canonicalHeaders,
    headerNames.join(";"), hash(payload)].join("\n");
  const scope = `${date}/${region}/execute-api/aws4_request`;
  const stringToSign = ["AWS4-HMAC-SHA256", amzDate, scope, hash(canonicalRequest)].join("\n");
  const dateKey = hmac(`AWS4${credentials.SecretAccessKey}`, date);
  const regionKey = hmac(dateKey, region);
  const serviceKey = hmac(regionKey, "execute-api");
  const signingKey = hmac(serviceKey, "aws4_request");
  headers.authorization = `AWS4-HMAC-SHA256 Credential=${credentials.AccessKeyId}/${scope}, ` +
    `SignedHeaders=${headerNames.join(";")}, Signature=${hmac(signingKey, stringToSign, "hex")}`;
  const response = await fetch(url, { method, headers, body: requestBody === undefined ? undefined : payload });
  const result = await response.json();
  return [response.status, result];
}

const scope = { tenantId: "demo", siteId: "demo-site" };
const product = { ...scope, contentType: "product", locale: "en-CA", status: "DRAFT",
  fields: { name: "Day 1 Node.js smoke", price: 12.5 } };
const article = { ...scope, contentType: "article", locale: "en-CA", status: "DRAFT",
  fields: { headline: "Same generic Node.js API" } };
const [productStatus, createdProduct] = await call("POST", `${baseUrl}/content`, product);
if (productStatus !== 201) throw new Error(JSON.stringify({ productStatus, createdProduct }));
const [articleStatus, createdArticle] = await call("POST", `${baseUrl}/content`, article);
if (articleStatus !== 201) throw new Error(JSON.stringify({ articleStatus, createdArticle }));
const query = new URLSearchParams(scope);
const productUrl = `${baseUrl}/content/${createdProduct.id}?${query}`;
const articleUrl = `${baseUrl}/content/${createdArticle.id}?${query}`;
const [getProductStatus, fetchedProduct] = await call("GET", productUrl);
if (getProductStatus !== 200 || JSON.stringify(fetchedProduct) !== JSON.stringify(createdProduct)) {
  throw new Error(JSON.stringify({ getProductStatus, fetchedProduct }));
}
const [getArticleStatus, fetchedArticle] = await call("GET", articleUrl);
if (getArticleStatus !== 200 || JSON.stringify(fetchedArticle) !== JSON.stringify(createdArticle)) {
  throw new Error(JSON.stringify({ getArticleStatus, fetchedArticle }));
}
const [updateStatus, updated] = await call("PUT", productUrl, {
  ...product, version: 1, fields: { name: "Updated by Node.js", price: 10.5 },
});
if (updateStatus !== 200 || updated.version !== 2) throw new Error(JSON.stringify({ updateStatus, updated }));
const [conflictStatus] = await call("PUT", productUrl, { ...product, version: 1 });
if (conflictStatus !== 409) throw new Error(`Expected stale update to return 409, received ${conflictStatus}`);
console.log(JSON.stringify({ result: "PASS", productId: createdProduct.id,
  articleId: createdArticle.id, version: updated.version }));
