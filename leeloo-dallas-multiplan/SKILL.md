---
name: leeloo-dallas-multiplan
description: Create multi-model implementation plans for a user-supplied planning target. Use when the user asks Codex to generate, compare, synthesize, or write a final master plan using Codex plus external LLM CLIs such as Claude and Grok, especially when the desired output is plan files under plans/[title]-[name-id].md.
---

# Leeloo Dallas Multiplan

## Dependency preflight

Before generating plans, identify the requested reviewer set and verify each
reviewer's installed CLI or configured API adapter, supported model/flags,
existing authentication, and needed connectivity. Grok requires an external
compatible client/adapter; none is bundled or assumed to exist. Local models
need their runtime and weights. If a required reviewer cannot run, stop the
requested multi-model workflow and report it. Continue with fewer reviewers
only with the user's explicit agreement; fewer than two independent models
must not be described as multi-model review. Do not install clients or silently
replace models, providers, or independent passes.

## Overview

Create several independent implementation plans for one user-supplied target,
then synthesize the strongest ideas into one final master plan. Treat the input
parameter as the exact thing the user wants a plan for.

## Required Input

Accept one input parameter:

- `plan_target`: the feature, fix, refactor, investigation, or other work the
  user wants to create an implementation plan for.

If the target is ambiguous, inspect the repository first. Ask the user only for
product or tradeoff decisions that cannot be discovered locally.

## Required Access

Use the host's existing permissions to read the target repository and write
only the requested plan files. External reviewers require separately available
CLI/API access, authentication, and permission to send the selected repository
context to that provider. This skill does not require disabling the sandbox
or changing global access settings.

Discover installed reviewers and current CLI help. Select available models
from the user's configuration or explicit request; do not assume particular
model IDs, private provider variants, or reasoning-effort flags. Ask only when
the choice materially affects the requested result.

## Plan Title

Create `[PTC]` locally; do not depend on another skill.

Use the same behavior as `plan-title-create`:

- Produce a concise slug-style title for the plan target.
- Use lowercase ASCII letters and digits.
- Replace spaces and punctuation with single hyphens.
- Remove leading/trailing hyphens.
- Prefer 3-8 meaningful words.
- Avoid filler words when they do not clarify the work.
- Keep the result stable and specific enough to group related plan files.
- Example: `Make log relay fulfillment atomic` becomes
  `make-log-relay-fulfillment-atomic`.

Write every generated plan file under:

```text
plans/[PTC]-[name-id].md
```

Use these exact `name-id` values:

- `gpt`
- `claude`
- `grok`
- `final`

## Workflow

Run phases 1 and 2 concurrently when possible. Run phase 3 only after every
available phase 1/2 plan has been written.

### Phase 1: Ask Codex for the GPT Plan

When a configured Codex CLI reviewer is available, use its selected GPT model.
The following is an illustrative command shape, subject to installed CLI
help, with `[PROMPTHERE]` replaced by a prompt containing
the exact `plan_target`, resolved `[PTC]`, target output path, and instructions
to inspect the relevant repository code and docs read-only before planning:

```bash
codex exec --model "$GPT_MODEL" --sandbox read-only -C . --output-last-message "plans/[PTC]-gpt.md" "[PROMPTHERE]"
```

The prompt must instruct Codex to return only the complete Markdown plan in its
final message, make no file writes, and produce a detailed, decision-complete
plan grounded in actual files, APIs, tests, and constraints. The outer Codex
command is responsible for capturing the final message in
`plans/[PTC]-gpt.md`. After Codex exits, verify that file exists and is
non-empty before counting the GPT pass as successful. If this reviewer is
unavailable, mark the pass unavailable rather than silently substituting a
different model or counting the host agent's own work as an independent pass.

### Phase 2: Ask External LLM CLIs for Plans

For each external model, run the CLI command below with `[PROMPTHERE]` replaced
by a prompt that includes:

- the exact `plan_target`
- the resolved `[PTC]`
- the target output path `plans/[PTC]-[name-id].md`
- instructions to inspect the repo before planning
- instructions to write a detailed, decision-complete implementation plan
- instructions to avoid implementation or unrelated repo mutations
- for non-Claude CLIs, instructions to write only that one plan file
- for Claude, instructions to print only the complete Markdown plan to stdout
  and perform no file writes

For Claude only, use a stdout-capture strategy instead of asking Claude to edit
the repository. The Claude prompt must instruct Claude to inspect the repository
read-only, print the complete Markdown plan to stdout, and not write, edit, or
mutate files. The outer Codex command is responsible for redirecting stdout to
`plans/[PTC]-claude.md`. This avoids Claude's interactive write approval while
keeping the multiplan run in control of file creation.

Commands:

Use the current user's configured model and only flags supported by the
installed reviewer. For example, after setting `CLAUDE_MODEL` to a verified
available identifier, a compatible Claude CLI may support:

```bash
claude --model "$CLAUDE_MODEL" --permission-mode dontAsk --allowedTools Read,Grep,Glob,LS -p "[PROMPTHERE]" > "plans/[PTC]-claude.md"
```

For a configured Grok reviewer, inspect its actual CLI help or authenticated
API adapter first. Use read-only repository access and capture its output to
the `grok` plan file. There is no bundled Grok client or guaranteed flag set.
Do not use blanket auto-approval flags to compensate for missing support.

Use the host's supported subprocess/session mechanism and its completion
notifications; do not depend on a particular tool name or poll when the host
forbids polling. Apply a bounded timeout appropriate to the user's request,
and distinguish a running reviewer from a failed one. After Claude exits, verify
`plans/[PTC]-claude.md` exists and is non-empty before counting the Claude pass
as successful. Use normal shorter retry judgment for the other external CLIs
unless the user explicitly grants a longer wait. If network, authentication,
process, or filesystem restrictions block a CLI, follow the active permissions
policy without disabling its safeguards. If a required reviewer remains
unavailable after a justified bounded retry, stop its dependent phase, preserve
any completed plans, and report the missing dependency. Resume synthesis with
a reduced reviewer set only when the user explicitly accepts that scope;
record omitted passes in the final plan's assumptions.

### Phase 3: Synthesize the Final Master Plan

After phases 1 and 2 complete, read all generated plan files for this `[PTC]`.
Analyze:

- intended changes and improvements
- implementation sequencing
- edge cases and failure modes
- testing and verification coverage
- API, schema, UI, CLI, docs, or migration impacts
- conflicts between plans
- ideas that are smart but risky, over-scoped, or unnecessary

If plans conflict on a product decision, data contract, destructive migration,
public API behavior, or other high-impact direction, interview the user before
choosing. For discoverable implementation facts, inspect the repository instead
of asking.

Then write one final, decision-complete master plan to:

```text
plans/[PTC]-final.md
```

The final plan should be implementable by another engineer or agent without
needing to make major decisions. Include:

- clear title and summary
- key implementation changes grouped by subsystem
- public API/interface/schema/docs impacts, if any
- test plan and acceptance criteria
- assumptions and explicitly chosen defaults
- unresolved questions only if user input is truly required

## Execution Rules

- Do not implement the `plan_target`; only create plan files.
- Do not overwrite unrelated plan files.
- If an output file already exists, inspect it first and decide whether the
  current request is an update to the same plan set or should use a more
  specific `[PTC]`.
- Use normal repository editing rules: preserve unrelated user changes and do
  not revert files you did not create.
- Prefer concise but detailed plans over exhaustive file inventories.
- Final response should list the created plan files and call out any skipped or
  failed external LLM pass.

## Dependencies and portability

The planning/synthesis instructions and slug rules are local; no other skill
is required. Independent multi-model passes need configured reviewer CLIs or
API adapters, their models, authentication, and possibly network access.
No reviewer implementation or model weights are bundled. Without them,
offer a clearly labeled single-agent plan only with the user's agreement.
A local reviewer adapter and JSON configuration could replace CLI-specific
invocation details; local models would still need a runtime and weights.
