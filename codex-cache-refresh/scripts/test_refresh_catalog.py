"""Run with: python3 -m unittest discover -s scripts -p 'test_*.py'."""
import sqlite3
from contextlib import closing
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import refresh_catalog as refresh


class ActiveDatabaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.db_dir = self.root / 'sqlite'
        self.db_dir.mkdir()
        env = patch.dict(refresh.os.environ, {'CODEX_HOME': str(self.root)})
        env.start()
        self.addCleanup(env.stop)

    def catalog(self, name):
        path = self.db_dir / name
        with closing(sqlite3.connect(path)) as conn:
            conn.executescript('''
                CREATE TABLE local_thread_catalog_hosts (host_id TEXT, host_kind TEXT);
                CREATE TABLE local_thread_catalog (host_id TEXT, thread_id TEXT, source_kind TEXT);
                CREATE TABLE local_thread_catalog_sync_state (host_id TEXT);
                CREATE TABLE local_thread_catalog_metadata (id INTEGER, catalog_revision INTEGER);
                INSERT INTO local_thread_catalog_metadata VALUES (1, 1);
                INSERT INTO local_thread_catalog_hosts VALUES ('chatgpt', 'chatgpt');
            ''')
        return path.resolve()

    def detect(self, output, returncode=1):
        result = subprocess.CompletedProcess([], returncode, output, '')
        with patch.object(refresh.subprocess, 'run', return_value=result):
            return refresh.detect_active_database()

    def test_open_handles_choose_renamed_database_over_stale_default(self):
        self.catalog('codex.db')
        active = self.catalog('new-channel.sqlite')
        output = f'p100\ncChatGPT\nf10\nn{active}\nf11\nn{active}-wal\n'
        self.assertEqual(self.detect(output), active)

    def test_wal_and_shm_handles_resolve_to_one_database(self):
        active = self.catalog('catalog.db')
        output = f'p100\ncCodex\nn{active}-wal\nn{active}-shm\n'
        self.assertEqual(self.detect(output), active)

    def test_multiple_active_catalogs_stop(self):
        first = self.catalog('first.db')
        second = self.catalog('second.db')
        with self.assertRaisesRegex(RuntimeError, 'Expected one catalog'):
            self.detect(f'p100\ncCodex\nn{first}\nn{second}\n')

    def test_unrelated_process_cannot_select_database(self):
        path = self.catalog('catalog.db')
        with self.assertRaisesRegex(RuntimeError, 'found none'):
            self.detect(f'p100\ncPython\nn{path}\n')

    def test_process_boundary_resets_app_identity(self):
        path = self.catalog('catalog.db')
        with self.assertRaisesRegex(RuntimeError, 'found none'):
            self.detect(f'p100\ncCodex\np101\nn{path}\n')

    def test_non_catalog_database_is_ignored(self):
        active = self.catalog('catalog.db')
        other = self.db_dir / 'summaries.db'
        sqlite3.connect(other).close()
        self.assertEqual(self.detect(f'p100\ncChatGPT\nn{other}\nn{active}\n'), active)

    def test_invalid_open_catalog_stops_instead_of_selecting_another(self):
        active = self.catalog('valid.db')
        invalid = self.catalog('incompatible.db')
        with closing(sqlite3.connect(invalid)) as conn:
            conn.execute('DROP TABLE local_thread_catalog_sync_state')
            conn.commit()
        with self.assertRaisesRegex(RuntimeError, 'failed validation'):
            self.detect(f'p100\ncCodex\nn{active}\nn{invalid}\n')

    def test_no_process_does_not_fall_back_to_existing_file(self):
        self.catalog('codex.db')
        with self.assertRaisesRegex(RuntimeError, 'found none'):
            self.detect('')

    def test_lsof_error_stops_detection(self):
        with self.assertRaisesRegex(RuntimeError, 'Database detection failed'):
            self.detect('', returncode=2)


if __name__ == '__main__':
    unittest.main()
