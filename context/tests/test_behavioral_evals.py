"""Test fixture preparation and state grading, not model compliance with the skill."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = SKILL_ROOT / 'scripts' / 'behavioral_evals.py'
SPEC = importlib.util.spec_from_file_location('behavioral_evals', SCRIPT)
evaluation = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(evaluation)


class BehavioralFixtureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.output = self.base / 'suite'

    def case(self, case_id):
        return evaluation.prepare(self.output, [case_id])[0]

    def test_all_cases_prepare_with_isolated_roots_and_no_placeholders(self):
        cases = evaluation.prepare(self.output)
        self.assertEqual(len(cases), 10)
        roots = {case['context_root'] for case in cases}
        self.assertEqual(len(roots), 10)
        for case in cases:
            with self.subTest(case=case['id']):
                path = Path(case['case_directory'])
                self.assertTrue(path.is_relative_to(self.output))
                self.assertNotIn('{context_root}', Path(case['prompt_file']).read_text())
                self.assertEqual(
                    json.loads((path / 'baseline.json').read_text()),
                    evaluation.snapshot(Path(case['fixture'])))
                collection = Path(case['fixture_collection'])
                self.assertFalse((collection / 'CHANGELOG.md').exists())
                self.assertFalse((collection / 'hardware' / 'absent').exists())
                self.assertFalse((Path(case['fixture']) / 'projects' / 'missing').exists())
                self.assertTrue((collection / 'atlas' / 'README.md').is_file())

    def test_no_change_cases_pass_state_checks_but_semantics_remain_pending(self):
        for case in evaluation.prepare(self.output):
            if case['allowed_changes'] == 'none':
                with self.subTest(case=case['id']):
                    result = evaluation.check_state(case['case_directory'], case['expected_workdir'])
                    self.assertTrue(result['state_checks_passed'])
                    self.assertEqual(result['changed_paths'], [])
                    self.assertIn('Pending', result['behavioral_assertions'])

    def test_wrong_working_directory_fails(self):
        case = self.case(2)
        result = evaluation.check_state(case['case_directory'], case['initial_workdir'])
        self.assertFalse(result['state_checks_passed'])
        self.assertFalse(result['checks']['working_directory_matches'])

    def test_unexpected_write_in_read_only_case_fails(self):
        case = self.case(1)
        (Path(case['context_root']) / 'new.md').write_text('unexpected')
        result = evaluation.check_state(case['case_directory'], case['expected_workdir'])
        self.assertFalse(result['state_checks_passed'])
        self.assertIn('collection/new.md', result['changed_paths'])

    def save_finding(self, case, record_name='notes.md'):
        topic = Path(case['context_root']) / 'atlas'
        record = topic / record_name
        record.write_text(record.read_text()
                          + '\n## Parser finding\n\n'
                          'The parser accepts empty input and returns an empty list.\n')
        log = topic / 'CHANGELOG.md'
        log.write_text(log.read_text()
                       + f'\n- Saved the parser [finding]({record_name}).\n')

    def test_scoped_save_passes_state_checks(self):
        case = self.case(3)
        self.save_finding(case)
        result = evaluation.check_state(case['case_directory'], case['initial_workdir'])
        self.assertTrue(result['state_checks_passed'], result)

    def test_save_in_readme_with_changelog_fragment_link_passes(self):
        case = self.case(3)
        self.save_finding(case, 'README.md')
        topic = Path(case['context_root']) / 'atlas'
        log = topic / 'CHANGELOG.md'
        log.write_text(log.read_text().replace(
            '[finding](README.md)', '[finding](README.md#parser-finding)'))
        result = evaluation.check_state(case['case_directory'], case['initial_workdir'])
        self.assertTrue(result['state_checks_passed'], result)
        self.assertNotIn('collection/atlas/notes.md', result['changed_paths'])

    def test_save_in_readme_without_changelog_change_fails(self):
        case = self.case(3)
        readme = Path(case['context_root']) / 'atlas' / 'README.md'
        readme.write_text(readme.read_text()
                          + '\nThe parser accepts empty input and returns an empty list.\n')
        result = evaluation.check_state(case['case_directory'], case['initial_workdir'])
        self.assertFalse(result['state_checks_passed'])
        self.assertFalse(result['checks']['record_and_changelog_changed'])

    def test_changelog_link_to_record_without_finding_fails(self):
        case = self.case(3)
        self.save_finding(case)
        log = Path(case['context_root']) / 'atlas' / 'CHANGELOG.md'
        # The baseline log already links README; it must not satisfy a notes save.
        log.write_text(log.read_text().replace('[finding](notes.md)', '[finding](README.md)'))
        result = evaluation.check_state(case['case_directory'], case['initial_workdir'])
        self.assertFalse(result['state_checks_passed'])
        self.assertTrue(result['checks']['finding_recorded'])
        self.assertFalse(result['checks']['changelog_links_to_finding'])

    def test_save_with_directory_mapping_change_fails(self):
        case = self.case(3)
        self.save_finding(case)
        readme = Path(case['context_root']) / 'atlas' / 'README.md'
        readme.write_text(readme.read_text().replace('Default working directory:', 'Removed setting:'))
        result = evaluation.check_state(case['case_directory'], case['initial_workdir'])
        self.assertFalse(result['state_checks_passed'])
        self.assertFalse(result['checks']['saved_directory_preserved'])

    def test_save_without_changelog_notes_link_fails(self):
        case = self.case(3)
        self.save_finding(case)
        log = Path(case['context_root']) / 'atlas' / 'CHANGELOG.md'
        log.write_text(log.read_text().replace('[finding](notes.md)', 'finding'))
        result = evaluation.check_state(case['case_directory'], case['initial_workdir'])
        self.assertFalse(result['state_checks_passed'])
        self.assertFalse(result['checks']['changelog_links_to_finding'])

    def test_missing_root_case_has_no_conflicting_selected_root_in_prompt(self):
        case = self.case(9)
        self.assertFalse(Path(case['context_root']).exists())
        prompt = Path(case['prompt_file']).read_text()
        self.assertIn(f"Selected collection: {case['context_root']}", prompt)

    def test_prepare_refuses_existing_output_without_changing_it(self):
        self.output.mkdir()
        sentinel = self.output / 'sentinel'
        sentinel.write_text('preserve')
        with self.assertRaises(FileExistsError):
            evaluation.prepare(self.output)
        self.assertEqual(sentinel.read_text(), 'preserve')
        self.assertEqual(list(self.output.iterdir()), [sentinel])

    def test_prepare_refuses_live_context_or_skill_destinations(self):
        for output in (evaluation.LIVE_CONTEXT_ROOT / 'forbidden-eval-output',
                       SKILL_ROOT / 'forbidden-eval-output'):
            with self.subTest(output=output), self.assertRaises(ValueError):
                evaluation.prepare(output)
            self.assertFalse(output.exists())

    def test_prepare_refuses_symlink_alias_into_live_context(self):
        alias = self.base / 'live-alias'
        alias.symlink_to(evaluation.LIVE_CONTEXT_ROOT, target_is_directory=True)
        with self.assertRaises(ValueError):
            evaluation.prepare(alias / 'forbidden-eval-output')
        self.assertFalse((alias / 'forbidden-eval-output').exists())

    def test_state_checker_does_not_read_outside_fixture_through_record_symlink(self):
        case = self.case(3)
        outside = self.base / 'outside.bin'
        outside.write_bytes(b'\xff')
        notes = Path(case['context_root']) / 'atlas' / 'notes.md'
        notes.unlink()
        notes.symlink_to(outside)
        result = evaluation.check_state(case['case_directory'], case['initial_workdir'])
        self.assertFalse(result['state_checks_passed'])
        self.assertFalse(result['checks']['finding_recorded'])
        self.assertEqual(outside.read_bytes(), b'\xff')

    def test_fixture_discovery_only_finds_synthetic_subject_in_test_examples(self):
        case = self.case(10)
        completed = subprocess.run(
            [sys.executable, '-B', str(SKILL_ROOT / 'scripts' / 'discover_context.py'),
             '--root', case['context_root'], '--topic', 'synthetic-wombat'],
            capture_output=True, text=True, check=True)
        result = json.loads(completed.stdout)
        self.assertTrue(result['inventory_complete'])
        self.assertEqual(result['directory_candidates'], [])
        self.assertEqual(result['summary']['matching_files_by_role']['topic-content'], 0)
        self.assertEqual(result['summary']['matching_files_by_role']['test-example'], 1)
        self.assertEqual(result['excluded_paths'], [{'path': '.git', 'reason': 'Git metadata'}])

    def test_unknown_case_refused_before_creating_output(self):
        with self.assertRaises(ValueError):
            evaluation.prepare(self.output, [999])
        self.assertFalse(self.output.exists())

    def test_cli_prepares_and_checks_a_single_case(self):
        created = subprocess.run(
            [sys.executable, '-B', str(SCRIPT), 'prepare', '--output', str(self.output),
             '--case', '5'], capture_output=True, text=True, check=True)
        case = json.loads(created.stdout)[0]
        checked = subprocess.run(
            [sys.executable, '-B', str(SCRIPT), 'check-state',
             '--case-directory', case['case_directory'],
             '--observed-workdir', case['expected_workdir']],
            capture_output=True, text=True, check=True)
        self.assertTrue(json.loads(checked.stdout)['state_checks_passed'])
        wrong = subprocess.run(
            [sys.executable, '-B', str(SCRIPT), 'check-state',
             '--case-directory', case['case_directory'],
             '--observed-workdir', case['initial_workdir']], capture_output=True, text=True)
        self.assertEqual(wrong.returncode, 1)


if __name__ == '__main__':
    unittest.main()
