"""Offline regression tests; all discovery runs use isolated temporary roots."""
import importlib.util
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = SKILL_ROOT / 'scripts' / 'discover_context.py'
SPEC = importlib.util.spec_from_file_location('discover_context', SCRIPT)
discovery = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(discovery)


class DiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()

    def write(self, name, text='Current topic notes'):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8')
        return path

    def scan(self, topic='printer', aliases=()):
        return discovery.discover(self.root, topic, aliases)

    def test_root_git_directory_is_excluded(self):
        self.write('.git/logs/HEAD', 'printer historical-only evidence')
        self.write('.git/objects/aa/bb', 'printer historical-only evidence')
        self.write('printer/README.md', 'Current printer')
        result = self.scan()
        self.assertEqual(result['excluded_paths'], [{'path': '.git', 'reason': 'Git metadata'}])
        self.assertTrue(result['inventory_complete'])
        self.assertFalse(any(p.startswith('.git') for p in result['directories']))
        self.assertEqual([f['path'] for f in result['files']], ['printer/README.md'])
        self.assertEqual(result['summary']['excluded_paths'], 1)

    def test_nested_worktree_pointer_is_excluded(self):
        self.write('legacy/project/.git', 'gitdir: /outside/worktrees/project')
        self.write('legacy/project/README.md', 'printer notes')
        result = self.scan()
        self.assertEqual(result['excluded_paths'][0]['path'], 'legacy/project/.git')
        self.assertTrue(result['inventory_complete'])
        self.assertEqual(len(result['files']), 1)

    def test_nested_git_directory_is_excluded(self):
        self.write('legacy/.git/config', 'printer old repository')
        self.write('legacy/notes.md', 'printer current notes')
        result = self.scan()
        self.assertEqual(result['excluded_paths'][0]['path'], 'legacy/.git')
        self.assertEqual(result['summary']['matching_files'], 1)

    def test_git_symlink_is_excluded_without_following(self):
        (self.root / '.git').symlink_to(self.root / 'nonexistent')
        result = self.scan()
        self.assertEqual(result['excluded_paths'][0]['path'], '.git')
        self.assertTrue(result['inventory_complete'])
        self.assertEqual(result['links'], [])
        self.assertEqual(result['errors'], [])

    def test_file_alias_into_git_metadata_is_excluded(self):
        target = self.write('.git/logs/HEAD', 'historical-only-printer')
        (self.root / 'history-alias.md').symlink_to(target)
        result = self.scan('historical-only-printer')
        self.assertTrue(result['inventory_complete'])
        self.assertEqual(result['summary']['matching_files'], 0)
        self.assertEqual(result['files'], [])
        self.assertEqual(result['links'][0]['coverage'], 'excluded Git metadata')

    def test_directory_alias_into_nested_git_metadata_is_excluded(self):
        self.write('nested/.git/logs/HEAD', 'historical-only-printer')
        (self.root / 'history').symlink_to(
            self.root / 'nested' / '.git' / 'logs', target_is_directory=True)
        result = self.scan('historical-only-printer')
        self.assertTrue(result['inventory_complete'])
        self.assertEqual(result['summary']['matching_files'], 0)
        self.assertFalse(any('.git' in Path(p).parts for p in result['directories']))

    def test_symlink_chain_cannot_reintroduce_git_content(self):
        target = self.write('.git/logs/HEAD', 'historical-only-printer')
        first = self.root / 'first'
        first.symlink_to(target)
        (self.root / 'second').symlink_to(first)
        result = self.scan('historical-only-printer')
        self.assertTrue(result['inventory_complete'])
        self.assertEqual(result['files'], [])

    def test_hidden_topics_skill_sources_and_gitignore_are_searched(self):
        names = ['.hidden/README.md', '.skills/context/scripts/source.py',
                 '.gitignore', 'notes/.git-notes.md']
        for name in names:
            self.write(name, 'printer source notes')
        result = self.scan()
        self.assertEqual({f['path'] for f in result['files']}, set(names))
        self.assertEqual(result['summary']['matching_files'], len(names))
        self.assertEqual(result['excluded_paths'], [])

    def test_infrastructure_and_examples_are_classified_not_topic_candidates(self):
        names = {
            '.skills/printer/SKILL.md': 'infrastructure',
            '.skills/printer/tests/source.py': 'test-example',
            '.skills/printer/evals/evals.json': 'test-example',
            '.skills/printer/fixtures/notes.md': 'test-example',
            '.opencode/agents/printer.md': 'infrastructure',
            '.claude/skills/printer/SKILL.md': 'infrastructure',
            '.agents/skills/printer/SKILL.md': 'infrastructure',
            'README.md': 'collection-metadata',
        }
        for name in names:
            self.write(name, 'printer example')
        result = self.scan()
        self.assertEqual({f['path']: f['role'] for f in result['files']}, names)
        self.assertEqual(result['directory_candidates'], [])
        by_role = result['summary']['matching_files_by_role']
        self.assertEqual(by_role['topic-content'], 0)
        self.assertEqual(by_role['test-example'], 3)
        self.assertEqual(by_role['infrastructure'], 4)
        self.assertEqual(by_role['collection-metadata'], 1)

    def test_real_hidden_topic_and_topic_scripts_remain_subject_evidence(self):
        self.write('.printer/README.md', 'printer topic')
        self.write('printer/tests/procedure.md', 'printer procedure')
        result = self.scan()
        self.assertEqual({f['role'] for f in result['files']}, {'topic-content'})
        self.assertEqual({p['path'] for p in result['directory_candidates']},
                         {'.printer', 'printer', 'printer/tests'})

    def test_standalone_root_notes_are_not_mislabeled_as_catalogue_metadata(self):
        self.write('printer-notes.md', 'printer evidence')
        self.write('README.md', 'printer locator')
        result = self.scan()
        self.assertEqual({f['path']: f['role'] for f in result['files']}, {
            'printer-notes.md': 'collection-content', 'README.md': 'collection-metadata'})
        self.assertEqual(result['summary']['matching_files_by_role']['collection-content'], 1)

    def test_alias_into_infrastructure_keeps_target_role(self):
        target = self.write('.skills/example/evals/evals.json', 'synthetic-wombat')
        (self.root / 'subject.md').symlink_to(target)
        result = self.scan('synthetic-wombat')
        self.assertEqual(result['links'][0]['role'], 'test-example')
        self.assertEqual(result['files'][0]['role'], 'test-example')
        self.assertEqual(result['summary']['matching_files_by_role']['topic-content'], 0)

    def test_git_history_does_not_generate_topic_matches(self):
        self.write('.git/logs/HEAD', 'unique historical printer')
        self.write('current/README.md', 'unrelated current notes')
        result = self.scan('unique historical printer')
        self.assertEqual(result['summary']['matching_files'], 0)
        self.assertEqual(result['directory_candidates'], [])

    def test_aliases_find_nested_legacy_notes(self):
        self.write('hardware/legacy-device/source.txt', 'Model M203 is still relevant')
        result = self.scan('HP LaserJet', ('M203',))
        item = result['files'][0]
        self.assertEqual(item['content_hits'][0]['query'], 'M203')
        self.assertEqual(item['sample_matching_lines'][0]['line'], 1)

    def test_internal_symlink_retains_content_coverage(self):
        target = self.write('printer/README.md', 'printer evidence')
        (self.root / 'alias.md').symlink_to(target)
        result = self.scan()
        self.assertTrue(result['inventory_complete'])
        self.assertEqual(len(result['links']), 1)
        self.assertEqual(len(result['files']), 1)

    def test_external_non_git_symlink_still_reports_coverage_error(self):
        with tempfile.TemporaryDirectory() as outside:
            (self.root / 'external').symlink_to(Path(outside).resolve(), target_is_directory=True)
            result = self.scan()
        self.assertFalse(result['inventory_complete'])
        self.assertIn('leaves Context root', result['errors'][0]['error'])

    def test_binary_content_is_still_inventoried(self):
        (self.root / 'archive.bin').write_bytes(b'\0printer')
        result = self.scan()
        self.assertEqual(result['files'][0]['kind'], 'non-text')
        self.assertEqual(result['files'][0]['coverage'], 'name/location only')
        self.assertTrue(result['inventory_complete'])

    def test_cli_absolute_path_works_from_unrelated_directory(self):
        self.write('printer/README.md', 'printer evidence')
        with tempfile.TemporaryDirectory() as cwd:
            completed = subprocess.run(
                [sys.executable, str(SCRIPT), '--root', str(self.root),
                 '--topic', 'printer'],
                cwd=cwd, capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(completed.stdout)['summary']['matching_files'], 1)

    def test_default_root_is_current_users_documents_context(self):
        self.assertEqual(discovery.DEFAULT_ROOT, Path.home() / 'Documents' / 'Context')

    def test_cli_uses_default_collection_when_root_is_omitted(self):
        self.write('printer/README.md', 'Current printer')
        output = io.StringIO()
        with mock.patch.object(discovery, 'DEFAULT_ROOT', self.root), redirect_stdout(output):
            status = discovery.main(['--topic', 'printer'])
        self.assertEqual(status, 0)
        result = json.loads(output.getvalue())
        self.assertEqual(result['root'], str(self.root))
        self.assertEqual(result['summary']['matching_files'], 1)

    def test_cli_resolves_default_collection_symlink(self):
        self.write('physical/printer/README.md', 'Current printer')
        target = self.root / 'physical'
        alias = self.root / 'context'
        alias.symlink_to(target, target_is_directory=True)
        with mock.patch.object(discovery, 'DEFAULT_ROOT', alias):
            for options in ([], ['--root', str(alias)]):
                with self.subTest(options=options):
                    output = io.StringIO()
                    with redirect_stdout(output):
                        status = discovery.main([*options, '--topic', 'printer'])
                    self.assertEqual(status, 0)
                    result = json.loads(output.getvalue())
                    self.assertEqual(result['root'], str(target))
                    self.assertEqual(result['summary']['matching_files'], 1)

    def test_cli_missing_default_collection_stops_without_creating_it(self):
        missing = self.root / 'Documents' / 'Context'
        output = io.StringIO()
        with mock.patch.object(discovery, 'DEFAULT_ROOT', missing), redirect_stdout(output):
            status = discovery.main(['--topic', 'printer'])
        self.assertEqual(status, 2)
        result = json.loads(output.getvalue())
        self.assertEqual(result['root'], str(missing))
        self.assertFalse(result['inventory_complete'])
        self.assertFalse(missing.exists())

    def test_cli_explicit_root_overrides_default_collection(self):
        self.write('printer/README.md', 'Current printer')
        missing_default = self.root / 'unused-default'
        output = io.StringIO()
        with mock.patch.object(discovery, 'DEFAULT_ROOT', missing_default), redirect_stdout(output):
            status = discovery.main(['--root', str(self.root), '--topic', 'printer'])
        self.assertEqual(status, 0)
        self.assertEqual(json.loads(output.getvalue())['root'], str(self.root))
        self.assertFalse(missing_default.exists())

    def test_missing_root_is_incomplete_with_an_error(self):
        missing = self.root / 'absent'
        result = discovery.discover(missing, 'printer')
        self.assertFalse(result['root_exists'])
        self.assertFalse(result['inventory_complete'])
        self.assertTrue(result['errors'])
        self.assertEqual(result['files'], [])
        self.assertFalse(missing.exists())

    def test_cli_missing_root_exits_nonzero_without_fallback(self):
        missing = self.root / 'absent'
        completed = subprocess.run(
            [sys.executable, '-B', str(SCRIPT), '--root', str(missing),
             '--topic', 'printer'], capture_output=True, text=True)
        self.assertEqual(completed.returncode, 2)
        result = json.loads(completed.stdout)
        self.assertEqual(result['root'], str(missing))
        self.assertFalse(result['inventory_complete'])
        self.assertEqual(result['summary']['directories'], 0)
        self.assertFalse(missing.exists())

    def test_file_root_is_incomplete(self):
        path = self.write('not-a-directory', 'printer')
        result = discovery.discover(path, 'printer')
        self.assertFalse(result['inventory_complete'])
        self.assertIn('not a directory', result['errors'][0]['error'])

    def test_root_permission_error_is_reported_not_raised(self):
        with mock.patch.object(Path, 'exists', side_effect=PermissionError('access denied')):
            result = discovery.discover(self.root, 'printer')
        self.assertFalse(result['inventory_complete'])
        self.assertIn('access denied', result['errors'][0]['error'])
        self.assertEqual(result['files'], [])

    def test_symlink_root_requires_explicit_resolved_root(self):
        alias = self.root / 'collection-alias'
        alias.symlink_to(self.root, target_is_directory=True)
        result = discovery.discover(alias, 'printer')
        self.assertFalse(result['inventory_complete'])
        self.assertIn('root is a symlink', result['errors'][0]['error'])

    def test_discovery_does_not_change_fixture_files(self):
        self.write('printer/README.md', 'printer evidence')
        self.write('.git/logs/HEAD', 'printer history')
        def snapshot():
            return {str(p.relative_to(self.root)): (p.read_bytes(), p.stat().st_mtime_ns)
                    for p in self.root.rglob('*') if p.is_file()}
        before = snapshot()
        self.scan()
        self.assertEqual(snapshot(), before)


class BehavioralCaseManifestTests(unittest.TestCase):
    def test_behavioral_cases_have_unique_ids_and_expected_checks(self):
        cases = json.loads((SKILL_ROOT / 'evals' / 'evals.json').read_text(encoding='utf-8'))
        self.assertEqual(cases['skill_name'], 'context')
        ids = [case['id'] for case in cases['evals']]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(ids), 10)
        for case in cases['evals']:
            with self.subTest(case=case['id']):
                self.assertTrue(case['prompt'])
                self.assertTrue(case['expected_output'])
                self.assertGreaterEqual(len(case['assertions']), 3)
                self.assertEqual(case['files'], [])
                self.assertIn('{context_root}', case['prompt'])
                self.assertIn(case['expected_workdir'], {'initial', 'atlas', 'context_root'})
                self.assertIn(case['allowed_changes'], {'none', 'atlas-save'})


if __name__ == '__main__':
    unittest.main()
