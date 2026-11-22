#!/usr/bin/env python3
"""Back up and reset only ChatGPT-derived Codex sidebar catalog state."""

import argparse
import os
import re
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


REQUIRED_COLUMNS = {
    "local_thread_catalog_hosts": {"host_id", "host_kind"},
    "local_thread_catalog": {"host_id", "thread_id", "source_kind"},
    "local_thread_catalog_sync_state": {"host_id"},
    "local_thread_catalog_metadata": {"id", "catalog_revision"},
}
BACKUP_SUFFIX = re.compile(r"^backup-(\d{8}-\d{6})(?:-[0-9a-f]{8})?\.db$")


def check_schema(conn):
    for table, required in REQUIRED_COLUMNS.items():
        columns = {row[1] for row in conn.execute(f"PRAGMA table_info({table})")}
        if not required <= columns:
            raise RuntimeError(f"Unexpected {table} schema; missing {sorted(required - columns)}")
    metadata = conn.execute(
        "SELECT id, catalog_revision FROM local_thread_catalog_metadata"
    ).fetchall()
    if len(metadata) != 1 or metadata[0][0] != 1:
        raise RuntimeError("Unexpected catalog metadata; no changes made")
    return metadata[0][1]


def detect_active_database():
    """Find a catalog opened by the desktop app, never by filename or mtime."""
    codex_dir = Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex").expanduser()
    db_dir = (codex_dir / "sqlite").resolve(strict=True)
    try:
        result = subprocess.run(
            ["/usr/sbin/lsof", "-nP", "+c", "0", "-F", "pcn", "+D", str(db_dir)],
            capture_output=True, text=True, timeout=15,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise RuntimeError(f"Cannot inspect app database handles: {exc}. Use --db only after verifying the active database.") from exc
    # lsof can return 1 with useful output when some requested files are not open.
    if result.returncode not in (0, 1):
        raise RuntimeError(f"Database detection failed: {result.stderr.strip()}. Use --db after verifying the active database.")
    opened = set()
    app_process = False
    for line in result.stdout.splitlines():
        if line.startswith("p"):
            app_process = False
        elif line.startswith("c"):
            command = line[1:]
            app_process = command in ("Codex", "ChatGPT") or command.startswith(("Codex Helper", "ChatGPT Helper"))
        elif line.startswith("n") and app_process:
            name = line[1:]
            for suffix in ("-wal", "-shm"):
                if name.endswith(suffix):
                    name = name[:-len(suffix)]
                    break
            path = Path(name)
            if path.suffix in (".db", ".sqlite", ".sqlite3") and path.is_file():
                path = path.resolve()
                if path.parent == db_dir:
                    opened.add(path)
    candidates = []
    for path in sorted(opened):
        conn = sqlite3.connect(f"{path.as_uri()}?mode=ro", uri=True)
        try:
            tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            if not tables.intersection(REQUIRED_COLUMNS):
                continue
            check_schema(conn)
            classified_hosts(conn)
        except (sqlite3.Error, RuntimeError) as exc:
            raise RuntimeError(f"Open catalog {path} failed validation: {exc}; no database selected") from exc
        finally:
            conn.close()
        candidates.append(path)
    if len(candidates) != 1:
        found = ", ".join(str(path) for path in candidates) or "none"
        raise RuntimeError(
            f"Expected one catalog open in Codex/ChatGPT; found {found}. "
            "Keep the intended app running or use --db after verifying its active database."
        )
    return candidates[0]


def classified_hosts(conn):
    hosts = [row[0] for row in conn.execute(
        "SELECT host_id FROM local_thread_catalog_hosts WHERE host_kind = 'chatgpt'"
    )]
    mismatched = conn.execute("""
        SELECT COUNT(*) FROM local_thread_catalog AS c
        LEFT JOIN local_thread_catalog_hosts AS h ON h.host_id = c.host_id
        WHERE c.source_kind = 'chatgpt' AND COALESCE(h.host_kind, '') <> 'chatgpt'
    """).fetchone()[0]
    if mismatched:
        raise RuntimeError(
            f"Found {mismatched} ChatGPT source rows outside ChatGPT hosts; no changes made"
        )
    return hosts


def counts(conn, hosts):
    if not hosts:
        return 0, 0
    marks = ",".join("?" for _ in hosts)
    catalog = conn.execute(
        f"SELECT COUNT(*) FROM local_thread_catalog WHERE host_id IN ({marks})", hosts
    ).fetchone()[0]
    sync = conn.execute(
        f"SELECT COUNT(*) FROM local_thread_catalog_sync_state WHERE host_id IN ({marks})", hosts
    ).fetchone()[0]
    return catalog, sync


def other_rows(conn, hosts):
    marks = ",".join("?" for _ in hosts)
    where = f"WHERE host_id NOT IN ({marks})" if hosts else ""
    return set(conn.execute(
        f"SELECT host_id, thread_id FROM local_thread_catalog {where}", hosts
    ))


def backup_database(conn, db_path, *, label="backup"):
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    path = db_path.with_name(f"{db_path.stem}.{label}-{stamp}-{uuid4().hex[:8]}.db")
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    os.close(fd)
    try:
        destination = sqlite3.connect(path)
        try:
            conn.backup(destination)
            result = destination.execute("PRAGMA integrity_check").fetchone()[0]
            if result != "ok":
                raise RuntimeError(f"Backup integrity check failed: {result}")
        finally:
            destination.close()
    except BaseException:
        path.unlink(missing_ok=True)
        raise
    return path


def prune_backups(db_path, keep=2):
    prefix = f"{db_path.stem}."
    backups = []
    for path in db_path.parent.iterdir():
        if not path.is_file() or path.is_symlink() or not path.name.startswith(prefix):
            continue
        match = BACKUP_SUFFIX.fullmatch(path.name[len(prefix):])
        if match:
            backups.append((match.group(1), path.name, path))
    backups.sort(reverse=True)
    for _, _, path in backups[keep:]:
        path.unlink()
    return len(backups[keep:])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--db", type=Path,
        help="Explicit verified catalog path (default: detect the running desktop app database with lsof)",
    )
    parser.add_argument("--apply", action="store_true", help="Back up and perform the targeted reset")
    args = parser.parse_args()
    db_path = args.db.expanduser().resolve(strict=True) if args.db else detect_active_database()
    selection = "explicit --db" if args.db else "auto-detected from running app handles"
    print(f"Database: {db_path} ({selection})")
    mode = "rw" if args.apply else "ro"
    conn = sqlite3.connect(f"{db_path.as_uri()}?mode={mode}", uri=True)
    conn.execute("PRAGMA busy_timeout = 10000")
    try:
        revision = check_schema(conn)
        hosts = classified_hosts(conn)
        before = counts(conn, hosts)
        print(
            f"ChatGPT hosts: {len(hosts)}; catalog rows: {before[0]}; "
            f"sync rows: {before[1]}; revision: {revision}"
        )
        if not args.apply:
            print("Read-only inspection. Pass --apply to refresh.")
            return
        if not any(before):
            print("Nothing to refresh; no catalog changes made.")
            print(f"Old refresh backups removed: {prune_backups(db_path)}")
            return
        backup = backup_database(conn, db_path)
        print(f"Backup: {backup}")

        # Hold the writer lock while selecting and deleting the target rows.
        conn.execute("BEGIN IMMEDIATE")
        try:
            check_schema(conn)
            if set(classified_hosts(conn)) != set(hosts):
                raise RuntimeError("ChatGPT host classification changed during backup")
            locked_before = counts(conn, hosts)
            preserved = other_rows(conn, hosts)
            marks = ",".join("?" for _ in hosts)
            deleted_catalog = conn.execute(
                f"DELETE FROM local_thread_catalog WHERE host_id IN ({marks})", hosts
            ).rowcount
            deleted_sync = conn.execute(
                f"DELETE FROM local_thread_catalog_sync_state WHERE host_id IN ({marks})", hosts
            ).rowcount
            if (deleted_catalog, deleted_sync) != locked_before:
                raise RuntimeError("Deleted row counts differed from the locked snapshot")
            updated = conn.execute("""
                UPDATE local_thread_catalog_metadata
                SET catalog_revision = catalog_revision + 1 WHERE id = 1
            """).rowcount
            if updated != 1 or other_rows(conn, hosts) != preserved:
                raise RuntimeError("Catalog metadata or non-ChatGPT rows changed unexpectedly")
            conn.commit()
        except BaseException:
            conn.rollback()
            raise
        print(
            f"After: ChatGPT catalog rows: {counts(conn, hosts)[0]}; "
            f"sync rows: {counts(conn, hosts)[1]}; revision: {check_schema(conn)}"
        )
        print(f"Old refresh backups removed: {prune_backups(db_path)}")
        print("Restart Codex, then verify broken ChatGPT entries are gone and Codex tasks remain available.")
    finally:
        conn.close()


if __name__ == "__main__":
    try:
        main()
    except (OSError, sqlite3.Error, RuntimeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
