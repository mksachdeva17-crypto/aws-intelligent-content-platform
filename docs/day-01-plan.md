# Day 1 — generic platform foundation

This follows the [latest shared ten-day plan](https://chatgpt.com/share/6aa82bd1-34ec-83e9-8c8c-8ec50eaebad3), which supersedes the earlier approval-only Day 1. The [active local plan](../_bmad-output/planning-artifacts/saa-c03-10-day-plan.md) limits work to **3 hours**. Day 1 is an implementation day; architecture review is part of it, not its sole exit criterion.

## 45 minutes — architecture

- Review the [architecture baseline](architecture-approval.md): generic ContentType/ContentEntry, single-tenant runtime with `tenantId`/`siteId`, management vs delivery separation, future event/publish ports.
- Choose the Day 1 DynamoDB keys and access paths for create/get/update; note where a hot tenant/site partition could appear.
- Confirm AWS account/profile, region, deployment permissions and spend ceiling before provisioning.
- Record why API Gateway + Lambda + DynamoDB is used now rather than EC2/ECS/RDS.

## 90 minutes — implementation

- Create repository structure, Terraform base and a minimal API Gateway → Lambda → DynamoDB deployment.
- Implement generic `POST /content`, `GET /content/{id}` and `PUT /content/{id}`. Payload uses `tenantId`, `siteId`, `contentType`, `locale`, `status`, `version` and arbitrary `fields`.
- Add local contract tests for create/get/update, missing/invalid envelope fields and stale version conflicts. Do not hard-code Article or Product or require article-specific title/body.
- Deploy via Terraform and run an AWS smoke test if prerequisites above are available. If not, validate IaC and code locally, and leave the cloud DoD pending.

## 45 minutes — walkthrough/interview practice

- Review the deployed request path, DynamoDB keys, Lambda concurrency and API throttling choices.
- Answer: **“How would this CMS handle one million API requests without redesigning the platform?”** Distinguish authoring traffic from future CloudFront/S3 delivery traffic.
- Record evidence: test results, endpoint response, Terraform output, resources created, estimated cost and teardown commands.

## Day 1 definition of done

- [ ] Generic CRUD works end-to-end in AWS, not just in a mock or diagram.
- [ ] Two different `contentType` values are stored/read through the same code path; full schema validation arrives Day 5.
- [ ] Tenant/site scope and optimistic version are present and tested.
- [ ] Terraform, test and smoke commands are reproducible from README.
- [ ] Architecture trade-off answer and cost/resource note are recorded.

None of these implementation checks is marked complete yet. This document is the adjusted plan, not a claim that Day 1 was built.
