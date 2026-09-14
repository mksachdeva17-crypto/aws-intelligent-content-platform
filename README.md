# aws-intelligent-content-platform
AWS-native content platform where content is structured, portable, event-driven and AI-ready from the foundation.

This repository is planning **MVP 1: a generic, schema-driven, multi-industry content platform**, following the [latest shared architecture and ten-day plan](https://chatgpt.com/share/6aa82bd1-34ec-83e9-8c8c-8ec50eaebad3). The plan is 3 hours per day; Day 1 itself deploys a thin generic CRUD slice. The repository contains planning artifacts and example content, **not a running CMS yet**.

- [Active ten-day implementation plan](_bmad-output/planning-artifacts/saa-c03-10-day-plan.md)
- [Architecture baseline](docs/architecture-approval.md)
- [Original architecture diagram](docs/assets/aws-intelligent-content-platform-architecture.png)
- [Generic content model](docs/generic-content-model.md)
- [Day 1 build checklist](docs/day-01-plan.md)
- [SAA-C03 learning coverage](docs/saa-c03-service-coverage.md)

BMAD v6.12.0 is installed under `_bmad/` with Codex skill entry points in `.agents/skills/`. Its `bmad-build` runner requires `uv`; that prerequisite is not yet installed because package retrieval failed local TLS certificate validation. Do not disable certificate checks to bypass it.
