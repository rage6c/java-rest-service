# Application Bootstrap

The application entry point is a composition root. It MUST contain startup wiring only.

```java
@SpringBootApplication
@ConfigurationPropertiesScan
public class CatalogApplication {
    public static void main(String[] args) {
        SpringApplication.run(CatalogApplication.class, args);
    }
}
```

Use focused configuration classes for persistence, HTTP clients, Kafka, security, observability, and task execution. Supply a `Clock.systemUTC()` bean for application time. Do not place seed data, CRUD logic, remote request orchestration, or schema changes in `main`.

- Validate configuration before accepting traffic.
- Apply migrations through the chosen controlled mechanism and validate mapping compatibility.
- Configure the security filter chain explicitly; restrict management endpoints and documentation exposure.
- Establish tracing/request context early and clear it after completion. Do not assume controller advice handles exceptions raised by every filter.
- Let Spring own client, connection-pool, listener, and executor lifecycle. Avoid manually spawning unmanaged threads.
- Treat profiles as deployment configuration, not conditional business logic.
- Do not run destructive initialization or production sample seeding from application runners.
- Start the outbox relay/listeners only with the required schema, configuration, and lifecycle coordination available.

A temporary Kafka outage need not prevent a DB-backed API from starting if its contract permits durable outbox buffering. Readiness and admission controls MUST reflect actual capacity and recovery policy; see [14-health-background-work.md](14-health-background-work.md).
