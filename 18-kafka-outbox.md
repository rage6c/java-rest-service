# Kafka Messaging and Transactional Outbox

## Delivery contract

Kafka is a partitioned event log. Records go to topics; instances in the same consumer group share processing, while distinct groups independently consume the topic. Do not model pub/sub by assigning every subscriber the same group ID.

For a business event associated with a database mutation, the service MUST use a transactional outbox or an explicitly reviewed durable equivalent. This standard selects the outbox. An after-commit callback or in-memory application event alone is not sufficient: the process can stop after DB commit and before publication.

Successful HTTP completion means the database mutation and outbox event committed. Kafka delivery is asynchronous and at least once. It does not mean subscribers completed processing. Kafka transactions can cover Kafka consume/process/produce operations; they do not make a relational database and broker one atomic resource. Spring documents failure handling between coordinated resource commits in [Kafka transactions](https://docs.spring.io/spring-kafka/reference/kafka/transactions.html).

## Event contract

Use a versioned schema (Avro, Protobuf, or JSON Schema) and enforce the chosen compatibility mode in CI/registry. Include:

```json
{
  "eventId": "a79283bb-b4b6-40fb-9b84-997ad0d98727",
  "eventType": "ProductCreated",
  "schemaVersion": 1,
  "occurredAt": "2026-09-09T08:30:00Z",
  "producer": "catalog-service",
  "aggregateType": "Product",
  "aggregateId": "c435b514-3abc-426f-93f8-ea996db41901",
  "aggregateVersion": 1,
  "data": {
    "name": "Notebook",
    "unitPrice": "12.50",
    "currency": "SGD",
    "stockQuantity": 20
  }
}
```

This event represents the API's validated currency explicitly and uses a decimal string for money under its schema. Do not infer currency from deployment timezone.

- Generate the event ID once, store it, and reuse the exact event on retry. Event time is when the business fact occurred, not the latest send attempt.
- Key by aggregate ID, or a tenant-qualified aggregate ID when needed. Put trace context in bounded Kafka headers; add correlation/causation IDs when the workflow needs them. Never use secrets as headers.
- `aggregateVersion` is a business event sequence assigned under aggregate concurrency control. Do not assume a pre-flush JPA `@Version` value is the committed sequence. If multiple events occur in a single change, define an event ordinal or independent sequence.
- Publish business facts with purpose-specific fields, not serialized JPA entities. Exclude secrets and unnecessary personal data. Validate size before commit; oversized data should use an authorized durable reference when appropriate.
- Prefer compatible additive changes. Removing/renaming fields, changing type/meaning/key, or changing enum assumptions requires migration. Test against supported consumer schemas, not only the latest schema.
- Topics MUST have an owner, naming convention (for example `catalog.product.events.v1`), partition plan, retention, ACLs, and replay policy. Breaking contract changes may require a new topic; not every additive schema change does.

## Producer policy

Explicitly configure `acks=all`, `enable.idempotence=true`, retries greater than zero, and a compatible in-flight limit (use 5 or lower for the baseline). Set bounded delivery/request/blocking timeouts and check `delivery.timeout.ms` covers request timeout plus linger. These constraints are documented in [Kafka producer configuration](https://kafka.apache.org/41/configuration/producer-configs/).

Example Spring Boot producer settings; serialization and security must be configured separately for the selected schema and platform:

```yaml
spring:
  kafka:
    bootstrap-servers: ${KAFKA_BOOTSTRAP_SERVERS}
    producer:
      acks: all
      retries: 10
      properties:
        "enable.idempotence": true
        "max.in.flight.requests.per.connection": 5
        "request.timeout.ms": 10000
        "delivery.timeout.ms": 30000
        "max.block.ms": 5000
```

Infrastructure SHOULD use replication factor at least 3 and `min.insync.replicas` at least 2 where the cluster supports that availability model. Review unclean leader election and retention against durability requirements. `acks=all` acknowledges current in-sync replicas; its durability depends on broker/topic configuration, not only the client.

Use a managed `KafkaTemplate`/producer adapter. Observe both synchronous send failures and asynchronous completion. Producer idempotence reduces duplicates from producer protocol retries; it does not deduplicate separate application-level replays after a restart. Do not discard the send future or log success before acknowledgment.

## Outbox storage and relay

Store at least `event_id` (unique), aggregate type/ID, event sequence, event type/schema version, payload, headers, occurred time, publication state, attempt count, next-attempt time, and published time. A polling relay also needs claim owner/token and lease expiry. Index pending work by state and due time; enforce aggregate sequence uniqueness if the contract requires it.

1. In a short local transaction, validate/mutate business rows and insert the immutable outbox event. Serialization or insert failure MUST roll back the business change.
2. Relay claims a bounded due batch in a short transaction using a supported locking/lease strategy, such as `FOR UPDATE SKIP LOCKED` plus a persisted claim token. Commit the claim before network I/O.
3. Send the stored record to the chosen topic/key. Await broker acknowledgment outside the DB transaction under a bounded send budget.
4. In a new short transaction, conditionally mark it published only if the worker still owns the claim token. A timeout/failure leaves the event retryable with backoff; an expired claim is recoverable.
5. Clean up acknowledged records under a documented retention/archive policy. Never purge pending or quarantined records just because they are old.

A lease MUST cover expected send time or be safely renewed. Conditional completion protects state from stale workers, but cannot undo an already transmitted stale send. Duplicate delivery remains possible. A crash after acknowledgment and before marking published MUST lead to safe republishing, not data loss.

A CDC relay such as Debezium is an alternative to application polling. Map the outbox schema to its connector contract, operate offsets/replication slots and retention, and avoid running both relays for the same events. The [Debezium outbox router](https://debezium.io/documentation/reference/stable/transformations/outbox-event-router.html) documents its event ID, key, and payload mapping. Polling-specific status fields are not automatically required by a CDC design.

## Ordering

Kafka order is per partition. Using the same key is necessary for aggregate ordering but does not prevent two relay workers from sending aggregate events out of sequence.

If ordering matters, serialize publication per aggregate and prevent sequence N+1 from being released while N is unresolved. Define handling of stale workers, duplicate older events, and sequence gaps. Consumers may need version checks or buffering/reconciliation. Increasing partition count can change key placement; review ordering during partition migrations. Retry topics and DLT diversion can allow later events to overtake failed events.

If ordering does not matter, state that explicitly and require consumers to tolerate reordering. Do not imply global event order.

## Consumers, where implemented

- Configure explicit group IDs and `enable.auto.commit=false`. Choose container acknowledgment behavior deliberately, such as record acknowledgment after successful listener completion; Spring explains modes in [listener container documentation](https://docs.spring.io/spring-kafka/reference/kafka/receiving-messages/message-listener-container.html).
- Listener delegates to a transactional service. Insert a unique `(consumer_name, event_id)` processed marker and update business state in the same DB transaction. Use an atomic insert-if-absent mechanism; do not catch a unique violation and continue in a failed transaction.
- Complete/acknowledge the Kafka record only after that DB transaction commits. If offset commit fails, replay must become a no-op through the processed marker. Keep markers at least as long as the supported replay window.
- Do not acknowledge before durable processing or swallow listener exceptions. Configure deserialization failures as well as business processing failures.
- If consuming transactional Kafka producers, use `read_committed` where aborted records must be hidden. This does not provide exactly-once HTTP effects.
- External side effects need their own durable command/outbox and idempotency strategy. A processed marker alone cannot atomically protect a remote call.
- Bound batch processing relative to `max.poll.interval.ms` and `max.poll.records`; test rebalances and shutdown. Listener concurrency beyond partition count does not create additional partition parallelism.

## Retry, quarantine, and replay

Classify transient infrastructure failures separately from invalid schema/data or deterministic business rejection. Use bounded attempts/backoff and total retry-age limits. After exhaustion, retain producer outbox work in an operator-visible quarantine state; it may be impossible to publish to a DLT while the broker is unavailable.

Consumers may route failed records to a DLT with original topic/partition/offset, event ID, attempts, and safe failure code. Commit the source offset only after confirmed durable recovery/DLT publication; DLT-send failure MUST not discard the source record. Define ordering consequences and access controls.

Every DLT/quarantine requires an owner, alert, retention, diagnostic procedure, and audited replay tool. Replays preserve original event IDs for unchanged events; corrected business events need an explicit new identity/causation policy. Do not replay blindly into live financial or inventory side effects. Monitor oldest pending age, lag, failed sends, and quarantine counts against the event-delivery objective.
