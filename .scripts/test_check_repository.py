"""Synthetic offline fixtures; no private source, service, or app is read."""
import importlib.util
from pathlib import Path
import tempfile
import unittest


SOURCE = Path(__file__).resolve().with_name("check_repository.py")
SPEC = importlib.util.spec_from_file_location("repository_check", SOURCE)
checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checker)


class RepositoryCheckTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def categories(self):
        return {item["category"] for item in checker.audit(self.root)["findings"]}

    def test_minimal_self_contained_skill(self):
        skill = self.root / "sample"
        skill.mkdir()
        (skill / "SKILL.md").write_text(
            "---\nname: sample\ndescription: Synthetic fixture.\n---\n"
            "# Sample\n\n## Dependency preflight\n\nStop if input is missing.\n\n"
            "## Dependencies and portability\n\nHost agent only.\n")
        self.assertEqual(checker.audit(self.root)["findings"], [])

    def test_missing_local_link(self):
        (self.root / "README.md").write_text("[Missing](missing.md)\n")
        self.assertIn("missing-local-link", self.categories())

    def test_per_skill_maintenance_changelogs_are_flagged(self):
        self.test_minimal_self_contained_skill()
        for name in ("CHANGELOG", "CHANGELOG.md", "Changelog.rst", "changelog.txt"):
            with self.subTest(name=name):
                path = self.root / "sample" / name
                path.write_text("# Maintenance history\n")
                self.assertIn("per-skill-maintenance-changelog", self.categories())
                path.unlink()

    def test_runtime_topic_changelog_fixture_is_not_maintenance_history(self):
        self.test_minimal_self_contained_skill()
        topic = self.root / "sample" / "tests" / "fixtures" / "topic"
        topic.mkdir(parents=True)
        (topic / "CHANGELOG.md").write_text("# Synthetic topic history\n")
        self.assertEqual(checker.audit(self.root)["findings"], [])

    def test_external_documentation_is_not_a_missing_local_file(self):
        (self.root / "README.md").write_text("[Example](https://example.com/)\n")
        self.assertEqual(checker.audit(self.root)["findings"], [])

    def test_machine_artifact_and_symlink_are_flagged_without_following(self):
        (self.root / ".DS_Store").write_bytes(b"\x00\xff")
        (self.root / "outside").symlink_to(self.root.parent, target_is_directory=True)
        self.assertIn("machine-or-private-artifact", self.categories())
        self.assertIn("symlink-needs-review", self.categories())

    def test_git_metadata_is_outside_scope(self):
        git = self.root / ".git"
        git.mkdir()
        (git / "private").write_bytes(b"\xff")
        self.assertEqual(checker.audit(self.root)["findings"], [])

    def test_personal_home_and_contact_patterns(self):
        home = "/" + "Users" + "/" + "private-person" + "/notes"
        email = "person" + "@" + "company.tld"
        categories = {category for category, _ in checker.findings_in_text(home + "\n" + email)}
        self.assertIn("personal-home-path", categories)
        self.assertIn("email-needs-review", categories)
        self.assertEqual(checker.findings_in_text("person@example.com"), [])

    def test_known_private_terms_do_not_appear_in_results(self):
        term = "synthetic private fixture"
        (self.root / "README.md").write_text(term)
        result = checker.audit(self.root, [term])
        self.assertEqual(result["findings"][0]["category"], "private-term")
        self.assertNotIn(term, repr(result))

    def test_syntax_and_external_imports_are_flagged(self):
        (self.root / "broken.py").write_text("def broken(:\n")
        (self.root / "external.py").write_text("import nonexistent_fixture_module\n")
        self.assertIn("python-syntax", self.categories())
        self.assertIn("nonstdlib-import-needs-review", self.categories())

    def test_local_module_is_not_an_external_dependency(self):
        (self.root / "helper.py").write_text("VALUE = 1\n")
        (self.root / "main.py").write_text("import helper\nimport json\n")
        self.assertEqual(checker.audit(self.root)["findings"], [])

    def test_absolute_python_shebang_is_checked_without_running_it(self):
        (self.root / "helper").write_text("#!/usr/bin/python3\nimport nonexistent_fixture_module\n")
        self.assertIn("nonstdlib-import-needs-review", self.categories())

    def test_stale_skill_index_is_flagged(self):
        (self.root / "README.md").write_text("[Old](old-skill/SKILL.md)\n")
        self.assertIn("skill-index-mismatch", self.categories())

    def test_skill_must_not_depend_on_a_sibling_resource(self):
        skill = self.root / "sample"
        skill.mkdir()
        (self.root / "outside.md").write_text("A repository-level resource.\n")
        (skill / "SKILL.md").write_text(
            "---\nname: sample\ndescription: Synthetic fixture.\n---\n"
            "## Dependency preflight\n\nStop if input is missing.\n\n"
            "## Dependencies and portability\n\n[Outside](../outside.md)\n")
        self.assertIn("resource-outside-skill", self.categories())

    def test_skill_requires_dependency_preflight(self):
        skill = self.root / "sample"
        skill.mkdir()
        (skill / "SKILL.md").write_text(
            "---\nname: sample\ndescription: Synthetic fixture.\n---\n"
            "## Dependencies and portability\n\nHost agent only.\n")
        self.assertIn("missing-dependency-preflight", self.categories())


if __name__ == "__main__":
    unittest.main()
