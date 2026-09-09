# Project Structure and Naming

## Required boundaries

Use packages by business capability, with layers inside each capability. A small service may use top-level layer packages if these boundaries remain clear.

```text
src/main/java/com/company/catalog/
  CatalogApplication.java
  configuration/                 Typed settings and bean wiring
  product/
    api/                         Controllers, HTTP request/response DTOs
    application/                 Use-case interfaces and implementations
    domain/                      Business models, rules, application exceptions
    persistence/                 JPA entities, repositories, persistence mapping
    integration/                 Outbound client interfaces, adapters, external DTOs
    messaging/                   Event contracts, outbox writer and relay
  error/                         Central HTTP exception handling
  observability/                 Logging, tracing, metrics
src/main/resources/
  application.yml
  application-{profile}.yml
  db/migration/
  logback-spring.xml              When custom appenders are required
src/test/java/com/company/catalog/
contracts/
  openapi/
  events/
```

- Controllers MUST delegate to application services. They MUST NOT query repositories, call HTTP clients, or publish Kafka records directly.
- Application services own business decisions and transaction boundaries. Repositories own queries; integration adapters own transport behavior; messaging adapters own publication.
- API DTOs, external-service DTOs, persistence entities, and event payloads MUST be separate contracts. Map explicitly across boundaries.
- Dependencies MUST NOT point from domain code into controllers. Shared utilities MUST NOT become a second business layer.
- Interfaces MUST describe use cases or dependency boundaries, such as `ProductService`, `CatalogClient`, and `OutboxWriter`. Avoid generic service abstractions that only repeat repository CRUD.
- Do not expose persistence entities, `EntityManager`, HTTP responses from dependencies, or Kafka transport records through API-facing service contracts.

## Naming

| Item | Convention | Example |
| --- | --- | --- |
| Package | Lowercase, reverse domain | `com.company.catalog.product` |
| Class/interface/record | UpperCamelCase, no `I` prefix | `ProductService`, `ProductResponse` |
| Implementation | Describe responsibility | `DefaultProductService`, `HttpCatalogClient` |
| Method/field/local | lowerCamelCase | `findById`, `unitPrice` |
| Constant | UPPER_SNAKE_CASE | `MAX_PAGE_SIZE` |
| Input DTO | Action + resource + Request | `CreateProductRequest` |
| Event | Past-tense business fact | `ProductCreated` |
| Exception | Meaning + Exception | `ProductNotFoundException` |
| Database identifier | snake_case | `catalog.product`, `unit_price` |

Use one public top-level type per file. Do not add `Async` to every I/O method: blocking Java methods are synchronous; async return types must reflect actual asynchronous behavior.
