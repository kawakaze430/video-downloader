#!/usr/bin/env bash
set -euo pipefail
setup_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_dir="$(cd -- "$setup_dir/../.." && pwd)"
cd -- "$repo_dir"
python3 - <<'PY'
import shutil
import sys
if sys.version_info < (3, 10):
    raise SystemExit('Python 3.10+ required')
if not shutil.which('openssl'):
    raise SystemExit('OpenSSL CLI required for verified HTTPS fixture tests')
PY
python3 tools/verify_repository.py
cd -- "$repo_dir/sources/downloader-blueprint"
python3 -m unittest discover -s tests -v
python3 -m compileall -q tools tests

