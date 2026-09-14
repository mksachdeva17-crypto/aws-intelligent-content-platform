---
title: AWS Intelligent Content Platform — MVP epics and stories
status: superseded
created: 2026-09-14
updated: 2026-09-14
sources: ["prds/prd-aws-intelligent-content-platform-2026-09-14/prd.md", "architecture/architecture-aws-intelligent-content-platform-2026-09-14/ARCHITECTURE-SPINE.md"]
---

# MVP epics and stories

> Superseded on 2026-09-14 by the [SAA-C03 implementation plan](saa-c03-10-day-plan.md). Stories will be re-cut after architecture approval.

This is a working decomposition of the PRD for the [ten-day plan](10-day-plan.md). It is not a claim that BMAD's interactive readiness gate or product-owner review has passed. Every acceptance criterion is observable in local tests or the demo.

## E1 — Content contract and authoring

**S1 (Day 2) — Validate the canonical Article model.** As an Author, I can create valid structured Article input and get actionable errors for invalid input. Traces FR-1, FR-3, NFR-4.

- AC1: Valid EN and FR fixtures parse and retain one `contentId` across locales.
- AC2: Empty title/body, unsupported locale, duplicate Tag IDs and unsupported block type return field-specific validation errors.
- AC3: Schema-versioned JSON contains no AWS keys or ARNs.

**S2 (Day 3) — Save immutable Draft Revisions.** As an Author, I can revise a draft without losing history. Traces FR-4, FR-5.

- AC1: Save creates a new Revision and advances only the matching Locale Variant's Draft Revision pointer.
- AC2: The previous Revision remains unchanged and listable.
- AC3: Two saves against the same expected Revision yield one success and one conflict; restore creates a new Revision.

**S3 (Day 4) — Manage locales and taxonomy.** As an Author, I can link FR to an EN Content Item and select governed Category/Tag IDs. Traces FR-2, FR-3, FR-9.

- AC1: One Content Item has distinct EN/FR Locale Variants and Revision chains.
- AC2: Duplicate locale, unknown Category/Tag IDs and cyclic Category parenting are rejected.
- AC3: Administrator can manage taxonomy; Author cannot change governed terms.

## E2 — Publishing and delivery

**S4 (Day 5) — Publish one locale.** As an Editor, I can select a Draft Revision and make its immutable Published Snapshot available to delivery consumers. Traces FR-6, FR-7, NFR-1.

- AC1: Publishing EN does not expose FR; unpublished FR delivery returns not found.
- AC2: Editing EN after publication leaves the English delivery response unchanged.
- AC3: Author publish attempt is forbidden; invalid Revision-to-Locale pairing is rejected.

**S5 (Day 6) — Emit and replay Publish Events safely.** As a downstream integrator, I can process publication without duplicate effects. Traces FR-8, NFR-3.

- AC1: One successful publish records one durable Publish Event with stable IDs and schema version.
- AC2: Replaying the same event twice produces one effective side effect.
- AC3: Simulated dispatcher failure leaves an event eligible for retry without losing the Published Snapshot.

## E3 — AWS foundation

**S6 (Day 7) — Define a minimal AWS deployment.** As a maintainer, I can inspect and validate infrastructure for the same contracts. Traces FR-10, NFR-5, AD-5–AD-7.

- AC1: Terraform validates without creating resources and names all billable services.
- AC2: DynamoDB/S3/EventBridge/SQS/API/Lambda permissions are scoped to required actions; no embedded credentials.
- AC3: README separates local demo from optional cloud deployment and states prerequisites/budget approval.

## E4 — Author experience and proof

**S7 (Day 8) — Complete a thin editorial flow.** As an Editor, I can draft, localize, tag and publish through a minimal UI. Traces UJ-1–UJ-3, FR-1–FR-7.

- AC1: Keyboard-only path can create EN, add FR, select taxonomy and publish EN.
- AC2: Validation and conflict messages identify the field/action and preserve unsaved input.
- AC3: UI clearly distinguishes Draft Revision from Published Snapshot per locale.

**S8 (Day 9) — Harden access and failure paths.** As a maintainer, I can see safe errors and diagnose failed operations. Traces FR-9, NFR-1–NFR-7.

- AC1: Anonymous draft/history request fails; role matrix passes automated API tests.
- AC2: Publish retries, event duplicates and stale updates have deterministic outcomes.
- AC3: Logs include correlation IDs but exclude credentials and draft bodies; accessibility smoke check passes.

**S9 (Day 10) — Deliver a repeatable demonstration.** As a new contributor, I can run the local journey and understand the architecture and gaps. Traces FR-10, SM-1–SM-3.

- AC1: Fresh-clone README commands seed data, start the system and run tests.
- AC2: Demo proves EN published, FR unpublished and post-publish English draft isolation.
- AC3: Handoff lists known risks, cloud cost assumptions, deferred features and next stories without parity claims.

## Readiness notes

S1 can start once locale-code policy is confirmed or explicitly frozen as a reversible assumption. S4 depends on per-locale publication policy. S6 cannot become a live deployment without an AWS account, region and spend cap. All stories remain draft until the PRD assumptions are reviewed.
