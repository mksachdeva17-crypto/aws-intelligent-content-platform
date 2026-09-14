---
title: AWS Intelligent Content Platform — MVP PRD
status: superseded
created: 2026-09-14
updated: 2026-09-14
---

# MVP PRD

> Superseded as a ten-day scope statement by the [SAA-C03 implementation plan](../../saa-c03-10-day-plan.md). Domain requirements remain inputs to the architecture approval, but this is not the full implementation PRD.

## Purpose and thesis

This is the product contract for a ten-working-day solo prototype. It turns the [brief](../../briefs/brief-aws-intelligent-content-platform-2026-09-14/brief.md) into testable requirements for the model, APIs and demo. The bet is that multilingual identity, taxonomy and portability must be modeled before adding an editor or AI features. The [canonical model](../../../../docs/content-model.md) defines the initial data shape; this PRD defines user-visible behavior.

## Target users and journeys

- **Author:** creates and revises content without accidentally exposing a draft.
- **Editor:** selects a reviewed revision and publishes a specific locale.
- **Administrator:** governs taxonomy and permissions for the prototype.
- **Delivery developer:** consumes stable published content through an API.

**UJ-1 — Maya authors an article.** Maya, an author, creates an English draft, enters title/body, selects a category and two tags, and adds an asset reference. A save creates an immutable revision. She can see its revision ID and edit further without changing earlier revisions.

**UJ-2 — Camille localizes it.** Camille opens the same Content Item and adds a French Locale Variant. The French draft has its own revision chain. She can compare which locales are published; neither draft is exposed to public consumers.

**UJ-3 — Jules publishes only English.** Jules, an editor, selects the current English Draft Revision and publishes it. A public request for `en` returns that exact snapshot; a public request for `fr` returns not found until French is independently published. Editing English afterward does not alter the published response.

**UJ-4 — Robin integrates delivery.** Robin calls the Delivery API by Content Item ID and locale, receives a schema-versioned Published Snapshot, and handles a clear not-found response for unpublished content.

## Glossary

- **Content Item:** language-neutral entity with one stable `contentId` and one or more Locale Variants.
- **Locale Variant:** a single locale of a Content Item, identified by `(contentId, locale)`.
- **Revision:** immutable version of a Locale Variant's editorial fields.
- **Draft Revision:** Revision currently selected for editing in a Locale Variant.
- **Published Snapshot:** immutable delivery copy of a selected Revision for one Locale Variant.
- **Category:** governed hierarchical taxonomy term.
- **Tag:** reusable non-hierarchical taxonomy term.
- **Asset Reference:** stable pointer to a binary asset and its metadata, not embedded bytes.
- **Publish Event:** `ContentPublished` record identifying the Published Snapshot.
- **Authoring API:** authenticated command/query surface for editorial work.
- **Delivery API:** read-only public surface that returns Published Snapshots only.

## Requirements

### Content and locale model

**FR-1 — Create Content Item.** An Author can create an Article Content Item with an English or French Locale Variant (UJ-1).

- A valid create returns a stable `contentId`, locale and first Revision ID.
- Unsupported locale, empty title or body, duplicate tags, or unknown taxonomy IDs are rejected with field-specific errors.

**FR-2 — Linked Locale Variant.** An Author can add the other supported Locale Variant to an existing Content Item (UJ-2).

- Both variants retain the same `contentId` and have independent Revision IDs and state pointers.
- Adding a second variant for the same locale is rejected.

**FR-3 — Taxonomy and Asset Reference.** An Author can attach existing Category and Tag IDs, and an optional Asset Reference, to a Revision (UJ-1).

- Category and Tag IDs remain separate types; unknown IDs are rejected.
- An Asset Reference includes an ID, media type and accessible alt text for images; binary content is not stored in a Revision.

### Revision and publish lifecycle

**FR-4 — Immutable Revision.** Saving changes creates a new Revision and advances the Draft Revision pointer (UJ-1).

- Prior Revision payloads remain byte-for-byte unchanged.
- An update with a stale expected revision is rejected as a conflict, not silently overwritten.

**FR-5 — History and restore.** An Author can list Revisions and restore a prior Revision as a new Draft Revision (UJ-1).

- Restore never rewrites or deletes the original Revision.

**FR-6 — Locale-specific publish.** An Editor can publish a selected Draft Revision, creating a Published Snapshot for that Locale Variant (UJ-3).

- Publishing English does not publish French; publishing does not mutate its source Revision.
- An Author without Editor permission cannot publish.
- The operation has a stable publish ID to support safe retries.

**FR-7 — Published delivery.** A Delivery API client can fetch the current Published Snapshot by Content Item ID and locale (UJ-3, UJ-4).

- An unpublished locale returns not found; drafts and unpublished revisions are never returned.
- The response contains `schemaVersion`, `contentId`, `locale`, Revision ID, taxonomy IDs and asset references.
- Later draft edits do not alter the response until a new publish succeeds.

**FR-8 — Publish Event.** A successful publish produces a Publish Event usable by downstream consumers.

- The event identifies its schema version, event ID, publish ID, Content Item ID, locale and Revision ID.
- Processing the same event twice has one effective side effect.

### Operations and access

**FR-9 — Role boundary.** Authoring commands require an Author, Editor or Administrator role. Only Editor/Administrator may publish; Administrator manages taxonomy.

- Anonymous calls cannot access draft or history routes.
- Role enforcement is tested at the API boundary; provider integration is a separate architecture decision.

**FR-10 — Repeatable demo.** A contributor can seed sample EN/FR content and execute UJ-1 through UJ-4 locally.

- README commands start the local system and run automated tests without a live AWS account.

## Cross-cutting quality requirements

- **NFR-1, data safety:** No Draft Revision may be returned by the Delivery API. Automated tests cover unpublished and post-publication-edit cases.
- **NFR-2, concurrency:** Concurrent updates with the same expected revision result in one success and one explicit conflict.
- **NFR-3, event delivery:** Publish consumers tolerate at-least-once delivery and out-of-order retries; no exactly-once claim.
- **NFR-4, portability:** IDs and JSON schema do not encode DynamoDB keys or AWS ARNs. Exported content can be interpreted without an AWS account.
- **NFR-5, cost control:** The local demo must not provision paid cloud resources. IaC validation is the Day 7 gate; a live deployment needs separate budget and account approval.
- **NFR-6, observability:** API and worker errors include a correlation ID in logs; no draft body or credentials in logs.
- **NFR-7, accessibility:** The thin editor uses labeled controls, keyboard-accessible actions and visible validation errors. Full audit is deferred.

## Explicit non-goals

No visual page builder, scheduled publishing, collaborative real-time editing, automatic locale fallback, bulk media processing, Word ingestion, generative AI, migration connector, OpenSearch index, production SLA, or Arc XP parity claim in this MVP.

## Success signals

- **SM-1:** UJ-1 through UJ-4 complete from the README with seeded content; validates FR-1–FR-10.
- **SM-2:** Automated tests prove 0 draft leaks in the specified negative cases; validates FR-7 and NFR-1.
- **SM-3:** Duplicate Publish Event replay produces 1 effective side effect; validates FR-8 and NFR-3.
- **Counter-metric:** Do not inflate service count or UI polish at the expense of a working, testable end-to-end slice.

## Assumptions and open questions

- `[ASSUMPTION]` Article is the sole implemented content type; Page is a later schema.
- `[ASSUMPTION]` MVP locales are `en` and `fr`, with no public fallback.
- `[ASSUMPTION]` The Day 8 UI can be thin and local; API behavior is the primary proof.
- `[ASSUMPTION]` Role checks can use local test identities before an identity provider is chosen.

1. Which AWS account, region, and monthly spend cap would be acceptable for an optional live deployment? No resource creation until answered.
2. Should the public locale codes be generic `en`/`fr` or region-specific (for example `en-CA`/`fr-CA`)? The initial model uses generic codes pending review.
3. Is independent publication per locale the desired editorial policy? It is the working assumption and must be confirmed before Day 5.

This PRD is a draft for review, not a claim of user-approved product decisions.
