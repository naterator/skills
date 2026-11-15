---
name: codex-cache-refresh
description: Refresh stale ChatGPT conversations in the Codex desktop Recents sidebar when opening them says the conversation no longer exists. Preserve local and remote Codex tasks.
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

Use this skill for deleted ChatGPT conversations that remain in the Codex desktop sidebar. The persistent catalog is a SQLite database, not an HTTP cache. Multiple current and obsolete databases can coexist; detect the one the running app has open rather than choosing by filename, modification time, or row count. This is a targeted catalog reset.

1. Check that the symptom matches: a ChatGPT conversation appears in Recents but opening it says it no longer exists. If the problem instead concerns a Codex task or another error, diagnose that case before changing the catalog.
2. Inspect the database schema and counts read-only with `python3 scripts/refresh_catalog.py` from this skill directory. By default, the script uses read-only `lsof` inspection to find catalog databases opened by Codex/ChatGPT desktop processes under `${CODEX_HOME:-~/.codex}/sqlite`, including WAL/SHM handles, then validates their catalog schema and host classification. It prints the selected path and stops if none or multiple qualify; it never falls back to a hardcoded filename. Keep the intended app running. If detection is unavailable or ambiguous, inspect the active app/database before passing `--db /verified/active/database.db` on both inspection and apply commands. The script requires ChatGPT hosts to be identified by `local_thread_catalog_hosts.host_kind='chatgpt'` and checks the catalog, sync-state, and revision tables. If the schema or classification differs, stop and investigate rather than guessing.
3. Run `python3 scripts/refresh_catalog.py --apply` against the same verified database. It makes a SQLite-consistent backup before writing, deletes catalog rows only for ChatGPT hosts, deletes only those hosts' sync-state rows, increments `catalog_revision` once, and checks that non-ChatGPT catalog rows remain intact. It then retains the two newest refresh backups and deletes older backups matching this skill's backup naming pattern, including the earlier `codex-dev.backup-YYYYMMDD-HHMMSS.db` pattern. Do not delete the host registry, other backups, or local and remote Codex task rows.
4. Report the backup path, backup-pruning count, and before/after catalog counts. Ask the user to restart Codex, then verify that a previously broken sidebar entry is gone and existing local and remote Codex tasks remain available. If the old entry returns, inspect the new catalog and sync behavior before repeating the mutation.

Running this skill at the user's request authorizes the targeted refresh. Do not run the mutation when the user asks only to explain, inspect, or create/update the skill.

## Dependencies and portability

The helper and regression tests are bundled and use Python 3.9+ standard
library modules, including SQLite; no pip packages or other skills are needed.
Actual refresh requires a compatible local Codex desktop catalog and filesystem
permission. Automatic discovery additionally uses `lsof`; an explicitly
verified `--db` path avoids that executable, not identity/schema checks.
The application and live user database must remain external; use synthetic
SQLite fixtures for offline development.
