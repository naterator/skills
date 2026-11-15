# Repository guidance

## Skill maintenance

- Do not create, restore, or append per-skill maintenance changelog files or
  changelog entries in this repository. Use Git commit history instead.
- Repair deleted changelog links without recreating maintenance logs. For
  other missing documentation, point to an existing resource or include
  useful instructions directly; do not add empty placeholders to silence checks.
- Do not move maintenance changelog entries into another dated journal as a
  workaround. Preserve actual validation evidence where useful, without
  turning routine edits into a maintenance log.
- This is a repository-maintenance policy, not a change to a skill's runtime
  contract. For example, the context skill may still require changelogs in
  an external user's topic collection. Synthetic runtime fixtures/templates
  may model those outputs.

## Verification

- Keep each skill self-contained, portable and sanitized as described in
  `README.md`. Preserve unrelated owner changes and existing license terms.
- Run `python3 -B .scripts/check_repository.py` after documentation changes.
  Run the checker tests when modifying that checker, and relevant isolated
  skill tests when changing behavior.
- Do not run live skill operations to validate documentation or installation.
- Do not commit, rewrite history, or push unless the user requests it.
