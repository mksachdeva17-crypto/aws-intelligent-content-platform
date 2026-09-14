---
title: AWS Intelligent Content Platform — MVP 1 ten-day implementation plan
status: aligned-to-shared-conversation-not-yet-started
updated: 2026-09-14
source: https://chatgpt.com/share/6aa82bd1-34ec-83e9-8c8c-8ec50eaebad3
---

# MVP 1: ten days, three hours per day

This plan follows the [latest shared product discussion](https://chatgpt.com/share/6aa82bd1-34ec-83e9-8c8c-8ec50eaebad3), especially its generated architecture diagram and final Day 1–10 schedule. It **replaces** the earlier approval-only Day 1 and the service-bingo implementation plan. The two goals are a credible multi-industry CMS foundation and hands-on SAA-C03 architecture practice. Each day has a hard **3-hour maximum**: 45 minutes architecture, 90 minutes implementation, 45 minutes code walkthrough/interview reasoning. Do not convert the last block into extra coding.

## Product contract

The core is generic: `ContentType`, `ContentEntry`, field definitions, asset, taxonomy, locale, version, workflow, channel and publish-target concepts. It must never special-case Article, Product, Mortgage Offer, Insurance Policy or Sports Team. Those become configurations or later industry packs. MVP 1 implements **one simple demo experience** and proves that at least three very different content types can be represented without modifying core code.

Management and delivery are separate: editors use Cognito → API Gateway → Lambda → DynamoDB; readers use CloudFront → published JSON in S3. EventBridge and SQS decouple publishing and search. The [architecture baseline](../../docs/architecture-approval.md) is the build contract. The [generic model](../../docs/generic-content-model.md) supersedes the earlier Article-first example.

The [original architecture diagram](../../docs/assets/aws-intelligent-content-platform-architecture.png) is committed as the visual reference. The text baseline clarifies the durable event path and stage-by-stage delivery.

## Day-by-day build gates

| Day | 90-minute implementation focus | AWS/architecture study in the other blocks | Definition of done |
| --- | --- | --- | --- |
| **1 — Foundation + generic CRUD** | Repository/Terraform base; API Gateway + Lambda + DynamoDB; generic `ContentType` and `ContentEntry` envelopes; `POST /content`, `GET /content/{id}`, `PUT /content/{id}`. Deploy the thin slice to AWS when access/budget are available. No Article/Product branch in core. | Serverless vs EC2/ECS, DynamoDB keys/hot partitions, Lambda/API limits, future tenant/site scoping. Interview: **How does this handle 1M API requests?** | Create, read and update arbitrary `fields` in AWS; tests pass; Terraform deploy and smoke commands documented. If cloud access is unavailable, code/IaC can be built but **Day 1 remains pending**, not passed. |
| **2 — Assets + delivery separation** | Private S3 asset bucket and presigned upload; asset metadata/reference; separate published-content S3 bucket and CloudFront. Add a minimal temporary publish action that writes static JSON; Day 3 replaces its orchestration with async flow. | S3 durability, origin access, cache TTL/invalidation, static vs dynamic delivery. Interview: **How do 10M news-page hits avoid crushing authoring APIs?** | Upload an image, reference it from content, and fetch published JSON via CloudFront without invoking the authoring API. |
| **3 — Event-driven publishing** | `ContentPublished` contract, EventBridge bus/rule, SQS publish queue + DLQ, publisher Lambda writing S3. Persist publish intent durably with content state (outbox or equivalent); the queue worker is retry-safe. | EventBridge vs SNS vs SQS, choreography vs synchronous publish, at-least-once processing, failure/replay. Interview: **What if the worker fails after Publish is clicked?** | A publish request eventually updates S3 through the queue; intentional failure/retry/DLQ path is demonstrated without losing intent. |
| **4 — Scale and back-pressure** | Load script, API throttling, Lambda reserved concurrency, SQS batch size/concurrency, stable publish idempotency key and duplicate-handling test. | Downstream rate limits, queue depth/age, exponential backoff and hot partitions. Interview: **How do 2M imported products flow into search limited to 500 writes/sec?** | A bounded load test shows queue growth and recovery without uncontrolled worker fan-out or duplicate effects. Do not generate a million paid AWS requests. |
| **5 — Dynamic schemas + taxonomy** | ContentType/Schema API with field definitions and validation; basic taxonomy. Configure `article`, `product` and `mortgage-offer` without core code changes. | Configuration vs code, schema evolution, references, DynamoDB access patterns. Interview: **How can one CMS model media, commerce and banking content?** | Three different content types accept valid entries, reject invalid fields, and attach taxonomy through the same core API. |
| **6 — Search and discovery** | Separate SQS search queue and indexer Lambda; OpenSearch index and simple search API. Reindex command reads authoritative published content. | Search vs primary database, eventual consistency, denormalization, reindexing and OpenSearch cost. Interview: **Why is OpenSearch not the source of truth?** | Published entries are searchable by text/taxonomy; rebuilding a deleted index from source is demonstrated or dry-run verified under cost guardrails. |
| **7 — Authentication and security** | Cognito sign-in; AUTHOR/EDITOR/ADMIN checks on management APIs; least-privilege Lambda IAM; S3 Block Public Access and encryption. | Authentication vs authorization, tenant-isolation design, IAM vs Cognito, KMS, Secrets Manager and WAF alternatives. Interview: **How is Tenant A prevented from reading Tenant B?** | Authenticated author can create; anonymous or unauthorized calls fail; delivery remains public only for published assets/content. Single tenant is implemented, tenant/site fields are not ignored. |
| **8 — Workflow, versions, visibility** | `DRAFT → REVIEW → APPROVED → PUBLISHED` transition rules; immutable version records; Step Functions only for a genuinely multi-step review/publish path; CloudWatch logs, metrics, dashboard and alarm. | Orchestration vs events, partial failure, version history, queue age, tracing. Interview: **Why did publishing rise to 20 minutes?** | Submit/approve/publish flow works, prior version is recoverable, and a forced publish failure is diagnosable from logs/metrics. |
| **9 — Resilience and DR** | Enable/test DynamoDB PITR and S3 versioning where affordable; run one recovery drill; write regional recovery runbook with RTO/RPO and active-passive vs active-active decision. **No expensive live multi-region build.** | Multi-AZ vs multi-region, Global Tables, replication, failover, cost vs resilience. Interview: **What survives a Region outage?** | Recovery evidence and a clearly bounded production DR design exist. This day includes hands-on restore work even though multi-region remains design-only. |
| **10 — Consolidation + interview demo** | Clean Terraform, tests, README, ADRs and one repeatable end-to-end demo: define type → create entry → attach asset → review → publish → EventBridge/SQS → S3/CloudFront → OpenSearch; rerun failure/load checks. No large new feature. | Defend latency, scale, availability, durability, consistency, security, observability, cost and DR choices. | Fresh-clone setup and demo work; for each major AWS component, explain why it exists, how it fails/scales, an alternative and the accepted trade-off. |

## Daily evidence, not just activity

Every day records: code/IaC changed, tests run, AWS resources touched, result of one smoke/failure test, cost impact, and the answer to that day's interview question. `docs/daily/` can hold these short records. A day is not complete merely because a service was provisioned or a diagram was drawn.

## MVP scope boundaries

Implemented: generic dynamic content types and entries, basic versions/taxonomy/assets, draft/publish, events/SQS, static S3/CloudFront delivery, basic OpenSearch, authentication, monitoring and Terraform. Locale, channel, publish-target and tenant/site are **first-class model/port concepts**; only one tenant, a basic locale path, one website channel and an S3 publish-target adapter need run in MVP 1.

Designed/stubbed: richer localization, AI, multi-region DR, extension SDK and additional publish targets. Later: advanced workflows, full multi-tenancy and complete industry packs. The CMS manages product descriptions or banking content; it does **not** implement carts, payments, account balances or claims processing. No speculative ECS/RDS/analytics side projects are scheduled in these three-hour days.

## Prerequisites and truthfulness

The shared plan expects a Day 1 AWS deployment. That requires an AWS account/profile, selected region, spending ceiling and appropriate permissions. None is inferred from the shared conversation. Until available, local code and Terraform validation can progress, but an AWS-dependent DoD remains pending. Expensive resources such as OpenSearch require a cost check before provisioning. The architecture diagram is a target, not evidence that any component is deployed.
