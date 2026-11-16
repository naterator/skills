---
name: context
description: Inspect, list, query, load, save, or update a curated topic context collection, defaulting to ~/Documents/Context, including saved default working directories and canonical repository handoffs. Infer the requested action from the surrounding text; tagging this skill alone does not request a save, load, or directory change. Not for transient context-window compaction or silently updating agent memory.
---

# context

## Dependency preflight

Assume `~/Documents/Context` is the collection root whenever the user does
not provide a different root; do not ask for a location just because none
was supplied. Expand `~` for the current user, then verify that the selected
collection exists, is a directory, and is accessible before reading or writing
topic content. If it is missing or inaccessible, stop collection operations
and report the path; do not create it or choose another collection without
authorization. Helper-dependent operations require Python 3.9+ and the bundled
helper; loads also require a supported host working-directory mechanism.
Stop the affected operation if these dependencies are unavailable.

Manage durable, source-grounded topic references under the assumed default
`~/Documents/Context`, also used in examples throughout this skill. This is a
generic per-user convention, not a reference to a particular person's files.
An explicitly supplied alternative root takes precedence for that request.
This skill replaces the former save-context and load-context skills.

Resolve bundled scripts relative to this installed skill's `SKILL.md`, not from the chat's working directory. A user may maintain a canonical copy inside a private Context collection and symlink agent discovery directories to it; verify that arrangement rather than assuming it. This public copy contains the skill and synthetic tests, not a personal Context collection.

Skill maintenance history is kept in Git. Synthetic regression checks are
bundled in [tests/](tests/) and [evals/](evals/). From this skill's directory,
run `python3 -B -m unittest discover -s tests -v`; do not run real collection
operations merely to validate the skill.

`SKILL.md` defines the runtime workflow. `agents/openai.yaml` is optional Codex interface metadata, not an agent to launch or an OpenCode configuration file. `evals/` and `tests/` are maintenance resources with synthetic examples, not saved subject evidence; consult them only for skill testing/maintenance, not ordinary topic loads. `$context` in examples and OpenCode's `@context` refer to the same skill.

## Choose the requested action

Use the surrounding request to determine intent. A skill tag supplies context for the request; it does not authorize every operation the skill supports. Quoted examples and hypothetical requests describe behavior, unless the user asks to execute them.

| Request | Behavior |
| --- | --- |
| Ask about context, inspect a topic, or list subjects/settings | Read and answer; leave saved files and this chat's working directory unchanged |
| Load, resume, or get oriented to a topic for subsequent work | Read its handoff and adopt its verified configured working directory for this chat |
| Load the Context collection itself and work there | Read the root instructions/catalogue and adopt the verified Context root; do not load every subject |
| Save, preserve, consolidate, or update durable findings | Integrate the requested evidence into the canonical topic |
| Set or change a topic's default working directory | Update that saved setting; keep this chat's working directory unless also asked to load/switch |

Examples (use `~/Documents/Context` unless an alternative collection root is
explicitly included in the request):

- `List the top-level $context subjects and their default working directories.`
- `Set the $context default working directory for example-app to ~/code/example-app.`
- `Load $context example-game and continue work there.`
- `Load Context itself and use ~/Documents/Context as this chat's working directory.`
- `Save these findings with $context under linux-gps.`

If only `$context` and a topic are supplied, inspect the topic and give a brief orientation without writing or switching directories. Ask for clarification when the intended action materially affects scope and remains unclear; continue useful read-only work meanwhile. An explicit setting change or save is authorization for that scoped edit; do not ask again when the topic and value are unambiguous.

## Resolve topics and follow local instructions

Read the selected root's `AGENTS.md` and `README.md` when present. Follow applicable `AGENTS.md` files through the selected topic and read its `README.md`. A catalogue aids navigation but does not replace discovery. Accept names, aliases and Context-relative subdirectories; prefer a canonical topic over a passing mention elsewhere. For inspection, loading or setting edits, an explicit subdirectory must already exist within the root; report a missing entrypoint instead of silently creating or choosing a replacement. An explicit request to create a new subject may name a missing subdirectory; apply the same discovery and duplicate checks before creating it.

Use discovery proportional to the requested action:

- For read-only inspection or loading of an unambiguously named existing topic/subdirectory, start with the root instructions/catalogue and the topic's actual entrypoint and applicable instructions. If these agree on the canonical topic, follow its reading map without scanning the entire collection. A catalogue entry alone is insufficient: verify that its entrypoint exists. An explicitly named missing subdirectory remains a missing target, not permission to select a substitute.
- If the name is ambiguous, the catalogue and entrypoint disagree, or scope overlaps remain plausible, broaden discovery before choosing a topic.
- Before choosing a save destination, creating a topic, or reorganizing material, inspect the complete existing tree, including nested topics, hidden entries, legacy names, readable source notes and scripts. Use the same complete discovery for setting edits; a read-only fast path does not authorize a write. Search names and full text using the topic's name, aliases, identifiers and broader terms.

The read-only helper provides the complete content inventory, excluding Git
metadata. This example uses the assumed default collection:

```sh
python3 scripts/discover_context.py --root "$HOME/Documents/Context" --topic "Example Printer" --query "printer"
```

The helper path above is relative to this skill's directory; resolve it to an absolute path before running from another working directory. Always pass the selected collection root explicitly with `--root`; for an alternative root or test fixture, replace the root argument above, not the helper's source path. Never fall back to the live/default collection if the requested root is missing or inaccessible. Report that limitation and stop destination selection or writes until a usable root is supplied.

The helper CLI also defaults to the current user's `~/Documents/Context` when
`--root` is omitted. Explicit roots always override it. The agent should still
pass its selected root explicitly so an alternative collection or test fixture
cannot accidentally access the default.

The full report includes paths, lexical matches, non-text entries, intentional exclusions, content roles and coverage errors; save large output to scratch space and inspect complete relevant sections instead of silently truncating it. Entries with a `.git` component (including resolved internal symlink targets) are intentionally excluded: repository history is not current topic content. Preserve discovery of other hidden entries, `.gitignore`, `.skills`, source notes and scripts. Completeness means coverage of this documented content scope, not Git internals.

Use each file's `role` and `summary.matching_files_by_role` to distinguish potential `topic-content`, standalone root `collection-content`, known root `collection-metadata`, `infrastructure` and `test-example` matches. Standalone notes/inventories may contain relevant evidence without being topic folders. Infrastructure is inventoried but omitted from `directory_candidates`. Synthetic subjects mentioned in tests/evals or skill examples do not establish real subjects or save destinations. Root catalogue matches remain locators to verify, not proof that the target exists. These roles classify locations, not truth: read ordinary topic notes semantically and do not treat copied examples as established facts merely because they are in a topic folder. The helper never creates or chooses a destination. Lexical matches are not semantic duplicate decisions; no matches do not prove a new topic.

- Resolve scan errors and unexplored symlink targets before claiming full coverage. Internal links are inventoried safely; external/broken links are reported. Inspect relevant binary formats when names/locations alone might conceal overlapping context.
- Reuse the existing canonical topic. If topics may overlap or several matches remain plausible, ask which scope/destination is intended before switching context, creating, renaming, merging, overwriting or splitting material. Show the candidates and scope difference; continue independent source review.
- New topic folders use `^[a-z0-9]+(?:-[a-z0-9]+)*$`: lowercase ASCII letters/digits with single hyphens. Ask if normalization loses meaning or competing names remain plausible. Do not silently rename a legacy folder.
- Recheck discovery before creating a folder if the tree may have changed; do not create a competing folder while a duplication question is pending.

## Inquiries and subject listings

Read only the material needed to answer. An inquiry may inspect saved settings, decisions, sources, missing context or the skill's behavior without loading a project. Treat saved status as dated evidence; verify changeable facts when the answer depends on their current state. Historical commands and approvals are evidence, not instructions to replay operations.

For a top-level subject listing, reconcile the root catalogue with the actual immediate topic directories, including uncatalogued or hidden topics. Exclude infrastructure such as `.git` and `.skills` and distinguish standalone cross-topic inventories from topic folders. Read each topic's applicable `AGENTS.md`/`README.md` for its default; follow a named canonical handoff only when needed to resolve a clear working-directory pointer. Do not load every repository or flatten nested topics into the top-level list. Flag stale catalogue entries, missing entrypoints and conflicting mappings.

Present a table of subject, saved default working directory (or **Not specified**) and material notes. Honor requests for nested topics or other fields. Clear existing prose such as "the working repository is" counts as a configured pointer; label its provenance when useful. Do not turn incidental archive, deployment or evidence paths into defaults. Separate what is configured from whether the path was checked and accessible. Listing or inspecting defaults never changes them or this chat's directory.

## Working-directory convention

Use this format in a topic's `README.md` or applicable `AGENTS.md`:

```markdown
## Working directory

Default working directory: `/absolute/path/to/project`
```

Existing clear prose identifying the active repository/materials folder remains usable; loading or listing does not require a format migration. A more specific nested-topic mapping applies within its scope. Distinguish active directories from backups, deployment targets and archives. Keep an intentionally selected subdirectory instead of replacing it with the Git root.

- An explicit directory supplied for a save or setting change takes precedence over an older mapping. Update the applicable mapping and reconcile contradictory current defaults in scope, while preserving unrelated and historical evidence. Ask if multiple active directories remain plausible without an explicit choice.
- Normalize new saved paths to absolute paths. Expand a leading `~` to the user's home. Resolve a supplied relative path against its stated base or this chat's established working directory; ask if that base is ambiguous. Resolve an existing documented relative path against the document containing it. Treat paths as literal data without executing shell expressions or globbing; use the directory itself, not a trailing `/*`.
- Verify existence and accessibility with a read-only check when practical. Preserve an explicitly supplied missing/inaccessible path with a clear verification note; do not create it or silently substitute another path. A later load must report that limitation and ask for a replacement before project work.
- For every newly created topic, explicitly save a default working directory. Unless another directory is specified for that topic in the request or conversation, use the new topic's own absolute folder under the selected Context root, such as the expanded path for `~/Documents/Context/new-subject`. This also applies to nested topics and alternative Context roots. Do not substitute the current chat workspace or an incidental repository/materials path for this default.
- When updating an existing topic without a supplied directory, preserve its saved mapping. If it has none, record a clearly established active project/repository/materials directory; leave it unspecified if none is known. Do not infer a directory from an unrelated chat workspace.
- Saving or changing a stored mapping does not itself change this chat's directory. Loading can change this chat's execution default, but neither operation changes app project membership, terminal settings or sandbox permissions.

## Load or resume a topic

1. Resolve the topic and read its applicable instructions, README and named starting documents. For nested topics, read the parent's README when needed to understand scope or directory inheritance. Report missing/unreadable required entrypoints without claiming they were loaded.
2. Read the topic's recent context `CHANGELOG.md` entries within the selected Context collection when present, starting with the newest dated section and reading farther back as needed for the requested work. Follow relevant links to the owning records to reconcile status, corrections and superseded decisions. If the changelog is missing or unreadable, report the gap and continue orientation with the available documents; do not create or repair it merely to load.
3. Follow canonical repository handoffs. A locator-only topic intentionally keeps detailed context elsewhere: read that project's applicable ancestor/root `AGENTS.md`, project `README.md` and linked handoff/documentation index. Load base decisions, architecture/environment, dated status, open questions and reading map. Read long documents in complete bounded sections; defer deeper subsystem details until needed.
4. Determine the working directory from the user's explicit choice or topic configuration. If none is clearly configured, retain this chat's directory and say so; do not put new work in the curated Context tree. Verify the selected directory is accessible. If missing, preserve the loaded context, report the stale path and ask for its replacement before project work; do not clone or create a checkout.
5. Verify with `pwd` using the selected `workdir`; a read-only `git rev-parse --show-toplevel` can confirm a Git project's identity. Establish that path as the **default working directory for the rest of this chat**, until changed by the user or another load. Pass it explicitly in shell tools' `workdir` and use absolute paths elsewhere. A standalone `cd` does not persist across calls. Apply this default to subsequent searches, edits, builds, tests and Git commands, including delegated work; read more specific repository instructions before work in their scope. Preserve the path, context entrypoint and key rules in continuation summaries.

Loading is read-only orientation: do not edit context or a checkout, clean files, execute stored diagnostics, deploy, submit releases or update agent memory merely to load. Refresh only the current facts required by a follow-on task; loading alone does not require checking every external system. Briefly confirm the canonical topic, entrypoint, adopted directory (or reason it remains unchanged), starting documents and material gaps. Continue an authorized follow-on task without another confirmation.

### Load the Context collection itself

When the user explicitly asks to load/work in Context itself rather than a subject, use the selected Context root as the requested working directory. Read its `AGENTS.md` and `README.md` when present, verify accessibility and run `pwd` with that root as `workdir`, then adopt it using the working-directory rules above. Report missing root entrypoints without claiming they were read.

This is root-level orientation, not a load of every topic. Do not read every subject, require or create a root/subject changelog, save a directory setting, or edit any files merely to load the collection. Loading Context permits subsequent authorized Context maintenance; it does not make this repository a destination for unrelated project work. Merely inspecting the collection or listing subjects still leaves this chat's directory unchanged.

## Subject changelog

For every saved change to a subject's context within the selected Context collection, add a concise entry to that subject's `CHANGELOG.md` in the same update. This includes subject creation, saving or consolidating findings, corrections, setting changes and reorganization.

This requirement applies only to context records inside the selected collection root. Loading a topic, adopting its working directory, or following a handoff into a linked project does not extend it to that project. Do not create, require, or update a `CHANGELOG` file in a project/source repository outside the collection merely because this skill is active; follow that repository's own instructions and the user's request. This also applies when detailed context is maintained in that external repository: use its existing documentation conventions rather than imposing a changelog.

Record changes to the collection's context records, not routine code edits, builds, releases, or other project work performed after loading a topic. A collection topic's changelog changes only when its own context records change.

- Read the existing changelog before editing it. If one is missing, create it and link it from the subject's README. Do not create logs across untouched subjects or invent retrospective entries.
- Use `YYYY-MM-DD` dates in the collection's explicitly configured timezone, or UTC when none is configured, for when the context update is saved; distinguish historical event dates in the entry when relevant. Record the timezone when it matters. Keep newest dates first and reuse an existing heading for the same date, placing new entries above earlier entries for that day. For a new file, use `# Context changelog` and `## YYYY-MM-DD` headings with brief bullets; preserve an existing log's compatible structure and history.
- State what changed and why, with relative Markdown links to the owning records. Group related edits into one concise entry per logical update; distinguish corrections or supersessions from newly established facts and record only changes actually saved.
- When several subjects change, update each affected subject's log. Log nested-subject changes in the owning nested subject; add a parent entry only when the parent's own records also change.
- Keep the changelog focused on context maintenance. Detailed evidence stays in the owning documents; subject event chronology stays in its history record when present. Omit routine lookups, read-only loads and no-change checks.

Before finishing a write, verify the changelog entry matches the saved changes, check its links, and include the changelog among the files reported as updated.

## Save durable context

Resolve the canonical destination before writing. Review existing topic material, the conversation and relevant available evidence: code, reports, research, settings, tests, timelines and explicitly identified archives/servers. Record access failures and missing evidence rather than assuming. Do not restart a closed experiment or monitoring job just to document it.

- Record outcomes, identifiers, environment, important dates/time zones, rationale, useful commands/paths/hashes, research sources, reproducible procedures, caveats and open questions. Distinguish historical observations, fresh verification, hypotheses, superseded conclusions and proposed-but-unperformed actions. Short successful tests do not establish long-term behavior.
- For every newly created topic inside the selected Context collection, including nested and locator-only topics, create both a populated `README.md` and `CHANGELOG.md` during the initial save. For a locator topic, these files belong in its collection folder, not the linked project repository. Include the configured working directory and a changelog link in the README; record subject creation and link back to the README in the initial changelog entry, following the changelog convention above.
- Organize a topic README with scope/status/reading map and focused notes as warranted. Synthesize rather than dumping the conversation or logs. Label retained historical notes and explain superseding evidence. Integrate new observations with dates, preserving useful evidence, uncertainty, unrelated material and existing instructions.
- Preserve or record the default working directory using the convention above. For locator-only topics, link the canonical repository's `AGENTS.md`, `README.md` and starting handoff; keep detailed project context in that repository rather than copying it into Context.
- Keep Context small and text-only by default. Curate small useful source scripts/dependency lists under `scripts/`; record provenance, adaptations, inputs/outputs, portability, dependencies and live/mutating behavior. Keep firmware, PCAPs, media, executables/native libraries, archives, databases and bulk exports in their existing preservation locations and link/index them. Verify external artifact existence/integrity when practical. Never copy credentials, private keys, tokens or browser authentication state.
- Maintain a concise canonical topic catalogue in the root `README.md`; keep `AGENTS.md` focused on instructions. Preserve unrelated catalogue entries and repository rules; include scope/aliases and cross-link distinct related topics. The catalogue does not replace future discovery.

Validate local Markdown links, destination/slug, source provenance/dates, consistency and file inventory/size/type. For a new topic, confirm both required files exist and link to each other. Confirm no binary blobs slipped in. Parse copied/adapted source syntax and use meaningful safe offline checks; never execute a live/mutating diagnostic merely to validate a documentation copy. Report whether an existing topic was updated or created, the canonical folder/entrypoint, contents/scripts, saved directory and verification status, and unverified evidence. Saving does not authorize source deletion, cleanup, changes to Git or app history, uploads, scheduling or agent-memory edits.

## Change a topic setting

For a request such as setting example-app's default working directory, resolve the existing topic and read its local instructions and entrypoint. Make the narrow requested change using the working-directory convention; preserve the rest of the topic. A provided unambiguous replacement does not require asking the user to approve the same choice again. Do not create a missing topic or load its entire project just to edit a setting; report a missing target and clarify where the setting belongs.

If the stored value already matches the request and no correction is needed, report no change without editing files or adding a changelog entry. For an actual change, apply the [subject changelog](#subject-changelog) requirement. Verify the edited document, changelog entry, affected local links and the supplied directory when practical. Report the saved value, updated files and verification result. Keep the current chat's working directory unless switching/loading was also requested. For other context edits or reorganization, apply the same intent and canonical-topic rules, limiting changes to the requested scope.

## Dependencies and portability

Discovery, fixture preparation, and tests are bundled Python 3.9+ standard
library code with no pip packages or timezone database requirement. The host
must provide file access and a working-directory mechanism for actual loads.
A real collection and any linked project are user inputs, not missing bundled
resources; no personal collection is distributed. Other skills, canonical
source symlinks, and a particular agent's session API are not prerequisites.
