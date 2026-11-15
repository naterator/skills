#!/usr/bin/env python3
"""Read-only Git/object inventory. No deletion, expiry, fetch, ref or config writes."""

import argparse
import codecs
import collections
import json
import os
from pathlib import Path
import subprocess
import sys


class AuditError(RuntimeError):
    pass


class Git:
    def __init__(self, repository):
        self.repository = Path(repository).resolve(strict=True)
        self.env = dict(os.environ, GIT_OPTIONAL_LOCKS="0", LC_ALL="C")
        self.warnings = []

    def run(self, *args, optional=False):
        result = subprocess.run(
            ["git", "-C", str(self.repository), *args], env=self.env,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120,
        )
        if result.stderr.strip():
            self.warnings.append(result.stderr.decode(errors="replace").strip())
        if result.returncode and not optional:
            raise AuditError(f"git {args[0]} failed: "
                             + result.stderr.decode(errors="replace").strip())
        return result.stdout if result.returncode == 0 else b""

    def text(self, *args, **kwargs):
        return self.run(*args, **kwargs).decode("utf-8", errors="surrogateescape")


def object_paths(git, *revisions):
    result = {}
    for row in git.text("rev-list", "--objects", *revisions).splitlines():
        oid, _, path = row.partition(" ")
        result[oid] = path
    return result


def tree_blobs(git, revision="HEAD"):
    result = {}
    for row in git.run("ls-tree", "-r", "-z", revision).split(b"\0"):
        if not row:
            continue
        metadata, path = row.split(b"\t", 1)
        _, kind, oid = metadata.decode().split()
        if kind == "blob":
            result.setdefault(oid, []).append(path.decode(errors="surrogateescape"))
    return result


def allocated_inventory(root):
    logical = allocated = files = 0
    seen = set()
    for directory, dirs, names in os.walk(root, followlinks=False):
        for name in dirs + names:
            path = Path(directory) / name
            info = path.lstat()
            identity = (info.st_dev, info.st_ino)
            if identity in seen:
                continue
            seen.add(identity)
            allocated += getattr(info, "st_blocks", 0) * 512
            if path.is_file() and not path.is_symlink():
                logical += info.st_size
                files += 1
    return {"logical_bytes": logical, "allocated_bytes": allocated, "files": files}


def binary_prefix(git, oid, size):
    process = subprocess.Popen(
        ["git", "-C", str(git.repository), "cat-file", "blob", oid],
        env=git.env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    try:
        prefix = process.stdout.read(min(size, 8192))
        if len(prefix) != min(size, 8192):
            raise AuditError(f"Short blob read: {oid}")
        if b"\0" in prefix:
            result = "NUL byte in first 8192 bytes"
        else:
            try:
                codecs.getincrementaldecoder("utf-8")().decode(prefix, final=False)
                result = None
            except UnicodeDecodeError:
                result = "non-UTF-8 prefix; review possible legacy text encoding"
        return result
    finally:
        process.stdout.close()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=10)
        process.stderr.close()


def audit(repository, classify=False):
    git = Git(repository)
    git_dir = Path(git.text("rev-parse", "--absolute-git-dir").strip())
    common = Path(git.text("rev-parse", "--path-format=absolute",
                           "--git-common-dir").strip())
    bare = git.text("rev-parse", "--is-bare-repository").strip() == "true"
    status = "" if bare else git.text("status", "--porcelain=v1", "-z")
    head = git.text("rev-parse", "--verify", "HEAD").strip()
    refs = []
    for row in git.text("for-each-ref",
                        "--format=%(refname)\t%(objectname)\t%(objecttype)").splitlines():
        ref, oid, kind = row.split("\t")
        refs.append({"ref": ref, "oid": oid, "type": kind})
    objects = {}
    for row in git.text(
        "cat-file", "--batch-all-objects",
        "--batch-check=%(objectname) %(objecttype) %(objectsize) %(objectsize:disk)",
    ).splitlines():
        oid, kind, size, disk = row.split()
        objects[oid] = {"type": kind, "logical_bytes": int(size),
                        "object_disk_bytes": int(disk)}
    current = tree_blobs(git)
    history = object_paths(git, "HEAD")
    all_refs = object_paths(git, "--all")
    reflogs = object_paths(git, "--all", "--reflog")
    reachable_ids = set(history) | set(all_refs) | set(reflogs)
    if reachable_ids - objects.keys():
        raise AuditError("Object inventory incomplete; possible concurrent change")
    groups = {
        "current_HEAD_blobs": set(current),
        "older_HEAD_history_blobs": {
            oid for oid in history if objects[oid]["type"] == "blob"
        } - current.keys(),
        "objects_only_reachable_from_other_refs": set(all_refs) - history.keys(),
        "objects_only_reachable_from_reflogs": set(reflogs) - all_refs.keys(),
        "unreachable_even_from_reflogs": set(objects) - reflogs.keys(),
    }

    def totals(ids):
        return {
            "objects": len(ids),
            "logical_bytes": sum(objects[oid]["logical_bytes"] for oid in ids),
            "object_disk_bytes": sum(objects[oid]["object_disk_bytes"] for oid in ids),
            "types": dict(collections.Counter(objects[oid]["type"] for oid in ids)),
        }

    paths_now = {path for paths in current.values() for path in paths}
    candidates = []
    by_path = collections.defaultdict(lambda: {
        "versions": 0, "logical_bytes": 0, "object_disk_bytes": 0,
    })
    for oid in groups["older_HEAD_history_blobs"]:
        path = history[oid]
        row = {"oid": oid, "path": path, **objects[oid],
               "path_exists_in_HEAD": path in paths_now}
        if classify:
            row["binary_prefix_evidence"] = binary_prefix(
                git, oid, objects[oid]["logical_bytes"])
        candidates.append(row)
        group = by_path[path]
        group["versions"] += 1
        group["logical_bytes"] += row["logical_bytes"]
        group["object_disk_bytes"] += row["object_disk_bytes"]
    candidates.sort(key=lambda row: row["object_disk_bytes"], reverse=True)
    worktrees = git.text("worktree", "list", "--porcelain")
    limitations = []
    checks = {
        "bare": bare,
        "shallow": git.text("rev-parse", "--is-shallow-repository").strip() == "true",
        "multiple_worktrees": worktrees.count("worktree ") != 1,
        "shared_common_directory": git_dir.resolve() != common.resolve(),
        "alternates": (common / "objects/info/alternates").exists()
                      or bool(os.environ.get("GIT_ALTERNATE_OBJECT_DIRECTORIES"))
                      or bool(os.environ.get("GIT_OBJECT_DIRECTORY")),
        "grafts": (common / "info/grafts").exists(),
        "replace_refs": any(ref["ref"].startswith("refs/replace/") for ref in refs),
        "partial_clone": bool(git.run(
            "config", "--get-regexp", r"^(extensions\.partialclone|remote\..*\.promisor)$",
            optional=True)),
    }
    for name, value in checks.items():
        if value:
            limitations.append(name)
    count_raw = git.text("count-objects", "-v")
    if any(line.startswith("garbage: ") and line != "garbage: 0"
           for line in count_raw.splitlines()):
        limitations.append("non-Git garbage needs exact-file inspection")
    if git.text("rev-parse", "--verify", "HEAD").strip() != head:
        raise AuditError("HEAD changed during audit")
    if not bare and git.text("status", "--porcelain=v1", "-z") != status:
        raise AuditError("Working/index state changed during audit")
    refs_after = git.text("for-each-ref",
                          "--format=%(refname)\t%(objectname)\t%(objecttype)")
    expected = "".join(f"{r['ref']}\t{r['oid']}\t{r['type']}\n" for r in refs)
    if refs_after != expected:
        raise AuditError("Refs changed during audit")
    return {
        "schema": 1, "operation": "read-only audit; no cleanup authorized",
        "repository": str(git.repository), "git_directory": str(git_dir),
        "common_directory": str(common), "head": head, "refs": refs,
        "dirty_or_untracked": bool(status), "worktrees": worktrees.splitlines(),
        "capability_warnings": limitations, "topology": checks,
        "git_directory_storage": allocated_inventory(common),
        "object_accounting_note": "Object disk sizes are approximate delta/pack "
                                  "accounting, not a promised reclaimable total.",
        "groups": {name: totals(ids) for name, ids in groups.items()},
        "unreachable_commit_ids": sorted(
            oid for oid in groups["unreachable_even_from_reflogs"]
            if objects[oid]["type"] == "commit"),
        "historical_blob_candidates": candidates,
        "historical_paths": [
            {"path": path, **values}
            for path, values in sorted(
                by_path.items(), key=lambda item: item[1]["object_disk_bytes"],
                reverse=True)],
        "count_objects": count_raw.splitlines(),
        "warnings": list(dict.fromkeys(git.warnings)),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--classify-binaries", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = audit(args.repo, args.classify_binaries)
        serialized = json.dumps(result, indent=2, ensure_ascii=True) + "\n"
        if args.output:
            destination = args.output.expanduser().resolve()
            common = Path(result["common_directory"]).resolve()
            if destination == common or destination.is_relative_to(common):
                raise AuditError("Refuse to write an audit report inside Git storage")
            fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(fd, "w") as handle:
                handle.write(serialized)
            print(json.dumps({"report": str(destination), "head": result["head"]}))
        else:
            print(serialized, end="")
    except (AuditError, OSError, subprocess.SubprocessError) as error:
        print(json.dumps({"error": str(error), "audit_complete": False}), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
