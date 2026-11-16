# video-downloader

One repository for a planned download and media workspace across Android,
web, browser extensions, Windows, macOS, and Linux. The supplied code is
organized for evaluation; these applications are not yet integrated.

Start with the detailed [project idea](PROJECT_IDEA.txt),
[repository audit](docs/REPOSITORY_AUDIT.txt), and [working agreement](AGENTS.md).

## Repository map

| Path | Purpose | Current status |
| --- | --- | --- |
| `sources/ab-download-manager/` | Kotlin desktop and Android foundation candidate | Supplied source; no integrated release validated |
| `sources/ab-browser-integration/` | Matching TypeScript browser companion candidate | Supplied source; build/security validation needed |
| `sources/downloader-blueprint/` | Previous planning, research, and Python fixture | Preserve prior work; 14 fixture tests verified |
| `AnalyseFuture/reference-projects/` | Intact MediaGrabber and ReClip references | Retained for later evaluation |
| `AnalyseFuture/prior-versions/` | Originals of documents/helpers revised here | Exact preservation copies |
| `archives/` | Original five ZIP files | Kept unchanged |
| `docs/` | Audit, full path inventory, and preservation evidence | Review scope and checks documented |
| `tools/` | Repository verification and local fixture setup | Standard-library checks; no platform downloads |

`AnalyseFuture` preserves material for later review. Nothing was classified as
attacker-added solely because it is a reference or uses another language.

## Verify and use the local fixture

From the repository root, with Python 3.10+ and OpenSSL installed:

```sh
python3 tools/verify_repository.py
bash tools/onboarding/setup.sh
cd sources/downloader-blueprint
python3 -m tools.fixtures.http_fixture --port 8765
```

The fixture binds to loopback and provides a deterministic download target;
it is not a downloader application. See its
[guide](sources/downloader-blueprint/tools/fixtures/README.md).
No package installation, private credentials, or live platform access is
required for these checks. The first command verifies preserved content and
archive extraction; it does not certify third-party code as safe.

## Direction and boundaries

The project idea prioritizes YouTube as the first named source research track
while retaining a reliable direct-file foundation. Facebook, Instagram, MP4,
HLS/DASH, and other workflows each need their own supported capability record.
Universal video access is not guaranteed. Platform permissions, DRM, server
behavior, browser/mobile restrictions, and formats impose real limits.

One product can retain Kotlin for desktop/Android, TypeScript for extensions,
and supporting tools without rewriting everything into one language. Foundation
adoption, integration, language migration, public releases, and hosted services
require separately authorized work.

## Preservation and licenses

All 1,449 files tracked at `0b2a1ad` are mapped to preserved copies in
[`docs/preservation-manifest.json`](docs/preservation-manifest.json).
All 1,438 archive payload files remain available unchanged. ZIP paths and
source locations are indexed in [`sources/archives.json`](sources/archives.json).

AB desktop/browser supply Apache-2.0 licenses; MediaGrabber/ReClip supply MIT
licenses. The blueprint supplies no root license. Preserve notices and review
transitive/binary licensing before distribution. No product license was chosen.
