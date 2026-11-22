#!/usr/bin/env python3
"""Preview or remove confirmed orphaned Remote Control catalog references."""

import argparse
from collections import Counter
from contextlib import closing
from hashlib import sha256
import json
import os
import re
from pathlib import Path
import socket
import sqlite3
import sys
from uuid import UUID

from refresh_catalog import backup_database, check_schema, detect_active_database


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def connect(path, mode="ro"):
    return sqlite3.connect(f"{path.resolve(strict=True).as_uri()}?mode={mode}",
                           uri=True, timeout=5, isolation_level=None)


def selected_host(conn, host_id):
    record = conn.execute(
        "SELECT host_kind FROM local_thread_catalog_hosts WHERE host_id=?", (host_id,)
    ).fetchone()
    require(record == ("remote-control",) and host_id.startswith("remote-control:"),
            "Select an exact Remote Control host ID")


def candidates(conn, host_id):
    """Known placeholder shape. This alone is never proof of an orphan."""
    selected_host(conn, host_id)
    rows = conn.execute("""
        SELECT * FROM local_thread_catalog
        WHERE host_id=? AND missing_candidate=0
          AND source_kind='vscode' AND thread_source='user' AND source_detail IS NULL
          AND source_created_at=source_updated_at AND source_created_at=source_recency_at
          AND project_id IS NULL AND pending_observed_title=0
          AND (
            display_title=cwd OR (
              length(display_title)>1 AND length(cwd)>=length(display_title)
              AND substr(display_title, -1)='…'
              AND substr(display_title, 1, length(display_title)-1)
                  =substr(cwd, 1, length(display_title)-1)
            )
          )
    """, (host_id,))
    names = [field[0] for field in rows.description]
    pos = names.index("thread_id")
    return {row[pos]: sha256(json.dumps(row).encode()).hexdigest() for row in rows}


def file_signature(path):
    stat = path.stat()
    def sidecar_signature(suffix):
        try:
            value = path.with_name(path.name + suffix).stat()
        except FileNotFoundError:
            return None
        return value.st_ino, value.st_size, value.st_mtime_ns

    return (stat.st_ino, stat.st_size, stat.st_mtime_ns,
            sidecar_signature("-wal"), sidecar_signature("-shm"))


def no_backing_records(home, ids):
    target_ids = sorted(ids)
    chunks = [target_ids[pos:pos + 256] for pos in range(0, len(target_ids), 256)]
    stores = [
        ("state_5.sqlite", (("threads", "id"),)),
        ("thread_history_1.sqlite", (("thread_turns", "thread_id"), ("thread_items", "thread_id"))),
        ("queue_1.sqlite", (("queued_items", "thread_id"),)),
    ]
    if (home / "sqlite/state_5.sqlite").is_file():
        stores.append(("sqlite/state_5.sqlite", (("threads", "id"),)))
    for filename, tables in stores:
        path = home / filename
        signature = file_signature(path)
        # A checkpointed WAL DB without sidecars can be opened read-only using
        # an immutable snapshot, provided the file and sidecars stay unchanged.
        checkpointed = not any(signature[-2:])
        with closing(connect(path, "ro&immutable=1" if checkpointed else "ro")) as conn:
            for table, column in tables:
                for block in chunks:
                    marks = ",".join("?" for _ in block)
                    row = conn.execute(f"SELECT 1 FROM {table} WHERE {column} IN ({marks}) LIMIT 1", block).fetchone()
                    require(row is None, f"A candidate has backing data in {filename}/{table}")
        require(file_signature(path) == signature, f"{filename} changed during inspection")
    index = home / "session_index.jsonl"
    if index.exists():
        with index.open() as stream:
            require(ids.isdisjoint(json.loads(line).get("id") for line in stream if line.strip()),
                    "A candidate exists in the session index")
    def raise_walk_error(error):
        raise error

    for folder in (home / "sessions", home / "archived_sessions"):
        try:
            folder.stat()
        except FileNotFoundError:
            continue
        for directory, subfolders, files in os.walk(folder, onerror=raise_walk_error):
            require(all(not (Path(directory) / child).is_symlink() for child in subfolders),
                    "Unable to verify a symlinked session directory")
            for filename in files:
                if filename.startswith("rollout-"):
                    matched = re.search(r"([0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12})(?:\.|$)",
                                        filename, re.IGNORECASE)
                    require(matched is None or matched[1].lower() not in ids, "A candidate has a rollout")


def load_manifest(path):
    data = json.loads(path.read_text())
    require(isinstance(data, dict), "Manifest must be a JSON object")
    host_id, client = data.get("host_id"), data.get("client")
    require(isinstance(host_id, str) and host_id.startswith("remote-control:")
            and host_id != "remote-control:" and isinstance(client, str) and client,
            "Missing manifest provenance")
    records = data.get("candidates")
    require(isinstance(records, dict) and records, "The manifest contains no candidates")
    for thread_id, fingerprint in records.items():
        require(str(UUID(thread_id)) == thread_id and isinstance(fingerprint, str) and re.fullmatch(r"[0-9a-f]{64}", fingerprint),
                "Invalid candidate ID or fingerprint")
    return data


def verify_owner(home, manifest):
    require(manifest["client"] != socket.gethostname(), "Run owner verification on the source computer")
    prefix = "remote-control:"
    host_id = manifest["host_id"]
    require(host_id.startswith(prefix), "Invalid Remote Control host ID")
    with closing(connect(home / "state_5.sqlite")) as conn:
        found = conn.execute("""
            SELECT server_name FROM remote_control_enrollments
            WHERE environment_id=? AND remote_control_enabled=1
        """, (host_id[len(prefix):],)).fetchall()
    require(len(found) == 1, "The owner does not match the connected environment")
    no_backing_records(home, set(manifest["candidates"]))
    return {**manifest, "verified_owner": found[0][0]}


def validate_targets(conn, manifest):
    check_schema(conn)
    expected = manifest["candidates"]
    found = candidates(conn, manifest["host_id"])
    require(all(found.get(thread_id) == value for thread_id, value in expected.items()),
            "A verified candidate has disappeared or changed in the catalog")


def catalog_rows(conn):
    cursor = conn.execute("SELECT * FROM local_thread_catalog")
    names = [entry[0] for entry in cursor.description]
    host, thread = names.index("host_id"), names.index("thread_id")
    snapshot = {}
    for row in cursor:
        key = row[host], row[thread]
        require(key not in snapshot, "Catalog contains duplicate host/thread rows")
        snapshot[key] = row
    return snapshot


def preserved_tables(conn):
    return {
        table: Counter(conn.execute(f"SELECT * FROM {table}"))
        for table in ("local_thread_catalog_hosts", "local_thread_catalog_sync_state")
    }


def apply_cleanup(db_path, manifest):
    eligible = {(manifest["host_id"], id) for id in manifest["candidates"]}
    with closing(connect(db_path, "rw")) as conn:
        conn.execute("BEGIN IMMEDIATE")
        try:
            validate_targets(conn, manifest)
            before = catalog_rows(conn)
            tables = preserved_tables(conn)
            revision = check_schema(conn)
            # A separate reader can back up the exact state held by the writer lock.
            with closing(connect(db_path)) as reader:
                backup = backup_database(reader, db_path, label="remote-ghosts")
            print(f"Backup: {backup}", flush=True)
            with closing(connect(backup)) as saved:
                require(catalog_rows(saved) == before and preserved_tables(saved) == tables
                        and check_schema(saved) == revision, "Backup differs from the locked catalog")
            rows = conn.executemany(
                "DELETE FROM local_thread_catalog WHERE host_id=? AND thread_id=?", sorted(eligible)
            ).rowcount
            require(rows == len(eligible), "Unexpected removal count")
            updated = conn.execute("""
                UPDATE local_thread_catalog_metadata SET catalog_revision=catalog_revision+1 WHERE id=1
            """).rowcount
            after = catalog_rows(conn)
            require(updated == 1 and check_schema(conn) == revision + 1 and preserved_tables(conn) == tables
                    and after == {key: row for key, row in before.items() if key not in eligible},
                    "Catalog changes exceeded the verified selection")
            require(conn.execute("PRAGMA quick_check").fetchone() == ("ok",),
                    "Catalog failed validation")
            conn.commit()
        except BaseException:
            conn.rollback()
            raise
    print(f"Removed {rows} stale references and preserved all {len(after)} other catalog rows.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("capture", "verify-owner", "preview", "apply"))
    parser.add_argument("input", help="Remote Control host ID for capture, otherwise a manifest path")
    parser.add_argument("--db", type=Path, help="Explicit verified viewing app catalog")
    parser.add_argument("--data-root", type=Path, help="Verified local Codex data directory")
    args = parser.parse_args()
    home = (args.data_root or Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex")).expanduser()
    if args.action == "verify-owner":
        print(json.dumps(verify_owner(home, load_manifest(Path(args.input)))))
        return
    db_path = args.db.expanduser().resolve(strict=True) if args.db else detect_active_database()
    if args.action == "capture":
        with closing(connect(db_path)) as conn:
            check_schema(conn)
            rows = candidates(conn, args.input)
        print(json.dumps({"client": socket.gethostname(), "host_id": args.input, "candidates": rows}))
        return
    manifest = load_manifest(Path(args.input))
    require(manifest["client"] == socket.gethostname() and isinstance(manifest.get("verified_owner"), str)
            and manifest["verified_owner"],
            "Use the owner-verified manifest on the original viewing Mac")
    no_backing_records(home, set(manifest["candidates"]))
    with closing(connect(db_path)) as conn:
        validate_targets(conn, manifest)
    if args.action == "preview":
        print(f"Catalog: {db_path}\nVerified stale references: {len(manifest['candidates'])}")
    else:
        apply_cleanup(db_path, manifest)


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, ValueError, sqlite3.Error) as error:
        sys.exit(f"Error: {error}")
