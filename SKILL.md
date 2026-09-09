---
name: java-rest-service-skill
description: Implement scoped changes in existing Java Spring Boot REST services, or review their database CRUD, downstream calls, and Kafka messaging against this standard. Use for Java service contract and architecture decisions; not for greenfield scaffolding, Android, desktop, or algorithm tasks.
---

# Java REST Service

Apply this repository's Java service standard to the requested implementation or review. Resolve the links below relative to this skill directory, even when working in another repository.

## Scope and mode

Use this skill for bounded changes in an existing service or a requested change/service review. The standard can inform a new service design, but this package does not supply a tested greenfield scaffold or a production reference relay. If the task is greenfield, state that limit and use the user's chosen scaffolding workflow; do not treat excerpts as a runnable starter.

For Java REST work, this skill supplies domain-specific rules. A general review skill may complement its review procedure; neither overrides user instructions or target-repository requirements. Combine compatible guidance and avoid duplicate reports. Do not claim automatic priority over other skills.

## Shared preparation

- Inspect the target repository's instructions, build, framework versions, contracts, and relevant conventions. Identify whether the task is implementation, review of a change, or review of the whole service; default a supplied diff/PR to change review.
- Read the baseline and rule definitions in [README.md](README.md), then the relevant topic files. Resolve references from this skill directory, not the target checkout. Do not also load the consolidated copy unless needed.
- Reuse the target's pinned versions and organization BOM. If the requested work needs a new dependency, verify an exact compatible version against the organization catalog or official release/compatibility documentation. Do not infer a current version from memory. Record the choice and avoid unrelated upgrades.

## Implementation

1. Define the affected behavior, contract, and failure cases. Inspect existing adapters and transaction patterns before adding a new abstraction.
2. Apply applicable rules to new or changed behavior and its required supporting code. Keep the diff within the requested outcome; editing one method does not authorize cleanup of every pre-existing convention in that file. Use the conflict rules below where needed.
3. Implement complete supporting types and configuration for the requested behavior. For outbox, idempotency, or exception-handler changes, inspect the actual persistence/broker/framework APIs and existing components; do not copy architectural pseudocode as production code. Validate crash/retry, duplicate, commit/rollback, and error-response cases applicable to the change using [testing guidance](15-testing.md).
4. Run the target project's configured build and appropriate tests. Check that integration tests, coverage, and scanners are wired into the invoked tasks before claiming they ran. Report missing infrastructure or unverified guarantees precisely.
5. Report the change, verification, and any scoped deviations or pre-existing risks. Do not present an unverified recovery guarantee as production-ready.

## Review

1. Always read [17-review-checklist.md](17-review-checklist.md), then the topic files for the affected paths and dependencies. For a whole-service review, cover applicable service capabilities rather than only a diff.
2. Check each suspected finding against actual code, configuration, callers, and existing tests. Identify a concrete trigger and consequence. Use a focused test or reproduction when feasible and useful; static evidence can establish a defect without an executable test. Label unresolved possibilities as verification gaps, not confirmed bugs.
3. Triage with the table below. Group repeated violations with one representative location and identify pre-existing issues separately. Avoid a report that restates every checklist rule.
4. Lead with actionable findings ordered by impact. Each finding includes a precise file/line, violated rule or behavior, trigger, consequence, and correction direction. Distinguish contract/correctness defects, conformance gaps, and optional improvements. State checks run and coverage limits; if no actionable findings remain, say so.
5. Review-only requests do not authorize implementation edits. Continue into fixes only when requested.

## Conflicts, open choices, and triage

| Situation | Action |
| --- | --- |
| New or changed behavior violates an applicable MUST without an authorized exception | Treat as a merge requirement. Fix within the implementation scope, or report the conformance gap in a review with its impact. Do not describe every conformance gap as a runtime bug. |
| Explicit user/target instruction conflicts with this standard | Follow the governing instruction, name both requirements, and record the deviation. Do not silently claim full conformance or ask again for an already authorized choice. |
| An existing convention conflicts with a MUST | Existing usage alone is not an exception. Conform new behavior where possible without unrelated refactoring. Explain an unresolved conflict and its effect on the requested outcome. |
| Pre-existing issue unrelated to a scoped change | Report material risks separately as follow-up work; do not expand the diff. If the change depends on or worsens the issue, include it in the scoped assessment. |
| Standard permits alternatives, such as PATCH format or concurrency representation | Reuse a documented compatible contract; otherwise choose and explain a reasonable default. Do not invent an approval requirement for an allowed design choice. |
| Missing decision changes externally visible semantics or data safety and cannot be inferred | Ask one focused question and continue independent work. Identify the actual decision needed; pause only the dependent work. |
| Exception to a MUST is needed but not already authorized | Identify the rule, impact, and proposed alternative for the responsible owner. Do not grant yourself a waiver. Record authorized exceptions with owner and expiry/follow-up when temporary. |
| SHOULD preference or cosmetic improvement | Explain the benefit only when useful; do not make it a merge blocker without a concrete defect or governing project requirement. |

Keep ordinary implementation choices moving. Escalate only decisions that need missing authority or information, not every difference from an example. In full-service reviews, report material pre-existing gaps within the requested scope; backlog classification does not mean the service conforms.

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
