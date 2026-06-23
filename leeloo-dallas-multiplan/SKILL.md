---
name: leeloo-dallas-multiplan
description: Create multi-model implementation plans for a user-supplied planning target. Use when the user asks Codex to generate, compare, synthesize, or write a final master plan using Codex plus external LLM CLIs such as claude, grok, composer, or gemini, especially when the desired output is plan files under plans/[title]-[name-id].md.
---

# Leeloo Dallas Multiplan

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
- `composer`
- `gemini`
- `final`

## Workflow

Run phases 1 and 2 concurrently when possible. Run phase 3 only after every
available phase 1/2 plan has been written.

### Phase 1: Create the GPT Plan

Create your own detailed implementation plan for `plan_target` as `gpt`.

Before writing, inspect the relevant repository code and docs enough to ground
the plan in actual files, APIs, tests, and constraints. Write the plan to:

```text
plans/[PTC]-gpt.md
```

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

```bash
claude --model opus --effort xhigh --permission-mode dontAsk --allowedTools Read,Grep,Glob,LS -p "[PROMPTHERE]" > "plans/[PTC]-claude.md"
grok --no-alt-screen --always-approve --effort xhigh --model grok-build -p "[PROMPTHERE]"
grok --no-alt-screen --always-approve --effort xhigh --model grok-composer-2.5-fast -p "[PROMPTHERE]"
agy --model "Gemini 3.1 Pro (High)" --print "[PROMPTHERE]"
```

Map commands to `name-id` values:

- `claude`: first command
- `grok`: second command
- `composer`: third command
- `gemini`: fourth command

Prefer `functions.exec_command` sessions so long-running CLIs can be polled to
completion. Claude may legitimately take a long time: when the `claude` pass
starts successfully, keep polling it for up to 30 minutes of wall-clock time
before treating it as hung or unavailable. After Claude exits, verify
`plans/[PTC]-claude.md` exists and is non-empty before counting the Claude pass
as successful. Use normal shorter retry judgment for the other external CLIs
unless the user explicitly grants a longer wait. If network, authentication,
process, or filesystem restrictions block a CLI, request escalation according to
the active permissions policy. If one external CLI remains unavailable after
reasonable retry, continue with the plans that were successfully produced and
state the missing plan in the final master plan assumptions.

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
