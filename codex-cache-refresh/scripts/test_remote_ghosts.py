"""Regression tests for the Remote Control cache cleanup."""

from contextlib import closing, redirect_stdout
import io
from pathlib import Path
import sqlite3
import tempfile
import unittest
from uuid import uuid4

import remote_ghosts


class RemoteGhostTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.path = Path(temp.name) / "catalog.db"
        self.host = "remote-control:test"
        self.ghost, self.chat = str(uuid4()), str(uuid4())
        with closing(sqlite3.connect(self.path)) as conn:
            conn.executescript("""
                CREATE TABLE local_thread_catalog_hosts(host_id TEXT, host_kind TEXT);
                CREATE TABLE local_thread_catalog(
                  host_id TEXT, thread_id TEXT, cwd TEXT, display_title TEXT,
                  missing_candidate INTEGER, source_kind TEXT, thread_source TEXT,
                  source_detail TEXT, source_created_at INTEGER, source_updated_at INTEGER,
                  source_recency_at INTEGER, project_id TEXT, pending_observed_title INTEGER
                );
                CREATE TABLE local_thread_catalog_metadata(id INTEGER, catalog_revision INTEGER);
                CREATE TABLE local_thread_catalog_sync_state(host_id TEXT, watermark INTEGER);
                INSERT INTO local_thread_catalog_hosts VALUES ('remote-control:test', 'remote-control');
                INSERT INTO local_thread_catalog_hosts VALUES ('local', 'local');
                INSERT INTO local_thread_catalog_metadata VALUES (1, 8);
                INSERT INTO local_thread_catalog_sync_state VALUES ('remote-control:test', 123);
            """)
            conn.executemany("""
                INSERT INTO local_thread_catalog VALUES (?, ?, '/project', ?, 0, 'vscode',
                  'user', NULL, 1, 1, 1, NULL, 0)
            """, ((self.host, self.ghost, "/project"), (self.host, self.chat, "Real chat"),
                  ("local", self.ghost, "/project")))
            conn.commit()
        with closing(remote_ghosts.connect(self.path)) as conn:
            self.manifest = {"host_id": self.host, "candidates": remote_ghosts.candidates(conn, self.host)}

    def test_only_verified_host_and_id_removed(self):
        self.assertEqual(set(self.manifest["candidates"]), {self.ghost})
        with redirect_stdout(io.StringIO()):
            remote_ghosts.apply_cleanup(self.path, self.manifest)
        with closing(remote_ghosts.connect(self.path)) as conn:
            self.assertEqual(set(remote_ghosts.catalog_rows(conn)), {("local", self.ghost), (self.host, self.chat)})
            self.assertEqual(conn.execute("SELECT * FROM local_thread_catalog_sync_state").fetchall(), [(self.host, 123)])
            self.assertEqual(remote_ghosts.check_schema(conn), 9)
        backup, = self.path.parent.glob("catalog.remote-ghosts-*.db")
        with closing(remote_ghosts.connect(backup)) as conn:
            self.assertEqual(len(remote_ghosts.catalog_rows(conn)), 3)
            self.assertEqual(remote_ghosts.check_schema(conn), 8)

    def test_unexpected_sync_change_rolls_back(self):
        with closing(remote_ghosts.connect(self.path, "rw")) as conn:
            conn.execute("""
                CREATE TRIGGER modify_sync AFTER DELETE ON local_thread_catalog
                BEGIN UPDATE local_thread_catalog_sync_state SET watermark=999; END
            """)
        with redirect_stdout(io.StringIO()), self.assertRaisesRegex(RuntimeError, "exceeded"):
            remote_ghosts.apply_cleanup(self.path, self.manifest)
        with closing(remote_ghosts.connect(self.path)) as conn:
            self.assertEqual(len(remote_ghosts.catalog_rows(conn)), 3)
            self.assertEqual(remote_ghosts.check_schema(conn), 8)
            self.assertEqual(conn.execute("SELECT watermark FROM local_thread_catalog_sync_state").fetchone(), (123,))

    def test_metadata_change_stops_cleanup(self):
        with closing(remote_ghosts.connect(self.path, "rw")) as conn:
            conn.execute("UPDATE local_thread_catalog SET display_title='Named' WHERE host_id=? AND thread_id=?",
                         (self.host, self.ghost))
        with self.assertRaisesRegex(RuntimeError, "changed"):
            remote_ghosts.apply_cleanup(self.path, self.manifest)
        with closing(remote_ghosts.connect(self.path)) as conn:
            self.assertEqual(len(remote_ghosts.catalog_rows(conn)), 3)

    def test_ellipsis_title_must_be_a_truncated_working_directory(self):
        cwd = "/project/" + "long-folder-name-" * 5
        cases = (
            (cwd[:79] + "…", {self.ghost}),
            (cwd[:79], set()),
            ("/another/" + cwd[9:79] + "…", set()),
            (cwd + "…", set()),
            ("…", set()),
        )
        with closing(remote_ghosts.connect(self.path, "rw")) as conn:
            for title, expected in cases:
                with self.subTest(title=title):
                    conn.execute(
                        "UPDATE local_thread_catalog SET cwd=?, display_title=? WHERE host_id=? AND thread_id=?",
                        (cwd, title, self.host, self.ghost),
                    )
                    self.assertEqual(set(remote_ghosts.candidates(conn, self.host)), expected)

    def test_owner_verification_requires_absence_in_the_enrolled_environment(self):
        home = self.path.parent / "owner"
        home.mkdir()
        stores = {
            "state_5.sqlite": """
                CREATE TABLE threads(id TEXT);
                CREATE TABLE remote_control_enrollments(
                  environment_id TEXT, remote_control_enabled INTEGER, server_name TEXT
                );
                INSERT INTO remote_control_enrollments VALUES ('test', 1, 'example-owner');
            """,
            "thread_history_1.sqlite": """
                CREATE TABLE thread_turns(thread_id TEXT);
                CREATE TABLE thread_items(thread_id TEXT);
            """,
            "queue_1.sqlite": "CREATE TABLE queued_items(thread_id TEXT);",
        }
        for filename, schema in stores.items():
            with closing(sqlite3.connect(home / filename)) as conn:
                conn.executescript(schema)
        manifest = {**self.manifest, "client": "example-viewer"}
        self.assertEqual(remote_ghosts.verify_owner(home, manifest)["verified_owner"], "example-owner")
        with closing(remote_ghosts.connect(home / "queue_1.sqlite", "rw")) as conn:
            conn.execute("INSERT INTO queued_items VALUES (?)", (self.ghost,))
        with self.assertRaisesRegex(RuntimeError, "has backing data"):
            remote_ghosts.verify_owner(home, manifest)

    def test_local_host_rejected(self):
        with closing(remote_ghosts.connect(self.path)) as conn:
            with self.assertRaisesRegex(RuntimeError, "Remote Control host ID"):
                remote_ghosts.candidates(conn, "local")


if __name__ == "__main__":
    unittest.main()
