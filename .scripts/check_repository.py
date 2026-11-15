#!/usr/bin/env python3
"""Offline source-tree checks; never execute skills, access apps, or fetch URLs.

This is a heuristic guard, not proof of anonymity or a full YAML parser.
Findings contain locations/categories, never the matched private value.
"""
import argparse
import ast
import importlib.util
import json
from pathlib import Path
import re
import sys
import sysconfig
from urllib.parse import unquote


PATTERNS = {
    "personal-home-path": re.compile(
        r"/(?:Users|home)/(?!USER(?:/|\b)|username(?:/|\b)|example(?:/|\b))"
        r"[A-Za-z0-9_.-]+/"),
    "credential-token": re.compile(
        r"-----BEGIN (?:[A-Z ]*PRIVATE KEY)|"
        r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|"
        r"sk-[A-Za-z0-9_-]{20,}|AKIA[A-Z0-9]{16})\b"),
    "credential-url": re.compile(r"https?://[^\s/@]+:[^\s/@]+@"),
}
EMAIL = re.compile(r"\b[\w.+-]+@([\w.-]+\.[A-Za-z]{2,})\b")
EXAMPLE_DOMAINS = {"example.com", "example.org", "example.net"}
ARTIFACT_NAMES = {".DS_Store", ".env", "Thumbs.db"}
ARTIFACT_DIRS = {"__pycache__", ".pytest_cache", ".site-backups"}
MAINTENANCE_CHANGELOG_NAMES = {
    "changelog", "changelog.md", "changelog.rst", "changelog.txt",
}


def findings_in_text(text, private_terms=()):
    results = []
    for number, line in enumerate(text.splitlines(), 1):
        for category, pattern in PATTERNS.items():
            if pattern.search(line):
                results.append((category, number))
        for match in EMAIL.finditer(line):
            domain = match.group(1).lower()
            reserved = domain in EXAMPLE_DOMAINS or any(
                domain.endswith("." + suffix)
                for suffix in (*EXAMPLE_DOMAINS, "invalid", "test", "example"))
            if not reserved:
                results.append(("email-needs-review", number))
        if any(term.casefold() in line.casefold() for term in private_terms if term):
            results.append(("private-term", number))
    return results


def is_stdlib(name):
    if name in getattr(sys, "stdlib_module_names", sys.builtin_module_names):
        return True
    # Python 3.9 fallback. Resolving a top-level spec does not import the module.
    try:
        spec = importlib.util.find_spec(name)
    except (ImportError, ValueError):
        return False
    if spec is None:
        return False
    if spec.origin in {"built-in", "frozen"}:
        return True
    if not spec.origin:
        return False
    origin = Path(spec.origin).resolve()
    stdlib = Path(sysconfig.get_path("stdlib")).resolve()
    return origin.is_relative_to(stdlib) and not any(
        part in {"site-packages", "dist-packages"} for part in origin.parts)


def audit(root, private_terms=()):
    root = Path(root).resolve()
    findings = []
    counts = {"files": 0, "skills": 0, "python_files": 0, "local_links": 0}
    skills = set()
    skill_roots = {path.parent.name: path.parent.resolve()
                   for path in root.glob("*/SKILL.md")}

    def record(category, relative, line=None):
        item = {"category": category, "path": str(relative)}
        if line is not None:
            item["line"] = line
        findings.append(item)

    # A Git worktree pointer is also excluded. No Git history or live data is read.
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if ".git" in relative.parts:
            continue
        if path.is_symlink():
            record("symlink-needs-review", relative)
            continue
        if any(part in ARTIFACT_DIRS for part in relative.parts):
            if path.is_dir() and path.name in ARTIFACT_DIRS:
                record("runtime-artifact", relative)
            continue
        if not path.is_file():
            continue
        counts["files"] += 1
        if (len(relative.parts) == 2 and relative.parts[0] in skill_roots
                and path.name.casefold() in MAINTENANCE_CHANGELOG_NAMES):
            record("per-skill-maintenance-changelog", relative)
        if path.name in ARTIFACT_NAMES or (
                path.name.startswith(".env.") and path.name != ".env.example"):
            record("machine-or-private-artifact", relative)
        for category, _ in findings_in_text(str(relative), private_terms):
            record(category, relative)
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            record("unreadable-or-binary-needs-review", relative)
            continue
        for category, line in findings_in_text(text, private_terms):
            record(category, relative, line)
        if path.name == "SKILL.md":
            counts["skills"] += 1
            if path.parent.parent == root:
                skills.add(path.parent.name)
            front = re.match(r"\A---\n(.*?)\n---(?:\n|$)", text, re.S)
            if not front:
                record("missing-frontmatter", relative)
            else:
                name = re.search(r"^name:\s*([^\n]+)", front.group(1), re.M)
                if not name or name.group(1).strip(" '\"") != path.parent.name:
                    record("skill-name-mismatch", relative)
                if not re.search(r"^description:", front.group(1), re.M):
                    record("missing-description", relative)
            if "## Dependencies and portability\n" not in text:
                record("missing-dependency-disclosure", relative)
            if "## Dependency preflight\n" not in text:
                record("missing-dependency-preflight", relative)
        if path.suffix == ".md":
            prose = re.sub(r"^```.*?^```[^\n]*", "", text, flags=re.M | re.S)
            for target in re.findall(r"!?\[[^\]]*\]\(([^)\n]+)\)", prose):
                target = target.split(' "')[0].strip("<>")
                if re.match(r"^[a-zA-Z][\w+.-]*:", target):
                    continue
                if target.startswith(("#", "/", "~")):
                    continue
                local = unquote(target.split("#")[0])
                if local:
                    counts["local_links"] += 1
                    resolved = (path.parent / local).resolve()
                    if not resolved.is_relative_to(root):
                        record("link-outside-repository", relative)
                    elif not resolved.exists():
                        record("missing-local-link", relative)
                    elif relative.parts[0] in skill_roots and not resolved.is_relative_to(
                            skill_roots[relative.parts[0]]):
                        record("resource-outside-skill", relative)
        first_line = text.splitlines()[0] if text else ""
        python_shebang = first_line.startswith("#!") and bool(
            re.search(r"\bpython(?:3(?:\.\d+)?)?(?:\s|$)", first_line))
        if path.suffix == ".py" or python_shebang:
            counts["python_files"] += 1
            try:
                tree = ast.parse(text, filename=str(relative))
            except SyntaxError as error:
                record("python-syntax", relative, error.lineno)
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    names = [alias.name.split(".")[0] for alias in node.names]
                elif isinstance(node, ast.ImportFrom) and not node.level:
                    names = [node.module.split(".")[0]] if node.module else []
                else:
                    continue
                for name in names:
                    bundled = (path.parent / (name + ".py")).is_file() or (
                        path.parent / name / "__init__.py").is_file()
                    if not bundled and not is_stdlib(name):
                        record("nonstdlib-import-needs-review", relative, node.lineno)
    readme = root / "README.md"
    if readme.is_file() and not readme.is_symlink():
        indexed = set(re.findall(r"\]\(([^/\s]+)/SKILL\.md\)", readme.read_text()))
        if indexed != skills:
            record("skill-index-mismatch", "README.md")
    return {"scope": "current-source-tree-only", "counts": counts,
            "findings": findings}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--deny-file", type=Path,
                        help="Private UTF-8 literal terms, one per line, outside the repository")
    args = parser.parse_args()
    root = args.root.resolve()
    if not root.is_dir():
        parser.error("--root must be an existing directory")
    terms = ()
    if args.deny_file is not None:
        deny_file = args.deny_file.resolve()
        if deny_file.is_relative_to(root):
            parser.error("keep private search terms outside the repository")
        terms = tuple(line.strip() for line in deny_file.read_text().splitlines()
                      if line.strip())
    result = audit(root, terms)
    print(json.dumps(result, indent=2))
    return 1 if result["findings"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
