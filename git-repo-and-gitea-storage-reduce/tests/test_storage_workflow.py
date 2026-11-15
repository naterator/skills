import hashlib
import json
import os
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
SKILL = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL / "scripts"


class StorageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Short paths avoid macOS's Unix-domain socket length limit for GPG.
        cls.workspace = tempfile.TemporaryDirectory(prefix="gs-")
        cls.base = Path(cls.workspace.name)
        cls.home = cls.base / "g"
        cls.home.mkdir(mode=0o700)
        cls.env = dict(os.environ)
        for name in list(cls.env):
            if name.startswith("GIT_") or name == "GNUPGHOME":
                cls.env.pop(name)
        cls.env.update({
            "GNUPGHOME": str(cls.home), "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_CONFIG_SYSTEM": os.devnull, "GIT_OPTIONAL_LOCKS": "0",
            "PYTHONDONTWRITEBYTECODE": "1", "LC_ALL": "C",
        })
        cls.gpg = shutil.which("gpg")
        cls.gpgconf = shutil.which("gpgconf")
        cls.fingerprint = None
        if cls.gpg and cls.gpgconf:
            generated = subprocess.run(
                [cls.gpg, "--batch", "--pinentry-mode", "loopback", "--passphrase", "",
                 "--quick-generate-key", "Storage Fixture <fixture@example.invalid>",
                 "ed25519", "sign", "0"],
                env=cls.env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                timeout=30,
            )
            if generated.returncode:
                subprocess.run(
                    [cls.gpgconf, "--homedir", str(cls.home), "--kill", "gpg-agent"],
                    env=cls.env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10,
                )
                cls.workspace.cleanup()
                raise RuntimeError(generated.stderr.decode(errors="replace"))
            keys = subprocess.check_output(
                [cls.gpg, "--batch", "--with-colons", "--list-secret-keys"],
                env=cls.env, text=True, stderr=subprocess.DEVNULL, timeout=20,
            )
            cls.fingerprint = next(
                row.split(":")[9] for row in keys.splitlines() if row.startswith("fpr:")
            )

    @classmethod
    def tearDownClass(cls):
        if cls.gpgconf and cls.fingerprint:
            subprocess.run(
                [cls.gpgconf, "--homedir", str(cls.home), "--kill", "gpg-agent"],
                env=cls.env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10,
            )
        cls.workspace.cleanup()

    def setUp(self):
        self.case = Path(tempfile.mkdtemp(prefix="case-", dir=self.base))
        self.repo = self.case / "repo"
        self.repo.mkdir()
        self.git("init", "-b", "main")
        self.git("config", "user.name", "Storage Fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("config", "commit.gpgsign", "false")
        if self.fingerprint:
            self.git("config", "gpg.program", self.gpg)
            self.git("config", "user.signingkey", self.fingerprint)
        old = b"\x89PNG\r\n\x1a\n\0" + random.Random(10).randbytes(64 * 1024)
        self.old_oid = self.git("hash-object", "-w", "--stdin", data=old).strip()
        (self.repo / "asset.bin").write_bytes(old)
        (self.repo / "guide.md").write_text("First guide\n")
        self.git("add", ".")
        self.git("commit", "-m", "feat: Add original binary")
        (self.repo / "asset.bin").write_bytes(
            b"\0" + random.Random(20).randbytes(64 * 1024))
        (self.repo / "guide.md").write_text("Current guide\n")
        self.git("add", ".")
        self.git("commit", "-m", "feat: Replace binary without losing current data")
        self.head = self.git("rev-parse", "HEAD").strip()
        self.current_oid = self.git("rev-parse", "HEAD:asset.bin").strip()
        self.tree = self.git("rev-parse", "HEAD^{tree}").strip()

    def git(self, *args, data=None, expected=0):
        p = subprocess.run(
            ["git", "-C", str(self.repo), *args],
            input=data, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            env=self.env, timeout=30,
        )
        self.assertEqual(p.returncode, expected, p.stderr.decode(errors="replace"))
        return p.stdout.decode()

    def cli(self, name, *args, expected=0):
        p = subprocess.run(
            [sys.executable, str(SCRIPTS / name), *map(str, args)],
            env=self.env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, timeout=90,
        )
        self.assertEqual(p.returncode, expected, p.stderr)
        return p

    def plan(self, **changes):
        if not self.fingerprint:
            self.skipTest("GPG/GPGCONF unavailable")
        bundle = self.case / "before.bundle"
        self.git("bundle", "create", str(bundle), "--all")
        data = {
            "schema": 1, "repository": str(self.repo), "branch": "main",
            "old_head": self.head, "remove_blob_ids": [self.old_oid],
            "auxiliary_tree_refs": [], "signing_key": self.fingerprint,
            "backup_bundle": str(bundle),
            "backup_sha256": hashlib.sha256(bundle.read_bytes()).hexdigest(),
        }
        data.update(changes)
        path = self.case / "plan.json"
        path.write_text(json.dumps(data))
        return path

    def git_file_snapshot(self):
        return {
            str(p.relative_to(self.repo / ".git")): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in (self.repo / ".git").rglob("*")
            if p.is_file() and not p.is_symlink()
        }

    def test_audit_is_read_only_and_separates_current_and_old(self):
        before = self.git_file_snapshot()
        result = json.loads(self.cli(
            "audit_git_storage.py", "--repo", self.repo, "--classify-binaries"
        ).stdout)
        self.assertEqual(before, self.git_file_snapshot())
        self.assertEqual(result["head"], self.head)
        old = next(x for x in result["historical_blob_candidates"]
                   if x["oid"] == self.old_oid)
        self.assertIsNotNone(old["binary_prefix_evidence"])
        self.assertNotIn(self.current_oid, {
            x["oid"] for x in result["historical_blob_candidates"]
        })

    def test_audit_recognizes_reflog_only_commits_and_unreachable_blobs(self):
        self.git("commit", "--allow-empty", "-m", "Temporary unpublished recovery")
        recovery = self.git("rev-parse", "HEAD").strip()
        self.git("update-ref", "refs/heads/main", self.head, recovery)
        orphan = self.git("hash-object", "-w", "--stdin", data=b"orphan\0bytes").strip()
        result = json.loads(self.cli("audit_git_storage.py", "--repo", self.repo).stdout)
        self.assertGreater(
            result["groups"]["objects_only_reachable_from_reflogs"]["objects"], 0)
        self.assertGreater(
            result["groups"]["unreachable_even_from_reflogs"]["objects"], 0)
        self.git("cat-file", "-e", orphan)

    def test_narrow_expiry_preserves_old_reachable_recovery_entries(self):
        ref = "refs/heads/fixture-old-recovery-log"
        env = dict(self.env, GIT_COMMITTER_DATE="946684800 +0000")
        subprocess.run(
            ["git", "-C", str(self.repo), "update-ref", "--create-reflog", ref, self.head],
            env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, timeout=20,
        )
        before = self.git("reflog", "show", "--format=%H", ref)
        self.assertIn(self.head, before)
        self.git("reflog", "expire", "--expire=never", "--expire-unreachable=now", ref)
        self.assertEqual(self.git("reflog", "show", "--format=%H", ref), before)
        self.git("-c", "gc.reflogExpire=never", "-c", "gc.reflogExpireUnreachable=never",
                 "gc", "--prune=now")
        self.assertEqual(self.git("reflog", "show", "--format=%H", ref), before)

    def test_protected_current_blob_is_refused(self):
        plan = self.plan(remove_blob_ids=[self.current_oid])
        result = self.cli("rewrite_signed_history.py", "--plan", plan, expected=2)
        self.assertIn("current-HEAD", result.stderr)
        self.assertEqual(self.git("rev-parse", "HEAD").strip(), self.head)

    def test_dirty_owner_work_is_preserved(self):
        plan = self.plan()
        (self.repo / "owner-notes.txt").write_text("Do not discard\n")
        result = self.cli("rewrite_signed_history.py", "--plan", plan, expected=2)
        self.assertIn("Dirty/untracked", result.stderr)
        self.assertEqual((self.repo / "owner-notes.txt").read_text(), "Do not discard\n")
        self.assertEqual(self.git("rev-parse", "HEAD").strip(), self.head)

    def test_stash_notes_tags_and_unknown_refs_are_not_deleted(self):
        self.git("tag", "preserve-me")
        plan = self.plan()
        result = self.cli("rewrite_signed_history.py", "--plan", plan, expected=2)
        self.assertIn("Unapproved ref", result.stderr)
        self.assertEqual(self.git("rev-parse", "refs/tags/preserve-me").strip(), self.head)

    def test_unknown_stash_is_preserved_without_guessing_it_is_unused(self):
        self.git("update-ref", "refs/stash", self.head)
        plan = self.plan()
        result = self.cli("rewrite_signed_history.py", "--plan", plan, expected=2)
        self.assertIn("Unapproved ref", result.stderr)
        self.assertEqual(self.git("rev-parse", "refs/stash").strip(), self.head)

    def test_unknown_notes_ref_and_git_storage_redirection_are_refused(self):
        self.git("notes", "add", "-m", "Retain useful note", "HEAD")
        plan = self.plan()
        result = self.cli("rewrite_signed_history.py", "--plan", plan, expected=2)
        self.assertIn("Unapproved ref", result.stderr)
        self.assertEqual(self.git("notes", "show", "HEAD").strip(), "Retain useful note")
        env = dict(self.env, GIT_INDEX_FILE=str(self.case / "alternate-index"))
        p = subprocess.run(
            [sys.executable, str(SCRIPTS / "rewrite_signed_history.py"), "--plan", str(plan)],
            env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30,
        )
        self.assertEqual(p.returncode, 2)
        self.assertIn("redirects storage/index", p.stderr)
        self.assertFalse((self.case / "alternate-index").exists())

    def test_signing_failure_does_not_change_refs_or_fall_back_unsigned(self):
        plan = self.plan()
        self.git("config", "gpg.program", shutil.which("false"))
        result = self.cli(
            "rewrite_signed_history.py", "--plan", plan, "--apply",
            "--expected-head", self.head, "--ack-rewrite-and-resign", expected=2,
        )
        self.assertIn("GPG key unavailable", result.stderr)
        self.assertEqual(self.git("rev-parse", "HEAD").strip(), self.head)
        self.assertFalse((self.case / "signed-rewrite-result.json").exists())

    def test_existing_recovery_receipt_is_not_overwritten(self):
        plan = self.plan()
        existing = self.case / "signed-rewrite-result.tmp"
        existing.write_text("Unreviewed prior-attempt recovery information\n")
        result = self.cli(
            "rewrite_signed_history.py", "--plan", plan, "--apply",
            "--expected-head", self.head, "--ack-rewrite-and-resign", expected=2,
        )
        self.assertIn("Existing temporary result", result.stderr)
        self.assertEqual(existing.read_text(), "Unreviewed prior-attempt recovery information\n")
        self.assertEqual(self.git("rev-parse", "HEAD").strip(), self.head)

    def test_bad_backup_or_wrong_signer_stops_without_ref_changes(self):
        plan = self.plan(backup_sha256="0" * 64)
        result = self.cli("rewrite_signed_history.py", "--plan", plan, expected=2)
        self.assertIn("SHA-256 mismatch", result.stderr)
        data = json.loads(plan.read_text())
        data["backup_sha256"] = hashlib.sha256(Path(data["backup_bundle"]).read_bytes()).hexdigest()
        data["signing_key"] = "A" * 40
        plan.write_text(json.dumps(data))
        result = self.cli("rewrite_signed_history.py", "--plan", plan, expected=2)
        self.assertIn("configured signing identity", result.stderr)
        self.assertEqual(self.git("rev-parse", "HEAD").strip(), self.head)

    def test_dry_run_does_not_write_sign_or_repoint(self):
        plan = self.plan()
        before = self.git_file_snapshot()
        result = json.loads(self.cli("rewrite_signed_history.py", "--plan", plan).stdout)
        self.assertIn("dry-run", result["mode"])
        self.assertEqual(before, self.git_file_snapshot())
        self.assertFalse((self.case / "signed-rewrite-result.json").exists())
        self.assertEqual(self.git("rev-parse", "HEAD").strip(), self.head)

    def test_signed_rewrite_preserves_tree_and_remaps_only_approved_tree_ref(self):
        old_tree = self.git("rev-parse", "HEAD~1^{tree}").strip()
        ref = "refs/tool/checkpoint"
        self.git("update-ref", ref, old_tree)
        plan = self.plan(auxiliary_tree_refs=[ref])
        self.cli("rewrite_signed_history.py", "--plan", plan, "--apply",
                 "--expected-head", self.head, "--ack-rewrite-and-resign")
        report = json.loads((self.case / "signed-rewrite-result.json").read_text())
        self.assertTrue(report["refs_updated"])
        self.assertEqual(report["commits_resigned"], 2)
        self.assertFalse(report["push_performed"])
        self.assertFalse(report["gc_performed"])
        self.assertEqual(self.git("rev-parse", "HEAD^{tree}").strip(), self.tree)
        self.assertNotEqual(self.git("rev-parse", ref).strip(), old_tree)
        signatures = self.git("log", "--format=%G? %GF").splitlines()
        self.assertEqual(signatures, ["G " + self.fingerprint] * 2)
        self.assertNotIn(self.old_oid, self.git("rev-list", "--objects", "--all"))
        # Only this isolated fixture's approved recovery history is discarded.
        self.git("reflog", "expire", "--expire=now", "--expire-unreachable=now", "--all")
        self.git("gc", "--prune=now")
        self.git("fsck", "--full", "--strict")
        self.git("cat-file", "-e", self.old_oid, expected=1)
        self.assertEqual(self.git("status", "--porcelain"), "")

    def test_plain_merge_parent_order_and_commit_count_are_preserved(self):
        if not self.fingerprint:
            self.skipTest("GPG/GPGCONF unavailable")
        self.git("checkout", "-b", "fixture-side", "HEAD~1")
        (self.repo / "side.txt").write_text("Retained merged source\n")
        self.git("add", "side.txt")
        self.git("commit", "-m", "feat: Add side branch input")
        self.git("checkout", "main")
        self.git("merge", "--no-ff", "fixture-side", "-m", "feat: Merge retained input")
        self.git("branch", "-d", "fixture-side")
        self.head = self.git("rev-parse", "HEAD").strip()
        self.tree = self.git("rev-parse", "HEAD^{tree}").strip()
        old_parents = self.git("show", "-s", "--format=%P", "HEAD").split()
        plan = self.plan()
        self.cli("rewrite_signed_history.py", "--plan", plan, "--apply",
                 "--expected-head", self.head, "--ack-rewrite-and-resign")
        report = json.loads((self.case / "signed-rewrite-result.json").read_text())
        new_parents = self.git("show", "-s", "--format=%P", "HEAD").split()
        self.assertEqual(
            new_parents, [report["commit_map"][oid] for oid in old_parents])
        self.assertEqual(report["commits_resigned"], 4)
        self.assertEqual(self.git("rev-parse", "HEAD^{tree}").strip(), self.tree)
        self.assertEqual((self.repo / "side.txt").read_text(), "Retained merged source\n")

    def test_configured_primary_with_validated_signing_subkey(self):
        if not self.fingerprint:
            self.skipTest("GPG/GPGCONF unavailable")
        uid = "Subkey Fixture <subkey@example.invalid>"
        common = [self.gpg, "--batch", "--pinentry-mode", "loopback", "--passphrase", ""]
        subprocess.run(
            common + ["--quick-generate-key", uid, "ed25519", "cert", "0"],
            env=self.env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            timeout=30, check=True,
        )
        listing = subprocess.check_output(
            [self.gpg, "--batch", "--with-colons", "--list-secret-keys", uid],
            env=self.env, text=True, stderr=subprocess.DEVNULL, timeout=20,
        )
        primary = next(row.split(":")[9] for row in listing.splitlines()
                       if row.startswith("fpr:"))
        subprocess.run(
            common + ["--quick-add-key", primary, "ed25519", "sign", "0"],
            env=self.env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            timeout=30, check=True,
        )
        self.fingerprint = primary
        self.git("config", "user.signingkey", primary)
        plan = self.plan()
        self.cli("rewrite_signed_history.py", "--plan", plan, "--apply",
                 "--expected-head", self.head, "--ack-rewrite-and-resign")
        report = json.loads((self.case / "signed-rewrite-result.json").read_text())
        self.assertEqual(self.git("log", "--format=%G? %GP").splitlines(),
                         ["G " + primary] * 2)
        self.assertTrue(all(row["verified_configured_fingerprint"] == primary
                            and row["actual_signing_fingerprint"] != primary
                            for row in report["signature_checks"]))


if __name__ == "__main__":
    unittest.main()
