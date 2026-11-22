---
name: codex-cache-refresh
description: Refresh stale ChatGPT conversations in Codex desktop Recents or remove verified orphaned Remote Control references. Preserve saved chats and other catalog entries.
---

# Codex Cache Refresh

## Dependency preflight

Require Python 3.9+ with `sqlite3`, the bundled `scripts/refresh_catalog.py`,
and an accessible compatible local Codex catalog. Automatic discovery also
requires `/usr/sbin/lsof` and the intended app's open database handles; only
an independently verified explicit `--db` path may replace that discovery.
Before any mutation, verify the selected schema, permissions, and backup
destination. If a required dependency or identity check fails, stop; do not
guess a database, fabricate a catalog, install tools, or broaden the reset.

## Stale ChatGPT conversations

Use this route for deleted ChatGPT conversations that remain in the Codex desktop sidebar. The persistent catalog is a SQLite database, not an HTTP cache. Multiple current and obsolete databases can coexist; detect the one the running app has open rather than choosing by filename, modification time, or row count. This is a targeted catalog reset.

1. Check that the symptom matches: a ChatGPT conversation appears in Recents but opening it says it no longer exists. If the problem instead concerns a Codex task or another error, diagnose that case before changing the catalog.
2. Inspect the database schema and counts read-only with `python3 scripts/refresh_catalog.py` from this skill directory. By default, the script uses read-only `lsof` inspection to find catalog databases opened by Codex/ChatGPT desktop processes under `${CODEX_HOME:-~/.codex}/sqlite`, including WAL/SHM handles, then validates their catalog schema and host classification. It prints the selected path and stops if none or multiple qualify; it never falls back to a hardcoded filename. Keep the intended app running. If detection is unavailable or ambiguous, inspect the active app/database before passing `--db /verified/active/database.db` on both inspection and apply commands. The script requires ChatGPT hosts to be identified by `local_thread_catalog_hosts.host_kind='chatgpt'` and checks the catalog, sync-state, and revision tables. If the schema or classification differs, stop and investigate rather than guessing.
3. Run `python3 scripts/refresh_catalog.py --apply` against the same verified database. It makes a SQLite-consistent backup before writing, deletes catalog rows only for ChatGPT hosts, deletes only those hosts' sync-state rows, increments `catalog_revision` once, and checks that non-ChatGPT catalog rows remain intact. It then retains the two newest refresh backups and deletes older backups matching this skill's backup naming pattern, including the earlier `codex-dev.backup-YYYYMMDD-HHMMSS.db` pattern. Do not delete the host registry, other backups, or local and remote Codex task rows.
4. Report the backup path, backup-pruning count, and before/after catalog counts. Ask the user to restart Codex, then verify that a previously broken sidebar entry is gone and existing local and remote Codex tasks remain available. If the old entry returns, inspect the new catalog and sync behavior before repeating the mutation.

Running this skill at the user's request authorizes the targeted refresh. Do not run the mutation when the user asks only to explain, inspect, or create/update the skill.

## Orphaned Remote Control Recents

Use this route when the viewer shows a stale Remote Control reference for an
enrolled source computer. A row whose title matches its working directory,
including a truncated prefix ending in an ellipsis, is only a candidate.
Identify the exact Remote Control host ID in the viewing catalog and confirm
which computer owns its enrollment. This route also needs user-authorized
read access to the Codex data directory and compatible backing stores on both
computers. Use the helper installed on each computer or a trusted command
session to it. The helper itself makes no network calls.

1. On the viewing computer, run `remote_ghosts.py capture HOST_ID` with Python
   and save its JSON output to a private scratch file. Use `--db` when the
   viewing catalog was independently verified instead of auto-detected.
   Compare the captured candidates with the symptom before proceeding.
2. On the source computer, run `remote_ghosts.py verify-owner CANDIDATES.json`
   with Python and save its output as the verified manifest. This checks the
   enrollment and requires the candidate IDs to be absent from known backing
   databases, the session index, and active and archived rollouts. Use the
   helper's `--data-root` option when either computer uses an explicitly
   verified non-default Codex data directory. Stop if schema, access, owner
   identity, or any backing record prevents verification.
3. Return the verified manifest privately to the original viewing computer.
   Run `remote_ghosts.py preview VERIFIED.json` with Python using the same
   catalog selection. This rechecks the viewer's backing records and the
   exact candidate fingerprints. Run `apply` with the same verified manifest
   only for a user-authorized cleanup. If relevant state changed after the
   owner check, recapture and reverify before applying.
4. The helper takes a SQLite-consistent backup under the writer lock and
   removes only the verified viewer catalog references. It verifies the other
   rows, host and sync tables, and revision before committing. Report the
   counts and local backup path. Verify that the stale references clear and
   real chats remain available.

Keep catalogs, manifests, IDs, and unredacted command output in private
storage. Use a trusted transfer for the owner-verification manifest.

## Dependencies and portability

The helpers and regression tests are bundled and use Python 3.9+ standard
library modules, including SQLite; no pip packages or other skills are needed.
Actual refresh requires a compatible local Codex desktop catalog and filesystem
permission. Automatic discovery additionally uses `lsof`; an explicitly
verified `--db` path avoids that executable, not identity/schema checks.
The application and live user database must remain external; use synthetic
SQLite fixtures for offline development.
