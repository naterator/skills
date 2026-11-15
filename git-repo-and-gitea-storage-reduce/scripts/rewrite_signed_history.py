#!/usr/bin/env python3
"""Guarded, dry-run-by-default binary-history rewrite. No push, expiry or GC."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
from audit_git_storage import Git, AuditError, binary_prefix, object_paths, tree_blobs


class Refusal(RuntimeError):
    pass


def require(condition, message):
    if not condition:
        raise Refusal(message)


def digest(path):
    result = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def verified_signer(status, configured):
    """Accept the exact signing key or its GPG-validated primary-key binding."""
    for line in status.splitlines():
        if not line.startswith(b"[GNUPG:] VALIDSIG "):
            continue
        fields = line.split()[2:]
        if len(fields) < 9:
            continue
        signer = fields[0].decode("ascii").upper()
        identities = {signer}
        if len(fields) >= 10:
            identities.add(fields[9].decode("ascii").upper())
        if configured in identities:
            return signer
    return None


def execute(repository, arguments, data=None, env=None, timeout=30):
    process = subprocess.Popen(
        ["git", "-C", str(repository), *arguments], stdin=subprocess.PIPE,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env,
        start_new_session=True,
    )
    try:
        stdout, stderr = process.communicate(input=data, timeout=timeout)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGTERM)
        try:
            process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.communicate()
        raise Refusal(f"Timed out: git {arguments[0]}; owned process group stopped")
    require(process.returncode == 0,
            f"git {arguments[0]} failed: {stderr.decode(errors='replace').strip()}")
    return stdout, stderr


def snapshot_refs(git):
    return git.text("for-each-ref",
                    "--format=%(refname)\t%(objectname)\t%(objecttype)\t%(symref)")


def commit_data(git, oid):
    raw = git.run("cat-file", "commit", oid)
    header, message = raw.split(b"\n\n", 1)
    fields = []
    for line in header.split(b"\n"):
        if line.startswith(b" "):
            require(bool(fields) and fields[-1][0] == b"gpgsig",
                    f"Unsupported continuation header in {oid}")
            fields[-1][1] += b"\n" + line
        else:
            key, value = line.split(b" ", 1)
            fields.append([key, value])
    require({key for key, _ in fields} <= {
        b"tree", b"parent", b"author", b"committer", b"gpgsig",
    }, f"Unsupported commit headers (encoding/mergetag/etc.) in {oid}")
    return fields, message


def value(fields, name):
    matches = [data for key, data in fields if key == name]
    require(len(matches) == 1, f"Expected exactly one {name!r} header")
    return matches[0]


def identity(environment, prefix, raw):
    match = re.fullmatch(rb"(.*) <([^>]*)> ([0-9]+) ([+-][0-9]{4})", raw)
    require(match is not None, f"Unsupported {prefix} identity format")
    name, email, epoch, zone = match.groups()
    environment[prefix + "_NAME"] = name.decode("utf-8")
    environment[prefix + "_EMAIL"] = email.decode("utf-8")
    environment[prefix + "_DATE"] = (epoch + b" " + zone).decode("ascii")


def check_bundle(git, bundle, expected_hash, branch_ref, old_head):
    require(bundle.is_file() and not bundle.is_symlink(), "Missing/linked recovery bundle")
    require(digest(bundle) == expected_hash, "Recovery bundle SHA-256 mismatch")
    with bundle.open("rb") as handle:
        require(handle.readline().startswith((b"# v2 git bundle", b"# v3 git bundle")),
                "Not a supported Git bundle")
        while True:
            line = handle.readline()
            require(bool(line), "Incomplete bundle header")
            if line == b"\n":
                break
            require(not line.startswith(b"-"),
                    "Incremental bundle is not an independent recovery backup")
    heads = git.text("bundle", "list-heads", str(bundle)).splitlines()
    require(f"{old_head} {branch_ref}" in heads,
            "Recovery bundle does not advertise the exact original branch tip")
    git.run("bundle", "verify", str(bundle))


def preflight(plan_path):
    redirected = [
        name for name in (
            "GIT_DIR", "GIT_COMMON_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE",
            "GIT_NAMESPACE", "GIT_SHALLOW_FILE", "GIT_REPLACE_REF_BASE",
        ) if os.environ.get(name)
    ]
    require(not redirected, "Git environment redirects storage/index: " + ", ".join(redirected))
    plan_path = Path(plan_path).expanduser().resolve(strict=True)
    plan = json.loads(plan_path.read_text())
    require(plan.get("schema") == 1, "Unsupported plan schema")
    git = Git(plan["repository"])
    root = Path(git.text("rev-parse", "--show-toplevel").strip()).resolve()
    require(git.repository == root, "Plan repository must be the checkout root")
    common = Path(git.text("rev-parse", "--path-format=absolute",
                           "--git-common-dir").strip()).resolve()
    git_dir = Path(git.text("rev-parse", "--absolute-git-dir").strip()).resolve()
    for external in (plan_path, Path(plan["backup_bundle"]).expanduser().resolve()):
        require(not external.is_relative_to(root) and not external.is_relative_to(common),
                "Plan and recovery bundle must be outside the checkout/Git storage")
    require(git.text("rev-parse", "--is-bare-repository").strip() == "false",
            "Bare rewrite needs a tailored plan")
    require(git.text("rev-parse", "--show-object-format").strip() == "sha1",
            "Only SHA-1 tree encoding is supported by this helper")
    require(git_dir == common, "Shared/common Git directory needs a tailored plan")
    require(git.text("worktree", "list", "--porcelain").count("worktree ") == 1,
            "Additional worktrees need a coordinated plan")
    require(git.text("rev-parse", "--is-shallow-repository").strip() == "false",
            "Shallow history is not supported")
    require(not (common / "objects/info/alternates").exists()
            and not os.environ.get("GIT_ALTERNATE_OBJECT_DIRECTORIES")
            and not os.environ.get("GIT_OBJECT_DIRECTORY"),
            "Alternate/shared object storage is not supported")
    require(not (common / "info/grafts").exists(), "Grafts are not supported")
    require(not git.run("config", "--get-regexp",
                       r"^(extensions\.partialclone|remote\..*\.promisor)$", optional=True),
            "Partial/promisor repositories need a tailored plan")
    require(not git.run("status", "--porcelain=v1", "-z"),
            "Dirty/untracked worktree or index: preserve owner work and stop")
    require(all(row[:1] == b"H" for row in
                git.run("ls-files", "-v", "-z").split(b"\0") if row),
            "Assume-unchanged/skip-worktree index entries need inspection")
    require(not any(row.startswith(b"160000 ") for row in
                    git.run("ls-tree", "-r", "-z", "HEAD").split(b"\0")),
            "Submodule histories need a tailored plan")
    branch = plan["branch"]
    git.run("check-ref-format", "--branch", branch)
    branch_ref = "refs/heads/" + branch
    require(git.text("symbolic-ref", "-q", "HEAD").strip() == branch_ref,
            "Checked-out branch differs from plan")
    old_head = git.text("rev-parse", "HEAD").strip()
    require(old_head == plan["old_head"], "HEAD moved since owner-reviewed plan")
    upstream = git.text("for-each-ref", "--format=%(upstream)", branch_ref).strip()
    auxiliary = set(plan.get("auxiliary_tree_refs", []))
    refs_before = snapshot_refs(git)
    refs = []
    for row in refs_before.splitlines():
        ref, oid, kind, symref = row.split("\t")
        refs.append((ref, oid, kind, symref))
        if ref == branch_ref:
            require(kind == "commit" and oid == old_head, "Invalid branch ref")
        elif upstream and ref == upstream:
            require(kind == "commit" and oid == old_head,
                    "Upstream tracking ref differs; resolve unpublished/diverged work")
        elif symref and upstream and symref == upstream:
            require(ref.startswith("refs/remotes/"), "Unexpected symbolic ref")
        elif ref in auxiliary:
            require(kind == "tree" and not symref, "Approved auxiliary ref is not a tree")
        else:
            raise Refusal("Unapproved ref requires a retention/rewrite plan: " + ref)
    require(auxiliary <= {ref for ref, _, _, _ in refs}, "Missing auxiliary tree ref")
    key = plan["signing_key"].upper()
    require(bool(re.fullmatch(r"[0-9A-F]{40}|[0-9A-F]{64}", key)),
            "Use a full OpenPGP fingerprint")
    require(git.text("config", "--get", "user.signingkey").strip().upper() == key,
            "Plan fingerprint differs from configured signing identity")
    signing_format = git.text("config", "--get", "gpg.format", optional=True).strip()
    require(signing_format in {"", "openpgp"}, "This helper requires OpenPGP")
    bundle = Path(plan["backup_bundle"]).expanduser().resolve()
    check_bundle(git, bundle, plan["backup_sha256"], branch_ref, old_head)
    bundle_heads = set(git.text("bundle", "list-heads", str(bundle)).splitlines())
    require(all(f"{oid} {ref}" in bundle_heads for ref, oid, _, _ in refs),
            "Recovery bundle is missing one or more original refs")
    protected = set(tree_blobs(git))
    history = object_paths(git, old_head)
    remove = set(plan["remove_blob_ids"])
    require(bool(remove), "Empty removal plan; do not re-sign history gratuitously")
    require(not (protected & remove), "Removal would delete a current-HEAD blob")
    require(remove <= history.keys(), "Selected object is outside branch history")
    for oid in sorted(remove):
        require(bool(re.fullmatch(r"[0-9a-f]{40}", oid)), "Invalid SHA-1 object ID")
        require(git.text("cat-file", "-t", oid).strip() == "blob", "Selected non-blob")
        size = int(git.text("cat-file", "-s", oid))
        require(binary_prefix(git, oid, size) is not None,
                "Selected blob looks like text; use a tailored reviewed plan")
    commits = git.text("rev-list", "--reverse", "--topo-order", old_head).splitlines()
    for oid in commits:
        fields, _ = commit_data(git, oid)
        identity({}, "GIT_AUTHOR", value(fields, b"author"))
        identity({}, "GIT_COMMITTER", value(fields, b"committer"))
    require(not list(common.rglob("*.lock")) and not (common / "gc.pid").exists(),
            "Git lock/GC marker exists; verify owned and concurrent writers")
    git.run("fsck", "--full", "--strict", "--no-progress")
    return {
        "plan": plan, "plan_path": plan_path, "git": git, "root": root,
        "old_head": old_head, "branch_ref": branch_ref, "upstream": upstream,
        "refs": refs, "refs_before": refs_before, "key": key, "bundle": bundle,
        "remove": remove, "protected": protected, "commits": commits,
        "old_tree": git.text("rev-parse", old_head + "^{tree}").strip(),
    }


def apply(context):
    c = context
    git = c["git"]
    report_path = c["plan_path"].with_name("signed-rewrite-result.json")
    require(not report_path.exists() and not report_path.is_symlink(),
            "Existing result: inspect prior attempt, do not overwrite")
    require(not report_path.with_suffix(".tmp").exists()
            and not report_path.with_suffix(".tmp").is_symlink(),
            "Existing temporary result: inspect prior attempt, do not overwrite")
    gpg = git.text("config", "--get", "gpg.openpgp.program", optional=True).strip()
    gpg = gpg or git.text("config", "--get", "gpg.program", optional=True).strip() or "gpg"
    with tempfile.TemporaryDirectory(prefix="signing-preflight-",
                                     dir=c["plan_path"].parent) as temporary:
        signature = Path(temporary) / "check.asc"
        check = subprocess.run(
            [gpg, "--batch", "--no-tty", "--pinentry-mode", "error", "--armor",
             "--local-user", c["key"], "--detach-sign", "--output", str(signature)],
            input=b"Owner-approved Git history rewrite signing preflight\n",
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30,
        )
        require(check.returncode == 0, "Configured GPG key unavailable; stop without fallback")
        verified = subprocess.run(
            [gpg, "--batch", "--status-fd", "1", "--verify", str(signature), "-"],
            input=b"Owner-approved Git history rewrite signing preflight\n",
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30,
        )
        require(verified.returncode == 0
                and verified_signer(verified.stdout, c["key"]) is not None,
                "Signing preflight fingerprint/verification failed")
    trees = {}
    commits = {}
    checks = []
    result = {
        "status": "in-progress", "original_head": c["old_head"],
        "signing_fingerprint": c["key"], "commit_map": commits,
        "tree_map": trees, "signature_checks": checks, "refs_updated": False,
        "push_performed": False, "gc_performed": False,
    }

    def save():
        temporary = report_path.with_suffix(".tmp")
        fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w") as handle:
            json.dump(result, handle, indent=2)
            handle.write("\n")
        temporary.chmod(0o600)
        temporary.replace(report_path)

    def new_tree(oid):
        if oid in trees:
            return trees[oid]
        raw = git.run("cat-file", "tree", oid)
        output = bytearray()
        offset = 0
        while offset < len(raw):
            space = raw.index(b" ", offset)
            nul = raw.index(b"\0", space)
            mode, name = raw[offset:space], raw[space + 1:nul]
            child = raw[nul + 1:nul + 21].hex()
            offset = nul + 21
            replacement = new_tree(child) if mode == b"40000" else child
            if replacement is None or (mode != b"40000" and child in c["remove"]):
                continue
            output.extend(mode + b" " + name + b"\0" + bytes.fromhex(replacement))
        if not output:
            replacement = None
        elif bytes(output) == raw:
            replacement = oid
        else:
            replacement = execute(c["root"], ["hash-object", "-w", "-t", "tree",
                                             "--stdin"], data=bytes(output),
                                  env=git.env)[0].decode().strip()
        trees[oid] = replacement
        return replacement

    def stable():
        require(git.text("rev-parse", "HEAD").strip() == c["old_head"], "HEAD changed")
        require(snapshot_refs(git) == c["refs_before"], "Refs changed during signing")
        require(not git.run("status", "--porcelain=v1", "-z"), "Owner work changed")

    try:
        save()
        empty = execute(c["root"], ["hash-object", "-w", "-t", "tree", "--stdin"],
                        data=b"", env=git.env)[0].decode().strip()
        for old in c["commits"]:
            fields, message = commit_data(git, old)
            tree = new_tree(value(fields, b"tree").decode()) or empty
            parents = [commits[data.decode()] for key, data in fields if key == b"parent"]
            environment = dict(git.env)
            identity(environment, "GIT_AUTHOR", value(fields, b"author"))
            identity(environment, "GIT_COMMITTER", value(fields, b"committer"))
            args = ["commit-tree", "-S" + c["key"], tree]
            for parent in parents:
                args += ["-p", parent]
            new = execute(c["root"], args, data=message, env=environment)[0].decode().strip()
            nf, nm = commit_data(git, new)
            require(nm == message and value(nf, b"author") == value(fields, b"author")
                    and value(nf, b"committer") == value(fields, b"committer"),
                    "Commit metadata/message differs")
            require(value(nf, b"tree").decode() == tree
                    and [v.decode() for k, v in nf if k == b"parent"] == parents,
                    "Commit tree/parent order differs")
            _, verification = execute(c["root"], ["verify-commit", "--raw", new], env=git.env)
            signer = verified_signer(verification, c["key"])
            require(signer is not None
                    and b"[GNUPG:] GOODSIG " in verification,
                    "New signature does not verify with configured fingerprint")
            commits[old] = new
            checks.append({"old": old, "new": new,
                           "verified_configured_fingerprint": c["key"],
                           "actual_signing_fingerprint": signer})
            save()
        tip = commits[c["old_head"]]
        require(git.text("rev-parse", tip + "^{tree}").strip() == c["old_tree"],
                "Current tip tree was not preserved")
        require(int(git.text("rev-list", "--count", tip)) == len(c["commits"]),
                "Commit count changed")
        require(not (set(object_paths(git, tip)) & c["remove"]),
                "Selected blobs remain reachable")
        require(c["protected"] <= object_paths(git, tip).keys(), "Current blob disappeared")
        updates = [(c["branch_ref"], tip, c["old_head"])]
        for ref, old, kind, _ in c["refs"]:
            if ref in c["plan"].get("auxiliary_tree_refs", []):
                replacement = new_tree(old) or empty
                require(not (set(object_paths(git, replacement)) & c["remove"]),
                        "Auxiliary tree still pins selected binary history")
                updates.append((ref, replacement, old))
        stable()
        transaction = "start\n" + "".join(
            f"update {ref} {new} {old}\n" for ref, new, old in updates
        ) + "prepare\ncommit\n"
        execute(c["root"], ["update-ref", "--stdin"], data=transaction.encode(), env=git.env)
        result.update({"refs_updated": True, "new_head": tip,
                       "tip_tree_preserved": c["old_tree"], "ref_updates": updates,
                       "commits_resigned": len(commits)})
        require(git.text("rev-parse", "HEAD").strip() == tip, "Post-update HEAD mismatch")
        require(not git.run("status", "--porcelain=v1", "-z"), "Post-update tree not clean")
        result["status"] = "complete-local-rewrite-not-pushed-or-pruned"
        return result
    except BaseException as error:
        result["status"] = "failed"
        result["error"] = str(error)
        raise
    finally:
        save()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", required=True)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--expected-head")
    parser.add_argument("--ack-rewrite-and-resign", action="store_true")
    args = parser.parse_args()
    try:
        context = preflight(args.plan)
        if not args.apply:
            print(json.dumps({
                "mode": "dry-run; no Git writes/signing/ref changes",
                "old_head": context["old_head"], "branch": context["branch_ref"],
                "commits_to_resign": len(context["commits"]),
                "binary_blob_versions_to_remove": len(context["remove"]),
                "signing_fingerprint": context["key"],
                "external_backup_verified": str(context["bundle"]),
                "tracking_ref_left_until_remote_publication": context["upstream"],
            }, indent=2))
            return 0
        require(args.ack_rewrite_and_resign and args.expected_head == context["old_head"],
                "Apply requires explicit acknowledgement and matching --expected-head")
        result = apply(context)
        print(json.dumps({k: v for k, v in result.items()
                          if k not in {"commit_map", "tree_map", "signature_checks"}}, indent=2))
        return 0
    except (Refusal, AuditError, OSError, ValueError, subprocess.SubprocessError) as error:
        print(json.dumps({"refused_or_failed": str(error)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
