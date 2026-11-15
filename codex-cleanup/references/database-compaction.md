# Database compaction

SQLite `VACUUM` repacks live records and indexes into fewer pages. It is a write transaction and can need about twice the database size in temporary free space. See [SQLite VACUUM](https://www.sqlite.org/lang_vacuum.html). Hidden rowids may change on tables without an INTEGER PRIMARY KEY: inspect whether the app uses hidden rowids and preserve them or skip compaction if that contract cannot be established. The helper compares named columns, schema, and table counts, not implicit rowids.

## Establish a stable window

1. Inventory the exact databases, free space, open-file holders, journal mode, and schema. Capture protected-file hashes before maintenance. Do not inspect credentials or print private message contents.
2. Prefer databases with no other open-file holders. If the app is already shut down, check for persistent app-server processes that can still write. Do not shut down the application hosting the current task without a workable completion/resume path.
3. For a brief live maintenance window, create an independent resume watchdog before pausing anything. Identify each holder's executable, PID identity/start time, and current state. Refuse unexpected holders or processes already paused by someone else. Do not use broad process-name killing.
4. Reserve writer slots with `BEGIN IMMEDIATE` on all selected databases before pausing holders; this prevents freezing them mid-write. Stop on a lock timeout and release any earlier reservations. `SIGSTOP` temporarily pauses a process; `SIGCONT` resumes it. Only use this on verified Codex holders on macOS, never unrelated apps, and never terminate the current analysis.
5. Pause only the verified holders, recheck for new holders, and keep the window bounded. A detached watchdog must resume the same process identities if the maintenance process fails or exceeds its deadline. Check elapsed time between phases; stop on deadline/holder drift. Register exception/signal cleanup that resumes holders. Derive timing from the current database sizes and checks, not a past run. Prefer offline maintenance when size or timing makes pausing unsafe.

## Compact and prove preservation

Within the stable window, for each selected database:

- Capture a full logical fingerprint, counts, usage counters, integrity, and foreign-key state. Use `scripts/storage_tools.py fingerprint-db --database PATH --out BEFORE.json`. Normal `mode=ro` includes WAL; lack of permission to open shared-memory state is a permission problem, not permission to omit the WAL.
- Commit the maintenance reservation, checkpoint through SQLite with `PRAGMA wal_checkpoint(TRUNCATE)`, and require a non-busy result. Keep the verified writers paused. Never delete journal files manually.
- Measure the checkpointed file size; run `VACUUM` with an existing trusted SQLite runtime, outside an open transaction. Do not alter schema, rows, journal mode, or retention policy. Checkpoint through SQLite again and require success.
- Capture the after fingerprint in the same stable window. Compare schema and every table's row count and SHA-256, including migrations and sequence tables. Require exact usage-counter equality, `quick_check=ok`, and unchanged foreign-key violations (normally zero). If existing integrity errors are present, stop before mutation rather than attempting repair as cleanup.
- Record measured savings and checks. Close maintenance connections, and resume all processes in a `finally` path. The watchdog remains until resumption is confirmed. Do not claim preservation if a watchdog resumed writers before comparison completed; that invalidates the comparison window even if VACUUM itself succeeded.

After resumption, verify each protected file's original byte prefix and confirm processes run normally and current runtime selection still exists. Live analysis may append new content; it must not lose old content. Fresh integrity checks can be made on normal read-only connections; label any immutable main-file check as WAL-limited.

## Failure handling

Lock/contention failure: release connections, resume holders, preserve files, and report which databases remain uncompacted. A failed VACUUM relies on SQLite journaling; do not swap in a stale snapshot or remove WAL files to force progress. A fingerprint mismatch requires investigation, not deleting discrepant rows to make counts match. Preserve evidence without dumping private conversation text.
