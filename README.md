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

## Current pass

The latest owner instruction is **do not run tests**. This restructuring only
reads/classifies content, groups files, updates references and preserves prior
versions. No post-move runtime/build/test success is claimed. See the validation
report for older observations and current limitations.

`bash tools/development/setup.sh` defaults to prerequisite information without
running tests/builds. Later, explicit authorized validation can use the opt-in
flags described in the continuation guide. No root CI or deployment was added.

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
