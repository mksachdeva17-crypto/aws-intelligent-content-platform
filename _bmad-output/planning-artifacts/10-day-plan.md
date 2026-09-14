---
title: AWS Intelligent Content Platform — 10-day BMAD plan
status: superseded
created: 2026-09-14
updated: 2026-09-14
---

# Ten-day delivery plan

> Superseded on 2026-09-14 by the [SAA-C03 implementation plan](saa-c03-10-day-plan.md). Retained as history; its Day 2–10 sequence is not the active plan.

Ten focused working days, beginning 2026-09-14. This replaces the earlier four-week outline. The target is a demonstrable foundation, not a production CMS or a competitive parity claim. Each day ends with evidence; if a gate fails, reduce the next day's scope before adding features.

| Day | BMAD stage / focus | Planned result | Exit evidence |
| --- | --- | --- | --- |
| 1 — Sep 14 | Analysis + planning + solutioning | Brief, PRD, canonical model, architecture spine, prioritized roadmap | Documents and EN/FR examples agree; assumptions visible |
| 2 — Sep 15 | Story 1: model contract | TypeScript package for content model, runtime validation, unit tests | Invalid locales, missing titles, duplicate taxonomy IDs rejected |
| 3 — Sep 16 | Story 2: authoring core | Local API to create/read/update drafts with revision history | API tests prove immutable revisions and conflict response |
| 4 — Sep 17 | Story 3: taxonomy + locales | Tag/category CRUD and translation linkage | EN/FR drafts share identity; taxonomy references resolve |
| 5 — Sep 18 | Story 4: publish/deliver | Publish one locale and serve only its snapshot | Published response remains stable after draft edits |
| 6 — Sep 21 | Story 5: events | `ContentPublished` outbox/worker contract and idempotent handling | Replay same event twice produces one effective publish side effect |
| 7 — Sep 22 | AWS slice | Minimal Terraform for API/Lambda/DynamoDB/S3/EventBridge/SQS, with cost guardrails | `terraform validate` and local tests pass; no mandatory live deployment |
| 8 — Sep 23 | Authoring UX | Thin editor for draft, locale, taxonomy and publish | Manual EN/FR walkthrough succeeds against local API |
| 9 — Sep 24 | Hardening | Role checks, error handling, logging, accessibility and security review | Test suite, lint/type checks, threat checklist, and failure-path demo pass |
| 10 — Sep 25 | Demo + handoff | Seed data, end-to-end demo, architecture/cost notes, next-phase backlog | Repeatable demo from README; known gaps and decisions documented |

## Epics and story order

The [working epic/story breakdown](epics-and-stories.md) supplies acceptance criteria and PRD traceability.

1. **E1 — Content contract:** S1 canonical model and validation; S2 immutable draft revisions; S3 locale/taxonomy relationships.
2. **E2 — Publishing:** S4 locale publish snapshot and read-only delivery; S5 idempotent publish event handling.
3. **E3 — AWS foundation:** S6 deployable minimal infrastructure and least-privilege configuration.
4. **E4 — Author experience and proof:** S7 thin editor; S8 role/error/observability hardening; S9 repeatable demo and handoff.

Stories are sequenced by dependency, not by AWS-service count. At each story: define acceptance criteria, write failing contract tests, implement, run tests, and review the diff before treating it as done.

## MVP demonstration contract

An editor creates an English article, attaches tags/category and an asset reference, creates a linked French variant, revises both, publishes English only, and retrieves the English published snapshot through the delivery API. French remains unavailable until separately published. Replaying its publish event must not duplicate the effective side effect. No Word import, AI, DAM transformation, or Arc XP migration is implied.

## Decision gates and risks

- **After Day 1:** Confirm the assumptions in the PRD before locking implementation details.
- **After Day 5:** If the local vertical slice is incomplete, defer editor UI and AWS deployment; finish behavior and tests first.
- **After Day 7:** Deploy only with an AWS account, budget/region choice, and explicit approval. Terraform validation does not create resources.
- **Cost/security:** OpenSearch, Bedrock, CloudFront/WAF, multi-region DR and production-grade Cognito integration are deferred; they are not required to prove the thesis.
- **Tooling:** BMAD’s installed planning assets work locally. `bmad-build` needs `uv`; the runner remains uninstalled because package retrieval failed certificate verification. Do not disable TLS checks to work around this.

## Day 1 artifact map

- [Product brief](briefs/brief-aws-intelligent-content-platform-2026-09-14/brief.md)
- [PRD](prds/prd-aws-intelligent-content-platform-2026-09-14/prd.md)
- [Architecture spine](architecture/architecture-aws-intelligent-content-platform-2026-09-14/ARCHITECTURE-SPINE.md)
- [Canonical model](../../docs/content-model.md)
- [Day 1 checklist](../../docs/day-01-plan.md)
