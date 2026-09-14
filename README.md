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

The Lambda code targets the [AWS Python 3.12 runtime](https://docs.aws.amazon.com/lambda/latest/dg/lambda-runtimes.html). The dependency-free unit tests also run on local Python 3.11:

```powershell
py -m unittest discover -s tests -v
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

For an end-to-end signed smoke test, install the pinned local test dependency, then run:

```powershell
py -m pip install -r requirements-dev.txt
py scripts/smoke_day1.py --url <management_api_url> --region <region> --profile <profile>
```

The smoke script creates and reads a demo `product` and `article` through the same generic path, updates the product, and checks that a stale update returns HTTP 409. It incurs small AWS request/storage charges. `GET` and `PUT` require `tenantId` and `siteId` query parameters; `POST` takes them from JSON. All content remains draft on Day 1. When finished, use `./scripts/terraform_day1.ps1 destroy` with the same profile/Region/CA settings and review the destruction plan before approval.

The verified management endpoint is `https://fokte33w34.execute-api.ca-central-1.amazonaws.com/`. It requires IAM-signed requests. Terraform state is currently local and ignored; until a shared encrypted backend is added, only the current state holder should apply or destroy this stack. Never exchange the state file through Git or chat.

## Deferred LocalStack Hobby checks

LocalStack was explicitly skipped for Day 1. The [LocalStack Hobby plan](https://docs.localstack.cloud/aws/licensing/) includes DynamoDB and Lambda, but **not API Gateway HTTP APIs**. The checked-in [Compose file](compose.localstack.yml) remains an optional future DynamoDB-adapter check; the complete route was tested in AWS. LocalStack requires an [auth token](https://docs.localstack.cloud/aws/getting-started/auth-token/); keep it in your shell environment, never in Git or chat. Docker Desktop's Linux engine must be running.

```powershell
# Copy .env.example to ignored .env, then put your own LocalStack token in .env.
docker compose -f compose.localstack.yml up -d
aws dynamodb list-tables --profile cms-local
py -m pip install -r requirements-dev.txt
py scripts/localstack_day1.py
docker compose -f compose.localstack.yml down
```

The `cms-local` AWS CLI profile on the current workstation also uses dummy credentials, `ca-central-1`, and the loopback endpoint. The test creates only a local DynamoDB table. Do not export `AWS_ENDPOINT_URL` globally for real AWS deployment.

BMAD v6.12.0 is installed under `_bmad/` with Codex skill entry points in `.agents/skills/`. Its `bmad-build` runner requires `uv`; that prerequisite is not yet installed because package retrieval failed local TLS certificate validation. Do not disable certificate checks to bypass it.
