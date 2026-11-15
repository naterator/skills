---
name: codex-cleanup
description: Audit Codex local disk usage and reclaim space from inactive runtime versions and unused SQLite pages while preserving history, current and archived analysis, and usage statistics. Use for Codex storage cleanup requests; not general Mac cleanup or stale-sidebar repair.
---

# Codex Cleanup

## Dependency preflight

Require Python 3.9+ with `sqlite3`, bundled `scripts/storage_tools.py`, and
the verified accessible target Codex home. Runtime deletion additionally
requires trustworthy current process/open-file inspection (`ps`/`lsof` or
equivalent host APIs). Live database pause/resume requires macOS and an
independent, tested identity-bound resume watchdog, which is not bundled.
If any requirement is missing, stop that operation and report it. Never pause
writers without the watchdog or delete runtimes without activity checks.
Offer offline maintenance only after a safe offline state is established;
do not improvise a live-maintenance substitute.

Reclaim Codex storage without discarding analysis or statistics. Audit first; apply only the cleanup the user has authorized. A request to inspect space is not permission to delete files. Existing session authorization counts: do not ask again for already-approved operations.

## Preservation boundary

Keep current and archived analysis, including `sessions/`, `archived_sessions/`, `history.jsonl`, `session_index.jsonl`, history/state/memory databases, memory files, attachments, and generated assets. Preserve every live database record and usage counter during compaction. Never treat archived analysis as a cache.

Do not delete a history database because its contents also appear in JSONL. Do not gzip, rename, truncate, or edit live rollout files to save space. Do not unlink SQLite `-wal` or `-shm` files. Do not reset the whole Codex home or app-support folder.

Security scan deletion is a separate destructive operation: it removes findings and analysis. It is excluded from ordinary cleanup. Perform it only when the user specifically requests that scope, using [Security storage notes](references/security-storage.md). A history-preserving request never authorizes scan deletion.

## Audit and select work

Resolve the active Codex home from the environment and app configuration; default to `~/.codex`. The app may be named Codex or ChatGPT; do not assume its display name identifies its storage layout. Check actual bundle identity, paths, and installed versions each time.

Run the bundled read-only inventory:

```sh
python3 scripts/storage_tools.py audit --home /absolute/codex-home --out /absolute/work/audit.json
```

Measure allocated bytes as well as logical size. APFS sharing/snapshots and ongoing app writes may make physical free-space gains differ. SQLite inventory uses an immutable main-file snapshot and explicitly marks WAL limitations; never use that snapshot mode for preservation proof.

Require successful helper exits and `inventory_complete=true`. Unreadable files/subtrees make the inventory incomplete and its totals lower bounds; resolve access or scope first. A failed preservation snapshot must never be reused as proof that all analysis was covered.

Prioritize unused software and unused database pages. `packages/app-server-daemon/releases/` can contain several old runtimes. Installed plugin runtimes, plugin/marketplace Git checkouts under `.tmp`, and old app databases are not automatically disposable. Small caches are lower priority and require confirming what they contain.

Give the user a concrete cleanup scope, recoverable-space estimate, and what remains protected. When they already requested the recommended reclamation, proceed within that scope without reopening approval.

## Remove inactive runtimes

Determine the `current` symlink target, update marker, retained rollback version, and running executable/open-file paths. Keep the current release, the previous known release by default, any active release, installation locks, and update metadata. Never hardcode the versions from a past run.

Delete only explicit, freshly revalidated version directories directly inside the resolved releases directory. Refuse symlink candidates, paths outside that directory, an unexplained current/update mismatch, or a failed process/open-file check. Stop if a candidate becomes active. Installed plugins and other runtimes are outside this default scope.

Before mutation, capture analysis-file hashes with `snapshot-files`; afterward use `verify-files`. These checks allow ongoing analysis to append bytes and allow the app to move a rollout between current and archived locations, but require its existing content to survive.

```sh
python3 scripts/storage_tools.py snapshot-files --home /absolute/codex-home --out /absolute/work/protected.json
python3 scripts/storage_tools.py verify-files --home /absolute/codex-home --manifest /absolute/work/protected.json --out /absolute/work/verification.json
```

## Compact databases without deleting records

Read [the compaction procedure](references/database-compaction.md) before database mutation. The usual candidates are `thread_history_1.sqlite`, `state_5.sqlite`, and `logs_2.sqlite`, but discover the actual files and schema instead of assuming versioned names are permanent.

Use SQLite's `VACUUM` and checkpoint facilities, not filesystem replacement of an open database. Establish a stable maintenance window and verify all table contents and usage counters before/after with the bundled `fingerprint-db` helper. It opens a normal read-only SQLite connection that includes committed WAL content. Do not replace a failed read with immutable mode for verification.

Prefer an already-offline app. If writers must be paused briefly, follow the bounded pause/resume safeguards in the reference, explain the interruption, and avoid terminating chats or analyses. If a safe window cannot be established, finish the authorized runtime removal and report database compaction as remaining work; do not claim it completed.

## Verify and report

Require successful analysis-file verification, identical database table/schema fingerprints and usage counters, integrity checks, and resumed processes. Recheck retained runtimes and active selection. Distinguish finished operations from skipped/failed ones and report measured reclaimed bytes. Keep evidence under the task's `work/` directory; save user-facing reports only when useful. Do not add backups or move history merely to make the space total look smaller.

## Dependencies and portability

Inventory, preservation snapshots, and database fingerprints use the bundled
Python 3.9+ standard-library helper, including SQLite. Real cleanup requires
the target Codex installation, user data, and filesystem permissions.
Runtime deletion needs trustworthy process/open-file inspection (`ps`/`lsof`
or equivalent host APIs); live pause/resume is macOS-specific. Prefer offline
database maintenance if a bounded watchdog is not available: a watchdog
implementation is not bundled. No other skill is required, and personal
databases/backups must not be copied into this repository.
