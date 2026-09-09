# Health Checks and Background Work

Expose separate liveness and readiness probes, typically `/actuator/health/liveness` and `/actuator/health/readiness`. Enable probes explicitly outside environments where automatically configured, and ensure probes exercise the application serving path if management uses a separate port. Spring Boot documents [Actuator probe behavior](https://docs.spring.io/spring-boot/reference/actuator/endpoints.html).

- Liveness MUST depend on the local application's ability to run, not DB, Kafka, or shared downstream availability. External outages must not trigger restart storms.
- Readiness MUST indicate whether this instance can safely accept its advertised traffic. Add required checks deliberately; readiness does not automatically include every dependency.
- A DB-backed write API normally requires DB access. An outbox-backed API can tolerate Kafka outage while backlog age/size stays inside the documented acceptance budget. Gate writes when that budget is exceeded.
- Do not make every shared downstream failure remove every healthy replica. Define degraded behavior and dependency checks per service capability.
- Probe I/O MUST be bounded, read-only, and lightweight. Do not publish test business events or perform writes on each probe.
- Restrict management details, environment/config endpoints, heap dumps, metrics, and administrative controls to authorized operators.

## Background lifecycle

Use managed schedulers/listener containers and explicit lifecycle management. Each DB batch invokes a separate managed transactional service. Do not assume a scheduler is single-instance across replicas.

- Outbox relays MUST coordinate claims through the database or a CDC connector. Configure lease expiry, recovery, batch limits, and bounded parallelism.
- Avoid overlapping work unless concurrency is designed and tested. Do not hold database locks for network waits.
- On shutdown, stop accepting new work, stop claiming batches, finish bounded in-flight work, stop listeners, and close managed producers/executors within the platform termination window.
- Leave uncompleted outbox work recoverable. Do not mark sends successful merely because shutdown started.
- Classify transient failures for bounded retries; alert and expose worker health for terminal failure. An alive HTTP server must not hide a dead relay indefinitely.

Runbooks MUST cover DB outage, Kafka outage, growing outbox backlog, poisoned events, consumer lag, DLT replay, credential rotation, and DR. Define RPO/RTO, restore ordering, idempotency-record retention, and replay reconciliation after restoring databases or topics.
