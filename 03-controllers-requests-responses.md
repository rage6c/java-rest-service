# Controllers, Requests, and Responses

## Endpoints exposed to other services

Use `@RestController`, an explicit versioned resource path, constructor injection, and purpose-specific DTOs. Prefer `ResponseEntity<T>` when status or headers vary.

| Operation | Example | Success | Required behavior |
| --- | --- | --- | --- |
| Create | `POST /api/v1/products` | 201 | Response DTO and `Location` after DB commit |
| List | `GET /api/v1/products?page=0&pageSize=25` | 200 | Bounded stable page; empty collection is valid |
| Read | `GET /api/v1/products/{id}` | 200 | Missing resource returns 404 |
| Replace | `PUT /api/v1/products/{id}` | 200 with DTO; 204 without body | Complete mutable representation; no implicit create |
| Partial update | `PATCH /api/v1/products/{id}` | 200 with DTO; 204 without body | Explicit patch media type and null/absent semantics |
| Delete | `DELETE /api/v1/products/{id}` | 204 | Missing resource returns 404 under this standard |
| Start asynchronous workflow | `POST /api/v1/jobs` | 202 | Persisted acceptance and a status resource in `Location` |

A repeated DELETE returning 404 can still be idempotent: the resource remains absent. Choose and document one behavior per API. GET MUST have no business side effects. Use 405 for unsupported methods and 415 for unsupported request media types.

PUT and PATCH operations MUST document their success response in OpenAPI: return 200 with the updated response DTO, or 204 with no response body. Use one default per operation. If a documented response preference permits both, define the selection rule and test both paths; do not switch arbitrarily.

## Inputs and contracts

- Bind explicitly with `@PathVariable`, `@RequestParam`, `@ModelAttribute`, and `@RequestBody`. Validate body DTOs with `@Valid`; configure and test parameter validation too.
- Use query DTOs for complex filtering. Default to zero-based pages, page size 25, maximum 100; reject invalid values. Allowlist sort fields and add an ID tie-breaker.
- Do not accept persistence entities as input. Reject or deliberately ignore unknown fields under a documented compatibility policy; never mass-assign them.
- Do not accept ownership, tenant, audit timestamps, or privilege fields from untrusted bodies. Resolve caller identity from trusted authentication.
- PUT MUST define all required mutable fields. PATCH MUST distinguish absent from explicit null and allowlist editable fields. Never implement PATCH as unrestricted reflection over an entity.
- Serialize timestamps as ISO 8601 UTC. Use `BigDecimal` with explicit scale and currency for monetary amounts. Avoid binary floating-point prices.
- Define request, response, header, and batch size limits. Never include secrets in URL parameters.

```java
public record CreateProductRequest(
        @NotBlank @Size(max = 120) String name,
        @NotNull @DecimalMin("0.01") @Digits(integer = 16, fraction = 2)
        BigDecimal unitPrice,
        @NotBlank @Pattern(regexp = "[A-Z]{3}") String currency,
        @NotNull @Min(0) Integer stockQuantity) {}

public record ProductResponse(
        UUID id, String name, BigDecimal unitPrice, String currency, int stockQuantity,
        long version, Instant createdAt, Instant updatedAt) {}
```

Validate currency against the supported ISO currency allowlist; the three-letter pattern only checks shape.

Normalize text intentionally and validate the normalized value before saving. Do not silently trim passwords, identifiers with significant whitespace, or signed payloads.

Controller excerpt; application service implementations and imports are omitted:

```java
@RestController
@RequestMapping("/api/v1/products")
public class ProductController {
    private final ProductService products;

    public ProductController(ProductService products) {
        this.products = products;
    }

    @PostMapping
    public ResponseEntity<ProductResponse> create(
            @Valid @RequestBody CreateProductRequest request) {
        ProductResponse result = products.create(request);
        return ResponseEntity.created(
                URI.create("/api/v1/products/" + result.id())).body(result);
    }

    @GetMapping("/{id}")
    public ProductResponse get(@PathVariable("id") UUID id) {
        return products.getById(id);
    }
}
```

Authorization MUST be enforced in the configured security boundary and resource access rules; annotations above alone do not secure the endpoint. See [19-security.md](19-security.md).

For list responses, use a stable application page DTO (`items`, `page`, `pageSize`, `hasNext`, optional `totalElements`) rather than serializing framework page internals. Large exports SHOULD run asynchronously or stream under an explicit media type and timeout. Once a stream starts, an error cannot reliably become a new JSON problem response.

For multipart uploads, enforce count and byte limits, validate actual content, generate storage names, prevent path traversal, and stream where practical. Return binary downloads with explicit content type and safe disposition; release streams on completion or failure.

## PATCH format

Each PATCH operation MUST select and document its supported format, media type, schema, and examples. Use JSON Merge Patch for object-field updates when its null and array semantics fit; use JSON Patch when callers need explicit operations. Do not treat a generic `application/json` body as an unspecified patch language.

| Format | Media type | Semantics |
| --- | --- | --- |
| [JSON Merge Patch, RFC 7396](https://www.rfc-editor.org/info/rfc7396/) | `application/merge-patch+json` | Omitted members remain unchanged; null removes a member; arrays are replaced as a whole |
| [JSON Patch, RFC 6902](https://www.rfc-editor.org/info/rfc6902/) | `application/json-patch+json` | Ordered operations such as add, remove, replace, and test; values may explicitly be null |

Reject unsupported request media types with 415. Apply a patch to an API-facing representation, validate the resulting state, and persist the complete change atomically. For JSON Patch, validate allowed operations and both `path` and `from` access where relevant; cap operation count and payload size. Reject changes to server-owned fields and removal of mandatory fields. Merge Patch cannot represent setting an object member to literal null separately from removing it; choose JSON Patch if that distinction matters.

## HTTP write idempotency and concurrency

Require an `Idempotency-Key` for commands whose automatic replay could duplicate costly or irreversible effects. Store a unique `(caller/tenant, operation, key)` record, canonical request hash, processing state, and replayable outcome durably. For a local DB write, commit that record with the change and outbox rows. Same key and same payload replays the original outcome; same key and different payload returns 409. Concurrent requests MUST be resolved by a database constraint, not a memory cache. Document in-progress behavior and the retention policy below.

For each idempotent operation, the service MUST document:

- A concrete retention duration and when its clock starts. Retain completed outcomes for at least the supported client retry window, including delayed retries after outages. Choose the duration from that contract rather than assuming one value fits every service.
- A cleanup policy that does not delete in-progress records solely because a response-retention TTL elapsed. Recover or reconcile abandoned processing before releasing its key.
- What happens after expiry: once a key is forgotten, reusing it can execute a new operation. Clients MUST NOT rely on deduplication beyond the advertised window; reconcile an ambiguous old outcome before sending a fresh command.
- Any longer-lived business uniqueness rule needed for effects that must never be repeated. A finite idempotency cache cannot enforce permanent uniqueness.

For example, an operation supporting retries for up to 24 hours could retain completed outcomes for 48 hours after completion to provide an operational margin. This is an example to validate against the service's retry and recovery requirements, not a universal retention default. Test replay before expiry, handling after expiry, and cleanup concurrent with in-progress requests.

For updates, require an expected `version` in the update DTO and compare it before mutation, alongside JPA `@Version` for concurrent commits; stale versions return 409. If adopting HTTP `ETag`/`If-Match` instead, document the validator and return 412 for failed preconditions and 428 for required missing preconditions. Do not silently overwrite a stale update.
