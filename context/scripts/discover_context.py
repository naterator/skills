#!/usr/bin/env python3
"""Read-only Context content inventory, excluding Git metadata; never chooses a destination."""
import argparse
import datetime
import difflib
import json
from pathlib import Path
import re
import stat
import unicodedata

DEFAULT_ROOT = Path.home() / 'Documents' / 'Context'
SLUG_PATTERN = r'[a-z0-9]+(?:-[a-z0-9]+)*'
TEXT_SUFFIXES = {'.md', '.markdown', '.txt', '.rst', '.py', '.sh', '.js', '.ts',
                 '.tsx', '.jsx', '.json', '.jsonl', '.yaml', '.yml', '.toml',
                  '.csv', '.xml', '.html', '.css', '.sql', '.rsc', '.ini', '.cfg', '.log'}
INFRASTRUCTURE_DIRS = {'.skills', '.opencode', '.claude', '.agents'}
ROOT_METADATA = {'AGENTS.md', 'README.md', 'CHANGELOG.md', 'CLAUDE.md', 'GEMINI.md',
                 '.gitignore', '.DS_Store'}
ROLES = {
    'topic-content': 'Potential subject evidence; review scope before selecting a destination.',
    'collection-content': 'Standalone root notes/inventories; review relevance, not a subject folder.',
    'collection-metadata': 'Root catalogue/configuration; a locator, not a subject folder.',
    'infrastructure': 'Skill or agent machinery; not subject evidence by itself.',
    'test-example': 'Infrastructure tests/examples; synthetic names are not saved subjects.',
}


def content_role(parts, is_directory=False):
    if parts and parts[0] in INFRASTRUCTURE_DIRS:
        if any(part in {'tests', 'evals', 'fixtures'} for part in parts[1:]):
            return 'test-example'
        return 'infrastructure'
    if not parts:
        return 'collection-metadata'
    if len(parts) == 1 and not is_directory:
        return 'collection-metadata' if parts[0] in ROOT_METADATA else 'collection-content'
    return 'topic-content'


def normalize(value):
    ascii_text = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', ' ', ascii_text).strip()


def slugify(value):
    return normalize(value).replace(' ', '-')


def search_text(value, queries):
    normalized = normalize(value)
    words = set(normalized.split())
    hits = []
    for query in queries:
        phrase = normalize(query)
        tokens = set(phrase.split())
        if phrase and (phrase in normalized or tokens <= words):
            hits.append({'query': query, 'phrase_match': phrase in normalized,
                         'all_query_words_present': tokens <= words})
    return hits


def discover(root, topic, aliases=()):
    root = root.expanduser().absolute()
    proposed = slugify(topic)
    if not re.fullmatch(SLUG_PATTERN, proposed):
        raise ValueError('Topic yields no ASCII slug; ask the user for a canonical topic name')
    queries = list(dict.fromkeys([topic, *aliases]))
    result = {
        'root': str(root), 'topic': topic, 'proposed_slug': proposed, 'queries': queries,
        'scanned_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'root_exists': False, 'inventory_complete': True,
        'directories': [], 'files': [], 'links': [], 'errors': [], 'directory_candidates': [],
        'excluded_paths': [],
        'content_roles': ROLES.copy(),
        'interpretation': 'Lexical discovery, not a duplicate decision. Review scope semantically; '
                           'infrastructure/test-example matches do not establish a saved subject. '
                           'Ask the user whenever new versus duplicate is unclear.',
    }

    def error(path, message):
        result['inventory_complete'] = False
        result['errors'].append({'path': str(path), 'error': message})

    visited_dirs, visited_files = set(), set()

    def relative(path):
        return str(path.relative_to(root))

    def visit(path):
        # Check every relative component, including resolved internal symlink targets.
        # A differently named alias into .git must not reintroduce repository history.
        if '.git' in path.relative_to(root).parts:
            result['excluded_paths'].append({'path': relative(path), 'reason': 'Git metadata'})
            return
        try:
            meta = path.lstat()
            if stat.S_ISLNK(meta.st_mode):
                link = {'path': relative(path), 'target': str(path.readlink())}
                result['links'].append(link)
                try:
                    target = path.resolve(strict=True)
                except (OSError, RuntimeError) as exc:
                    error(path, 'Unresolved symlink: ' + str(exc))
                    return
                link['resolved_target'] = str(target)
                if not target.is_relative_to(root):
                    error(path, 'Symlink leaves Context root; review destination scope before following')
                    return
                if '.git' in target.relative_to(root).parts:
                    link['coverage'] = 'excluded Git metadata'
                else:
                    link['role'] = content_role(target.relative_to(root).parts, target.is_dir())
                visit(target)
                return
            if stat.S_ISDIR(meta.st_mode):
                if path in visited_dirs:
                    return
                visited_dirs.add(path)
                rel = relative(path)
                role = content_role(path.relative_to(root).parts, is_directory=True)
                result['directories'].append(rel)
                if role == 'topic-content':
                    canonical = slugify(path.name)
                    similarity = difflib.SequenceMatcher(None, proposed, canonical).ratio()
                    hits = search_text(rel, queries)
                    overlap = sorted(set(proposed.split('-')) & set(canonical.split('-')))
                    if canonical == proposed or similarity >= 0.60 or hits or overlap:
                        result['directory_candidates'].append({
                            'path': rel, 'role': role, 'name_matches_slug': canonical == proposed,
                            'normalized_name': canonical, 'name_similarity': round(similarity, 3),
                            'shared_name_tokens': overlap, 'query_hits': hits})
                for child in sorted(path.iterdir(), key=lambda p: p.name):
                    visit(child)
                return
            if not stat.S_ISREG(meta.st_mode):
                result['files'].append({
                    'path': relative(path), 'kind': 'special', 'bytes': meta.st_size,
                    'role': content_role(path.relative_to(root).parts)})
                error(path, 'Special filesystem entry; content not searched')
                return
            if path in visited_files:
                return
            visited_files.add(path)
            item = {'path': relative(path), 'bytes': meta.st_size,
                    'role': content_role(path.relative_to(root).parts),
                    'name_hits': search_text(relative(path), queries)}
            result['files'].append(item)
            with path.open('rb') as stream:
                prefix = stream.read(8192)
            utf16 = prefix.startswith((b'\xff\xfe', b'\xfe\xff'))
            if b'\0' in prefix and not utf16:
                item.update(kind='non-text', coverage='name/location only')
                if path.suffix.lower() in TEXT_SUFFIXES:
                    error(path, 'Expected text has binary NULs; inspect before claiming complete coverage')
                return
            try:
                text = path.read_text(encoding='utf-16' if utf16 else 'utf-8-sig')
            except UnicodeError:
                item.update(kind='non-text-or-unsupported-encoding', coverage='name/location only')
                if path.suffix.lower() in TEXT_SUFFIXES:
                    error(path, 'Expected text has unsupported encoding; inspect rather than skipping')
                return
            item.update(kind='text', coverage='full text searched', content_hits=search_text(text, queries))
            lines = text.splitlines()
            item['headings'] = [line.strip()[:240] for line in lines if re.match(r'^#{1,6}\s', line)][:12]
            if item['content_hits']:
                samples = []
                for number, line in enumerate(lines, 1):
                    if search_text(line, queries):
                        samples.append({'line': number, 'text': line.strip()[:400]})
                        if len(samples) == 4:
                            break
                item['sample_matching_lines'] = samples
        except OSError as exc:
            error(path, str(exc))

    try:
        result['root_exists'] = root.exists()
        if root.is_symlink():
            error(root, 'Context root is a symlink; confirm the resolved root and rerun explicitly')
        elif not result['root_exists']:
            error(root, 'Context root does not exist or is inaccessible; no content was scanned')
        elif not root.is_dir():
            error(root, 'Context root is not a directory')
        else:
            root = root.resolve(strict=True)
            result['root'] = str(root)
            visit(root)
    except (OSError, RuntimeError) as exc:
        error(root, 'Context root could not be inspected: ' + str(exc))
    result['directory_candidates'].sort(
        key=lambda x: (not x['name_matches_slug'], -x['name_similarity'], x['path']))
    result['summary'] = {
        'directories': len(result['directories']), 'files': len(result['files']),
        'full_text_files': sum(f.get('kind') == 'text' for f in result['files']),
        'non_text_or_special_files': sum(f.get('kind') != 'text' for f in result['files']),
        'matching_files': sum(bool(f.get('name_hits') or f.get('content_hits')) for f in result['files']),
        'matching_files_by_role': {
            role: sum(bool(f.get('name_hits') or f.get('content_hits'))
                      for f in result['files'] if f['role'] == role)
            for role in ROLES},
        'links': len(result['links']), 'errors': len(result['errors']),
        'excluded_paths': len(result['excluded_paths']),
    }
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=DEFAULT_ROOT,
                        help='Collection root (default: ~/Documents/Context); pass explicitly for alternative roots/fixtures')
    parser.add_argument('--topic', required=True)
    parser.add_argument('--query', action='append', default=[], help='Alias or broader term; repeat as needed')
    args = parser.parse_args(argv)
    try:
        result = discover(args.root, args.topic, args.query)
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result['inventory_complete'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
