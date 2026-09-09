# Concurrency and Performance

The default stack is blocking Spring MVC with JPA and `RestClient`. Ordinary synchronous methods are appropriate. Do not wrap each database operation in `CompletableFuture` merely to imitate .NET async methods.

- Do not execute JPA/JDBC or blocking HTTP calls on reactive event-loop threads. A reactive service must explicitly choose its persistence and execution model.
- Virtual threads are optional after compatibility and load testing. They do not increase database connection capacity or remove the need for concurrency limits.
- Use bounded executors, queues, connection pools, batch sizes, and payloads. Specify saturation behavior and load shedding; never create unbounded task fan-out.
- Avoid blocking I/O on the common `ForkJoinPool` or `parallelStream()`. Explicitly own executors used by `CompletableFuture`.
- `@Async` and transaction proxying are separate concerns. A background task needs its own transaction through a managed service; do not pass managed entities to another thread.
- Durable work MUST be represented in a database or broker before the request completes. An in-memory future or `@Async` invocation is not durable acceptance.
- Preserve interrupt status when handling `InterruptedException`, then stop or propagate. Use bounded shutdown waits.
- Enforce server request deadlines, HTTP transport timeouts, JDBC/query timeouts, and lock waits. Java has no automatic equivalent of ASP.NET request cancellation propagated through every JPA call.
- Do not assume client disconnection rolls back an already committed transaction. Idempotency handles safe retries after ambiguous responses.
- Profile query plans, indexes, allocation, connection usage, serialization, and tail latency before introducing caches or parallelism.
- Caches MUST define keys, tenant isolation, TTL, invalidation, stale-read tolerance, and size limits. Do not cache authorization decisions across principals accidentally.
- Compress suitable responses at the application or gateway after measuring CPU/latency; avoid recompressing already-compressed binary formats.

Use pagination for ordinary collection APIs. Stream only with an explicit contract and resource cleanup. Do not hold a database transaction open for an unbounded slow client download.
