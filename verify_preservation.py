"""Verify preserved files and extracted ZIP members without executing source code."""

import hashlib
import json
from pathlib import Path, PurePosixPath
import stat
import subprocess
import sys
import zipfile


ROOT = Path(__file__).resolve().parents[2]


def local_path(value):
    path = ROOT / value
    if not path.resolve().is_relative_to(ROOT) or path.is_symlink():
        raise ValueError(f'Unsafe repository path: {value}')
    return path


def verify():
    preservation = json.loads((ROOT / 'AnalyseFuture/migration-records/preservation-manifest.json').read_text())
    records = subprocess.check_output(
        ['git', 'ls-tree', '-r', '-z', preservation['baseline_commit']], cwd=ROOT)
    baseline = {}
    for record in records.split(b'\0'):
        if record:
            metadata, path = record.split(b'\t', 1)
            mode, kind, oid = metadata.decode().split()
            if kind != 'blob':
                raise ValueError(f'Unexpected baseline object: {path.decode()}')
            baseline[path.decode()] = (mode, oid)
    declared = {item['original_path'] for item in preservation['files']}
    if declared != set(baseline):
        raise ValueError('Preservation manifest does not cover the exact baseline Git tree')
    records = subprocess.check_output(['git', 'ls-files', '--stage', '-z'], cwd=ROOT)
    tracked = {}
    for record in records.split(b'\0'):
        if record:
            metadata, path = record.split(b'\t', 1)
            mode, oid, stage = metadata.decode().split()
            if stage != '0':
                raise ValueError('Resolve Git index conflicts before verification')
            tracked[path.decode()] = (mode, oid)

    oids = list(dict.fromkeys(oid for _, oid in baseline.values()))
    batch = subprocess.run(
        ['git', 'cat-file', '--batch'], cwd=ROOT,
        input=('\n'.join(oids) + '\n').encode(),
        stdout=subprocess.PIPE, check=True).stdout
    blobs = {}
    offset = 0
    for oid in oids:
        end = batch.index(b'\n', offset)
        header = batch[offset:end].split()
        if len(header) != 3 or header[:2] != [oid.encode(), b'blob']:
            raise ValueError('Unexpected Git batch object')
        size = int(header[2])
        start = end + 1
        data = batch[start:start + size]
        if len(data) != size or batch[start + size:start + size + 1] != b'\n':
            raise ValueError('Truncated Git batch object')
        blobs[oid] = (hashlib.sha256(data).hexdigest(), size)
        offset = start + size + 1

    seen = set()
    destinations_preserved = set()
    for item in preservation['files']:
        original = item['original_path']
        if original in seen:
            raise ValueError(f'Duplicate baseline path: {original}')
        seen.add(original)
        destination = item['preserved_path']
        if destination in destinations_preserved:
            raise ValueError(f'Duplicate preserved destination: {destination}')
        destinations_preserved.add(destination)
        mode, oid = baseline[original]
        if (item['git_mode'], item['git_blob_oid']) != (mode, oid):
            raise ValueError(f'Baseline Git metadata mismatch: {original}')
        if (item['git_blob_sha256'], item['git_blob_bytes']) != blobs[oid]:
            raise ValueError(f'Baseline Git content hash mismatch: {original}')
        if tracked.get(destination) != (mode, oid):
            raise ValueError(f'Preserved Git blob/mode not tracked: {destination}')
        path = local_path(item['preserved_path'])
        data = path.read_bytes()
        if len(data) != item['bytes'] or hashlib.sha256(data).hexdigest() != item['sha256']:
            raise ValueError(f'Preserved content changed: {path.relative_to(ROOT)}')
        if item['git_mode'] == '100755' and not path.stat().st_mode & 0o111:
            raise ValueError(f'Executable flag missing: {path.relative_to(ROOT)}')
    print(f"PASS: all {len(seen)} baseline files preserved and tracked from {preservation['baseline_commit'][:7]}")

    index = json.loads((ROOT / 'archives/source-index.json').read_text())
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
                relative = str(PurePosixPath(*parts[1:]))
                destination = item.get('member_paths', {}).get(
                    relative, str(base.relative_to(ROOT) / Path(*parts[1:])))
                path = local_path(destination)
                if path in destinations:
                    raise ValueError(f'Duplicate extracted path: {path.relative_to(ROOT)}')
                destinations.add(path)
                expected.add(path)
                if path.read_bytes() != source.read(member):
                    raise ValueError(f'Extracted content differs: {path.relative_to(ROOT)}')
            # Active docs/manifests can have repaired references. The member map
            # selects exact pre-edit originals; generated dependencies are not
            # recursively traversed or treated as application input.
            if len(expected) != item['files']:
                raise ValueError(f'Archive file count mismatch: {item["archive"]}')
            total += len(expected)
    print(f'PASS: {len(index)} original archives and {total} extracted files match byte-for-byte')


if __name__ == '__main__':
    try:
        verify()
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError, zipfile.BadZipFile) as error:
        print(f'FAIL: {error}', file=sys.stderr)
        sys.exit(1)
