---
name: java-rest-service-skill
description: Implement, update, or review Java Spring Boot REST services using this coding standard for database CRUD, downstream service calls, and Kafka events. Use for service architecture and contract decisions; not for unrelated Java desktop, Android, or algorithm tasks.
---

# Java REST Service

Apply this repository's Java service standard to the requested implementation or review. Resolve the links below relative to this skill directory, even when working in another repository.

## Workflow

1. Inspect the target repository's instructions, build, framework versions, and existing conventions. Preserve the user's explicit choices and task scope; do not introduce a framework migration or unrelated infrastructure.
2. Read the baseline and rule definitions in [README.md](README.md), then only the topic files relevant to the change. Prefer those focused files over loading the consolidated standard as well.
3. Implement the requested behavior, or assess the existing implementation against applicable rules. Treat code excerpts as patterns requiring complete supporting types, configuration, and tests.
4. Verify the changed behavior with the target project's configured build and appropriate tests. Do not assume Maven/Gradle verification includes integration tests, coverage, or scanners unless those checks are wired into the build.
5. Report the outcome, validation performed, and remaining limitations. For reviews, lead with actionable findings and file/line references; distinguish defects from optional design choices.

## Topic routing

| Work | Read |
| --- | --- |
| Architecture and ownership | [Project structure](01-project-structure-naming.md), [service transactions](04-services-queries-transactions.md) |
| REST CRUD and contract changes | [Endpoints and DTOs](03-controllers-requests-responses.md), [versioning](12-api-versioning.md), [OpenAPI](13-contract-documentation.md) |
| Database queries, mappings, migrations | [Queries and transactions](04-services-queries-transactions.md), [persistence](05-persistence-exceptions-validation.md) |
| Downstream integrations | [Clients and resilience](07-integration-clients.md), [concurrency](10-concurrency-performance.md) |
| Kafka publication or consumption | [Kafka and outbox](18-kafka-outbox.md), [end-to-end flow](20-end-to-end-flow.md) |
| Configuration and startup | [Configuration](02-configuration.md), [DI](06-dependency-injection.md), [bootstrap](09-bootstrap.md) |
| Security and operations | [Security](19-security.md), [observability](08-logging-observability.md), [health and workers](14-health-background-work.md) |
| Verification and review | [Style](11-formatting-style.md), [tests](15-testing.md), [dependencies](16-build-dependency-checks.md), [review checklist](17-review-checklist.md) |

## Essential invariants

- Keep HTTP, business logic, persistence, downstream transport, and event contracts at separate boundaries.
- Use the repository's supported versions and execution model. The default here is blocking MVC/JPA with stateless Spring services and bounded I/O.
- Commit a database mutation and its required outbox event in one local transaction. Publish through a recoverable relay; do not promise atomic DB/HTTP/Kafka completion.
- Preserve event IDs across retries, design consumers for duplicates, and enforce explicit ordering where required.
- Make HTTP write replay, PATCH semantics, concurrency preconditions, and response codes explicit in the contract.
- Apply resource/tenant authorization and redact secrets across API, logging, and messaging boundaries.

## Maintaining this standard

When editing these topic files, run `python3 scripts/build-standard.py` and `python3 scripts/build-standard.py --check` from the skill directory. This generator only synchronizes documentation; it does not compile Java or validate an implementing service. Keep review history separate from normative instructions.
