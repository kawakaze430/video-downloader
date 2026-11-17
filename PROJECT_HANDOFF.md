# Project handoff, feature status and complete task board

**Owner:** kawakaze430 · **Repository:** [video-downloader](https://github.com/kawakaze430/video-downloader) · **Updated:** 17 November 2026.

**Read this first before implementing anything.** This is the current entry point
for another developer or AI tool. It describes the existing work, its limits,
the remaining tasks, and the evidence required from a pull request.

Feature evidence was last recorded at **`e65fb0c`** in the
[validation report](AnalyseFuture/VALIDATION_REPORT.txt) and
[structured results](AnalyseFuture/validation-results/2026-11-17/summary.json).
This documentation update does not rerun those tests or establish a new build.
Older recovery reports and feature inventories remain historical evidence;
their earlier “not tested” or “typecheck failing” statements must be read with
the newer validation results below.

## 1. What we are building

One coherent download and media workspace across **Windows PC, macOS, Linux,
Android, browser extensions and, later, a website**. It should let users collect
permitted downloads, choose available media formats, recover interrupted jobs,
process their own media locally and find the results again.

The long-term source ambition includes YouTube first, Facebook, Instagram,
other supported sites, direct MP4/WebM/MOV files, and permitted HLS/DASH streams.
Every source needs a specific supported workflow, tests, maintenance ownership
and appropriate permission. “Every video from every site” is an ambition, not
an implemented or credible permanent guarantee. Viewing access alone does not
establish download permission. DRM/access-control bypass is outside the plan.

The repository already contains substantial reusable code and research.
**Do not start from zero or rewrite everything into one language.** Evaluate
the Kotlin desktop/Android foundation and TypeScript browser companion first.
Python supports the original fixture and selected tools. FFmpeg and optional
source connectors are separate dependencies, not reasons to replace the engine.

The product name, original-code license, distribution model, first supported
platform pair and paid/cloud scope still need owner decisions. No AI feature,
production hosted service, cross-device sync or universal platform connector
has been implemented merely by organizing these sources.

## 2. What currently works, and what does not yet have evidence

Status meanings:

- **Verified in this scope:** the stated checks executed successfully.
- **Source present:** relevant code exists; full product behavior is unverified.
- **Reference only:** preserved alternative code, excluded from production.
- **Blocked:** a concrete prerequisite prevented the attempted check.
- **Planned:** implementation or adoption has not been established.

| Area | Current status | Evidence and practical limit |
| --- | --- | --- |
| Original synthetic HTTP/HTTPS fixture | Verified | 14 tests, plus 8 CLI checks; Range, redirect, truncation and verified TLS. It is a test target, not the app. |
| Kotlin HTTP transport | Verified compile and selected behavior | 11 real loopback client tests: bytes/hash, ranges, reassembly, non-range responses, redirects, truncation, headers, user agents and error/auth classification. |
| Full queue/job lifecycle | Source present | Kotlin job, queue and storage classes exist. App restart, durable recovery, cancellation and multi-job behavior still need tests. |
| Browser source and message contracts | Verified in this scope | Strict source/type checks, compile-time negative examples and 13 Node tests pass. No `skipLibCheck` bypass. |
| Chrome/Firefox bundles and ZIPs | Verified packaging | Both build/package; CRC and manifest references checked. Source ZIP is nonempty and limited to the extension subtree. |
| Installed browser UI/native pairing | Blocked/unrun | Available Chromium administrator policy disables unpacked extension loading. No installed-extension or native-host success is claimed. |
| Full desktop application | Blocked build | `SchemaKt:0.2.3` cannot resolve because the proxy denies `jitpack.io` with 403. |
| Android application | Source present; build blocked | Assembly/unit-test targets were attempted separately and stopped at the same dependency. Device behavior is unverified. |
| MediaGrabber alternative | Reference only; selected checks verified | 24 parser/quality/RPC tests and 6 real converter/probe checks pass in isolation. Its unsafe transfer patterns remain unresolved. |
| ReClip alternative | Reference only; selected checks verified | 19 isolated mocked route/download tests pass. Authentication, SSRF, quota and persistence gaps still prevent hosted adoption. |
| Source preservation | Verified | Original file/Git mappings and all five ZIPs/1,438 payload members checked; originals were retained before fixes. |
| Browser production dependency audit | Last observed: 0 advisories | Compatible lodash/zod updates applied. This result does not certify dev dependencies, all references, or future versions. |
| Windows/macOS installers and physical Android | Unrun | Separate supported-machine, signing, update and device tests are needed. |
| AI/library/cloud/source expansion | Planned | See the future vision; no shipping capability is claimed. |

**81 selected test cases passed:** 14 fixture + 11 Kotlin transport + 13 browser
+ 19 ReClip + 24 MediaGrabber. Additional CLI, preservation and converter checks
are recorded separately. This is not a claim that all product features work.

### Completed fixes to preserve

- Version/hash-guarded declaration preparation fixes published browser typing
  defects while retaining strict checks and runtime JavaScript.
- Explicit `type-fest` declaration dependency and positive/negative message tests.
- Native message envelope/error/ID tests after compatible dependency updates.
- ReClip rejects malformed/non-object JSON and non-string URLs before work starts.
- MediaGrabber DASH parsing accepts matching single- or double-quoted attributes.
- Official Gradle 9.8 wrapper restored and distribution checksum pinned;
  supplied originals preserved. A version mismatch was not proof of compromise.
- Workspace-owned JDK/Gradle/Android configuration support without changing `HOME`.
- Browser source packaging runs at Git root; generated ZIPs can be refreshed.

## 3. Where every file and folder belongs

Use these guides together:

- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md): architecture and ownership rules.
- [Complete individual file guide](docs/repository/FILE_GUIDE.md): every tracked
  file, its purpose and its collection, including new validation files.
- [Complete individual folder guide](docs/repository/FOLDER_GUIDE.md): all tracked
  directory ancestors, not just the top level.
- [Original-to-new mapping](AnalyseFuture/ORIGINAL_TO_NEW_PATH_MAPPING.txt) and
  [preservation manifest](AnalyseFuture/migration-records/preservation-manifest.json):
  provenance and exact original/active/retained paths.
- [Dependency relationships](AnalyseFuture/repository-inventory/dependency-relationships.json):
  static source relationships; not a proven runtime call graph.

The complete guides are separate so this handoff stays readable on GitHub.
Git metadata is managed through Git, not copied into documentation. Dependency
caches and generated outputs are excluded from commits; the
[local generated-file inventory](AnalyseFuture/repository-inventory/LOCAL_GENERATED_FILE_INVENTORY.txt)
records the earlier local paths and why they are not product source.

| Functional collection | Responsibility | Files a developer should start with |
| --- | --- | --- |
| Root documentation | Current navigation, ownership and handoff | `README.md`, `AGENTS.md`, this file, `PROJECT_STRUCTURE.md` |
| `apps/download-manager/` | One Gradle multi-project application | `settings.gradle.kts`, `gradle.properties`, `gradle/libs.versions.toml` |
| `downloader/core/` inside that app | HTTP/HLS jobs, parts, queues, persistence, network policies | `DownloadManager.kt`, `HttpDownloadJob.kt`, `HttpDownloaderClient.kt`, `OkHttpHttpDownloaderClient.kt`, queue/db/destination packages |
| `downloader/monitor/` | Job/progress/speed observation | Existing monitor/observer implementations |
| `shared/app/` | Shared application state, pages, settings and UI behavior | Shared page components, settings storage, category and notification utilities |
| `shared/config/` | Settings schema/datastore integration | Schema/config classes; depends on SchemaKt |
| `shared/utils/` | Platform/common helpers consumed by other modules | Existing network, file, coroutine and platform utilities |
| `shared/resources/`, `shared/compose-utils/` | Localization, icons, resource contracts and shared controls | Resource accessors and UI widgets; retain consumer-relative locations |
| `shared/updater/`, `shared/auto-start/` | Update and OS startup behavior | Platform appliers and registration code; source exists, release trust remains open |
| `desktop/` | Desktop entrypoints, windows, native host, packaging and OS adapters | `desktop/app`, `app-utils`, `shared`, `mac_utils`, `slf4j-impl` |
| `android/app/` | Activities, browser/share intake, download service, storage and permissions | `AndroidManifest.xml`, `ABDMApp.kt`, services/pages/storage packages |
| `integration/server/` | Local HTTP endpoints and bridge callbacks | `Endpoints.kt`, `IntegrationSettings.kt`, `Integration.kt`, request models |
| `buildSrc/`, `compositeBuilds/`, `gradle/` | Build conventions, plugins, version catalogue and wrapper | Keep their relative project references intact |
| `apps/browser-extension/` | One npm/Vite browser application | `package.json`, lockfile, `vite.config.ts`, `tsconfig*.json`, `VALIDATION.md` |
| Browser `src/backend/` | Native/HTTP transports, contracts and error handling | `Backend.ts`, `NativeMessagingApi.ts`, `HttpApi.ts`, `nativemessaging/` |
| Browser `src/linkgrabber/`, `contextmenus/`, `contentscripts/` | Intake and interception | `DownloadLinkInterceptor.ts` and each user/capture path |
| Browser `src/media/`, `manifest/`, `configs/` | Media models, package permissions and preferences | Existing parsers, browser-specific manifest builders, `Config.ts` |
| Browser UI/entrypoints/assets | Popup/options/background/content entrypoints and UI consumers | `entrypoint/`, `optionsui/`, `browseractionpopup/`, `public/` and source assets |
| Browser `scripts/`, `tests/` | Guarded declaration compatibility and focused tests | `prepare-types.mjs`, manifest/native protocol tests, compile-only contracts |
| `tools/fixtures/`, `tests/fixtures/` | Original synthetic server and regression source | `http_fixture.py`, `test_http_fixture.py` |
| `tools/development/` | Explicit setup and pinned Gradle launcher | `setup.sh`, `gradle.py` |
| `tools/repository/` | Preservation verification | `verify_preservation.py`; inspect history/index requirements before editing originals |
| `tests/references/` | Isolated alternative-code checks | `README.md`, `test_reclip.py`, `mediagrabber.test.cjs` |
| `docs/project/` | Previous blueprint, decisions, milestones and 17-source study | `docs/FEATURE_MATRIX.md`, `DECISIONS.md`, `REUSE_DECISION_MATRIX.md`, `context-archive/` |
| `archives/` | Five supplied ZIP originals and member mapping | `README.md`, `source-index.json`; never unpack over edited files |
| `AnalyseFuture/reference-projects/` | Alternative MediaGrabber/ReClip code | Not active services, production imports or root workspaces |
| `AnalyseFuture/incomplete-features/` | Orphan imports-only browser stub | Existing `BackendProvider.ts`; do not restore merely to satisfy a filename |
| `AnalyseFuture/historical-implementations/`, `prior-versions/`, `validation-originals/` | Exact earlier versions | Preserve byte/Git evidence; do not normalize or execute them casually |
| `AnalyseFuture/validation-results/` | Dated results, commands and logs | `2026-11-17/summary.json` plus component evidence |
| `AnalyseFuture/repository-inventory/`, `migration-records/` | File/dependency inventories, mapping and migration provenance | Historical catalogues describe their recorded baseline, not every later commit |
| `AnalyseFuture/*.txt`, `recovery-notes/`, `security-reports/` | Findings, future vision, request history and prior observations | Prefer the newest dated validation evidence over old unchecked status |

Do not sort by extension, flatten source sets, combine independent protocols by
filename, deduplicate required licenses/resources, or include `AnalyseFuture/`
in a production glob. One runtime responsibility should have one selected owner.
Reference code can inform a later adapter after compatibility/security review.

## 4. Remaining product features: complete original backlog crosswalk

The original [feature matrix](docs/project/docs/FEATURE_MATRIX.md) contains the
49 product IDs below and their acceptance targets. These IDs are retained so
existing planning is not lost. “Source” below is not “complete product feature.”

| ID | Feature | Current evidence / remaining work | Main task |
| --- | --- | --- | --- |
| D01 | Direct HTTPS download | HTTP adapter verified; full app workflow still blocked/unverified | CORE-001 |
| D02 | Progress, ETA and speed | UI/monitor source; accuracy and unknown totals need end-to-end checks | CORE-002 |
| D03 | Pause/resume | Range transport verified; durable paused job resume unverified | CORE-001 |
| D04 | Retry/restart recovery | Job/part persistence source; interruption/restart matrix missing | CORE-001 |
| D05 | Cancel/cleanup | Source; worker/partial-file cleanup tests needed | CORE-001 |
| D06 | Queue/concurrency limits | Queue source; fairness and caps unverified | CORE-002 |
| D07 | Safe destinations/filenames | Existing helpers; malicious paths/collisions need tests | SEC-003 |
| D08 | Integrity validation | Transport hash check and checksum UI source; job completion gating unverified | CORE-001 |
| D09 | Segmented transfers | Part source and range reassembly checks; full scheduler integration unverified | CORE-002 |
| D10 | Scheduling/speed limits | Source; measured limits, clock and sleep behavior needed | CORE-002 |
| D11 | Categories/search/history | Application/storage/UI source; persistence and usability verification needed | UX-001 |
| D12 | Proxy/network configuration | Source; explicit configured routes/auth tests needed | CORE-003 |
| D13 | Bulk intake/deduplication | Source/reference behavior; unified product tests needed | CORE-002 |
| D14 | Job-list import/export | No completed product workflow established | AUTO-001 |
| D15 | CLI/authenticated local API | Entrypoints/server source; safe stable product contract unverified | AUTO-001 |
| B01 | Browser-to-desktop handoff | Source; installed paired flow blocked/unrun | BROWSER-001 |
| B02 | Popup/context menu | Source, manifest/native unit coverage; installed behavior unrun | BROWSER-001 |
| B03 | Safe pairing/native messaging | Contract checks pass; authorization and abuse tests missing | SEC-001 |
| B04 | Job progress in extension | Source relationship; real app-state feedback unverified | BROWSER-001 |
| B05 | Permitted media detection | AB media source and alternative detection code; no broad source coverage claim | MEDIA-002 |
| B06 | Permitted non-DRM HLS/DASH | Source and isolated parser tests; active stream-to-output integration missing | MEDIA-002 |
| B07 | Firefox | Bundle/package verified; installed runtime and pairing unrun | BROWSER-002 |
| B08 | Minimal permissions | Broad host/cookie access remains; minimization work required | SEC-002 |
| B09 | Optional remote target | Planned; no trusted-device remote product implemented | AUTO-002 |
| M01 | Import owned local media | Reference capability, no unified active workflow established | MEDIA-001 |
| M02 | MP4/MKV/WebM remux | Isolated FFmpeg/converter evidence; full supported matrix not established | MEDIA-001 |
| M03 | Audio extraction | Reference code; active formats/presets/output validation needed | MEDIA-001 |
| M04 | Compression/presets | Candidate processing logic; measured supported presets needed | MEDIA-001 |
| M05 | Trim/merge | No complete active product workflow established | MEDIA-003 |
| M06 | Subtitles | Source/reference opportunities; supported import/export needed | MEDIA-003 |
| M07 | Audio/language selection | Models/parsing references; final track selection and output proof needed | MEDIA-002 |
| M08 | Batch conversion | Planned integration with the single job owner | MEDIA-001 |
| M09 | Available 4K/8K processing | Conditional on source/hardware/codecs; never guarantee authentic higher quality | MEDIA-001 |
| M10 | Personal media library | Planned; no semantic/search library shipped | AI-001 |
| M11 | AI transcription/tagging | Planned, opt-in research after reliable core | AI-001 |
| M12 | Source connector architecture | yt-dlp reference only; approved maintained connectors not active | SOURCE-001 |
| W01 | Public product website | No active product website established | WEB-001 |
| W02 | Upload-based converter | Planned secure service; ReClip is not production approval | WEB-002 |
| W03 | Direct-URL web job UI | ReClip isolated tests; hardened public workflow not implemented | WEB-002 |
| W04 | Server queue/workers | Planned; do not add Redis/cloud bills without approved need | WEB-002 |
| W05 | Accounts/billing | Owner decision and later implementation | GOV-001 |
| P01 | Reproducible builds | Selected scopes pass; full desktop/Android blocked | BUILD-001 |
| P02 | Automated tests | 81 selected cases; full integration/PR CI incomplete | CI-001 |
| P03 | Signed installers | Unrun/unreleased | RELEASE-001 |
| P04 | Verified updates/rollback | Updater source exists; app update trust unverified | SEC-004 |
| P05 | SBOM/third-party notices | Partial source licenses retained; full shipped inventory open | GOV-002 |
| P06 | Privacy-safe diagnostics | Requirements and selected handling; complete redaction tests missing | SEC-002 |
| P07 | Localization/accessibility | Resource/UI source; supported language/accessibility tests unrun | UX-002 |
| P08 | Plugin SDK/marketplace | Planned and demand-dependent | AUTO-002 |

## 5. Task rules, priorities and assignments

- **P0:** needed for a credible, safe first app/extension flow.
- **P1:** needed for a supported beta/1.x release.
- **P2:** expansion after the earlier evidence and owner decisions exist.
- All owners below are **roles to assign**, not named people already committed.
- **Ready** means a tool can investigate/implement that bounded task after the
  owner assigns it. It does not approve the entire roadmap in one PR.
- **Blocked/decision** tasks need the stated prerequisite. Finish independent
  work; do not bypass access controls or invent permissions/credentials.
- Reuse existing code first. Each implementation PR must update this task board
  and link evidence; a description in an upstream README is not acceptance.

### Recommended order

1. Owner resolves ENV-001/ENV-002 and GOV-001 decisions in parallel.
2. First external implementation PR: **CI-001**, initially fixture/browser
   checks, adding core only with its explicit prerequisites. No root CI exists now.
3. Once access is available: BUILD-001 and ANDROID-001, then BROWSER-001.
4. SEC-001/SEC-002 and CORE-001 are required before a public beta.
5. Add local media, supported sources and releases one measured slice at a time.

### P0: environment, builds, safety and first working flow

#### ENV-001 — Restore the required dependency route

- **State/owner:** blocked; environment owner. **Depends on:** approved runtime network settings.
- **Work:** review/save/apply the prepared addition for `jitpack.io`, preserving
  other allowed destinations. Confirm the runtime policy actually changed.
- **Acceptance:** `com.github.amir1376:SchemaKt:0.2.3` resolves through an approved
  route, then record a fresh build attempt. Saving a draft alone is not success.
- **Do not:** change library versions, disable TLS/checksums, retry unchanged
  requests indefinitely, or use an unapproved proxy to evade the denial.

#### ENV-002 — Obtain an approved installed-extension test environment

- **State/owner:** blocked; browser/environment administrator.
- **Work:** provide a permitted browser/profile/policy for unpacked development
  extensions. Current Chromium explicitly reports administrator denial.
- **Acceptance:** the intended extension is visibly installed and its background
  worker starts. Record browser version, extension build and policy context.
- **Do not:** bypass the policy or equate Node/ZIP checks with installed behavior.

#### BUILD-001 — Complete the full desktop build

- **State/owner:** blocked on ENV-001; desktop/build engineer.
- **Files:** `apps/download-manager/desktop/app/`, its shared modules,
  `gradle/`, and `tools/development/gradle.py`.
- **Work/check:** run `:desktop:app:compileKotlin` through the helper. Fix actual
  build failures narrowly; retain version/catalog and platform conventions.
- **Acceptance:** exit 0 at a recorded commit, complete logs, and reproducible
  prerequisites. Discover the supported run task with `tasks --all` before
  documenting an app-start command; do not invent one from another framework.

#### ANDROID-001 — Establish Android assembly and test evidence

- **State/owner:** blocked on ENV-001; Android engineer.
- **Files:** `apps/download-manager/android/app/`, shared modules, manifest/build config.
- **Work/check:** run `:android:app:assembleDebug` and
  `:android:app:testDebugUnitTest`; fix genuine setup/compile failures.
- **Acceptance:** identify the new APK, commit/toolchain, and actual executed,
  skipped or absent test counts. Add meaningful tests if no suite exists.
  Assembly alone does not prove install/device compatibility or store approval.

#### CI-001 — Add repeatable validation to implementation PRs

- **State/owner:** ready for assignment; release/CI engineer. **Depends on:** no app-feature decisions for the fixture/browser portion.
- **Files:** new reviewed root `.github/workflows/` configuration, existing test
  entrypoints, optional development documentation. Existing nested workflows are inactive.
- **Work:** frozen browser install with ignored hooks, explicit compatibility
  preparation, strict type tests, Node tests, bundles; original Python fixture
  tests; core transport target with JDK 25/SDK configuration where supported.
- **Acceptance:** an observed clean PR run with counts, working directories,
  lockfile-aware caches and artifact checks. No production secrets, live media,
  unsafe fork execution or recursive inclusion of `AnalyseFuture/`.
- **Boundary:** do not make failing checks green by skipping assertions/types;
  report external prerequisites and optional jobs separately.

#### CORE-001 — Prove durable job lifecycle and output integrity

- **State/owner:** source ready for investigation; downloader engineer; full-app checks depend on BUILD-001.
- **Files:** core `HttpDownloadJob.kt`, `DownloadManager.kt`, `queue/`, `db/`,
  destinations, current desktop tests and the synthetic fixture.
- **Work:** exercise pause, resume, cancellation, retry, app restart, interrupted
  writes, stale ETag/changed content, ignored ranges, corrupt hashes and disk errors.
- **Acceptance:** deterministic tests demonstrate no corrupted completed file,
  unsafe append, lost recoverable state or orphan worker; expected hash failures
  never become successful jobs. Preserve original files during failure simulation.
- **Boundary:** the 11 current tests exercise HTTP transport, not these complete jobs.

#### CORE-002 — Verify queues, concurrency, scheduling and progress

- **State/owner:** source present; downloader/UI engineer. **Depends on:** CORE-001 for recovery assertions.
- **Files:** `downloader/core/queue/`, `downloader/monitor/`, shared home/batch/queue pages.
- **Work:** measure active-worker caps, fairness, retries/backoff, segmented jobs,
  speed limits, duplicate intake, scheduled starts and sleep/clock changes.
- **Acceptance:** bounded concurrency and correct persistent state; UI reports
  actual bytes/stages and unknown totals honestly. Compare segmentation fairly;
  do not advertise arbitrary speed multipliers.

#### SEC-001 — Require authorization for job-creating bridge operations

- **State/owner:** open security work; desktop/extension engineer.
- **Files:** `integration/server/.../Endpoints.kt`, `IntegrationSettings.kt`,
  shared `DefaultAppSettings.kt`, desktop native host, browser backend transports.
- **Work:** review optional authentication around `/add`, pairing, extension ID
  admission, request validation, rate limits and replay/duplicate handling.
- **Acceptance:** unauthorized/hostile-origin requests cannot create jobs; an
  authorized explicit action works exactly once. Add negative tests for each
  supported ingress. Loopback binding is not an authorization boundary.

#### SEC-002 — Minimize permissions and sensitive header forwarding

- **State/owner:** open; browser/security engineer.
- **Files:** browser `Config.ts`, `DownloadLinkInterceptor.ts`, context menus,
  content scripts, manifests, backend/native transports and diagnostics.
- **Work:** define explicit user-controlled policy; apply it to all intake paths,
  redirects and error logging. Review broad host/cookie permissions and defaults.
- **Acceptance:** synthetic secrets reach only the approved destination when
  allowed, never cross origins accidentally or appear in logs; disabled forwarding
  applies consistently. No real account cookies are required for automated tests.

#### SEC-003 — Verify filesystem and resource boundaries

- **State/owner:** ready for investigation; downloader/security engineer.
- **Files:** destination/file-name utilities, incomplete file handling and job workers.
- **Work:** test traversal, symlinks, reserved names, collisions, atomic completion,
  disk exhaustion, malicious metadata and cancellation/resource limits.
- **Acceptance:** user-selected boundaries hold, existing files are not silently
  overwritten, incomplete output is not labelled complete, and failures recover safely.

#### BROWSER-001 — Demonstrate installed browser-to-desktop flow

- **State/owner:** blocked on ENV-002/BUILD-001; browser + desktop engineers.
- **Files:** extension `entrypoint/`, popup/options/context menus, backend, desktop native host.
- **Work:** install the package and approved helper, pair explicitly, send a
  controlled authorized URL, observe progress/error state and duplicate suppression.
- **Acceptance:** one user action produces one completed, verified app job;
  missing helper, wrong version, disconnect and unauthorized caller are handled
  usefully. Record current app/extension commits and the actual test browser.

#### GOV-001 — Record owner-controlled product decisions

- **State/owner:** decision required; project owner, with appropriate advice.
- **Work:** select product identity, original-code license/contribution policy,
  first supported OS/browser pair, distribution model, supported-source policy
  and spending ceiling. Update the decision register rather than invent approval.
- **Acceptance:** explicit dated decisions and unresolved items; no upstream brand
  or public GitHub visibility is treated as a license grant for all material.

### P1: supported beta, media and distribution

#### CORE-003 — Test explicit network/proxy configuration

- **Owner/state:** downloader engineer; source present.
- **Files:** core connection/proxy providers and relevant platform configuration.
- **Work:** exercise direct, system and supported explicit proxy routes with
  controlled endpoints; test authentication, redirects and timeout classification.
- **Acceptance:** configuration precedence works, credentials remain protected,
  certificate verification remains enabled and unsupported routes fail clearly.

#### BROWSER-002 — Validate supported browsers independently

- **Owner/state:** browser engineer; packaged source, installed behavior unrun.
- **Depends on:** BROWSER-001 for the first supported browser.
- **Work:** test Firefox and any approved Edge/Safari expansion against current
  manifest/policy requirements, APIs, permissions and paired host registration.
- **Acceptance:** separate versioned compatibility entries and meaningful runtime
  checks. Do not infer one browser's approval or behavior from another bundle.

#### BROWSER-003 — Maintain and eventually retire declaration compatibility

- **Owner/state:** browser maintainer; current workaround verified.
- **Files:** `scripts/prepare-types.mjs`, compile-only contract tests, package/lock metadata.
- **Work:** track upstream repairs; assess dependency changes deliberately. Retain
  hash/version preconditions and negative examples until a supported fix replaces them.
- **Acceptance:** clean frozen install, strict source/contract checks, 13 current
  browser tests and relevant artifact checks remain green; no runtime protocol
  change or broad type cast replaces the actual repair.

#### SEC-004 — Establish application update trust and rollback

- **Owner/state:** release/security engineer; updater source is not certified.
- **Files:** `shared/updater/`, platform update appliers, installer scripts and desktop packaging.
- **Work:** authenticate release metadata/artifacts, verify before execution,
  replace safely, handle interruption and roll back to a known-good version.
- **Acceptance:** tampered/expired/wrong-platform updates are rejected and a
  failed update does not destroy the working installation. The Gradle checksum
  repair only protects build bootstrap; it does not validate this updater.

#### GOV-002 — Complete shipped dependency, binary and asset notices

- **Owner/state:** release maintainer with owner/legal decisions; incomplete.
- **Files:** component licenses, lock/catalogue data, assets, FFmpeg/other binary provenance.
- **Work:** record exact versions, licenses, notices, source origin and build flags;
  generate the SBOM/NOTICE set for actual shipped components only.
- **Acceptance:** all shipped dependencies/assets are accounted for; copyleft and
  binary obligations are explicitly accepted before adoption. Preserve originals.

#### AUDIT-001 — Keep dependency and diagnostic risks visible

- **Owner/state:** maintainers; browser runtime audit last observed clean.
- **Work:** reassess runtime and development dependencies, test-helper patches,
  redacted diagnostics and exploitability. Separate toolchain/dev findings from
  shipped runtime findings instead of claiming all security is solved.
- **Acceptance:** dated reports, targeted tested fixes and explicit unresolved
  risks. No disabling verification or unreviewed major dependency migration.

#### ANDROID-002 — Verify real device behavior and permissions

- **Owner/state:** Android/mobile QA; depends on ANDROID-001 and SEC-003.
- **Work:** test install/uninstall, share intents, scoped storage/file provider,
  foreground service, notifications, reboot/network changes, battery and mobile
  data controls on a stated device/version matrix; review broad existing permissions.
- **Acceptance:** owned test files are saved safely, interruption/recovery is
  observed and permissions are justified. Desktop helper binaries are not assumed
  to work on Android. Store eligibility needs separate review.

#### UX-001 — Make the existing app workflow understandable

- **Owner/state:** product/desktop/mobile engineer; UI source exists.
- **Work:** verify intake, preview, destination, queue/history/category/search,
  transfer-versus-processing progress, duplicate decisions and useful errors.
- **Acceptance:** representative users finish and recover a controlled job;
  unknown sizes/ETA and unsupported sources are labelled honestly.

#### UX-002 — Accessibility and localization verification

- **Owner/state:** UI/accessibility owner; resources exist, coverage unproven.
- **Work:** keyboard/screen-reader/contrast checks, plural/date/number behavior,
  right-to-left layout where supported, and complete strings on each supported surface.
- **Acceptance:** recorded tasks pass in named locales/devices; no claim of a
  language or accessibility feature solely from a resource file's presence.

#### MEDIA-001 — Integrate a safe local media-processing worker

- **Owner/state:** media engineer; isolated reference proof, active integration planned.
- **Depends on:** CORE-001, GOV-002 and resource/security boundaries.
- **Work:** reuse reviewed FFmpeg concepts for probing, compatible remux, selected
  audio/video presets and batch jobs; use the existing job owner, argument arrays,
  limits, cancellation and safe outputs. Review binaries and platform builds.
- **Acceptance:** deterministic owned fixtures prove correct streams/duration,
  audio/video sync and failures. Preserve original media. Do not import the
  reference's unsafe downloader simply to obtain its converter.

#### MEDIA-002 — Validate permitted streaming and track selection

- **Owner/state:** media/browser engineer; AB/reference source and isolated parsing tests exist.
- **Work:** controlled non-DRM HLS/DASH manifests, separate audio/video, languages,
  subtitles, variants, redirects, segment expiry and live/VOD distinctions.
- **Acceptance:** selected tracks produce the expected playable output, missing
  segments fail clearly and quality reflects available source variants. Parser
  unit success alone is not an end-to-end streaming implementation.

#### MEDIA-003 — Add bounded editing/subtitle workflows

- **Owner/state:** media engineer; product workflow planned.
- **Depends on:** MEDIA-001/002.
- **Work:** approved trim/merge and SRT/VTT import/export workflows using compatible
  formats, clear limits and original preservation.
- **Acceptance:** synchronization, metadata, unsupported formats, cancellation and
  resource failures have synthetic regression coverage; no quality-restoration claims.

#### SOURCE-001 — Define YouTube-first supported-source contracts

- **Owner/state:** owner + connector maintainer; research/permission decision.
- **Work:** define exact permitted/official export workflows, metadata and output
  types. Evaluate the existing optional connector reference only where suitable.
- **Acceptance:** an approved capability entry states platform/content type,
  authorization, adapter/version, formats, tested devices, limits and maintainer.
  YouTube API access or an extractor list does not establish universal downloads
  or browser-store approval.

#### SOURCE-002 — Expand to other sources only with maintainable evidence

- **Owner/state:** connector maintainer; planned after SOURCE-001 and core reliability.
- **Work:** Facebook/Instagram and other selected permitted workflows, direct
  files and allowed playlists/live recordings, one explicit capability at a time.
- **Acceptance:** tested scope and degradation/error handling, not a copied site
  count. Private/deleted/expired/DRM media and unavailable original quality are
  not promised. Do not collect account data or embed secrets in fixtures.

#### RELEASE-001 — Produce supported platform installers

- **Owner/state:** release engineer; blocked on build/security/license gates.
- **Work:** Linux/Windows/macOS packaging with stated OS/architecture support,
  signing/notarization where required, clean install/update/uninstall and release evidence.
- **Acceptance:** independent machine results and verified artifacts/notices.
  Do not run original replacement scripts or publish releases as a shortcut.
  Secret requirements go through secure settings; never paste values into chat.

#### WEB-001 — Build the public information site

- **Owner/state:** web/product owner; planned after identity decisions.
- **Work:** original accessible product pages, supported-capability matrix,
  documentation, install guides, privacy information and verified release links.
- **Acceptance:** responsive/a11y checks and accurate claims. No arbitrary public
  downloader backend or paid deployment is implied by a website task.

### P2: expansion after the reliable core

#### WEB-002 — Evaluate a bounded dashboard or hosted service

- **Owner/state:** web/service owner; decision and design first.
- **Depends on:** trusted device/API contracts, security review, budget and demand.
- **Work:** distinguish a paired local dashboard from uploaded-media/server-side
  processing. ReClip is an interface/reference input, not the production foundation.
- **Acceptance:** authenticated jobs, SSRF-safe network policy, limits, cleanup,
  retention/deletion and measured cost. No public deployment without owner instruction.

#### AUTO-001 — Versioned CLI/API and job-list automation

- **Owner/state:** engine/API maintainer; source opportunities, product contract open.
- **Depends on:** SEC-001/002 and proven job lifecycle.
- **Work:** review existing CLI/local server before creating replacements; define
  stable import/export contracts, idempotency, error semantics and migration behavior.
- **Acceptance:** authenticated bounded automation with compatibility tests and
  clear permission/destination handling; no second state database or queue.

#### AUTO-002 — Remote devices and plugin ecosystem research

- **Owner/state:** architecture/security owner; optional future scope.
- **Work:** trusted-device pairing, sync conflict/deletion semantics, plugin
  permissions/isolation/update trust and separate mobile/iOS feasibility if requested.
- **Acceptance:** a small reviewed prototype with named maintainer, costs and
  threat model before a production commitment. An account login is not secure sync.

#### AI-001 — Evaluate useful, optional AI for owned/licensed media

- **Owner/state:** AI/product owner; no AI implementation established.
- **Depends on:** reliable media/library foundations and owner-approved models/costs.
- **Work:** opt-in transcription, correction, transcript/semantic search, tags,
  chapter or subtitle translation suggestions. Prefer local processing where practical.
- **Acceptance:** representative accuracy/latency/resource tests, original retention,
  deletion/export, explicit cloud consent and non-AI fallbacks. Untrusted media text
  cannot command privileged actions. No hidden uploads or guaranteed breakthroughs.

#### RESEARCH-001 — Revisit one-, two-, and three-to-five-year opportunities

- **Owner/state:** owner/maintainers; conditional research, not a delivery promise.
- **Work:** after each release review demand for more connectors/devices, a personal
  library, AI improvements, teams, plugins and optional services. Reuse the
  [detailed vision](AnalyseFuture/PROJECT_VISION_AND_FUTURE_ROADMAP.txt).
- **Acceptance:** each funded feature has a maintainer, prototype, dependency/cost
  assessment and measurable value. AI cannot guarantee access, authentic missing
  detail, unlimited speed or permanent support for every source.

## 6. Commands and evidence another tool should use

Start from the **repository root** and read component instructions before work.
The prepared cloud used JDK 25, Gradle 9.8, Android platform 37.0/build-tools
37.0.0. A different machine must install the declared prerequisites and set
appropriate `JAVA_HOME`/`ANDROID_HOME`; do not change `HOME` to work around permissions.
The helper uses writable workspace caches and inherited proxy/system trust settings.

```sh
# Existing fixture and preservation commands
bash tools/development/setup.sh --run-tests
python3 tools/repository/verify_preservation.py

# Real HTTP transport tests, independent of the blocked full-app graph
python3 tools/development/gradle.py :downloader:core:desktopTest \
  --configure-on-demand --no-daemon --max-workers=4

# Full-app targets: previously attempted, blocked by required JitPack access
python3 tools/development/gradle.py :desktop:app:compileKotlin \
  --no-daemon --max-workers=4
python3 tools/development/gradle.py :android:app:assembleDebug \
  :android:app:testDebugUnitTest --configure-on-demand --no-daemon --max-workers=4
```

From `apps/browser-extension`:

```sh
npm ci --ignore-scripts
npm test
npm run typecheck
npm run build
npm run pack:chrome
npm run pack:firefox
npm run pack:src
npm audit --omit=dev
```

Check the generated ZIPs for nonempty content, valid CRC, correct local manifest
references and absence of unrelated archives/dependencies. They are generated
outputs, not source files to commit. Package success does not prove browser approval.

For references, follow [tests/references/README.md](tests/references/README.md).
ReClip checks need the documented isolated Flask environment; subprocess/thread
work is mocked. MediaGrabber checks point at a separately installed copy using
`MEDIA_GRABBER_VALIDATION_ROOT`. Do not add the examples to a production workspace.

For every check record: current commit, command, working directory, toolchain,
exit code, executed/passed/failed/skipped counts, artifact identity, and limits.
`NO-SOURCE`, exit 0 with zero tests, bundles and actual application flows are
different outcomes. Retry after a meaningful change, not repeated unchanged denial.

## 7. External-tool PR workflow and my review role

The owner's latest instruction is that **other implementation tools create
pull requests**, and review happens before their work enters `main`. This
supersedes the old global “no PRs” instruction for those future tasks.
The existing direct-main authorization is used only to finish this handoff update.

1. Owner assigns one task ID or a clearly bounded combination with dependencies.
2. Tool fetches current `main`, preserves user changes, reads this handoff and
   relevant component instructions, then creates a task branch and PR to `main`.
3. Commit reviewable progress frequently and push the task branch during active
   work. Do not push external implementation directly to `main`, force-push,
   rewrite published history or remove backup refs. Merge updated `main` into
   a published task branch rather than force-pushing rewritten commits.
4. Make a narrow change using existing implementations. Preserve uncertain or
   superseded material with original paths/reasons; never archive live secrets.
5. If editing a file used as original evidence, retain the original first and
   update preservation/member mappings correctly. Never replace an original
   hash with the new content hash to disguise a change.
6. Run relevant checks; document blockers and actual counts. Update the task
   state and current evidence. Do not mark a task Done from source inspection alone.
7. Provide the PR link here or ask me to check the repository. I can review the
   current PR code/evidence during an active conversation, report findings and
   request focused corrections. Review applies to the recorded PR commit; new
   commits need reassessment.
8. Owner authorizes merge/release separately. Monitoring/review is not automatic
   permission to merge, deploy, publish artifacts or send external messages.

**Monitoring limit:** no continuous watcher or scheduled PR-review service is
installed. I cannot inspect new PRs between messages. Future CI can provide
automatic checks after CI-001 is implemented; human/assistant review still
requires a review request. No PR link has been supplied for review in this handoff.

### Required PR description

```text
Task ID and concrete problem:
Base commit and current PR commit:
Behavior before -> after:
Changed feature owners/files:
Reuse/consolidation choice and preserved originals:
Dependency, security, permission and licensing implications:
Commands + working directories + exit codes + test counts:
Artifacts and runtime evidence:
Blocked, skipped and unrun checks:
Remaining risks and rollback/continuation:
Task-board/status documentation updated:
```

### Review checklist

- [ ] Scope matches the assigned task; no unrelated rewrite or second engine.
- [ ] Feature ownership, imports, source sets, assets and internal links remain valid.
- [ ] Preserved originals, license/NOTICE files and historical evidence remain recoverable.
- [ ] Tests exercise behavior and relevant negative cases; no removed assertions,
  disabled type/security checks, zero-test success claims or stale result files.
- [ ] Dependency changes and compatibility patches are reviewed; TLS/checksum and
  update integrity remain enabled. No credentials/private media in source or logs.
- [ ] Browser/API/filesystem/resource boundaries match the stated trust model.
- [ ] `AnalyseFuture`, caches and source ZIPs stay outside production imports/builds.
- [ ] Build, package, installed UI and full integration outcomes are distinguished.
- [ ] Current PR commit is the one reviewed and checked; all blockers are explicit.
- [ ] Owner-controlled decisions and merge/release authorization are respected.

### Copyable assignment for another tool

```text
Repository: kawakaze430/video-downloader
Read PROJECT_HANDOFF.md, AGENTS.md, PROJECT_STRUCTURE.md and the current
validation evidence. Task: [one task ID assigned by owner].

Use existing code and the documented feature owner. Create a task branch and
PR against main. Do not push implementation directly to main, force-push,
rewrite published history or delete valuable files. Preserve uncertain work
and original evidence correctly under AnalyseFuture, excluded from production.

Implement only this task, repair affected references, and run meaningful checks.
Report exact commands, commits, counts, artifacts and all blocked/unrun work.
Do not weaken tests/types/TLS/checksums or invent product readiness. Update the
handoff task status/evidence. Open the PR with the required description and
return its URL for review; do not merge or deploy without owner authorization.
```

## 8. How to keep this handoff current

On each accepted implementation, update the relevant task with its state,
owner, PR, commit, evidence and remaining work. Update the feature crosswalk
only to the scope actually verified. Retain older dated reports instead of
rewriting them as if new tests had always passed. Regenerate file/folder guides
when paths change. Do not interpret this proposed task board as approval to
implement all features, select a license or spend money in one operation.

The next developer should be able to answer: what exists, what was checked,
what remains uncertain, which task is next, and how its success will be proved.
