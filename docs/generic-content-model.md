# Generic content model — MVP 1

Source: the [latest shared product discussion](https://chatgpt.com/share/6aa82bd1-34ec-83e9-8c8c-8ec50eaebad3). This supersedes the earlier [Article-specific draft](content-model.md). The core must not contain an `Article` class, article-only API or title/body requirement.

## Primitives

| Primitive | Minimum MVP meaning | Later extension |
| --- | --- | --- |
| Tenant / Site | Scope every major record with `tenantId` and `siteId`; run one synthetic tenant in MVP | Tenant administration and isolation policies |
| ContentType | Named, versioned set of Field Definitions | Industry packs and schema migrations |
| ContentEntry | Stable ID, type ID, locale, status and arbitrary typed `fields` | References and channel-specific projections |
| Field Definition | Name, type, required flag and optional constraints | Rich-text, references, lists and custom validators |
| Asset | Stable asset ID/metadata; bytes in private S3 | Renditions and full DAM |
| Taxonomy | Reusable category/tag terms referenced by ID | Hierarchies and localized labels |
| Locale | Entry's language/region identity, with future translation linkage | Fallback and translation workflows |
| Version | Immutable content snapshot and current pointer | Diff/restore and audit policy |
| Workflow | State transition rules | Custom multi-stage workflows |
| Channel | Where content is intended to be consumed | Website, mobile, partner API and more |
| PublishTarget | Port for materializing published content; S3 adapter in MVP | External APIs, feeds and partner destinations |
| Event | Schema-versioned lifecycle fact | Extension subscriptions |

## Day 1 envelope

The Day 1 CRUD endpoint accepts a **generic envelope**, not a fully validated industry schema. Day 5 adds ContentType field definitions and validation without changing the entry identity or URL.

```json
{
  "id": "entry-123",
  "tenantId": "demo",
  "siteId": "demo-site",
  "contentType": "product",
  "locale": "en-CA",
  "status": "DRAFT",
  "version": 1,
  "fields": {
    "name": "Running Shoes",
    "price": 129.99,
    "featuredImage": "asset-123"
  },
  "taxonomy": ["sports", "running"]
}
```

The same CRUD code must also store `article` and `mortgage-offer` entries with different `fields`. Day 1 validates the envelope/JSON type, identity and tenant/site scope, while Day 5 validates field definitions. `status` is authoring state; public delivery depends on a separate published S3 projection, never direct draft reads.

## Field definitions introduced on Day 5

Start with `text`, `rich-text`, `number`, `boolean`, `date`, `asset`, `reference`, `list`, `taxonomy` and `json` as the long-term vocabulary. Implement only types needed by the three demo schemas during this sprint; document unsupported types rather than accepting them silently. The `ContentType` definition is versioned so existing entries can be interpreted against the schema used at creation.

Example *configuration* (not core code):

```json
{
  "contentType": "mortgage-offer",
  "schemaVersion": 1,
  "fields": {
    "term": {"type": "text", "required": true},
    "rate": {"type": "number", "required": true},
    "offerType": {"type": "text", "required": true}
  }
}
```

Media `article` and ecommerce `product` definitions follow the same format. Neither makes the CMS a news site, a commerce checkout or a banking transaction engine.

## Identity, version and event rules

- `(tenantId, siteId, id)` is the access/ownership boundary; all reads and writes enforce it. Do not trust client-supplied tenant scope after Cognito is added on Day 7.
- A version is immutable. Updates use a conditional expected version; clients receive a conflict on stale writes.
- Locale and channel are data/ports from Day 1 but only one working locale path and website delivery channel are required in MVP 1. Translation relationships and fallback are later features.
- A publish request records durable intent and a stable publish ID; EventBridge/SQS may deliver events more than once. S3 projection and search indexer handle duplicates.
- Public URLs and exports contain canonical IDs and field values, not DynamoDB keys or ARNs.
