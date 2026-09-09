# Service Security

Java services exposing endpoints to other services MUST enforce an explicit authentication and authorization boundary. Apply the same identity and access rules to internal callers.

- Authenticate service callers using the organization's standard, typically OAuth2 resource-server validation or mTLS with a trusted identity mapping. Network location alone is insufficient.
- For JWTs, validate signature, trusted issuer, intended audience, expiry and other applicable time claims, then authorize required scopes. Audience validation MUST be configured and tested, not assumed from an issuer URL. Spring provides configurable validation in its [JWT resource server documentation](https://docs.spring.io/spring-security/reference/servlet/oauth2/resource-server/jwt.html).
- Enforce resource and tenant authorization in application access rules and scoped queries. Never derive trusted tenant identity solely from a body field or arbitrary header.
- If a gateway supplies identity, document cryptographically or network-enforced trust, reject spoofed headers, and prevent direct bypass of that boundary.
- Use standard Spring Security handlers and least-privilege routes. Avoid custom token parsing or homegrown cryptography.
- Configure stateless API sessions where appropriate. Disable CSRF only when the authentication model does not rely on automatically attached browser credentials; document and test that assumption. CORS is not service authentication.
- Use TLS for HTTP, database, and Kafka connections as supported by the platform. Validate certificates/hostnames; never use trust-all clients in deployed profiles.
- Use per-service DB roles and Kafka topic/group ACLs. Separate migration privileges from runtime privileges and restrict replay/admin tools.
- Store and rotate credentials through the platform. Avoid unbounded secret retention in logs, traces, errors, events, or test fixtures.
- Enforce request/body/header limits, rate limits, and dependency concurrency limits. Validate inputs and bind SQL parameters.
- Restrict management endpoints and production documentation. Return redacted errors through both MVC and security-filter handlers.

Where the organization provides these controls in shared infrastructure, document the boundary and prove that the service cannot bypass it. These are requirements for the implementing service, not an instruction to build a new identity provider.
