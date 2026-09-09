# API Versioning and Compatibility

Use explicit URL major versions, such as `/api/v1/products`, for endpoints consumed by independently deployed services. An internal network does not eliminate compatibility requirements.

- Do not silently route unversioned calls to the latest major version. Reject unsupported routes or provide an explicitly documented stable legacy alias.
- Within a major version, preserve field names/types, requiredness, status semantics, identity rules, pagination, authorization expectations, and idempotency behavior.
- Adding an optional response field is usually compatible only when consumers tolerate unknown properties. Enum expansion, validation tightening, default changes, and altered ordering require consumer assessment.
- Breaking changes require a new major contract or a coordinated migration agreed with every consumer. Application build versions are not API versions.
- Publish migration instructions, deprecation notice, sunset date, and usage metrics. Remove a version only after the agreed migration and sunset conditions are met.
- Maintain an OpenAPI document and contract tests for every supported major version.
- Use parallel deployment and expand/contract database migrations so old and new service instances can coexist.
- Version Kafka schemas independently of HTTP routes. An API major change does not automatically require a new topic.

This intentionally resolves the reference's conflicting rules about internal API versioning and defaulting to the latest version: independently deployed consumers always get an explicit stable contract here.
