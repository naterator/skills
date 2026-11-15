---
name: git-commit-with-message-and-push
description: Draft and execute a git commit using a commit-formatted
  message derived from the current code changes, then push it to
  `origin/main`. Use when the user asks to commit the current worktree
  with a sensible message based on the diff rather than supplying the
  exact message themselves.
---

# Git Commit With Message And Push

## Dependency preflight

Require Git, the intended target worktree, and usable commit identity/configuration.
Before committing, verify the requested push destination is configured and
reachable with existing authorized credentials; remote pushes need connectivity.
An SSH route additionally requires SSH/agent tools and an available approved
key; Keychain-based recovery requires macOS support. If a required dependency
or credential is unavailable, stop before the dependent commit/push phase and
report it. Do not create keys, change authentication/remote configuration,
install tools, or silently switch transports to bypass the failure.

Review the current changes, create one commit-formatted message, stage the
requested worktree, commit it, and push `origin main`.

## Fast Path

Use the fast path when Codex created or already reviewed the changes in the
current task and the worktree has not changed since validation:

- Trust the current task context. Do not reread source diffs or rerun tests.
- Run the required preflight checks, preferably together in one parallel
  read-only tool call.
- Continue with staging, one staged-patch check, commit, push, and final
  verification.

Read only targeted diffs when the worktree is unfamiliar, contains unexpected
files, has changed since review, or its intent is unclear. Do not read a broad
full diff by default.

## Workflow

1. Run one read-only preflight from the repository root:
   - `git status --short`
   - `git diff --stat`
   - `git diff --cached --stat`
   - inspect the repo-root `.codex` path
   Run independent checks in parallel when supported. If there are no
   meaningful changes, stop without creating an empty commit.
2. Confirm scope and intent:
   - Prefer one coherent commit for the visible change set.
   - A request for "all files" authorizes every eligible visible change.
   - If unrelated changes exist and the user did not authorize all files,
     report them and stop before committing.
3. Draft the message using exactly this structure:
   ```text
   <type>: <specific imperative summary>

   - high-signal behavior or architectural detail
   - additional detail as needed
   ```
   Use a conventional type such as `feat`, `fix`, `refactor`, `docs`, `test`,
   or `chore`. Keep every line at 72 characters or less, use one blank line
   after the subject, and keep the flat bullet list contiguous. Describe
   behavior and intent rather than listing files.
4. Stage the requested changes with standalone `git add`:
   - By default include every modified, deleted, untracked, and unstaged file.
   - Follow an explicit partial-staging request instead.
   - Never create, stage, or commit a repo-root `.codex` path.
   - Remove an empty untracked repo-root `.codex` file before staging.
   - If repo-root `.codex` is not an obvious empty transient file, stop and
     ask before touching it.
5. Verify the staged result once, preferably in one parallel read-only call:
   - `git status --short`
   - `git diff --cached --stat`
   - `git diff --cached --check`
   Confirm no eligible files were omitted. Do not repeat an unstaged
   `git diff --check`. If nothing is staged, stop.
6. Run standalone, non-interactive `git commit` with the drafted message.
   Never amend unless the user explicitly requests it.
7. Run standalone `git push origin main`. Use host or elevated execution on
   the first attempt when available. On `Permission denied (publickey)`, use
   the recovery procedure below instead of repeatedly retrying.
8. Verify in one read-only call that the worktree is clean and
   `git rev-parse HEAD` equals `git rev-parse origin/main`.
9. Report the commit hash and subject briefly.

Do not rerun tests or builds when they already passed for the unchanged
worktree. Do not run `git diff --name-status` when status already provides the
needed inventory. Do not reread the commit subject when commit output already
reported it. Keep `git add`, `git commit`, and `git push` as separate commands;
never join them with shell operators.

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

## Dependencies and portability

Message formatting and review rules are local; no other skill is required.
Actual commits need Git and a target repository. Push requires an authorized
remote, credentials, and connectivity unless the remote is a local Git path.
SSH-agent tools are required only for SSH recovery; Keychain integration is
macOS-specific. Keep credentials and private repositories external. A bundled
preflight wrapper and temporary local bare-remote tests could reduce repeated
shell orchestration, but cannot replace Git or a real remote service.
