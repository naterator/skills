---
name: plan-title-create
description: Create a concise slug-style title for a plan. Use when Codex needs to name, title, summarize, or generate a filename-like heading for an implementation plan, remediation plan, project plan, TODO plan, or planning document the user just created or provided.
---

# Plan Title Create

## Workflow

Create exactly one title unless the user asks for options.

Base the title on the plan's overall purpose, not on incidental details, file paths, ticket numbers, or process words. Prefer the core action and affected system.

Use this output format:

- 4 to 8 words.
- All lowercase.
- Hyphens instead of spaces.
- ASCII letters, digits, and hyphens only.
- No surrounding quotes, bullets, labels, punctuation, or explanation.

Treat each hyphen-separated segment as one word. Do not use empty segments, leading hyphens, or trailing hyphens.

Avoid generic titles such as `implementation-plan`, `detailed-remediation-plan`, `final-master-plan`, or `project-task-plan`. Include the substantive change, such as `batch-org-concurrency-limit-lookups` or `propagate-context-through-rate-limiters`.

If the plan content is unavailable or more than one recent plan could be intended, ask one concise clarifying question instead of guessing.

## Examples

Plan about replacing per-org billing queries in scheduler claiming:

`batch-org-concurrency-limit-lookups`

Plan about passing request context into rate limiter Redis operations:

`propagate-context-through-rate-limiters`

Plan about making optional backup inputs warning-only:

`skip-missing-optional-backup-inputs`
