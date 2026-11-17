# video-downloader

One repository for a cross-platform download and media workspace. Kotlin owns
shared desktop/Android source; the TypeScript browser companion handles intake
and handoff. Optional AI/media/cloud features remain proposals, not verified
integrated capabilities.

Start with [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md), the
[recovery audit](AnalyseFuture/REPOSITORY_AUDIT.txt), and the detailed
[plain-text future vision](AnalyseFuture/PROJECT_VISION_AND_FUTURE_ROADMAP.txt).

## Functional collections

- `apps/download-manager/`: intact Gradle desktop/Android/download-engine project.
- `apps/browser-extension/`: matching npm/Vite extension with its own assets.
- `tools/fixtures/` and `tests/fixtures/`: original synthetic fixture and checks.
- `tools/development/` and `tools/repository/`: local setup and preservation tools.
- `docs/project/`: original blueprint, decisions, feature backlog and research.
- `archives/`: unchanged ZIP backups and per-member preservation index.
- `AnalyseFuture/`: future vision, recovery reports, prior versions, orphan code
  and non-active reference implementations.

See the complete ownership rules and per-file mapping in PROJECT_STRUCTURE.md
and AnalyseFuture/ORIGINAL_TO_NEW_PATH_MAPPING.txt. Component internals are
kept together because imports, source sets, resources and packaging depend on
those relationships. There is no new universal framework or language rewrite.

## Validation

The owner subsequently authorized testing and fixes. Read the current
[validation report](AnalyseFuture/VALIDATION_REPORT.txt) for observed results,
failed initial checks, fixes and external blockers. Earlier no-test wording in
recovery reports describes the completed restructuring pass.

- Fixture: `bash tools/development/setup.sh --run-tests`.
- Download transport: `python3 tools/development/gradle.py :downloader:core:desktopTest --configure-on-demand --no-daemon --max-workers=4`.
- Browser: from `apps/browser-extension`, run `npm ci --ignore-scripts`,
  `npm test`, `npm run build`, then the `pack:*` scripts as needed.
- Archived examples: follow `tests/references/README.md`; tests use isolated
  copies and synthetic/mocked data, never a production archive import.

81 test cases passed across these scopes. Full desktop/Android builds are
blocked by proxy denial of `jitpack.io`; installed extension UI is blocked by
Chromium administrator policy. These are not claims of complete product readiness.
The report records toolchain requirements and the exact next actions.

## Preservation and licenses

The starting point was `7a7e2f6`; a remote recovery tag preserves it. Every one
of its 1,458 tracked files has an original-to-retained path and hash record in
AnalyseFuture/migration-records/preservation-manifest.json. Changed documents
and configurations have exact originals under historical-implementations.

AB desktop/browser supply Apache-2.0 licenses; MediaGrabber/ReClip supply MIT
licenses. The blueprint supplies no root product license. Preserve notices and
review dependencies, platform permissions and distributed binaries before release.

This project targets permitted source workflows. A universal claim to save every
video from every site is not established by source availability or future AI.
