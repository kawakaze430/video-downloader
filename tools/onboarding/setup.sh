#!/usr/bin/env bash
set -euo pipefail
cd /workspace/video-downloader
python3 - <<'PY'
import sys, shutil, zipfile
from pathlib import Path
assert sys.version_info >= (3,10), "Python 3.10+ required"
assert shutil.which("openssl"), "OpenSSL CLI required for HTTPS tests"
dest=Path("/workspace/onboarding-sources")
with zipfile.ZipFile("Downloader--main.zip") as z:
    for info in z.infolist():
        target=dest/info.filename
        if not target.resolve().is_relative_to(dest.resolve()):
            raise RuntimeError("Unsafe archive path")
        if info.is_dir():
            continue
        data=z.read(info)
        if target.exists():
            if target.read_bytes()!=data:
                raise RuntimeError("Preserving modified file: "+str(target))
        else:
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(data)
PY
cd /workspace/onboarding-sources/Downloader--main
python3 -m unittest discover -s tests -v
python3 -m compileall -q tools tests

