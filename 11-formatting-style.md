# Formatting and Java Style

- Select and pin one formatter configuration in the build, such as Spotless with an approved Java formatter. CI MUST verify the same formatting used locally. Example snippets use four-space indentation; repository formatter output is authoritative.
- Use UTF-8, LF line endings, a final newline, and explicit imports. Remove unused imports and wildcard imports.
- Name variables for intent. Use `var` only where the initializer makes the type clear; avoid it when it conceals units, contracts, or generics that matter.
- Prefer immutable records for DTOs and explicit behavior on business objects. Defensively copy mutable collections exposed by immutable contracts.
- Use `Optional<T>` for meaningful optional return values, not as JPA fields or mandatory request fields. Never return null instead of an empty collection.
- Declare a nullability convention supported by the chosen baseline and static analyzer. Bean Validation and compile-time null analysis solve different problems.
- Use try-with-resources for resources owned by the current method. Do not close shared Spring-managed clients or pools per request.
- Catch narrow exceptions, preserve causes, and avoid empty catch blocks. Do not use exceptions for normal loop control.
- Use `BigDecimal` created from decimal text or exact values for money, with explicit rounding. Use `Instant`, `LocalDate`, and `Duration` according to meaning; never use the server default timezone implicitly.
- Avoid public mutable fields, magic numbers, large utility classes, and commented-out code. Comments explain decisions and invariants.
- Use static analysis such as Checkstyle and SpotBugs with reviewed rules. A warning suppression MUST explain the local reason; do not disable entire rule families to pass CI.

Commit `.editorconfig`, formatter settings, and analyzer configuration in each implementing service. This documentation repository does not prescribe unconfigured build commands as if checks already existed.
