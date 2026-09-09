# Testing

Use JUnit Jupiter with a version compatible with the approved build baseline, Mockito where useful, and behavior-focused assertions. Unit tests MUST avoid live databases, brokers, network services, and wall-clock timing. Inject `Clock` and stub dependency boundaries.

Integration tests MUST use the production database engine and Kafka in isolated test infrastructure, typically Testcontainers. Do not treat H2 or mocked repositories as proof of production SQL, locking, migrations, or broker behavior. Use an HTTP stub server for transport-level client testing.

| Area | Required scenarios |
| --- | --- |
| HTTP CRUD | Create/Location, list/empty page, read/update/delete success, missing IDs, invalid JSON/fields/query, method/media handling |
| Authorization | Missing/invalid identity, missing scope, object/tenant access denial, forged ownership input |
| Persistence | Migrations, real SQL, uniqueness race, optimistic-lock race, rollback, stable pagination, bounded query count |
| Outbound client | Success, expected absence, 4xx/5xx mapping, invalid body, timeout, disconnect, budget exhaustion, idempotent retries |
| DB + event | Commit saves both; serialization/outbox failure rolls back both; Kafka outage retains pending work |
| Relay | Crash before send; crash after broker acknowledgment before sent-state commit; lease recovery; concurrent workers |
| Consumers, if present | Duplicate event, crash after DB commit before offset commit, schema failure, ordering policy, rebalance |
| Recovery | Retry exhaustion, DLT failure, authorized replay, restart recovery, shutdown within deadline |
| Contracts | OpenAPI responses, event schema compatibility, stable key/event ID across publication retries |

Test transactions through Spring proxies, not only by directly constructing service classes. Include tests that actually commit; a test-managed rollback can hide commit-time failures and after-commit behavior. Use deterministic synchronization for concurrency tests and bounded condition polling instead of arbitrary sleeps.

Require overall line coverage of at least 80% and new/changed line coverage of at least 90%. Collect with JaCoCo and enforce changed-line coverage with a diff-aware tool. Generated code and other exclusions MUST be explicit and reviewed. Passing percentages do not excuse missing negative-path or race-condition assertions.

For Maven services, configure unit tests under Surefire and integration tests under Failsafe so `./mvnw -B verify` runs both. For Gradle services, wire the integration-test task into `check` before claiming `./gradlew check` validates it. CI MUST fail on skipped required infrastructure tests; document local prerequisites.
