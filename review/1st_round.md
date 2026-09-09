# Review Round 1 — Java Service Coding Standard

Date: 2026-09-09
Reviewer: Claude Code
Scope: README.md, `JAVA-SERVICE-CODING-STANDARD.md` (consolidated), topic files `01`–`20`, `scripts/build-standard.py`

Editorial note: Cross-platform comparisons and provenance commentary have been removed to keep these notes focused on Java. Findings and verification below describe the original review snapshot.

## What this is

A Java/Spring REST service coding standard — 20 topic documents plus a
generator (`scripts/build-standard.py`) that assembles them into the consolidated
`JAVA-SERVICE-CODING-STANDARD.md` (971 lines). Scope is honest and tightly drawn:
service-to-service REST, relational CRUD, downstream calls, and Kafka with a
transactional outbox.

## Verification performed

| Check | Result |
| --- | --- |
| `python3 scripts/build-standard.py --check` — consolidated doc in sync with topics | Pass |
| External links resolve to the correct pages (fetched: Kafka 4.1 producer-configs, Spring Kafka transactions, Spring Kafka message-listener-container, Spring Security JWT resource server, Spring Boot externalized-config) | All valid |
| Code excerpts checked against current semantics (Spring Boot 4.x / Spring Security 7.x docs era, Kafka 4.1 config defaults) | No errors found |

## Overall verdict

**High quality; no blocking defects.** Unusually careful work for this genre. What stands out:

- **Technical accuracy and currency.** Kafka producer settings are coherent
  (`delivery.timeout.ms` >= `request.timeout.ms` + linger); claims are framed
  correctly ("`acks=all` acknowledges current in-sync replicas; durability depends
  on broker config"). The Kafka 4.1 defaults (idempotence on, `retries = MAX`)
  make the example settings redundant-but-explicit rather than wrong.
  Read-only transaction semantics (04), the pre-flush `@Version` warning
  (18), and "OSIV is not a design basis" are all precisely right.
- **Sophisticated outbox/relay treatment** (18): `FOR UPDATE SKIP LOCKED` claims,
  persisted claim tokens, conditional completion vs. stale workers, the
  ack-before-sent-state-commit window, CDC (Debezium) alternative,
  quarantine/DLT ownership. Most standards stop at "use an outbox."
- **Nuance where it matters**: "a dependency rejecting this service's credentials
  is not the caller's 401"; "a test-managed rollback can hide commit-time
  failures"; "`save()` is not a commit"; problem responses handled by both
  controller advice *and* security-filter handlers.
- **Good governance discipline**: MUST/SHOULD/MAY defined; exceptions require
  recorded decisions; no framework version pinning asserted (wise, given Boot 4.x
  is current); code blocks labeled as excerpts or
  pseudocode so they are not mistaken for a compile-checked reference service.

## Findings

### 1. Medium (pending intent): packaging doesn't match the name — no SKILL.md

The folder is `java-rest-service-skill`, but the README explicitly states this
"is a coding standard and does not install or modify a Codex skill," and there is
no skill metadata (frontmatter, usage/trigger guidance, invocation examples).

- If the target is an AI assistant consuming this as a skill: the entry point is
  missing.
- If it is a human-facing engineering standard: the `-skill` suffix and parent
  folder (`ChatGPT/`) are misleading.

**Action:** decide the target; either add `SKILL.md` + skill packaging, or rename
to something like `java-rest-service-coding-standard`.

### 2. Low: repository hygiene

- `git init` was run but nothing is committed (branch `master`, no commits).
- No `.gitignore`; `.idea/` is untracked.
- Consider `main` instead of `master`.
- Worth adding: a CI step running `python3 scripts/build-standard.py --check` so
  topic/consolidated drift fails the build instead of being a manual step.

### 3. Low: Kafka docs link pinned to `/41/`

All other links are unversioned `docs.spring.io` URLs (which serve the current
baseline — good), but the producer-configs link
(`18-kafka-outbox.md:45`) points at versioned Kafka 4.1 docs, whose own page
notes newer versions exist. Consider `https://kafka.apache.org/documentation/#producerconfigs`
or a link to the org's pinned broker docs, consistent with the "we don't pin
versions" stance.

### 4. Nit: wording

- `20-end-to-end-flow.md:18` — "Optional required reference lookup" is
  contradictory on its face (means "optional lookup, required when reference data
  is needed"). The sequence diagram also labels it "Optional required reference
  lookup (bounded)".
- `03` DELETE row — "Missing resource returns 404 under this standard" reads
  defensively; the table already *is* the standard. The DELETE-returns-404 choice
  itself is fine and well-justified.

### 5. Nit: versioning rationale worth one line

Topic 12 picks URL major versioning. One sentence on why URL-major was chosen
over header/negotiated versioning for internal APIs (e.g., visible routing,
debuggability, and contract-test tooling) would clarify the decision for Java
service developers.

### 6. Minor gaps worth considering (optional, not defects)

- **PATCH media type**: the standard could name RFC 7386 (JSON Merge Patch) vs
  RFC 6902 (JSON Patch) and require picking one per resource.
- **Idempotency-record retention** (`03`): says "covering the client retry
  window," a real requirement with no starting value. A retention default here
  (unlike timeouts) would be directly usable by implementers.
- **PUT/PATCH success code**: "200 or 204" is given as a range; choosing one per
  resource in the OpenAPI contract would be enforceable.

## Suggested actions

1. Commit the baseline (add `.gitignore` first), then decide the SKILL.md vs.
   rename question (Finding 1).
2. Optionally apply the one-line fixes in Findings 4–5.
3. Optionally: CI check for consolidated-doc drift; fill the minor gaps in
   Finding 6.

## Resolution update — findings 1 and 6

- **1 resolved:** Added [SKILL.md](../SKILL.md) with discovery metadata, implementation/review workflow, focused topic routing, and [README invocation examples](../README.md).
- **6 resolved:** [Endpoint guidance](../03-controllers-requests-responses.md) now specifies JSON Merge Patch (RFC 7396, replacing the review's obsolete RFC 7386 citation) and JSON Patch (RFC 6902), their media types and semantics, concrete per-operation retention/expiry requirements with an illustrative duration, and 200-with-DTO versus 204-without-body response rules. The consolidated standard is regenerated from those rules.
