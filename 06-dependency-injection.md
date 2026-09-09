# Dependency Injection

- MUST use constructor injection and `final` dependency fields. No field injection or application-level service locator calls.
- Controllers, stateless application services, repositories, configured clients, and typed configuration normally use Spring's singleton bean scope.
- Singleton beans MUST NOT store mutable request state, caller identity, an active transaction, a JDBC connection, or a shared entity instance.
- Inject Spring-managed repository/transaction-aware persistence proxies. Do not share a raw `EntityManager` between threads. A transaction-bound persistence context is not the same as a singleton context.
- Use request scope only for a real request-scoped concern, with a scoped proxy/provider when required. Background work MUST receive immutable context explicitly.
- Register infrastructure through focused `@Configuration` classes and `@Bean` methods. Use `@Qualifier` for multiple implementations and keep component scans within owned packages.
- Keep dependency graphs acyclic. Do not enable circular references to conceal responsibility problems.
- Create interfaces at meaningful service and external boundaries; do not create an interface for every DTO or trivial helper.
- Objects requiring proxy advice must be created by Spring. Do not instantiate a transactional service with `new` in production orchestration code.

Stateless Spring services are normally singleton beans. In the blocking MVC/JPA stack, transaction state and persistence contexts are bound to the executing thread through Spring-managed infrastructure.
