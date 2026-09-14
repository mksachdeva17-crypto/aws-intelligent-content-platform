---
title: AWS Intelligent Content Platform — Product Brief
status: superseded
created: 2026-09-14
updated: 2026-09-14
---

# Product brief

> Superseded as a ten-day scope statement by the [SAA-C03 implementation plan](../../saa-c03-10-day-plan.md). Its core content vision remains useful, but the prior narrow MVP is not the active target.

## Thesis

Enterprise publishers need to create structured content once and deliver it across channels without treating translation, taxonomy, or portability as bolt-ons. This project tests that thesis with a small AWS-native, headless CMS foundation. It is an independent prototype inspired by the user's CMS experience, not a Bell product or an assertion that it already outperforms Arc XP.

## Problem and audience

Authors and editors need to manage related language variants, discover content through consistent tags/categories, keep a trustworthy edit history, and publish a reviewed version without exposing drafts. Delivery consumers need a stable published representation. The first audience is a small editorial team and the developer integrating its public API. A large media/telecom organization is a reference scenario, not a committed customer.

## First-version solution

Represent each article as a language-neutral identity with English and French variants. Each variant has immutable revisions and independent draft/published pointers. Taxonomy and asset references are portable IDs rather than vendor-specific page markup. The system supports a draft → publish flow and a read-only delivery API. A publish event establishes the seam for later search indexing, cache invalidation, and analytics.

## Differentiation to test, not claim

- Multilingual identity and per-locale publishing in the core model.
- First-class tagging and categories, rather than a later plugin.
- Portable structured content and export-friendly IDs/schemas.
- Event-driven extension seam for future AI, import, search and migration workflows.

These are design intentions. Competitive superiority, migration speed, and commercial value require later evidence.

## Ten-day success signal

A repeatable demo completes the EN/FR editorial journey in the roadmap and passes automated tests for validation, immutable revisions, optimistic conflicts, draft isolation, and idempotent event replay. A new contributor can run the demo from the README. This is a prototype acceptance target, not an SLA.

## Scope boundary

In: articles, EN/FR, tags/categories, asset references, draft/publish, revision history, authoring/delivery APIs, publish event contract, thin editor, minimal AWS infrastructure definition.

Out: AEM/Arc XP parity, Word import, AI generation/translation, image enhancement, full DAM, migrations, personalization, multi-region DR, production operations.

## Assumptions requiring review

- `[ASSUMPTION]` English and French are the only MVP locales.
- `[ASSUMPTION]` Article is the first content type; pages follow the same model later.
- `[ASSUMPTION]` A solo prototype and architecture showcase, rather than a production pilot, is the ten-day outcome.
- `[ASSUMPTION]` Editors publish each locale independently; no automatic fallback is exposed in the public API.

## Beyond the prototype

If the foundation works, prioritize Word ingestion with human review, AI-assisted metadata/translation, richer asset workflows, and migration adapters. Each should preserve the canonical model rather than change its identity rules.
