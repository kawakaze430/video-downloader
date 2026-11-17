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
case "${1:-}" in
  "")
    printf '%s\n' 'Prerequisites found. No tests, builds, downloads or services were run.'
    printf '%s\n' 'See PROJECT_STRUCTURE.md and AnalyseFuture/NEXT_DEVELOPER_INSTRUCTIONS.txt.'
    ;;
  --verify-preservation)
    python3 tools/repository/verify_preservation.py
    ;;
  --run-tests)
    # Explicit opt-in for a later owner-authorized validation task.
    python3 -m unittest discover -s tests/fixtures -v
    ;;
  *)
    printf '%s\n' 'Usage: bash tools/development/setup.sh [--verify-preservation|--run-tests]' >&2
    exit 2
    ;;
esac
