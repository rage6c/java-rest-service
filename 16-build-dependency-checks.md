# Build, Dependencies, and Vulnerability Checks

Use one build system per service, Maven by default or Gradle where already standardized. Commit its wrapper and verify wrapper/distribution integrity. Pin the Java toolchain and compiler release, framework BOM, plugins, and container base image.

- Use the Spring Boot dependency management BOM for compatible framework and client versions. Record exceptions and test them; do not independently override Hibernate or Kafka clients casually.
- Select a supported patched release under the organization's support policy. Do not interpret the example Java language level as a claim about the newest JDK or Spring release.
- No dynamic version ranges, unreviewed snapshots, or unpinned build plugins in release builds.
- Review direct and transitive dependencies, deprecated APIs, licenses, and container/OS packages. Produce an SBOM for release artifacts.
- Critical vulnerabilities block merge/release. High vulnerabilities block unless documented risk acceptance has an owner and expiry. Medium findings require a tracked remediation plan. Apply this same policy in CI.
- Use a pinned approved scanner, such as OWASP Dependency-Check or the enterprise equivalent, with an up-to-date advisory database. A failed/stale scan MUST NOT silently pass as a clean report.
- Dependency exceptions MUST identify the component, advisory, exposure, mitigation, owner, and review/expiry date.
- Test framework upgrades against serialization, transactions, security defaults, contracts, and recovery behavior. Keep unrelated upgrades separate.

Required CI pipeline: reproducible dependency resolution; compile; formatting/static analysis; unit and integration tests; overall and changed-line coverage; OpenAPI/event compatibility checks; vulnerability/license scan; immutable artifact/container build and SBOM. Archive test, scan, and contract reports.

Typical commands, only after the implementing service wires the relevant checks into its build:

```bash
./mvnw -B verify
./mvnw -B dependency:tree
```

Gradle alternative:

```bash
./gradlew --no-daemon check
./gradlew --no-daemon dependencies
```

A dependency tree is not a vulnerability scan. Declare scanner/plugin versions in the service build and document its actual CI invocation. Gradle services SHOULD commit dependency locks and verification metadata; Maven services SHOULD pin the resolved inputs and use controlled repositories/BOMs, without pretending Maven has Gradle's native lock-file workflow.
