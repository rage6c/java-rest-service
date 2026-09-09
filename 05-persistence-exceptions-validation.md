# Persistence, Exceptions, and Validation

## Mapping and migrations

Use Spring Data JPA/Hibernate for the default relational persistence model. A service may select JDBC, jOOQ, or another store through an architecture decision; the consistency and boundary rules still apply.

- JPA mapping annotations belong on persistence entities. Keep API DTOs separate. Unlike the C# reference, Java does not require an EF-style fluent mapping layer; use JPA XML only when that is the repository convention.
- Specify schema and table names explicitly for databases supporting schemas. Configure the default Hibernate schema consistently. For databases using a catalog instead, document the equivalent mapping.
- Define column lengths, nullability, numeric precision/scale, keys, relationships, and optimistic locking. Enforce invariants through migrations, not only Java validation.
- Use Flyway or Liquibase as the single migration owner. Never use `ddl-auto=create`, `create-drop`, or `update` in production. Prefer `validate` for Hibernate.
- Run migrations through a controlled deployment step or a coordinated startup mechanism with locking. Runtime DB credentials SHOULD NOT have schema-alteration rights.
- Use expand/migrate/contract changes for rolling deployments. Do not edit migrations already applied in shared environments. Test both clean install and upgrade from the previous supported schema.
- Use UTC instants for audit times and an injected `Clock`; choose native database types that preserve the instant correctly.

Entity excerpt, not a complete class:

```java
@Entity
@Table(name = "product", schema = "catalog")
public class ProductEntity {
    @Id
    private UUID id;

    @Version
    private long version;

    @Column(name = "name", nullable = false, length = 120)
    private String name;

    @Column(name = "unit_price", nullable = false, precision = 18, scale = 2)
    private BigDecimal unitPrice;

    protected ProductEntity() {} // Required for persistence construction.
    // Explicit constructors, behavior, other mapped fields, and accessors omitted.
}
```

Avoid Lombok `@Data` on entities: generated equality, hashing, and string output can traverse associations or mutable persistence state. Do not serialize entities into events.

## CRUD requirements

| Operation | Mandatory checks |
| --- | --- |
| Create | Normalize and validate; assign server identity/audit data; DB uniqueness constraint; insert corresponding event if contract requires it |
| Read | Scope by authorized tenant/resource; project required fields; bounded lists; return 404 for absence |
| Update | Load authorized entity; validate expected version and transitions; change allowed fields; persist event in same transaction |
| Delete | Check ownership, references, and business rules; choose physical or soft delete explicitly; persist deletion event in same transaction |

A pre-insert `exists` check may improve an error message but MUST NOT replace a unique constraint. Define uniqueness scope and case normalization. Map only recognized duplicate-key constraints to 409; a connection failure or unrelated integrity failure is not a duplicate.

Soft deletion MUST define query filtering, uniqueness reuse, retention, purge behavior, and event semantics. Cascade deletes MUST be intentional; avoid cascading across aggregate ownership. Bulk updates MUST account for bypassed entity callbacks, stale persistence context, version checks, and event creation.

## Errors and validation

Use `@RestControllerAdvice`, normally extending `ResponseEntityExceptionHandler`, to centralize HTTP error handling. Spring provides RFC 9457 `ProblemDetail` and `application/problem+json` support. See [Spring error responses](https://docs.spring.io/spring-framework/reference/web/webmvc/mvc-ann-rest-exceptions.html).

| Condition | Status |
| --- | --- |
| Malformed JSON, invalid field, missing input, invalid path/query | 400 |
| Missing/invalid authentication | 401 |
| Authenticated caller lacks permission | 403 |
| Resource absent, or intentionally hidden by access policy | 404 |
| Known unique conflict, stale body version, invalid state transition | 409 |
| Failed `If-Match` precondition | 412 |
| Payload too large / unsupported media type | 413 / 415 |
| Local request rate limit | 429, with retry guidance when known |
| Invalid upstream response | 502 |
| Required dependency unavailable / circuit open | 503 |
| Timed-out upstream request when acting as gateway | 504 |
| Unexpected application defect | 500 |

Map downstream failures according to the local API contract, not by copying every downstream status. A dependency rejecting this service's credentials is not the caller's 401.

```json
{
  "type": "urn:problem:catalog:validation",
  "title": "Request validation failed",
  "status": 400,
  "detail": "One or more fields are invalid.",
  "instance": "/api/v1/products",
  "code": "VALIDATION_FAILED",
  "traceId": "4bf92f3577b34da6a3ce929d0e0e4736",
  "errors": [{"field": "name", "code": "NotBlank", "message": "Must not be blank"}]
}
```

Use stable machine-readable codes. Include safe field paths and messages, never rejected secret values. Handle framework binding/validation failures as well as application exceptions. Security-filter failures need dedicated handlers because controller advice does not cover the entire filter chain. Log unexpected exceptions once with a trace identifier; never send stack traces, SQL, or raw upstream bodies to callers.
