---
name: find-new-work
description: Audit the current repository for prioritized bug fixes, test
  gaps, stale tests, product enhancements, and documentation drift.
  When the user asks to find new work, refresh TODO.md, identify follow-up
  engineering tasks, clean up outdated tests, and keep AGENTS.md and
  README.md aligned with the codebase.
---

# Find New Work

Find and land worthwhile follow-up work without inventing backlog
noise. Prefer issues that are grounded in actual code, tests, and
public contract drift.

## Workflow

1. Start with the canonical docs.
   - Read `AGENTS.md` and `README.md`.
   - Read `TODO.md` before proposing anything new.
2. Inspect the codebase broadly.
   - Search for stale route names, dead handlers, duplicated logic,
     mismatched request/response types, and doc drift.
   - Review tests for missing coverage, outdated assertions, and tests
     that no longer match current behavior.
   - Favor real findings over speculative cleanup.
3. Classify findings before editing `TODO.md`.
   - `P0`: correctness, security, data loss, broken behavior, or
     regressions that can ship bad behavior now
   - `P1`: important bugs, missing coverage on risky paths, major DX or
     reliability issues
   - `P2`: useful enhancements, moderate test debt, maintainability
     improvements
   - `P3`: low-risk cleanup, polish, or optional product follow-ups
4. Deduplicate against `TODO.md`.
   - Do not add a new item if the same work already exists, even if the
     wording differs.
   - Prefer tightening an existing item over adding a near-duplicate.
5. Update code and tests when the request includes execution.
   - Add missing tests for the issues you fix.
   - Update stale tests whose assertions no longer match current
     behavior.
   - Remove tests that only cover deleted or intentionally retired
     behavior.
6. Sync durable docs after code changes.
   - Keep `README.md` aligned with the implementation.
   - Update `AGENTS.md` only with durable engineering facts relevant to
     the code in the project.

## TODO Rules

- Keep entries short, actionable, and implementation-oriented.
- Group new entries under the correct priority band.
- Mention the concrete risk or gap, not just a vague cleanup label.
- Avoid file-by-file inventories in `TODO.md`.

## Review Heuristics

- Prefer durable improvements over churn-heavy refactors.
- If you cannot prove a problem from the code, docs, tests, or command
  output, do not add it as backlog.
