# Day 1 — generic platform foundation

Status: **complete on 2026-09-14**. The project owner approved the architecture, and the generic thin slice was deployed and verified in AWS `ca-central-1`.

This follows the [latest shared ten-day plan](https://chatgpt.com/share/6aa82bd1-34ec-83e9-8c8c-8ec50eaebad3), which supersedes the earlier approval-only Day 1. The [active local plan](../_bmad-output/planning-artifacts/saa-c03-10-day-plan.md) limits work to **3 hours**. Day 1 is an implementation day; architecture review is part of it, not its sole exit criterion.

## 45 minutes — architecture

- Review the [approved architecture baseline](architecture-approval.md) and agree on the Day 1 API contract before splitting work.
- Use a DynamoDB entry key that includes tenant, site, and entry ID; store a current pointer plus immutable version snapshots. A conditional update rejects a stale expected version.
- For Day 1 only, `GET` and `PUT` require explicit `tenantId` and `siteId` query parameters; `POST` gets them from the body. API routes require AWS IAM-signed requests, but caller-provided scope is still **not** trusted tenant isolation; Day 7 binds scope to Cognito claims.
- Use API Gateway + Lambda + DynamoDB for the low-operations, pay-per-use foundation. Defer containers and relational storage until access patterns justify them.

## 90 minutes — implementation

- **Contributor A — API/domain/tests:** generic `POST /content`, `GET /content/{id}` and `PUT /content/{id}` with tenant, site, type, locale, status, version and arbitrary fields; thin Lambda entry point; two content types and failure cases tested.
- **Contributor B — infrastructure/deployment:** parameterized Terraform for IAM-protected HTTP API Gateway, Lambda, DynamoDB, least-privilege roles, logs, deployment wrapper and smoke script.
- **Integration:** API contract merged with the Lambda package, deployed through `cms-deploy`, and tested through the live endpoint.

## 45 minutes — walkthrough/interview practice

- Reviewed the request path, DynamoDB keys, Lambda scaling and API authorization.
- Answered: **“How would this CMS handle one million API requests without redesigning the platform?”** See the [Day 1 evidence](daily/day-01.md).
- Recorded test, deployment, endpoint, drift, authorization, cost and teardown evidence.

## Day 1 definition of done

- [x] Generic CRUD works end-to-end in AWS, not just in a mock or diagram.
- [x] Two different `contentType` values are stored/read through the same code path; full schema validation arrives Day 5.
- [x] Tenant/site scope and optimistic version are present and tested.
- [x] Terraform, test and smoke commands are reproducible from README.
- [x] Architecture trade-off answer and cost/resource note are recorded.

Day 2 is the next build gate: private assets plus a separate S3/CloudFront delivery path.
