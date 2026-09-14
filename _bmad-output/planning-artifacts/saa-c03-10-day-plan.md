---
title: AWS Intelligent Content Platform — MVP 1 ten-day implementation plan
status: day-1-complete-day-2-pending
updated: 2026-09-14
source: https://chatgpt.com/share/6aa82bd1-34ec-83e9-8c8c-8ec50eaebad3
---

# MVP 1: ten days, three hours per day

This plan follows the [latest shared product discussion](https://chatgpt.com/share/6aa82bd1-34ec-83e9-8c8c-8ec50eaebad3), especially its generated architecture diagram and final Day 1–10 schedule. It **replaces** the earlier approval-only Day 1 and the service-bingo implementation plan. The two goals are a credible multi-industry CMS foundation and hands-on SAA-C03 architecture practice. Each day has a hard **3-hour maximum**: 45 minutes architecture, 90 minutes implementation, 45 minutes code walkthrough/interview reasoning. Do not convert the last block into extra coding.

The project owner approved the [architecture baseline](../../docs/architecture-approval.md) on 2026-09-14. Day 1 coding, AWS deployment, signed smoke test, and evidence are complete. Two contributors can split API/domain/tests and Terraform/deployment work as detailed in the [Day 1 plan](../../docs/day-01-plan.md).

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

## Mandatory daily SAA-C03 gate

Every implementation day creates a detailed `docs/daily/day-NN.md` from `docs/daily/TEMPLATE.md`. It records the as-built request/event path, code and IaC changed, AWS resources touched, tests and failure checks, cost impact, operational evidence, and scenario questions with reasoned answers across all four official SAA-C03 domains: secure, resilient, high-performing, and cost-optimized architectures.

Before the day can pass, review every service introduced or changed against those domains. An in-scope weakness must be implemented and reverified that day. A control dependent on a future feature may be deferred only when the record names the target day, explains why the current slice is still safe, and provides an interim control. Provisioning a service or drawing a diagram is never sufficient evidence.

## MVP scope boundaries

Implemented: generic dynamic content types and entries, basic versions/taxonomy/assets, draft/publish, events/SQS, static S3/CloudFront delivery, basic OpenSearch, authentication, monitoring and Terraform. Locale, channel, publish-target and tenant/site are **first-class model/port concepts**; only one tenant, a basic locale path, one website channel and an S3 publish-target adapter need run in MVP 1.

Designed/stubbed: richer localization, AI, multi-region DR, extension SDK and additional publish targets. Later: advanced workflows, full multi-tenancy and complete industry packs. The CMS manages product descriptions or banking content; it does **not** implement carts, payments, account balances or claims processing. No speculative ECS/RDS/analytics side projects are scheduled in these three-hour days.

## Prerequisites and truthfulness

Day 1 was deployed through a project-scoped role in `ca-central-1` under the owner's below-USD-$10 monthly target. The target is not a billing hard cap. Later expensive resources such as OpenSearch still require a fresh cost check before provisioning. The architecture diagram remains a target; only resources listed in each daily evidence record should be treated as deployed.
