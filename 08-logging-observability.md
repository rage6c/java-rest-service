# Logging and Observability

Use SLF4J with the project's managed logging backend, normally Logback. Emit structured JSON in deployed environments and preserve typed fields in the log collector.

```java
log.info("Product created: productId={} eventId={}", productId, eventId);
```

- MUST use parameterized messages or structured key/value logging, never string concatenation for dynamic log messages.
- Include service, environment, build version, timestamp, severity, logger, trace ID and span ID. Event logs include event ID and aggregate ID; relay logs include attempt and outcome.
- Log HTTP method, route template, status, and duration. Avoid raw URLs containing identifiers or query secrets.
- Never log tokens, cookies, credentials, private keys, full personal-data payloads, or database connection secrets. Use safe allowlisted fields and sanitize user-controlled strings.
- ERROR means an unexpected or terminal failure requiring attention. WARN covers retries approaching exhaustion or degraded behavior. INFO covers important lifecycle/business transitions. DEBUG is temporary diagnostic detail.
- Log each unexpected exception with its cause at the owning boundary; do not duplicate the same stack trace in every layer.
- Keep audit events distinct from debug logs. Record actor, action, target, time, and outcome in the approved durable audit destination where required.

## Console and rolling files

Retain the reference's console plus rolling-file default for deployments that require service-managed files: roll daily and at 10 MB, retain up to 31 days, and set an explicit total disk cap (starting value 1 GB). Use per-instance paths and central collection. Verify retention on busy days, disk-full behavior, access permissions, and redaction.

For containers whose platform collects stdout, console-only logging is an allowed documented deployment choice; avoid duplicating each record through both file and stdout collectors. No deployment may rely solely on uncollected ephemeral local files.

## Metrics and traces

Use Micrometer and the approved tracing integration. Instrument inbound HTTP, outbound HTTP, DB calls, producer sends, and consumers. Propagate context through Kafka headers and asynchronous execution; restore/clear thread-local context after use.

Required metrics include request rate/error/latency, DB pool saturation and query latency, downstream latency/retries/timeouts/circuit state, Kafka send failures, outbox pending count and oldest age, relay throughput, consumer lag when applicable, DLT count, and executor rejection. Use bounded labels such as route templates and dependency names; never use user, event, product, or trace IDs as metric labels.

Set alert thresholds from the API latency and event-delivery objectives. A growing oldest outbox age is actionable even while HTTP returns 201 successfully.
