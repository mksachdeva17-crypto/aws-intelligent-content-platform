# Canonical Content Model v1 (Day 1 contract)

> Historical Article-first draft, superseded by the [generic MVP 1 content model](generic-content-model.md) after the latest shared architecture discussion. The EN/FR examples remain useful test fixtures but must not define core classes or Day 1 validation rules.

This model is storage-agnostic. DynamoDB keys, S3 object keys, ARNs and delivery URLs are implementation mappings, never canonical identifiers. The [PRD](../_bmad-output/planning-artifacts/prds/prd-aws-intelligent-content-platform-2026-09-14/prd.md) defines behavior; this file defines identity and invariants. Choices below are provisional until the user reviews the marked assumptions.

## Entities and ownership

| Entity | Identity | Owns / references |
| --- | --- | --- |
| Content Item | `contentId` | `contentType`, schema version, available locales |
| Locale Variant | `(contentId, locale)` | Draft Revision pointer, Published Snapshot pointer |
| Revision | `revisionId` | Immutable editorial payload, taxonomy IDs, asset references, creation metadata |
| Published Snapshot | `publishId` | Copy of exactly one Revision's delivery fields for one locale |
| Category | `categoryId` | Governed label and optional parent Category |
| Tag | `tagId` | Reusable label; no parent |
| Asset | `assetId` | Media metadata and binary storage mapping outside content JSON |
| Publish Event | `eventId` | One publish transition, schema version and reference IDs |

`contentId` does not change across translations. Revisions belong to exactly one Locale Variant. A `revisionId` is globally unique and immutable. A Published Snapshot may be superseded by a later publish but is not rewritten. Deletion/retention policy is deferred; no hard-delete operation is part of the MVP.

## Article Revision payload

```text
schemaVersion: 1
contentId: stable UUID
contentType: "article"
locale: "en" | "fr"                 [ASSUMPTION: generic language codes]
revisionId: stable UUID
revisionNumber: positive integer, monotonic within (contentId, locale)
title: non-empty plain text
slug: locale-specific, non-empty URL segment
summary: optional plain text
body: ordered array of typed blocks (v1: paragraph, heading)
categoryIds: zero or one category ID in v1
tagIds: unique array of tag IDs
assetRefs: array of {assetId, role, mediaType, altText?}
createdAt: ISO 8601 UTC timestamp
createdBy: actor ID
```

`body` blocks have `blockId`, `type`, and type-specific fields. Unknown block types are rejected by the v1 validator; later types require a schema version or explicit compatibility rule. `heading` has `level` 2–4 and `text`; `paragraph` has `text`. Images remain Asset References rather than embedded body bytes. For image references, `altText` must be non-empty unless the image is explicitly decorative; the decorative flag is deferred from the first example.

## Lifecycle

```text
Create locale -> Revision 1, Draft Revision = Revision 1, Published Snapshot = none
Save(expected Draft Revision) -> new immutable Revision, advance Draft Revision
Restore(old Revision) -> new immutable Revision copied from old, advance Draft Revision
Publish(selected Draft Revision) -> immutable Published Snapshot, advance published pointer, emit Publish Event
Save after publish -> new Draft Revision; Published Snapshot is unchanged
```

A request with a stale expected Draft Revision must fail with a conflict. Publishing checks that the selected Revision belongs to the same Locale Variant. English and French pointers are independent; one locale may be published while the other remains draft. The Delivery API reads only Published Snapshots and returns not found for a locale with none. No automatic fallback in v1.

## Taxonomy and portability rules

- A Category is hierarchical, but cycles are forbidden. A Tag is not hierarchical.
- Revision payloads store IDs, not mutable taxonomy labels. Labels may be localized later without rewriting history.
- IDs are not database keys or vendor names. Content export includes schema version, records and referenced taxonomy/asset manifests.
- Slug uniqueness is per locale within the prototype's single content space; multi-site/tenant namespace is deferred.
- Importers for Word, Arc XP or AEM may map into this model later; none are built in the ten-day MVP.

## Publish Event v1

```json
{
  "schemaVersion": 1,
  "eventType": "ContentPublished",
  "eventId": "uuid",
  "publishId": "uuid",
  "contentId": "uuid",
  "locale": "en",
  "revisionId": "uuid",
  "occurredAt": "2026-09-14T14:00:00Z"
}
```

Consumers deduplicate by `eventId` or the publish-specific idempotency key. At-least-once delivery means duplicates are expected, not a data-quality surprise. The exact outbox/storage mechanism is chosen during implementation after access-pattern tests.

## Example records

- [English Locale Variant](../examples/article-en.json): published Revision 1, later draft Revision 2.
- [French Locale Variant](../examples/article-fr.json): draft Revision 1, not published.

Both use the same `contentId`, demonstrating independent state. Example UUIDs and editorial copy are synthetic.
