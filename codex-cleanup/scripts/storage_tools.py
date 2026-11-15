#!/usr/bin/env python3
"""Read-only inventory and preservation evidence; never removes source data."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import pickle
import sqlite3
import sys


def home_path(value):
    path = Path(value or os.environ.get('CODEX_HOME', '~/.codex')).expanduser().resolve()
    if not path.is_dir():
        raise ValueError(f'Codex home is not an existing directory: {path}')
    return path


def quote(name):
    return '"' + name.replace('"', '""') + '"'


def digest_prefix(path, length):
    digest = hashlib.sha256()
    remaining = length
    with path.open('rb') as f:
        while remaining:
            data = f.read(min(4 * 1024 * 1024, remaining))
            if not data:
                raise ValueError(f'Protected file was truncated: {path}')
            remaining -= len(data)
            digest.update(data)
    return digest.hexdigest()


def source_files(root):
    def traversal_error(error):
        raise error

    for folder in ['sessions', 'archived_sessions']:
        base = root / folder
        if base.is_symlink():
            raise ValueError(f'Protected directory is a symlink; inspect it separately: {base}')
        if not base.exists():
            continue
        for current, dirs, files in os.walk(base, followlinks=False, onerror=traversal_error):
            if any((Path(current) / name).is_symlink() for name in dirs + files):
                raise ValueError(f'Symlink in protected analysis tree: {current}')
            for name in sorted(files):
                yield Path(current) / name
    for name in ['history.jsonl', 'session_index.jsonl']:
        path = root / name
        if path.is_symlink():
            raise ValueError(f'Protected index is a symlink: {path}')
        if path.is_file():
            yield path


def snapshot_files(root):
    records = []
    for path in source_files(root):
        size = path.stat().st_size
        records.append({'relative_path': str(path.relative_to(root)), 'bytes': size,
                        'sha256': digest_prefix(path, size)})
    return {'codex_home': str(root), 'files': records, 'file_count': len(records)}


def verify_files(root, manifest):
    if Path(manifest['codex_home']).resolve() != root:
        raise ValueError('Manifest belongs to a different Codex home')
    moves = []
    failures = []
    index = None
    for record in manifest['files']:
        relative = Path(record['relative_path'])
        if relative.is_absolute() or '..' in relative.parts:
            raise ValueError('Manifest contains an invalid relative path')
        path = root / relative
        if not path.exists():
            if relative.parts[0] not in ['sessions', 'archived_sessions']:
                failures.append({'path': str(relative), 'reason': 'missing index'})
                continue
            if index is None:
                index = {}
                for candidate in source_files(root):
                    if candidate.relative_to(root).parts[0] in ['sessions', 'archived_sessions']:
                        index.setdefault(candidate.name, []).append(candidate)
            candidates = index.get(path.name, [])
            if len(candidates) != 1:
                failures.append({'path': str(relative), 'reason': 'missing or ambiguous relocated file'})
                continue
            path = candidates[0]
            moves.append({'from': str(relative), 'to': str(path.relative_to(root))})
        if not path.resolve().is_relative_to(root) or path.is_symlink():
            raise ValueError(f'Protected path resolves outside Codex home or is a symlink: {path}')
        try:
            if path.stat().st_size < record['bytes'] or digest_prefix(path, record['bytes']) != record['sha256']:
                failures.append({'path': str(relative), 'reason': 'existing content changed or truncated'})
        except (OSError, ValueError) as exc:
            failures.append({'path': str(relative), 'reason': str(exc)})
    return {'preserved': not failures, 'files_checked': len(manifest['files']),
            'moves': moves, 'failures': failures}


def fingerprint_db(path):
    # Do not use immutable here: preservation proof must include committed WAL.
    con = sqlite3.connect(path.as_uri() + '?mode=ro', uri=True, timeout=10)
    try:
        con.execute('PRAGMA query_only=ON')
        con.execute('BEGIN')
        schema = list(con.execute("SELECT type,name,tbl_name,sql FROM sqlite_master WHERE sql IS NOT NULL ORDER BY type,name"))
        result = {'schema_sha256': hashlib.sha256(pickle.dumps(schema, protocol=4)).hexdigest(), 'tables': {}}
        names = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
        for name in names:
            columns = list(con.execute('PRAGMA table_info(' + quote(name) + ')'))
            keys = [r[1] for r in sorted(columns, key=lambda r: r[5]) if r[5]]
            ordering = ','.join(quote(k) for k in (keys or [r[1] for r in columns]))
            digest = hashlib.sha256()
            count = 0
            for row in con.execute('SELECT * FROM ' + quote(name) + ' ORDER BY ' + ordering):
                content = pickle.dumps(tuple(row), protocol=4)
                digest.update(len(content).to_bytes(8, 'big'))
                digest.update(content)
                count += 1
            result['tables'][name] = {'rows': count, 'sha256': digest.hexdigest()}
        counters = None
        if 'threads' in names:
            cols = {r[1] for r in con.execute('PRAGMA table_info(threads)')}
            if {'archived', 'tokens_used'} <= cols:
                counters = list(con.execute('SELECT count(*),sum(archived),sum(tokens_used) FROM threads').fetchone())
        return {'database': str(path), 'includes_committed_wal': True, 'fingerprint': result,
                'thread_statistics': counters, 'quick_check': [r[0] for r in con.execute('PRAGMA quick_check')],
                'foreign_key_violations': [list(r) for r in con.execute('PRAGMA foreign_key_check')]}
    finally:
        con.close()


def audit(root):
    groups = {}
    largest = []
    errors = []
    def traversal_error(error):
        errors.append({'path': error.filename, 'error': str(error)})

    for current, dirs, names in os.walk(root, followlinks=False, onerror=traversal_error):
        for name in names:
            path = Path(current) / name
            if path.is_symlink():
                continue
            try:
                stat = path.stat()
                key = path.relative_to(root).parts[0]
                group = groups.setdefault(key, {'files': 0, 'logical_bytes': 0, 'allocated_bytes': 0})
                group['files'] += 1
                group['logical_bytes'] += stat.st_size
                group['allocated_bytes'] += getattr(stat, 'st_blocks', 0) * 512
                largest.append({'path': str(path), 'logical_bytes': stat.st_size,
                                'allocated_bytes': getattr(stat, 'st_blocks', 0) * 512})
            except OSError as exc:
                errors.append({'path': str(path), 'error': str(exc)})
    databases = []
    candidates = list(root.glob('*.sqlite')) + list((root / 'state/plugins').glob('*/*.sqlite3'))
    for path in sorted(candidates):
        if path.is_symlink():
            continue
        item = {'database': str(path), 'snapshot_ignores_wal': True,
                'wal_bytes': Path(str(path) + '-wal').stat().st_size if Path(str(path) + '-wal').exists() else 0}
        try:
            con = sqlite3.connect(path.as_uri() + '?mode=ro&immutable=1', uri=True)
            try:
                for key in ['page_size', 'page_count', 'freelist_count']:
                    item[key] = con.execute('PRAGMA ' + key).fetchone()[0]
                item['unused_main_file_bytes'] = item['page_size'] * item['freelist_count']
            finally:
                con.close()
        except sqlite3.Error as exc:
            item['error'] = str(exc)
        databases.append(item)
    runtime = root / 'packages/app-server-daemon'
    current = runtime / 'current'
    marker = runtime / 'auto-update-version'
    return {'codex_home': str(root), 'inventory_complete': not errors,
            'total_allocated_bytes': sum(v['allocated_bytes'] for v in groups.values()),
            'groups': dict(sorted(groups.items(), key=lambda x: x[1]['allocated_bytes'], reverse=True)),
            'largest_files': sorted(largest, key=lambda x: x['allocated_bytes'], reverse=True)[:20],
            'databases': databases, 'errors': errors,
            'runtimes': {'current': str(current.resolve()) if current.exists() else None,
                         'update_marker': marker.read_text().strip() if marker.is_file() else None,
                         'releases': sorted(p.name for p in (runtime / 'releases').iterdir()) if (runtime / 'releases').is_dir() else []}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for command in ['audit', 'snapshot-files', 'verify-files']:
        p = sub.add_parser(command)
        p.add_argument('--home')
        p.add_argument('--out', required=True)
        if command == 'verify-files':
            p.add_argument('--manifest', required=True)
    p = sub.add_parser('fingerprint-db')
    p.add_argument('--home')
    p.add_argument('--database', required=True)
    p.add_argument('--out', required=True)
    args = parser.parse_args()
    output = Path(args.out).expanduser().resolve()
    root = home_path(args.home)
    if output.is_relative_to(root):
        raise ValueError('Write evidence outside Codex home so protected data cannot be overwritten')
    if output.suffix.lower() != '.json':
        raise ValueError('Evidence output must have a .json extension')
    if args.command == 'fingerprint-db':
        path = Path(args.database).expanduser().resolve()
        if not path.is_file() or output == path or str(output).startswith(str(path) + '-'):
            raise ValueError('Database must exist and output must not overwrite its database or journal files')
        result = fingerprint_db(path)
    else:
        if args.command == 'audit':
            result = audit(root)
        elif args.command == 'snapshot-files':
            result = snapshot_files(root)
        else:
            result = verify_files(root, json.loads(Path(args.manifest).read_text()))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'command': args.command, 'output': str(output), 'preserved': result.get('preserved')}, indent=2))
    if result.get('preserved') is False:
        return 1
    if result.get('inventory_complete') is False:
        print('Error: inventory is incomplete; reported totals are lower bounds, not a cleanup plan', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError, sqlite3.Error) as exc:
        print(f'Error: {exc}', file=sys.stderr)
        sys.exit(2)
