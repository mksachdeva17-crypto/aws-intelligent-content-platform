# aws-intelligent-content-platform
AWS-native content platform where content is structured, portable, event-driven and AI-ready from the foundation.

This repository is building **MVP 1: a generic, schema-driven, multi-industry content platform**, following the [latest shared architecture and ten-day plan](https://chatgpt.com/share/6aa82bd1-34ec-83e9-8c8c-8ec50eaebad3). The architecture is approved. Day 1 generic CRUD is deployed and verified in `ca-central-1`.

- [Active ten-day implementation plan](_bmad-output/planning-artifacts/saa-c03-10-day-plan.md)
- [Architecture baseline](docs/architecture-approval.md)
- [Original architecture diagram](docs/assets/aws-intelligent-content-platform-architecture.png)
- [Generic content model](docs/generic-content-model.md)
- [Day 1 build checklist](docs/day-01-plan.md)
- [SAA-C03 learning coverage](docs/saa-c03-service-coverage.md)
- [Contributor and agent instructions](AGENTS.md)
- [Day 1 evidence](docs/daily/day-01.md)

## Day 1 local checks

The Lambda targets the supported AWS `nodejs22.x` runtime on ARM64. Install Node.js 22 or 24, then run the built-in Node test suite:

```powershell
npm ci
npm test
```

## Day 1 AWS deployment

Install Terraform and confirm a **non-root** AWS profile, Region, permissions and spend ceiling first. The project owner selected `ca-central-1` and a **monthly spend below USD $10**. That is a target, not an automatic hard cap; inspect billing before applying and tear down the Day 1 stack after testing. On the current workstation, `cms-dev` uses [AWS CLI browser-based login](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sign-in.html), while `cms-deploy` assumes the project-scoped deployment role. The owner explicitly deferred MFA for this learning environment; enabling MFA remains recommended. The `hakim` profile was observed to be account-root and must not be used to deploy. Run `scripts/aws_preflight.ps1` to verify the selected identity. Do not use `--no-verify-ssl`. The management routes use [IAM authorization](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-access-control-iam.html); the invoking identity needs `execute-api:Invoke`. IAM authentication is temporary, not tenant isolation; Day 7 adds Cognito and scopes tenant/site from claims.

```powershell
./scripts/aws_preflight.ps1 -Profile <non-root-profile> -Region <region>
terraform -chdir=infra/day1 fmt -check
terraform -chdir=infra/day1 init
terraform -chdir=infra/day1 validate
./scripts/terraform_day1.ps1 plan -Profile cms-deploy -Region ca-central-1 -CaBundle <trusted-ca.pem>
# Review the saved plan, then:
./scripts/terraform_day1.ps1 apply -Profile cms-deploy -Region ca-central-1 -CaBundle <trusted-ca.pem>
./scripts/terraform_day1.ps1 output -Profile cms-deploy -Region ca-central-1 -CaBundle <trusted-ca.pem>
```

For an end-to-end IAM-signed smoke test, run:

```powershell
npm run smoke:aws -- --url <management_api_url> --region <region> --profile <profile>
```

The smoke script creates and reads a demo `product` and `article` through the same generic path, updates the product, and checks that a stale update returns HTTP 409. It incurs small AWS request/storage charges. `GET` and `PUT` require `tenantId` and `siteId` query parameters; `POST` takes them from JSON. All content remains draft on Day 1. When finished, use `./scripts/terraform_day1.ps1 destroy` with the same profile/Region/CA settings and review the destruction plan before approval.

The verified management endpoint is `https://fokte33w34.execute-api.ca-central-1.amazonaws.com/`. It requires IAM-signed requests. Terraform state is currently local and ignored; until a shared encrypted backend is added, only the current state holder should apply or destroy this stack. Never exchange the state file through Git or chat.

LocalStack was explicitly skipped for Day 1 and its unused configuration was removed. The complete route is verified in AWS.

Every completed implementation day must include a detailed record under `docs/daily/`, based on [the daily template](docs/daily/TEMPLATE.md). The record includes SAA-C03 scenario questions across security, resilience, performance, and cost. An in-scope gap blocks completion until it is fixed and reverified; future-feature dependencies must name the planned day rather than being silently ignored.

BMAD v6.12.0 is installed under `_bmad/` with Codex skill entry points in `.agents/skills/`. Its `bmad-build` runner requires `uv`; that prerequisite is not yet installed because package retrieval failed local TLS certificate validation. Do not disable certificate checks to bypass it.
