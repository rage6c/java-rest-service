# Merge Review Checklist

All applicable MUST rules are merge requirements. Mark an item not applicable only with a reason. An exception needs a recorded decision, owner, and follow-up where temporary.

## Architecture and endpoints

- [ ] Thin controllers; separate API, persistence, downstream, and event models.
- [ ] Constructor injection; no mutable caller state in singleton beans.
- [ ] Explicit versioned endpoints and complete OpenAPI contract.
- [ ] CRUD statuses, validation, bounded paging, allowed sorting, and safe errors tested.
- [ ] Caller and resource/tenant authorization enforced and tested.
- [ ] Write idempotency and stale-update behavior match the contract.

## Database and integrations

- [ ] Explicit table/schema mapping and reviewed production-engine migrations.
- [ ] Database constraints enforce uniqueness and relational invariants under races.
- [ ] SQL handles filtering/projection/paging; no unbounded scans or accidental N+1.
- [ ] Transaction advice actually applies; failure/commit scenarios tested.
- [ ] DB mutation and required event insert share one local transaction.
- [ ] No downstream or Kafka wait inside a DB write transaction.
- [ ] Typed downstream clients wire real timeouts, identity, safe error mapping, and trace propagation.
- [ ] Retries are bounded and safe after an ambiguous remote outcome.

## Kafka and recovery

- [ ] Stable event ID, schema, aggregate key, version/sequence, and safe payload.
- [ ] Producer acknowledgment and idempotence settings are explicit and compatible.
- [ ] Outbox publication records acknowledgment before sent-state transition.
- [ ] Claim fencing/lease recovery and duplicate publication are handled.
- [ ] Ordering policy survives multiple workers, retries, and partition changes.
- [ ] Consumers, if implemented, commit offsets after durable processing and deduplicate in the DB transaction.
- [ ] Retry limits, DLT/quarantine ownership, alerts, retention, and replay procedure exist.
- [ ] No unsupported claim of exactly-once delivery across DB/HTTP/Kafka.

## Operations and verification

- [ ] Typed validated configuration; no committed or logged secrets.
- [ ] Liveness/readiness reflect actual failure and buffering policy.
- [ ] Tracing, latency/error metrics, oldest outbox age, and relevant lag alerts exist.
- [ ] Bounded pools/queues/batches and graceful shutdown tested.
- [ ] Unit/integration/contract tests pass; 80% overall and 90% changed-line coverage.
- [ ] Formatting, static analysis, dependency/container scans and required CI checks pass.
- [ ] Deployment, schema compatibility, recovery and DR runbooks updated.

## Review examples

Good: query with a bounded repository projection, then return an API page DTO. Bad: `repository.findAll().stream().filter(...)` for a public list endpoint.

Good: call a configured `CatalogClient` outside the DB transaction. Bad: instantiate an HTTP client and retry payment POST unconditionally inside `@Transactional`.

Good: commit `product` and `outbox_event` together, then publish through a recoverable relay. Bad:

```java
repository.save(product);
kafkaTemplate.send(topic, product.getId().toString(), event);
return response; // DB commit and asynchronous Kafka success are uncoordinated.
```

Good: preserve `eventId` when retrying the same stored event. Bad: generate a new event ID on every publication attempt, defeating consumer deduplication.

Good: a consumer DB transaction inserts its deduplication key and changes business state together. Bad: commit an offset first, then update the DB.
