# SAA-C03 coverage through the CMS

The [latest shared plan](https://chatgpt.com/share/6aa82bd1-34ec-83e9-8c8c-8ec50eaebad3) uses the CMS to practice architecture reasoning, not to deploy every service in the [official SAA-C03 list](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-associate-03/saa-03-in-scope-services.html). This replaces the earlier service-bingo matrix. At three hours per day, hands-on depth in the core path is more valuable than dozens of unrelated resource stacks.

| Topic | Hands-on in MVP 1 | Comparison/question to defend |
| --- | --- | --- |
| Compute and APIs | API Gateway, Lambda; concurrency/throttling/load tests | When EC2, ECS/Fargate or ALB would be preferable |
| Database and consistency | DynamoDB content/types/versions, conditional updates, partition/access-path review | RDS/Aurora vs DynamoDB; hot partitions; eventual consistency |
| Storage and edge | Private S3 assets/published JSON, presigned upload, CloudFront cache/origin controls | S3 vs EFS/EBS, static vs dynamic delivery, cache policy |
| Event integration | EventBridge, SQS/DLQ, idempotent Lambda workers | EventBridge vs SNS vs SQS, Step Functions vs choreography |
| Search | OpenSearch indexer and rebuild path | Why search is a projection, not the primary database; cost trade-off |
| Security | Cognito, IAM, S3 Block Public Access, encryption/KMS configuration | Authentication vs authorization, tenant isolation, WAF and Secrets Manager choices |
| Operations | CloudWatch logs/metrics/alarms, Terraform, load/failure drill | RTO/RPO, multi-AZ/multi-region, backup cost, DR topology |

The [ten-day schedule](../_bmad-output/planning-artifacts/saa-c03-10-day-plan.md) attaches an interview question to every day's working code. Advanced AI, analytics pipelines, alternate databases, container labs, full multi-region deployment and specialized AWS services are **not** mandatory builds in this MVP. They remain later experiments or reasoned alternatives, which is a scope correction from the previous plan.
