# Calls to Other Services

## Client boundary

Each downstream system MUST have a typed application-facing interface and a transport adapter. External request/response DTOs remain private to that boundary. Services MUST NOT construct URLs, parse raw HTTP bodies, or handle transport exceptions directly.

Use Spring `RestClient` for this standard's blocking MVC/JPA stack. Use `WebClient` for a deliberately reactive stack or reactive integration. Spring describes these respective execution models in its [REST client documentation](https://docs.spring.io/spring-framework/reference/integration/rest-clients.html). Use generated clients only with reviewed schemas and the same timeout/error policies.

Build and reuse configured client beans. Configure the actual underlying HTTP transport, not just a custom property that no code consumes. Client setup MUST wire base URL, connection establishment timeout, connection acquisition timeout where pooled, response/request timeout, TLS, authentication, tracing, and connection lifecycle.

```java
public interface CatalogClient {
    CatalogItem getItem(UUID id);
}
```

Adapter method excerpt, assuming `restClient` is a configured, injected bean:

```java
public CatalogItem getItem(UUID id) {
    CatalogItemPayload payload = restClient.get()
            .uri("/api/v1/items/{id}", id)
            .retrieve()
            .onStatus(status -> status.value() == 404, (request, response) -> {
                throw new CatalogItemUnavailableException(id);
            })
            .body(CatalogItemPayload.class);
    if (payload == null) {
        throw new InvalidCatalogResponseException("Missing response body");
    }
    return toCatalogItem(payload);
}
```

The full adapter MUST also translate connection/timeout, unexpected status, and deserialization failures; the excerpt only illustrates the normal call and expected absence mapping. Validate business-critical response fields. Never return an empty success to hide dependency failure.

## Timeouts and resilience

- Define a total use-case deadline and per-attempt budget, including pool acquisition, connect/TLS, response, backoff, and retries. Client settings vary by transport; test actual elapsed behavior.
- Retry only transient failures and operations proven safe to replay. A timeout may occur after the remote side effect committed.
- GET reads are typical retry candidates. POST commands need a downstream-supported idempotency key, reused across attempts. PUT/DELETE are retryable only if the actual downstream contract is idempotent.
- Use bounded attempts, exponential backoff with jitter, and a cap within the remaining deadline. Respect `Retry-After` only when it fits the budget. Do not retry validation, authorization, or deterministic business errors.
- Define one retry owner. Nested retries across adapters, framework interceptors, and gateways can multiply traffic.
- Use the platform-approved resilience library for circuit breaking and bounded concurrency where needed. Test open, half-open, and recovery paths.
- Cancellation of local waiting does not guarantee cancellation of the remote operation. Reconcile ambiguous outcomes through idempotency/status lookup.
- Fallbacks MUST preserve business correctness. Never manufacture inventory, payment approval, or successful writes.

## Identity and observability

Use HTTPS and the approved service identity mechanism, such as scoped OAuth client credentials or mTLS. Cache/rotate tokens through the security library. Never blindly forward the inbound `Authorization` header to another audience.

Propagate trace context using instrumentation. Allowlist custom headers; cap and sanitize correlation IDs. Restrict destinations and redirect behavior to prevent SSRF and credential leakage. Record dependency, operation, outcome, latency, retry count, and timeout type; redact payloads and credentials.

Keep calls outside database write transactions. For multi-service mutations, use a persisted workflow or saga; a DB rollback cannot undo a successful remote call.
