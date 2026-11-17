# Project structure and ownership

This is one planned download/media project with desktop, Android and browser
source implementations. AI capabilities are future proposals. The repository
does not yet provide a verified integrated universal downloader.

Every one of the **1,458 files tracked at `7a7e2f6`** was inventoried by content
and ownership before these moves. Existing work is preserved. No tests were
run after the owner's instruction to limit this pass to organization.

```text
.
├── AGENTS.md                         owner instructions
├── README.md                         current entry point
├── PROJECT_STRUCTURE.md              this ownership map
├── apps/
│   ├── download-manager/              one Gradle multi-project application
│   │   ├── android/app/               Android activities, service, storage, UI
│   │   ├── desktop/                   desktop app and OS-specific adapters
│   │   ├── downloader/core/           transfer engine, jobs, parts, persistence
│   │   ├── downloader/monitor/        transfer observation and speed reporting
│   │   ├── integration/server/        browser/local HTTP integration
│   │   ├── shared/                    shared app, settings, UI and resources
│   │   ├── compositeBuilds/           Gradle plugins and build platform support
│   │   ├── buildSrc/                  convention/build helpers
│   │   └── gradle/                    version catalogue and wrapper
│   └── browser-extension/             one npm/Vite browser companion
│       ├── src/backend/               native and HTTP app connections
│       ├── src/interceptors/          user/browser download interception
│       ├── src/media/                 HLS/quality selection
│       ├── src/contextmenus/          explicit link intake
│       ├── src/contentscripts/        page/selection message handling
│       ├── src/manifest/              Chrome/Firefox manifests and permissions
│       ├── src/optionsui/             configuration UI
│       └── public/                    extension icons and localization
├── tools/
│   ├── fixtures/                     deterministic HTTP/HTTPS target
│   ├── development/setup.sh           no-test default; later explicit opt-ins
│   └── repository/verify_preservation.py  preservation utility, not run here
├── tests/fixtures/                    preserved fixture regression source
├── docs/project/                      earlier blueprint, decisions and research
├── archives/                          five original ZIPs and source-index.json
└── AnalyseFuture/
    ├── *.txt                          requested findings, mapping and handoff
    ├── PROJECT_VISION_AND_FUTURE_ROADMAP.txt  canonical detailed product idea
    ├── repository-inventory/           machine-readable baseline file analysis
    ├── migration-records/              exact path/hash preservation manifest
    ├── historical-implementations/     originals of revised files
    ├── incomplete-features/browser-extension/  unreferenced backend stub
    ├── reference-projects/             intact MediaGrabber and ReClip examples
    ├── prior-versions/                 older preserved pre-review versions
    └── recovery-notes/                 earlier audit and recovery request
```

## Why files stay together

The Gradle settings include desktop, Android, downloader, integration and shared
modules by relative project path. Kotlin package names, source sets, resources,
platform implementations and build files remain together. Pulling all `.kt`
files into one folder would break those relationships. The same applies to the
extension's Vite root, `~` source alias, manifests, HTML, scripts and assets.

Icons and localized resources belong to their consumer, including repeated
Android launcher definitions at required density/resource locations. LICENSE
files remain in each supplied component. Identical bytes do not make those
files safely interchangeable.

The original Python fixture is no longer hidden inside planning documents.
Its `tools.fixtures` import namespace is retained at the repository root, and
its existing tests are collected under `tests/fixtures`. Documentation links
to those files were repaired. The blueprint remains historical project context
under `docs/project`; its upstream workflow is nested and inactive.

The orphan `BackendProvider.ts` contained imports only, exported nothing,
referenced a missing module, and had no source consumers. It is preserved under
`AnalyseFuture/incomplete-features`; `src/backend/Backend.ts` remains the
existing owner of browser dispatch. No transfer algorithm or bridge protocol
was merged into another implementation without validation.

## Where new work belongs

- Transfers, persistence, queues and retry: `apps/download-manager/downloader`.
- Shared desktop/Android application features: `apps/download-manager/shared/app`.
- OS-specific UI/services: the existing `android` or `desktop` module.
- Browser intake/transport/UI: the appropriate existing extension feature folder.
- Fixture behavior and regression source: `tools/fixtures` and `tests/fixtures`.
- Product decisions and original research: `docs/project` and the future vision.
- Uncertain examples, superseded originals and migration evidence: `AnalyseFuture`.

Do not create a second queue/history implementation or global shared package
just because another reference has a similarly named function. Compare its
protocol, state model, dependencies, permissions and unique behavior first.

## Exclusion and compatibility

There is no root npm workspace or recursive Gradle build including archives.
Primary entrypoints operate from their explicit application directory.
`AnalyseFuture` and `archives` are excluded from a repository-root Docker build
context. This does not sandbox deliberately executed archived code. Review the
security report before using examples or running original installer scripts.

The extension source-pack script is scoped to `HEAD:apps/browser-extension`
instead of archiving the entire monorepo. Nested upstream workflows remain
historical references; no root CI or deployment was activated.

Git's LF normalization for two Windows batch files and their CRLF checkout
bytes are tracked separately. The preservation manifest records original path,
retained path, active path, byte hash, Git object and mode. Original versions of
documents/configuration changed for path repair remain recoverable.

## Reading order and execution

Read `README.md`, `AnalyseFuture/REPOSITORY_AUDIT.txt`, the file and feature
inventories, and `AnalyseFuture/NEXT_DEVELOPER_INSTRUCTIONS.txt`. The detailed
future vision covers Android, web, extensions, Windows, macOS, Linux, source
coverage, AI options, limits, and one-/two-/three-to-five-year research horizons.

This pass deliberately runs no tests. Commands documented for a later authorized
task are not evidence they passed after migration. Preserve the backup tag
`recovery-baseline-2026-11-17-7a7e2f6`, published history and existing branches.
