"""Verify preserved files and extracted ZIP members without executing source code."""

import hashlib
import json
from pathlib import Path, PurePosixPath
import stat
import sys
import zipfile


ROOT = Path(__file__).resolve().parent.parent


def local_path(value):
    path = ROOT / value
    if not path.resolve().is_relative_to(ROOT) or path.is_symlink():
        raise ValueError(f'Unsafe repository path: {value}')
    return path


def verify():
    preservation = json.loads((ROOT / 'docs/preservation-manifest.json').read_text())
    seen = set()
    for item in preservation['files']:
        original = item['original_path']
        if original in seen:
            raise ValueError(f'Duplicate baseline path: {original}')
        seen.add(original)
        path = local_path(item['preserved_path'])
        data = path.read_bytes()
        if len(data) != item['bytes'] or hashlib.sha256(data).hexdigest() != item['sha256']:
            raise ValueError(f'Preserved content changed: {path.relative_to(ROOT)}')
        if item['git_mode'] == '100755' and not path.stat().st_mode & 0o111:
            raise ValueError(f'Executable flag missing: {path.relative_to(ROOT)}')
    print(f"PASS: all {len(seen)} baseline files preserved from {preservation['baseline_commit'][:7]}")

    index = json.loads((ROOT / 'sources/archives.json').read_text())
    total = 0
    destinations = set()
    for item in index:
        archive = local_path(item['archive'])
        if hashlib.sha256(archive.read_bytes()).hexdigest() != item['sha256']:
            raise ValueError(f'Archive hash mismatch: {item["archive"]}')
        base = local_path(item['directory'])
        with zipfile.ZipFile(archive) as source:
            members = source.infolist()
            if source.testzip() is not None:
                raise ValueError(f'Invalid ZIP CRC: {item["archive"]}')
            prefixes = {PurePosixPath(member.filename).parts[0] for member in members}
            if len(prefixes) != 1:
                raise ValueError(f'Unexpected ZIP roots: {item["archive"]}')
            expected = set()
            for member in members:
                parts = PurePosixPath(member.filename).parts
                if (member.filename.startswith('/') or '..' in parts
                        or stat.S_ISLNK(member.external_attr >> 16)):
                    raise ValueError(f'Unsafe ZIP member: {member.filename}')
                if member.is_dir():
                    continue
                path = local_path(str(base.relative_to(ROOT) / Path(*parts[1:])))
                if path in destinations:
                    raise ValueError(f'Duplicate extracted path: {path.relative_to(ROOT)}')
                destinations.add(path)
                expected.add(path)
                if path.read_bytes() != source.read(member):
                    raise ValueError(f'Extracted content differs: {path.relative_to(ROOT)}')
            actual = {path for path in base.rglob('*') if path.is_file()
                      and '__pycache__' not in path.relative_to(base).parts}
            extras = actual - expected
            if extras:
                names = ', '.join(str(path.relative_to(ROOT)) for path in sorted(extras))
                raise ValueError(f'Unindexed component files: {names}')
            if len(expected) != item['files']:
                raise ValueError(f'Archive file count mismatch: {item["archive"]}')
            total += len(expected)
    print(f'PASS: {len(index)} original archives and {total} extracted files match byte-for-byte')


if __name__ == '__main__':
    try:
        verify()
    except (OSError, ValueError, KeyError, zipfile.BadZipFile) as error:
        print(f'FAIL: {error}', file=sys.stderr)
        sys.exit(1)
