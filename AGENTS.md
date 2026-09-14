# Contributor and agent instructions

This repository builds a generic, AWS-native CMS. Two people may work on it concurrently; keep changes small and review one another's pull requests.

## Source of truth

- The approved architecture is [docs/architecture-approval.md](docs/architecture-approval.md); the PNG there is conceptual, while the written invariants are the implementation contract.
- The active schedule is [_bmad-output/planning-artifacts/saa-c03-10-day-plan.md](_bmad-output/planning-artifacts/saa-c03-10-day-plan.md). Use [docs/day-01-plan.md](docs/day-01-plan.md) for the current build gate.
- [docs/generic-content-model.md](docs/generic-content-model.md) defines the core envelope. Older Article-first BMAD artifacts are superseded; do not implement from them.

## Implementation guardrails

- Keep the core industry-neutral: no Article-, Product-, or Mortgage-specific branches.
- Every entry access is scoped by tenant and site, including reads. Until Cognito is added, caller-provided scope is demo-only and must not be presented as secure tenant isolation.
- Use optimistic concurrency and immutable entry versions. DynamoDB is authoritative; public S3 output and search are projections.
- Keep management and delivery paths separate. Do not expose drafts via public delivery.
- Do not provision AWS resources until the account/profile, region, permissions, and spend ceiling are confirmed. Do not commit credentials, Terraform state, personal BMAD config, or generated caches.
- Never use the account-root AWS profile for Terraform deployment. Run `scripts/aws_preflight.ps1` against the chosen non-root profile first.
- Add tests and reproducible commands with each implementation slice. Record actual cloud evidence only after running it.
- Day 1 Terraform state is local and ignored. Until a remote encrypted backend is configured, only the current state holder may apply or destroy the shared AWS stack.
- End every implementation day with `docs/daily/day-NN.md`, using `docs/daily/TEMPLATE.md`. Cover all four SAA-C03 domains, include scenario questions with reasoned answers, and record commands/evidence.
- A day cannot pass with an unresolved gap in the services or architecture implemented that day. Fix and reverify it the same day. A dependency intentionally scheduled for a later day is allowed only when the daily record names that day, explains the boundary, and shows the current slice remains safe.

## Working together

- Prefer one short-lived branch per person/task and review before merging to `main`; coordinate API and infrastructure interfaces before coding in parallel.
- Day 1 ownership and merge order are in [docs/day-01-plan.md](docs/day-01-plan.md). One contributor owns API/domain/tests; the other owns Terraform/deployment/smoke scripts. Both review the deployed result.
- The committed `_bmad/` and `.agents/skills/` directories pin the shared BMAD v6.12.0 workflow. Put team-wide BMAD customization in `_bmad/custom/config.toml`; personal preferences belong in ignored `_bmad/config.user.toml` or `_bmad/custom/config.user.toml`.
