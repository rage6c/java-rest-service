# Services, Queries, and Transactions

## Service contracts

Application interfaces express use cases and return DTOs or application models. They MUST NOT return JPA entities, database streams, lazy collections, or HTTP transport objects. Example:

```java
public interface ProductService {
    ProductResponse create(CreateProductRequest request);
    ProductResponse getById(UUID id);
    ProductPageResponse search(ProductSearchQuery query);
    ProductResponse update(UUID id, UpdateProductRequest request);
    void delete(UUID id);
}
```

Services own data-dependent validation, authorization of resource access, orchestration, mapping, and transaction scope. Inject `Clock` for time and dependency interfaces for outbound operations. Avoid catch-and-continue behavior after a failed write.

## Query execution

- Use Spring Data query methods, JPQL, Criteria/Specifications, or an explicitly selected SQL library inside persistence adapters.
- Apply filtering, ordering, projection, and paging in SQL before materialization. Java `Stream.filter()` over `findAll()` does not translate back to SQL.
- Use bounded, deduplicated scalar collections for `IN` queries. Short-circuit empty inputs and handle database parameter limits for bulk requests.
- Bind query parameters. Sort identifiers MUST come from an allowlist; bind variables cannot protect dynamically concatenated SQL identifiers.
- Use projections for read APIs. Fetch only required associations with deliberate joins/entity graphs and inspect query counts for N+1 behavior.
- Do not paginate a collection fetch join without verifying the database pagination behavior; page IDs first if needed.
- Execute queries and map required lazy state within the owning transaction. Do not depend on Open Session in View.
- JPA read-only transactions provide optimization hints; they do not make returned entities immutable or enforce a write prohibition. Use projections and avoid entity mutations in read paths. See [Spring Data transactionality](https://docs.spring.io/spring-data/jpa/reference/jpa/transactions.html).

## Transaction rules

Place `@Transactional` on public application service methods invoked through Spring-managed proxies. Use `@Transactional(readOnly = true)` for read use cases. A call from one method to another on the same instance does not activate proxy transaction advice; use a separate bean or `TransactionTemplate`. Spring documents this in [transaction annotation behavior](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/annotations.html).

- A business write and its outbox inserts MUST use one database, one transaction manager, and one transaction. Do not use `REQUIRES_NEW` for the outbox insert.
- Keep transactions short. Do not hold DB locks while calling another service or waiting for Kafka.
- Specify the transaction manager when multiple managers exist. A Kafka manager is not a JPA transaction manager.
- Business exceptions SHOULD extend `RuntimeException`. Spring normally rolls back for unchecked exceptions; configure `rollbackFor` when checked failures must roll back and test the behavior. See [Spring rollback rules](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/rolling-back.html).
- Do not catch a persistence exception and continue using a rollback-only transaction. Translate recognized conflicts outside the failed transaction or at the HTTP boundary.
- A successful `save()` or `flush()` is not a successful commit. Return HTTP success only after the transactional proxy completes.
- Choose isolation and locks for actual invariants. Validate race conditions with concurrent tests. Avoid blanket serializable isolation or unbounded lock waits.
- `@Transactional` does not automatically propagate into new threads or make HTTP calls and Kafka atomically commit with the database.

When a downstream read is needed before persistence, perform it outside the transaction, then revalidate local invariants inside the write. A remote availability check is not a reservation. Multi-service state changes MUST use explicit workflow state, idempotent commands, reconciliation, and compensating actions where needed. Do not promise distributed atomicity without an implementation that supplies it.
