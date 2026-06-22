# Nate's Agent Skills

This repository contains reusable AI agent skills for Codex and similar coding
agents. Each skill lives in its own directory with a `SKILL.md` file that
defines when to use it and the workflow it should follow.

## Skills

- [`file-cabinet-rename`](file-cabinet-rename/SKILL.md): Renames existing files
  into a consistent `YYYY-MM-DD - FileSummary.ext` format while preserving file
  contents.
- [`find-new-work`](find-new-work/SKILL.md): Audits a repository for grounded
  follow-up work, including bug fixes, test gaps, stale tests, product
  enhancements, and documentation drift.
- [`git-commit-with-message-and-push`](git-commit-with-message-and-push/SKILL.md):
  Inspects the current worktree, drafts a commit message, commits all intended
  changes, and pushes to `origin/main`.
- [`gitea-issue`](gitea-issue/SKILL.md): Uses the `tea` CLI to list, inspect,
  prioritize, edit, and close Gitea issues from a project directory.
- [`leeloo-dallas-multiplan`](leeloo-dallas-multiplan/SKILL.md): Generates
  multi-model implementation plans and synthesizes them into a final master
  plan.
- [`plan-title-create`](plan-title-create/SKILL.md): Produces concise,
  lowercase, hyphenated titles for implementation plans and related planning
  documents.

## License

This repository is licensed under the [BSD 3-Clause License](LICENSE).
