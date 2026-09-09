# OpenAPI and Event Documentation

Every exposed service API MUST have a version-controlled OpenAPI contract or a reproducibly generated contract artifact. Use one approach consistently; select an OpenAPI integration compatible with the pinned Spring Boot baseline.

Document for each operation:

- Stable `operationId`, route, HTTP method, purpose, caller permissions/scopes.
- Path/query/header/body schemas, bounds, requiredness, null behavior, format, and safe examples.
- Success and applicable error responses using the common problem schema.
- Pagination, sorting, concurrency version or ETag, and idempotency-key behavior.
- Side effects, emitted event types, and what successful HTTP completion guarantees.
- Timeout/retry expectations, rate limiting, and asynchronous status resources where relevant.

The service MUST distinguish “database commit and durable event scheduling succeeded” from “all subscribers processed the event.” Document eventual consistency explicitly.

Keep OpenAPI JSON and UI disabled on public production routes by default. Provide internal authenticated documentation or publish the reviewed artifact to the service catalog. Never include real tokens or customer examples. CI MUST detect incompatible contract changes and verify representative runtime responses match the contract.

For Kafka, keep schemas and examples under `contracts/events/`, or a linked registry with versioned source. Use AsyncAPI or equivalent event documentation to define topic, owner, key, envelope, schema version, producer/consumer groups, retention, ordering, delivery, retries, and dead-letter policy. REST documentation does not substitute for an event contract.

The service README MUST include local startup, dependency provisioning, build/test commands, migrations, environment variables, health routes, ownership, SLOs, and runbook links.
