# Review Round 2 — Java Service Coding Standard

Date: 2026-09-09
Reviewer: Claude Code
Scope: Deltas since round 1 — new `SKILL.md`, README rewrite (`.NET` context removed, "Java technology choices" added, AI-skill entry point), expanded PATCH/idempotency/response policy in `03-controllers-requests-responses.md`, repository hygiene commits. Re-review of the full document set for consistency. Round 2.5 adds a deep-fit analysis of the artifact's validity as a build/review skill (section below).

## Verification performed

| Check | Result |
| --- | --- |
| `python3 scripts/build-standard.py --check` — consolidated doc in sync after 03/README edits | Pass |
| RFC links added in 03 (`rfc-editor.org/info/rfc7396/`, `rfc6902/`) resolve | Both valid |
| Scrub coherence: grep for `.NET`/`EF`/`C#`/`AsNoTracking`/`xUnit`/`Serilog`/`Codex` across docs | No leftovers; rewritten sentences stand alone and read correctly |
| SKILL.md relative links all point at existing files | Pass |
| Git state: commits on `main`, `.gitignore` covers `.idea/` and build output, review history tracked | Pass |

## Round 1 disposition

| # | Finding | Status |
| --- | --- | --- |
| 1 | No SKILL.md / packaging mismatch | **Resolved** — SKILL.md added; quality reviewed below |
| 2 | Repository hygiene | **Resolved** — 4 commits on `main`, `.gitignore`, `.idea/` excluded |
| 3 | Kafka docs link pinned to `/41/` | **Open** — `18-kafka-outbox.md:45` unchanged |
| 4 | Wording: "Optional required reference lookup"; "under this standard" | **Partially resolved** — 20-end-to-end-flow now says "Reference lookup if needed (bounded)"; the DELETE phrase remains at `03:14` (and consolidated `:201`) |
| 5 | Versioning rationale | **Resolved in substance** — 12 now closes with "URL major versions make the selected contract visible in routing, logs, and contract tests" |
| 6 | PATCH media type, idempotency retention, PUT/PATCH response codes | **Resolved** — reviewed below |

**Correction to round 1:** my round-1 note cited RFC 7386 for JSON Merge Patch; the correct citation is **RFC 7396**, which the resolution uses. Reviewer error, not a document error.

## Verdict

Quality is maintained and the package is now self-consistent as a standalone Java standard plus skill entry point. The resolution work (03 rewrite, README rewrite, SKILL.md) is careful and does not introduce contradictions. No new blocking issues in the documents themselves.

That verdict covers the *standard*. The deep-fit analysis below qualifies the *skill* claim separately: the standard is sound, but as an executable procedure the build claim is only fully valid for in-repo changes, and the review path needs procedure work (findings C–G).

## Review of the changes

### 03 — PATCH, idempotency retention, response codes (resolved finding 6)

- **PATCH format section is technically accurate.** Media types (`application/merge-patch+json`, `application/json-patch+json`), RFC 7396 semantics (omitted = unchanged, null = remove, arrays replaced whole), and RFC 6902 operation semantics are all correctly stated.
- **The subtle merge-patch limitation is handled**: "Merge Patch cannot represent setting an object member to literal null separately from removing it; choose JSON Patch if that distinction matters" — this is the distinction most treatments miss, and it interacts correctly with the existing "PATCH MUST distinguish absent from explicit null" rule.
- Good operational details: reject unsupported media types with 415, allowlist JSON Patch operations and both `path` and `from`, cap operation count and payload size, apply-then-validate-then-commit atomically.
- **Idempotency retention is now concrete and well-hedged**: retention duration with clock start, no deletion of in-progress records, expiry semantics, and the correct point that a finite idempotency cache cannot enforce permanent uniqueness (which needs a longer-lived business rule). The 24 h retry / 48 h retention example is explicitly labeled non-universal. This addresses the gap cleanly without re-introducing unvalidated defaults.
- **200-with-DTO vs 204-without-body** is now an explicit per-operation documented choice — enforceable via OpenAPI as suggested.

### SKILL.md (new artifact)

Structurally sound: proper frontmatter (`name`, `description`), positive and negative scope in the description, workflow steps that respect the target repository's own build/versions, topic routing to avoid loading the whole standard, and honest "essential invariants" that match the topics. The maintenance note correctly points to the generator.

**New finding A (low): missing conflict-handling instruction.** Workflow step 1 preserves the user's explicit choices, but the skill gives no guidance for the common case where the *target repository's existing conventions* conflict with a MUST in this standard. An agent then either silently rewrites working code or silently deviates. Recommend adding an explicit rule: name the applicable rule and surface the conflict to the user; do not silently refactor working code to conform, and do not silently waive a MUST.

**New finding B (nit): invocation syntax is agent-specific.** The README example (`Use $java-rest-service-skill to ...`) is a Codex-style invocation. Claude Code invokes skills by slash command or by request wording, not `$name`. The docs already hedge with a portable fallback ("ask the agent to read this repository's SKILL.md"), which is the right generic path — consider making the example syntax-neutral since the skill claims no product affinity.

## Deep-fit analysis: validity as a build/review skill (round 2.5)

Question posed to this review: *is this artifact actually valid as a skill for building a service, or for reviewing one?* The standard is sound; the question is whether the packaging turns it into an executable procedure.

**Framing.** A coding standard is declarative (MUST/SHOULD). A skill is procedural (do X, then Y, then decide Z). `SKILL.md` supplies a 5-step workflow, a routing table, and an "essential invariants" compression, so it has real procedural content. But the workflow is one generic loop whose steps skew implementation, and the declarative bulk carries differently in each mode.

### Review mode — valid, with two gaps

The standard is unusually good review material: per-operation MUST tables (03, 05), a condition→status mapping, and a ready-made merge checklist (17). A reviewer can walk the checklist nearly line-by-line. Two procedural holes:

- **Finding E (medium-low): review is not a first-class branch.** Step 2 says "read the topic files relevant to the change" — `17-review-checklist.md` appears only in the routing table's last row, so a reviewer can complete a review without ever seeing the checklist. Step 4 ("verify the changed behavior with the target project's configured build") is implementation-flavored; it does not tell the reviewer to verify findings against code and line numbers, or to run the build/tests to confirm a claimed bug before reporting it.
- **Finding F (medium-low): no triage/escalation protocol.** Reviewing an *existing* service against 100+ MUSTs produces noise. The skill gives no rule for which violations are merge-blocking, which need a recorded decision, and which are backlog — the reviewer either reports everything (noise) or silently filters (deviation). The standard itself mandates recorded decisions for exceptions; the skill never tells the agent how to *arrive* at that decision or when to stop and ask the user versus proceed with a documented default. This generalizes round-2 finding A beyond repo-vs-standard conflicts to all judgment calls (the standard deliberately leaves PATCH format, soft vs. physical delete, ordering policy, ETag vs. version-in-body open).

### Build mode — valid for bounded in-repo changes; overclaimed for greenfield

- **Finding C (medium): the "Implement ... services" claim presumes an existing repository.** Step 1 reads "inspect the target repository's instructions, build, framework versions, and existing conventions." For greenfield there is no scaffold path, no dependency-selection guidance, and the standard deliberately declines to state versions — an agent fills from training data (possibly stale — e.g., pre-Boot-4.x-era artifacts) and thereby violates the standard's own pinning MUST. A build skill needs a version-selection rule: ask the user or use the org BOM; never invent a version.
- **Finding D (medium): the highest-risk implementation has no code.** The standard is honest that its snippets are excerpts/pseudocode, "not a compiled reference service." For *review* that is fine — rules are what reviewers need. For *build* it is a material hole exactly where correctness risk is highest: the outbox relay (claim tokens, leases, SKIP LOCKED, conditional completion — the most failure-prone component in the design), the durable idempotency store, and the ProblemDetail advice exist as prose only. An agent will synthesize the hardest 20% of the system from the weakest evidence.
- **Finding F (second half): scope-containment is unpinned.** "Preserve the user's explicit choices and task scope" (step 1) collides with MUST-conformance when the touched file already violates rules (e.g., field injection in a controller the agent must edit). The skill does not say *conform within the changed surface; report pre-existing violations separately; never expand the diff for conformance*. Under MUST pressure, an implementing agent is at real risk of standard-creep diffs.

### What holds

For the uses that do hold — reviewing a service, or implementing targeted changes inside an existing repository — the packaging is right: progressive disclosure via the routing table, honest invariants, generator + `--check` maintenance loop, conflict-aware step 1. Findings C–F are fixable in `SKILL.md` prose alone; only D needs a new artifact (one reviewed reference relay skeleton), and only if the greenfield claim is kept.

**Finding G (nit): trigger overlap.** In a Claude Code environment, "review" in the description overlaps the built-in `code-review`/`code-review-skill` skills. Fine if this standard should win for Java REST services — but state that intent, and make the README invocation examples syntax-neutral (round-2 finding B) since the `$name` form is product-specific.

---

## Remaining open items

1. **Low** — `18-kafka-outbox.md:45`: Kafka producer-configs link pinned to `/41/` while the page itself notes newer versions; the other doc links are deliberately unversioned.
2. **Nit** — `03:14` (and consolidated `:201`): "Missing resource returns 404 under this standard" — the table is the standard; the qualifier reads defensively. The DELETE-returns-404 decision itself is fine.
3. **Medium (C)** — Greenfield overclaim: either narrow the description to "implement changes in / review existing services" or add a scaffold path and a version-selection rule (ask or org BOM; never invent).
4. **Medium (D)** — No code for relay / idempotency store / ProblemDetail advice; an agent builds the hardest parts from prose. Ship one reviewed reference skeleton if the build claim is kept.
5. **Medium-low (E)** — Make review a first-class workflow branch: route reviews through `17-review-checklist.md`, require verifying findings against code before reporting.
6. **Medium-low (F)** — Add an escalation/triage protocol: blocking vs. recorded-decision vs. backlog; conform-within-changed-surface vs. report-preexisting-violations; when to ask vs. default-and-document for the standard's open choices.
7. **Nit (G)** — Clarify intended precedence over built-in review skills; make invocation examples product-neutral (carries round-2 finding B).

## Suggested actions

1. Decide the build claim (C). If kept: add the scaffold/version rule and the reference relay skeleton (D). If narrowed, adjust the description and README wording.
2. Add the review branch and escalation protocol to `SKILL.md` (E, F) — all prose-only changes.
3. Close items 1–2 whenever convenient (link target swap; phrase deletion + regenerate).
4. No further content changes recommended this round.

## Resolution update

The following disposition applies to the updated skill; the original review above is retained as a historical snapshot.

| Finding | Disposition |
| --- | --- |
| A — conflicts | Addressed: explicit handling for governing instructions, conventions, authorized exceptions, and unresolved decisions. Existing practice is not an automatic waiver. |
| B — invocation | Addressed: README uses product-neutral requests and host-supported selection, with direct SKILL.md access. |
| C — greenfield claim | Addressed by narrowing: implementation targets existing services. Greenfield design may use the standard, but the skill does not advertise a tested scaffold. Version selection uses repository pins, an organization catalog, or verified official compatibility information. |
| D — reference implementations | No new production skeleton added. Narrowing resolves the scaffold claim; high-risk changes still require complete implementation, API inspection, and applicable failure-path verification. A generic untested relay would not establish correctness. |
| E — review workflow | Addressed: reviews must load the merge checklist, verify suspected findings against code, distinguish static evidence from unresolved hypotheses, and cite precise locations. Tests are used when useful and feasible, not required to establish every static defect. |
| F — triage and scope | Addressed: changed-scope merge requirements, separate pre-existing gaps, recorded exceptions, and default-versus-clarification guidance. The checklist now matches the skill's scope policy. |
| G — overlap | Clarified: this skill provides Java REST rules and complements general review procedures; it does not claim automatic precedence over other skills or governing instructions. |
| Kafka citation | Retained intentionally. A versioned technical citation supports the documented settings and does not pin every implementing service to that version. |
| DELETE wording | Addressed: removed the redundant qualifier and regenerated the consolidated document. |

Validation covers skill structure, documentation links, and consolidated output consistency. No production relay scaffold or live service execution is claimed by this update.
