# M0 reuse decision matrix — 17 source-code candidates

**Reviewed:** 15 November 2026. **Decision status:** engineering recommendation, **NOT owner approval**. Exactly **two primary foundations** are recommended. The other 15 are selective dependencies, deferred connectors, or study references; none is imported into Downloader.

## Evidence standard and limitations

- Read the actual repository files using a pinned GitHub default-branch commit, with build manifests, relevant implementation modules, and/or source test directories. This is **source triage**, not a complete 17-project security, licensing, binary, or quality certification.
- Checked default-branch commit, repository metadata (license field, archived status, language, commit date), root layout, and selected source/build files for all 17. Full third-party dependency license inventories, SBOMs, automated tests, binaries, and runtime compatibility are **not yet verified** for those projects.
- Separately cloned and read source for AB desktop, AB extension, ReClip, and MediaGrabber. **Only the AB extension** was bundled and typechecked in this pass; AB desktop Gradle launch failed. No site-specific extraction tests were run.
- The GitHub license field can be NOASSERTION even when source contains license documents. A root license cannot settle obligations of bundled binaries. Activity indicates maintenance interest, not a passing build.
- Use links below as **primary source evidence**, not as code-import authorization. Consult [legal/security requirements](LEGAL_SECURITY.md) and [first audit](M0_AUDIT.md).

## Exactly two selected primary foundations

### 1. AB Download Manager — REUSE/ADAPT, conditional

- **Pinned source:** [amir1376/ab-download-manager at 68f0ea6](https://github.com/amir1376/ab-download-manager/commit/68f0ea6e8ba5cbeb02c92342cd3bf7475378ae68), Apache-2.0 root LICENSE, Kotlin/Kotlin Multiplatform + Compose.
- **Actual code:** downloader/core/src/commonMain/.../DownloadManager.kt persists jobs via IDownloadListDb and supports path/filename validation and collision strategies. queue/QueueManager.kt loads persisted queues. desktop/app/build.gradle.kts wires the engine, monitor, shared app, native messaging launcher and integration server. The downloader/core module uses OkHttp and HLS parser.
- **Existing integration:** integration/server/.../Endpoints.kt provides /add, /ping, /queues; desktop native messaging host writes Chrome allowed_origins and Firefox allowed_extensions with configured IDs.
- **Build risk:** wrapper requests Gradle 9.8; gradle.properties specifies jvm.toolchain=25 (the current cloud image provides JDK 21). Wrapper bootstrap cannot reach the binary release asset from this environment. No desktop binary or Windows demonstration exists here.
- **Security debt:** default loopback HTTP API enabled, API key enforcement disabled; /add supports silent options through the UI integration path. Must harden before public distribution.
- **Why chosen:** reuse one coherent direct-transfer engine, desktop UI, persistence and native companion instead of rebuilding a general downloader in a new framework.

### 2. AB Download Manager Browser Integration — REUSE/ADAPT, conditional

- **Pinned source:** [amir1376/ab-download-manager-browser-integration at bf6811d](https://github.com/amir1376/ab-download-manager-browser-integration/commit/bf6811dd8a3ee2b47b94d70e13c2c7e70be7be05), Apache-2.0 root LICENSE, TypeScript/React/Vite.
- **Actual code:** src/manifest/manifest.chrome.ts emits Manifest V3; src/backend/Backend.ts selects HTTP or native messaging; src/backend/HttpApi.ts calls localhost /add and /ping; src/backend/nativemessaging/NativeMessagingTransport.ts implements message IDs/timeouts; src/linkgrabber/DownloadLinkInterceptor.ts already recognizes HLS .m3u8 requests.
- **Build evidence:** npm ci PASS; Chrome production build PASS; Firefox production build PASS. Standalone TypeScript check FAILS due an unresolved NativeMessaging import, Manifest author type mismatch, and webext-bridge / type-fest declarations.
- **Security debt:** all-host content scripts, broad host_permissions and cookies/webRequest/nativeMessaging permissions need minimization and justification. HTTP fallback prioritizes loopback when native is not connected.
- **Why chosen:** already speaks AB's protocol. Replacing it with MediaGrabber would require a second helper protocol plus extra native executables.

**These two are a compatible candidate pair, not a proved integrated release.** No source-code import until license/brand/platform choices are approved, third-party notices reviewed, and the owner approves the selected commits.

## Full decision matrix (all 17)

Key: REUSE = proposed core foundation; ADAPT = later selective dependency/module after review; REFERENCE ONLY = research architecture/UX, not copying code; DEFER = hold pending scope/policy; REJECT = not suitable as a primary foundation.

| # | Project | Actual implementation/build evidence inspected | Root-license evidence | Decision and rationale |
| --- | --- | --- | --- | --- |
| 1 | [AB Download Manager](https://github.com/amir1376/ab-download-manager) | Kotlin Gradle, downloader/core DownloadManager and QueueManager; persisted DB, native host | Apache-2.0 LICENSE | **REUSE** primary desktop. Build/toolchain/security gates remain. |
| 2 | [AB Browser Integration](https://github.com/amir1376/ab-download-manager-browser-integration) | TS/React/Vite, MV3 manifest, native + HTTP adapters, HLS interception; two bundler builds PASS, typecheck FAIL | Apache-2.0 LICENSE, package.json | **REUSE** primary extension. Maintain protocol compatibility with #1. |
| 3 | [ReClip](https://github.com/averygan/reclip) | Flask app.py subprocesses yt-dlp on submitted URL; in-memory jobs; Dockerfile installs FFmpeg | MIT LICENSE | **REFERENCE ONLY** web UI. Current backend has no visible auth, strict URL/SSRF control, quotas or durable jobs. Unsafe as a hosted default. |
| 4 | [MediaGrabber](https://github.com/miroshArtem/MediaGrabber) | TS MV3 manifest, injected main-world script, Node coapp native host; THIRD_PARTY_NOTICES.md | MIT LICENSE; bundled FFmpeg Windows GPLv3 per notices | **REFERENCE ONLY** for selected discovery/native patterns. Broad page permissions and extra executable/licensing surface. |
| 5 | [HLS Downloader](https://github.com/puemos/hls-downloader) | TS/pnpm workspaces, src/core use-cases for playlist/segments, core Vitest/typecheck scripts, MV2/MV3 build variants | MIT LICENSE and core package | **ADAPT LATER** for authorized HLS tests if AB's existing handling is insufficient; no duplication without measured gap. |
| 6 | [Parabolic](https://github.com/NickvisionApps/Parabolic) | C#/.NET 10 Shared, GNOME/WinUI solutions; DownloadService and yt-dlp dependency/service | MIT LICENSE | **REFERENCE ONLY** desktop video UX alternative. New .NET UI stack plus yt-dlp-first workflow costs more than current AB pair. |
| 7 | [FFmpeg](https://github.com/FFmpeg/FFmpeg) | C, configure, libavcodec/libavformat, tests; LICENSE.md enumerates optional GPL components | LGPL 2.1+ baseline, GPL when enabled; binary-dependent | **ADAPT LATER** as trusted external processor for owned media, with binary provenance and license review. Not a product base. |
| 8 | [yt-dlp](https://github.com/yt-dlp/yt-dlp) | Python package pyproject.toml, yt_dlp implementation and test suite | Unlicense core; optional/bundled libraries differ | **DEFER** rights-reviewed connector, not universal public-site support or Chrome-store shortcut. |
| 9 | [Gopeed](https://github.com/GopeedLab/gopeed) | Go 1.26 module, pkg/download state/persistence, many _test.go files, Flutter/Dart UI | GPL-3.0 LICENSE | **REFERENCE ONLY** engine/API/extension architecture; new Go/Flutter stack plus copyleft source obligations. |
| 10 | [Motrix](https://github.com/agalwood/Motrix) | Electron/TS, pnpm, native messaging bridge tests and desktop/server packaging scripts | package.json MIT; repository license API NOASSERTION; aria2/bundles must be audited | **REFERENCE ONLY** mature UI, bridge tests, release workflows. Avoid second Electron core and unclear bundled-code obligations. |
| 11 | [aria2](https://github.com/aria2/aria2) | C++ DownloadEngine.cc, CLI/JSON-RPC engine, src/test directories | GPL-2.0 COPYING | **REFERENCE ONLY** segmented transfers and RPC, not embed in an unapproved proprietary binary. |
| 12 | [Cobalt](https://github.com/imputnet/cobalt) | Svelte/web, Node/Express API src/cobalt.js and security modules | AGPL-3.0 LICENSE | **REFERENCE ONLY** simple web UX and API boundaries; AGPL/network obligations and different product scope. |
| 13 | [MeTube](https://github.com/alexta69/metube) | Python app, yt-dlp worker, app/url_guard.py with SSRF protections and documented limitations, tests directory | AGPL-3.0 LICENSE | **REFERENCE ONLY** job UI and SSRF lessons; no hosted import under unresolved license. |
| 14 | [Pinchflat](https://github.com/kieraneglin/pinchflat) | Elixir/Phoenix mix.exs, Oban jobs, Ecto/SQLite, test directory | AGPL-3.0 LICENSE | **REFERENCE ONLY** scheduling and library workflow; service architecture is out of M1 scope. |
| 15 | [Tube Archivist](https://github.com/tubearchivist/tubearchivist) | Django 6, Celery, Redis, backend/download/views.py; authenticated views and download tests | GPL-3.0 LICENSE | **REFERENCE ONLY** indexed media library and administrative workflows; heavyweight hosted components. |
| 16 | [YoutubeDL-Material](https://github.com/Tzahi12345/YoutubeDL-Material) | Node/Express backend + web UI, backend/package.json test script, Node 16 engine and older dependencies | MIT LICENSE | **DEFER** historical full-stack UX. Older runtime/dependency set creates update and security cost. |
| 17 | [yt-dlp-web-ui](https://github.com/marcopiovanello/yt-dlp-web-ui) | Go 1.26, server/rpc/service.go and persistent queue/RPC model | GPL-3.0 LICENSE; GitHub archived=true | **REJECT as foundation** (archived/copyleft); source may be studied for ideas but not integrated. |

## Reproducible commit pins — default branches observed 15 November 2026

The short SHAs used in prose are not sufficient for source import: use these **full** commits. A newer default-branch HEAD is not an implicit upgrade.

| # | Repository | Observed exact default-branch commit |
| --- | --- | --- |
| 1 | amir1376/ab-download-manager | 68f0ea6e8ba5cbeb02c92342cd3bf7475378ae68 |
| 2 | amir1376/ab-download-manager-browser-integration | bf6811dd8a3ee2b47b94d70e13c2c7e70be7be05 |
| 3 | averygan/reclip | 1d161d15a4fe93d9b3371377f0a421dc3e965b10 |
| 4 | miroshArtem/MediaGrabber | daf968e2f9ad853b318a10196f0e21c586798db5 |
| 5 | puemos/hls-downloader | 21ba8008a545843b9b34ff709614133873dc59a7 |
| 6 | NickvisionApps/Parabolic | 1118e6a3abbf5ffc1f764c4c9781f98d4c0482d4 |
| 7 | FFmpeg/FFmpeg | 0834db516348d253b2c51f969188501d324c698d |
| 8 | yt-dlp/yt-dlp | ee2559128c7ddc471de5aeaa584a9a4ae6836ec3 |
| 9 | GopeedLab/gopeed | be0a395447d788419e83acdfd693e48a1a1706bf |
| 10 | agalwood/Motrix | 8e12a8d0d84fbb87c3b12dc25df4834286bb0eaf |
| 11 | aria2/aria2 | 9e7273583f83e881e3ec067b523ba88724088d2f |
| 12 | imputnet/cobalt | a636575b09de1fc55d9b8cd98cac88f5f2f16b42 |
| 13 | alexta69/metube | 7746086e0e920925cb14c8f4843084e29548a877 |
| 14 | kieraneglin/pinchflat | 67d8bd5598f4461c5435bcc66fc8d02b00c607cb |
| 15 | tubearchivist/tubearchivist | 5a18613136122dd8fe83d43d95ea1b8af00d79eb |
| 16 | Tzahi12345/YoutubeDL-Material | 28234c0d4ba65059be18f3692f6f5e5b1170b1a6 |
| 17 | marcopiovanello/yt-dlp-web-ui | c7ad3bd79c7c520a7d17e7f2ba19d962be8e7897 |

**Activity nuance:** GitHub repo-level pushed_at may reflect other branches; the pins above use the actual default-branch commit response. Example: Parabolic's inspected default-branch commit is older than the repo's most recent pushed_at. The archived status of #17 was directly verified.

## Maintenance and release signals (GitHub API, 15 November 2026)

These are API metadata observations, **not evidence of security patching or successful releases**. The pushed date is repository-wide and may reflect a non-default branch. The tag/date are from GitHub's latest-release endpoint; *not returned* means the endpoint did not return an identifiable release in this inspection, not that upstream has no tagged releases. A release may refer to code other than the default-branch source pin above.

| # | Repo pushed (UTC date) | Latest-release tag returned | Release date (UTC) | Archived |
| --- | --- | --- | --- | --- |
+| 1 | 2026-11-06 | v1.11.4 | 2026-11-03 | no |
| 2 | 2026-10-31 | v1.5.0 | 2026-07-27 | no |
| 3 | 2026-07-09 | not returned | — | no |
| 4 | 2026-08-11 | v1.1.1 | 2026-08-11 | no |
| 5 | 2026-11-10 | v5.6.0 | 2026-10-31 | no |
| 6 | 2026-11-15 | 2026.5.0 | 2026-05-24 | no |
| 7 | 2026-11-15 | not returned | — | no |
| 8 | 2026-11-14 | 2026.10.26 | 2026-10-26 | no |
| 9 | 2026-11-15 | v1.9.3 | 2026-03-18 | no |
| 10 | 2026-11-15 | v2.4.2 | 2026-11-15 | no |
| 11 | 2026-06-25 | release-1.37.0 | 2023-11-15 | no |
| 12 | 2026-04-06 | not returned | — | no |
| 13 | 2026-11-14 | 2026.11.14 | 2026-11-14 | no |
| 14 | 2025-12-16 | v2025.9.26 | 2025-09-26 | no |
| 15 | 2026-10-25 | v0.6.0 | 2026-10-25 | no |
| 16 | 2026-03-08 | v4.3.2 | 2023-05-26 | no |
| 17 | 2026-08-21 | v4.0.0 | 2026-06-29 | yes |

**Maintenance implications:** AB desktop has a recent release, while the extension's latest-release endpoint returned an older tag despite newer pinned source; confirm **protocol compatibility for the exact commits**. The age of aria2's GitHub release and YoutubeDL-Material's older Node runtime do not automatically establish vulnerabilities; they increase verification burden. The archived yt-dlp-web-ui is unsuitable as a primary maintained foundation.

## Feature ownership: reuse, adapt, build or defer

| Initial requirement | Upstream evidence | Work in Downloader | Decision |
| --- | --- | --- | --- |
| HTTP(S) engine, multi-part download and resume | AB downloader/core download manager, HTTP connection/destination and parts | Targeted fixture-driven tests, confirm range fallback and checksum | **REUSE + VERIFY** |
| Queue, concurrency, scheduling and restart history | AB queue manager with persisted DB, default settings and downloadable jobs | Measure recovery, schedule behavior, invalid state | **REUSE + VERIFY** |
| Download path and naming | AB DownloadManager validates path/filename and collision choice | Threat tests for traversal, platform names, disk full | **ADAPT** |
| Browser context menu / handoff | AB extension existing code and desktop native host | Version compatibility, acceptance demo, negative tests | **REUSE + HARDEN** |
| Native messaging extension-ID whitelist | AB desktop native messaging manifest source | Brand-specific IDs, user pairing and message validation tests | **ADAPT** |
| Local HTTP bridge and silent add | AB optional API-key checks and extension HTTP-first fallback | Require secure default; guard against web-origin abuse and unauthorized silent jobs | **BUILD SECURITY CHANGE** |
| Browser permissions | AB extension all-host scripts, cookies/webRequest/nativeMessaging | Narrow hosts and permissions, justify UX and consent | **ADAPT** |
| Checksums and integrity declaration | Not yet proven as an end-to-end AB UI acceptance flow | SHA-256 fixture assertion, atomic output verification | **BUILD/VERIFY** |
| Controlled HTTPS and disconnect test infrastructure | Our Python local fixture | HTTPS, If-Range, abrupt EOF, CI tests now implemented | **BUILD — FIXTURE ONLY** |
| HLS detection/stream handling | AB extension .m3u8 and desktop HLS credentials already present | Test permitted fixture before evaluating another HLS codebase | **REUSE + VERIFY** |
| MP4/MP3/containers/subtitles | FFmpeg code and license docs | Safe separate process, bounded jobs, format tests and distribution review | **ADAPT LATER** |
| Web interface/backend | ReClip offers a minimal example but accepts arbitrary URLs and in-memory jobs | Original product website later; SSRF/auth/quotas before hosted jobs | **DEFER** |
| Site-specific extraction | yt-dlp offers extractors, with permissions/law/policy constraints | Explicit rights/source policy and regression tests | **DEFER** |
| Advanced catalog, AI, billing, cross-device sync | No selected core baseline | Demand/cost/security decisions after beta | **DEFER** |

## Distribution / license / security risk register

| Risk | Current evidence | Required before release |
| --- | --- | --- |
| No project license or contributor grant | Downloader lacks a LICENSE; ADR-009 unresolved | Owner chooses ownership/distribution/contribution policy; do not treat this doc as permission |
| Apache attribution | Both selected roots have Apache-2.0 LICENSE | Preserve copyright/NOTICE and review nested libraries/assets and license-scanner output |
| Kotlin/desktop third-party obligations | Compose, OkHttp, Arrow, HLS parser, JNA, Android tooling, native packager in Gradle scripts | Dependency SBOM, notices, per-binary attribution, platform build conditions |
| Browser supply chain | npm lockfile with Vite 4, TypeScript 5.9.3, webext-bridge 6.0.1, type-fest dependency | Fix typecheck, review vulnerable/obsolete packages, SBOM and minimal permissions |
| Native/HTTP trust | Native host lists allowed extension IDs; localhost auth disabled by default; silent add possible | Threat model, authenticated pairing and origin rejection tests |
| FFmpeg | LICENSE.md LGPL baseline and GPL components when enabled; vendor builds differ | Approve exact binary/configuration and notices, avoid unreviewed codecs |
| MediaGrabber native binaries | THIRD_PARTY_NOTICES.md identifies a GPLv3 FFmpeg Windows bundle | Avoid accidental incompatible distribution from selective code import |
| GPL/AGPL alternatives | Gopeed, aria2, Cobalt, MeTube, Pinchflat, Tube Archivist, archived UI | Reference only unless explicit owner/legal approval and obligations fulfilled |
| Web URL handling | ReClip accepts arbitrary URL passed to yt-dlp; in-memory jobs; no visible quotas/auth | Do not deploy as a public fetch service; explicit SSRF/redirect/limit design |
| Platform policies | Chrome Web Store specifically flags extensions facilitating YouTube downloads | Test with authorized direct files, complete store policy review before distribution |

## Confidence and next evidence needed

- **High confidence in integration direction:** two primary roots are Apache-2.0 and communicate through a designed native/HTTP bridge; extension bundling is reproducible.
- **Moderate confidence in feature reuse:** source code for engine/DB/queue/HLS is present, but no end-to-end desktop tests or Windows verification performed in this audit.
- **Low confidence in release readiness:** Java 25 toolchain and Gradle bootstrap, TypeScript typecheck, transitive license/SBOM, browser permissions, localhost API authentication and store policy gates remain open.
- **No verified performance ranking:** none of 17 was speed-benchmarked against the same authorized server/hardware.

**Final M0 recommendation to owner:** adopt **AB Download Manager + AB Browser Integration** only after approving license, scope, branding and Windows/Chrome target. Keep one Kotlin engine, its natural companion extension, and add only evidence-backed adapters. Do not import ReClip, MediaGrabber, Gopeed, Motrix or any GPL/AGPL project as a second core.
