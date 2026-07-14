---
name: git-commit-with-message-and-push
description: Draft and execute a git commit using a commit-formatted
  message derived from the current code changes, then push it to
  `origin/main`. Use when the user asks to commit the current worktree
  with a sensible message based on the diff rather than supplying the
  exact message themselves.
---

# Git Commit With Message And Push

Inspect the current changes, draft a commit-ready message, and then run
`git commit` with that message before pushing `origin main`.

## Workflow

1. Inspect the current change set before drafting.
   - Start with `git status --short`.
   - Use `git diff --stat` and `git diff --cached --stat`.
   - Read targeted diffs when the intent is unclear.
2. Infer the primary change theme.
   - Prefer one coherent commit message for the visible change set.
   - If the worktree contains obviously unrelated edits, say so briefly
     and summarize only the likely intended subset when possible.
3. Draft a git commit-formatted message for the current change set.
   - Use exactly this structure:
     ```text
     <type>: <summary>

     - item detail 1
     - item detail 2
     - item detail 3
     - additional item details as needed
     ```
   - Use a conventional type like `feat`, `fix`, `refactor`, `docs`,
     `test`, or `chore` when it is clear from the diff.
   - The first line must be the one-line summary.
   - Put exactly one blank line between the summary and the first bullet.
   - Use flat `- ` bullets for further details.
   - Include as many bullets as needed to adequately summarize the
     meaningful changes; do not default to exactly three bullets.
   - Do not insert blank lines between bullet points. The bullet list must
     be contiguous.
4. Keep every line at 72 characters or less.
5. Stage all current worktree changes from the repository root.
   - Include every modified, deleted, newly created, untracked, and
     unstaged file shown by `git status --short`.
   - Treat a request to commit the current worktree as permission to
     include all visible worktree changes by default.
   - The repo-root `.codex` safety rules below are mandatory exceptions
     and always override the include-all default.
   - If the user explicitly asks for partial staging, follow that instead.
   - Never create, stage, or commit a repo-root `.codex` file.
   - If an empty untracked repo-root `.codex` file is present, remove it
     before staging and continue.
   - If a repo-root `.codex` path exists and is not an obvious transient
     empty file, stop and ask the user before touching it.
   - Run `git add` as its own standalone command.
6. Run `git commit` using the drafted subject and body.
   - Do not use interactive git workflows.
   - Prefer a normal multi-line commit message.
   - Never amend an existing commit unless the user explicitly asks.
   - Run `git commit` as its own standalone command.
7. Run `git push origin main`.
   - Run `git push origin main` as its own standalone command.
   - When the execution environment supports host or elevated execution,
     use it for the first push attempt so SSH credentials are available.
   - If an SSH push fails with `Permission denied (publickey)`, follow the
     SSH agent recovery procedure below instead of repeatedly retrying.
8. Report the commit and push result briefly after both commands succeed.
9. If there are no meaningful changes, say so and do not create an empty
   commit.

## SSH Agent Recovery

When an SSH remote works in the user's terminal but not in the execution
environment:

1. Run `ssh-add -l` to check whether this process has an SSH agent.
2. If no agent is available, describe the problem as a missing SSH agent,
   not as a repository access-rights failure.
3. On macOS, use a non-interactive verbose SSH check to identify a local
   key the server accepts. Start a short-lived agent with a unique socket
   under `/private/tmp`, then load that key with
   `ssh-add --apple-use-keychain <accepted-key>`.
4. Set `SSH_AUTH_SOCK` only for the standalone `git push origin main`
   command. Keep the push elevated when host execution is available.
5. Terminate the short-lived agent after the push, including when the push
   fails.

Do not change the remote URL or the user's persistent SSH configuration as
part of recovery. If the key cannot be loaded non-interactively, stop and
ask the user to attach an agent or restore authentication.

## Output Rules

- The final commit message should still follow normal git commit style.
- Format the message as a subject, one blank line, then flat bullets:
  `<type>: <summary>`, blank line, then one or more contiguous `- detail`
  lines.
- Always keep exactly one blank line after the summary line and before the
  first bullet.
- Never include blank lines between individual bullet points.
- Use enough bullets to summarize the actual change set; three bullets is
  not a target or limit.
- If the worktree contains obviously unrelated edits, say so briefly and
  do not commit unless the user clearly wants the whole set committed.
- Stage all untracked and unstaged worktree changes from the repo root
  before committing unless the user explicitly asks for different staging
  behavior or a repo-root `.codex` safety rule requires exclusion.
- Exclude transient repo-root `.codex` artifacts from staging. The
  `.codex` safety rule always applies even when committing all untracked
  and unstaged files.
- If `git add .` produces no staged changes, explain that there is
  nothing to commit.
- After a successful commit, push to `origin main`.
- Do not use compound shell commands such as `git add && git commit`.
- Run `git add`, `git commit`, and `git push` as separate CLI commands.

## Execution Rules

- Keep the subject specific and action-oriented.
- Mention user-visible behavior or architectural intent, not file lists.
- Keep bullets short and high signal, with no blank lines between them.
- Before running `git commit`, inspect the final message and verify the
  body is one contiguous bullet list with no empty line between bullets.
- If there are no meaningful staged changes, do not invent a commit.
- Do not leave behind transient repo-root `.codex` files after staging or
  committing.
- Do not leave untracked or unstaged files out of the commit unless the
  user explicitly asked for partial staging or a repo-root `.codex`
  safety rule requires exclusion.
- After committing, push with `git push origin main`.
- After the commit and push succeed, report the created commit hash and
  subject briefly.
- Do not use compound CLI commands joined with `&&`, `;`, or pipes.
- Run `git add`, `git commit`, and `git push` individually so preapproved
  command prefixes can apply without prompting.
