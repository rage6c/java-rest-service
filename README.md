# Java Service Coding Standard

Version: 1.0

Date: 2026-09-09

Scope: Java REST services exposing service-to-service endpoints, performing relational database CRUD, calling downstream services, and publishing Kafka events.

This standard is for Java developers building and reviewing Spring Boot services. It defines implementation patterns for REST endpoints, relational persistence, downstream integrations, and Kafka messaging. Official documentation is linked in the relevant topics.

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

## Java technology choices

| Concern | Standard |
| --- | --- |
| Persistence | JPA/Hibernate entities with explicit table/schema mapping and versioned migrations |
| Queries | Spring Data repositories, database-side filtering/projection, and read-only transactions |
| Dependency injection | Constructor injection and stateless Spring singleton beans |
| Execution model | Blocking Spring MVC/JPA with bounded I/O and explicit timeout/cancellation handling |
| Logging | SLF4J/Logback with central collection and deployment-appropriate appenders |
| Testing | JUnit Jupiter/Mockito and integration tests against the production database engine and Kafka |
| Build and dependencies | Maven or Gradle, managed versions, static analysis, and JVM dependency scans |
| API contracts | Explicit URL major versions for independently deployed callers |
| Security | Service authentication, scope checks, and resource/tenant authorization |
| Messaging | Transactional outbox, acknowledged publication, duplicate handling, and controlled replay |

Required line coverage is at least 80% overall and 90% for new/changed code. Numerical timeout, size, and retention defaults are engineering starting values; validate them against the service contract and deployment capacity.

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

## Documentation sources

Topic files link to official Spring Framework, Spring Boot, Spring Data, Spring Security, Spring for Apache Kafka, Apache Kafka, and Debezium documentation for framework behavior. The MUST/SHOULD rules define this standard's implementation policy for Java services.

## Maintaining the consolidated copy

After editing the numbered topics or introductory policy, run:

```bash
python3 scripts/build-standard.py
python3 scripts/build-standard.py --check
```

The [generator](scripts/build-standard.py) uses only Python's standard library. The check verifies that the consolidated document matches its source topics; it does not compile the illustrative Java snippets.
