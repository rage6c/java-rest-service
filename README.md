# Java Service Coding Standard

Version: 1.0

Date: 2026-09-09

Scope: Java REST services exposing service-to-service endpoints, performing relational database CRUD, calling downstream services, and publishing Kafka events.

This standard adapts the structure and engineering intent of `/Users/rage6c/Documents/docs/rest-api-coding-standard/`. The source is C#/.NET; this is a Java-specific standard, not a literal API-name translation. Spring and Kafka mechanics were checked against official documentation linked in the relevant topics.

## Baseline and rule strength

The default architecture is Spring Boot with Spring MVC, Spring Data JPA/Hibernate, Bean Validation, a managed synchronous REST client, and Spring for Apache Kafka. Examples use Java 21 language features or earlier. Each implementing repository MUST pin an organization-supported JDK, Spring Boot release/BOM, database driver, Kafka-compatible client, and build tool. This standard does not assert a latest patch version or prescribe a runtime upgrade.

MUST/MUST NOT are required. SHOULD is the default unless a documented technical reason justifies another choice. MAY is optional. Architecture choices such as reactive persistence, non-relational storage, or a durable alternative to the outbox require a recorded decision preserving the stated guarantees. Topic files and the consolidated document express the same standard; edit the topic files and regenerate the consolidated copy together.

Code blocks are focused excerpts or explicitly labeled pseudocode. Imports and supporting types may be omitted. They are not a compiled reference service or a complete security/deployment configuration.

## Core decisions

- Thin controllers; application services own business rules and transactions.
- Separate API DTOs, persistence entities, downstream DTOs, and event payloads.
- Typed configuration validated at startup; constructor injection and stateless singleton services.
- Database constraints, migrations, bounded queries, and optimistic concurrency.
- Configured downstream clients with deadlines, deliberate retries, and service identity.
- One local transaction for DB change plus outbox event; asynchronous at-least-once Kafka delivery with stable event IDs.
- Explicit API/event contracts, centralized problem responses, tracing, operational recovery, and meaningful integration tests.

## Deliberate adaptations from the reference

| Reference approach | Java standard decision |
| --- | --- |
| EF Core Fluent API with annotation-free entities | Explicit JPA mapping annotations on persistence-only entities; named schema/table and migrations retained |
| `AsNoTracking` and SQL-translated LINQ | Read-only transactions/projections and database-side repository queries; Java Streams are not a SQL query provider |
| Request-scoped business services | Stateless Spring singleton beans with transaction-bound persistence contexts |
| `Task` and `CancellationToken` throughout | Consistent blocking MVC/JPA by default, bounded I/O and explicit cancellation limits |
| Serilog console and rolling files | SLF4J/Logback; retain rolling-file policy with a documented stdout-only container option |
| xUnit/Moq and NuGet | JUnit Jupiter/Mockito, real-engine integration tests, Maven/Gradle and JVM dependency scans |
| Conflicting internal/unversioned API rules | Explicit stable URL major version for independently deployed callers |
| No new access-control middleware | Explicit service authentication/authorization boundary for the requested exposed endpoints |
| No dedicated Kafka consistency chapter | Durable outbox, producer acknowledgments, duplicate handling, ordering, quarantine and replay |

The reference's 80% overall and 90% new/changed line coverage thresholds are retained. Numerical timeout, size, and retention defaults in this standard are engineering starting values; validate them against the service contract and deployment capacity.

## Reading options

Read [JAVA-SERVICE-CODING-STANDARD.md](JAVA-SERVICE-CODING-STANDARD.md) for the complete consolidated standard, or use the topic files below. Start with the [end-to-end flow](20-end-to-end-flow.md) and [merge checklist](17-review-checklist.md) for an implementation overview.

## Topic index

| Topic | File |
| --- | --- |
| Project Structure and Naming | [01-project-structure-naming.md](01-project-structure-naming.md) |
| Configuration | [02-configuration.md](02-configuration.md) |
| Controllers, Requests, and Responses | [03-controllers-requests-responses.md](03-controllers-requests-responses.md) |
| Services, Queries, and Transactions | [04-services-queries-transactions.md](04-services-queries-transactions.md) |
| Persistence, Exceptions, and Validation | [05-persistence-exceptions-validation.md](05-persistence-exceptions-validation.md) |
| Dependency Injection | [06-dependency-injection.md](06-dependency-injection.md) |
| Calls to Other Services | [07-integration-clients.md](07-integration-clients.md) |
| Logging and Observability | [08-logging-observability.md](08-logging-observability.md) |
| Application Bootstrap | [09-bootstrap.md](09-bootstrap.md) |
| Concurrency and Performance | [10-concurrency-performance.md](10-concurrency-performance.md) |
| Formatting and Java Style | [11-formatting-style.md](11-formatting-style.md) |
| API Versioning and Compatibility | [12-api-versioning.md](12-api-versioning.md) |
| OpenAPI and Event Documentation | [13-contract-documentation.md](13-contract-documentation.md) |
| Health Checks and Background Work | [14-health-background-work.md](14-health-background-work.md) |
| Testing | [15-testing.md](15-testing.md) |
| Build, Dependencies, and Vulnerability Checks | [16-build-dependency-checks.md](16-build-dependency-checks.md) |
| Merge Review Checklist | [17-review-checklist.md](17-review-checklist.md) |
| Kafka Messaging and Transactional Outbox | [18-kafka-outbox.md](18-kafka-outbox.md) |
| Service Security | [19-security.md](19-security.md) |
| End-to-End Reference Flow | [20-end-to-end-flow.md](20-end-to-end-flow.md) |

## Reference provenance

The local source folder's README and topics 01–17 informed the structure, rules, examples, and adaptation table. Its `SKILL.md` describes how to apply the C# standard; this deliverable is a coding standard and does not install or modify a Codex skill. Official documentation links explain framework behavior; this document's MUST/SHOULD rules are the proposed Java service policy.

## Maintaining the consolidated copy

After editing the numbered topics or introductory policy, run:

```bash
python3 scripts/build-standard.py
python3 scripts/build-standard.py --check
```

The [generator](scripts/build-standard.py) uses only Python's standard library. The check verifies that the consolidated document matches its source topics; it does not compile the illustrative Java snippets.
