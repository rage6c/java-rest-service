# Configuration

- Application settings MUST bind to typed, immutable `@ConfigurationProperties` objects, registered through `@ConfigurationPropertiesScan` or `@EnableConfigurationProperties`.
- Validate required fields and cross-field relationships during startup. Include the Bean Validation provider; `@Validated` alone does not supply one.
- Use `Duration` for timeouts, `URI` for service addresses, and typed enums for modes. Validate positive bounded durations and approved HTTPS destinations with custom validation where necessary.
- Business services MUST NOT read `Environment`, raw `@Value` strings, or environment variables directly.
- Keep credentials outside committed files. Inject them through the platform secret store or mounted configuration. Never provide production credential fallbacks.
- Configuration errors MUST fail startup with a useful, redacted message. Temporary dependency unavailability is handled through readiness and recovery, not treated as invalid configuration.

Example declaration (imports omitted):

```java
@ConfigurationProperties(prefix = "clients.catalog")
@Validated
public record CatalogClientProperties(
        @NotNull URI baseUrl,
        @NotNull Duration connectTimeout,
        @NotNull Duration requestTimeout) {
    @AssertTrue(message = "catalog timeouts must be positive and bounded")
    public boolean isTimeoutBudgetValid() {
        return connectTimeout != null && requestTimeout != null
                && connectTimeout.compareTo(Duration.ZERO) > 0
                && requestTimeout.compareTo(connectTimeout) >= 0
                && requestTimeout.compareTo(Duration.ofSeconds(30)) <= 0;
    }
}
```

The deployment MUST also validate the URI scheme, host allowlist, and absence of embedded credentials. A syntactically valid URI is not necessarily an authorized destination.

```yaml
spring:
  application:
    name: catalog-service
  datasource:
    url: ${DB_URL}
    username: ${DB_USERNAME}
    password: ${DB_PASSWORD}
  jpa:
    open-in-view: false
    hibernate:
      ddl-auto: validate
    properties:
      hibernate.default_schema: catalog
clients:
  catalog:
    base-url: ${CATALOG_BASE_URL}
    connect-timeout: 1s
    request-timeout: 3s
```

These are configuration excerpts, not complete deployment configuration. Timeout numbers are starting values to validate against the service latency budget.

Use `local`, `sit`, `uat`, `dr`, and `prod` profiles consistently. Set the active profile externally. Shared defaults belong in `application.yml`; profile files contain only non-secret differences. Non-production profiles MUST NOT connect to production databases, topics, or APIs. Test DR credentials, endpoints, and recovery behavior.

Document the actual property sources used by each deployment. Profile configuration overrides shared configuration; environment variables and command-line settings can override files. Do not invent a generic precedence position for every secret-store integration. Spring Boot defines the full ordering in its [externalized configuration documentation](https://docs.spring.io/spring-boot/reference/features/external-config.html).
