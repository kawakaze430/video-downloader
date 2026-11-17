# M0 audit log — first engineering pass

**Initial pass:** 13 November 2026. **Follow-up:** 15 November 2026.

**Status:** IN PROGRESS — 17 study repositories triaged at pinned commits, both upstream extension bundles build, local Python fixture tests pass. No user-facing Downloader application has been imported or released.

**Scope:** In-depth initial source audit of AB desktop/extension, targeted source investigation of 15 additional candidates, reproducible build probes, and original test fixture work. Full dependency licensing and third-party binary verification remain open.

This log distinguishes **observed source/build evidence** from proposed feature work. It is intended to let a new developer or Codex agent resume without spending time rebuilding features upstream already supplies.

## Reproducible source pins

| Candidate | Source | Checked-out commit | Declared license | Assessment |
| --- | --- | --- | --- | --- |
| Desktop base | [amir1376/ab-download-manager](https://github.com/amir1376/ab-download-manager) | [68f0ea6e8ba5cbeb02c92342cd3bf7475378ae68](https://github.com/amir1376/ab-download-manager/commit/68f0ea6e8ba5cbeb02c92342cd3bf7475378ae68) | Apache-2.0, root LICENSE | **Strong provisional base**; desktop runtime/test not yet verified |
| Browser companion | [amir1376/ab-download-manager-browser-integration](https://github.com/amir1376/ab-download-manager-browser-integration) | [bf6811dd8a3ee2b47b94d70e13c2c7e70be7be05](https://github.com/amir1376/ab-download-manager-browser-integration/commit/bf6811dd8a3ee2b47b94d70e13c2c7e70be7be05) | Apache-2.0, root LICENSE and package.json | **Builds for Chrome**; security review still needed |

The two directories were shallow-cloned for inspection only. **Neither upstream codebase is committed into the Downloader project.** Brand assets, bundled tools, transitive dependencies and notices require separate review even when a root repository declares Apache-2.0.

## Build evidence

| Check | Environment/command | Observed result |
| --- | --- | --- |
| Extension dependency install | Linux, Node 24.22.1, npm 11.9.0; from browser integration clone: `npm ci --ignore-scripts --no-audit --no-fund` | **PASS**, 535 packages installed from existing lockfile |
| Chrome MV3 extension build | Same clone: `npm run build:chrome` | **PASS**, Vite built 452 modules and emitted `dist/chrome/manifest.json` in 6.87 s |
| Firefox extension build | Same clone: `npm run build:firefox` | **PASS**, Vite built 453 modules and emitted `dist/firefox/manifest.json` in 20.09 s; browser install not tested |
| Standalone TypeScript validation | Same clone: `npx tsc --noEmit` | **FAIL**, exit code 2: missing `~/backend/NativeMessaging`; manifest `author` type mismatch; `webext-bridge`/`type-fest` generic/type errors. Bundling success does **not** imply type correctness. |
| Actual Chrome install and desktop handoff | Not attempted; full desktop application not built | **NOT VERIFIED** |
| Upstream extension automated tests | No `test` script in inspected `package.json` | **NOT AVAILABLE IN PACKAGE SCRIPTS**; add project tests |
| Gradle wrapper bootstrap (desktop prerequisite) | Linux, OpenJDK 21.0.13; in desktop clone: `./gradlew --version` | **BLOCKED**, exit code 1: wrapper requests `https://services.gradle.org/distributions/gradle-9.8.0-bin.zip` but fails `java.net.SocketException: Network is unreachable`. No Gradle desktop compile attempted. |
| Desktop unit/integration tests | Tests not run | **NOT VERIFIED** |

Extension build warnings: deprecated Vite CommonJS API, older Browserslist/caniuse-lite data, several deprecated npm packages, and a `process` module browser-externalization warning. These are not build failures, but should be tracked in dependency maintenance and a clean-browser smoke test. The independent typecheck failure **is** a quality blocker for adopting this code as-is.

## What the sources already provide

| Area | Evidence in pinned source | Reuse decision |
| --- | --- | --- |
| Download engine | Desktop repo has `downloader/core`, `downloader/monitor`, `desktop/app`, `shared/app` modules and Gradle projects | Reuse candidate; validate actual downloading, resume, history and failure handling with controlled fixtures |
| User-configurable concurrency/retries | `shared/app/.../DefaultAppSettings.kt` exposes `maxConcurrentDownloads = 3`, `maxDownloadRetryCount = 3`, thread count and speed-limit controls | Prefer reuse; tests still needed |
| Desktop HTTP API | `integration/server/.../Integration.kt` binds to `127.0.0.1`; `Endpoints.kt` has `POST /add`, `POST /ping`, `GET /queues` | Adapt and harden, not greenfield |
| Native browser messaging | Extension `src/backend/nativemessaging/NativeMessagingTransport.ts` and `src/backend/Backend.ts` | Reuse, test host registration, origin validation and handoff |
| Fallback HTTP extension integration | Extension `src/backend/HttpApi.ts` invokes localhost API and can attach configured key | Audit auth and origin handling; require secure pairing |
| Chrome Manifest V3 | Extension `src/manifest/manifest.chrome.ts`; emitted `dist/chrome/manifest.json` has `manifest_version: 3` | Existing MV3 foundation; packaging and browser store review pending |
| HLS link interception | Extension `src/linkgrabber/DownloadLinkInterceptor.ts` matches `.m3u8` patterns and labels media type `hls` | **Do not build a second HLS detector yet**; test permitted non-DRM fixtures |
| Download context menus | Extension source and README describe user-initiated download actions | Prefer reuse; manual UX test pending |
| Site-specific extractors | No broad verified site-support audit in this pass | No promised support; enforce rights/platform-policy review first |

## Security findings — must address before release

**SEC-001 (high-priority design blocker): the upstream loopback API permits unauthenticated requests by default.** In `shared/app/src/commonMain/kotlin/com/abdownloadmanager/shared/storage/appsettings/DefaultAppSettings.kt`, `apiEnabled` defaults to `true` while `apiAuthEnabled` defaults to `false`. The server `integration/server/.../Endpoints.kt` explicitly skips API-key validation on some routes when `apiKeyEnforced` is false; the app binds to loopback `127.0.0.1`. For **our proposed distribution**, make authentication and origin/pairing protections mandatory for downloaded jobs, test malicious webpage requests, and consider disabling HTTP fallback if safe native messaging suffices. Loopback binding alone is not authentication. No exploit is asserted or tested here.

**SEC-002 (review before public Chrome distribution): the upstream MV3 manifest requests broad access.** The built extension contains `host_permissions: ["*://*/*"]`, matches all HTTP(S) pages with its content script, and asks for `cookies`, `webRequest`, `downloads`, `nativeMessaging`, `tabs`, `notifications`, `storage` and `contextMenus`. Establish feature-to-permission justification, reduce scope where feasible, test data minimization and verify store compliance. Do not submit the unreviewed upstream package as our product.

**SEC-003 (user media and URL policy):** Header/cookie forwarding, redirects, private-network requests, DRM, protected sources and platform terms must be reviewed. Only test with content the owner controls or has explicit permission to process. No YouTube extraction demo is a release gate.

## Reproducible blocker handoffs

### BLK-001: Gradle 9.8 bootstrap network restriction

~~~text
Task ID: A05/A06
Environment: Linux / OpenJDK 21.0.13 / pinned desktop clone
Command: ./gradlew --version
Observed: Downloading https://services.gradle.org/distributions/gradle-9.8.0-bin.zip
          java.net.SocketException: Network is unreachable (exit 1)
Expected: Gradle wrapper starts, allowing targeted desktop compile/tests.
Tried: Confirmed source checkout, JDK version and Gradle distribution URL.
Suggested fix for Codex: use an environment where that download is explicitly allowed,
  or provision the exact verified Gradle 9.8 distribution into a local cache;
  then run narrow desktop tests/build. Do not disable TLS verification or use
  arbitrary mirrors and do not claim a desktop build passed.
~~~

### BLK-002: Upstream extension does not typecheck

~~~text
Task ID: A09 / future B01
Environment: Linux / Node 24.22.1 / npm 11.9.0 / pinned extension clone
Commands: npm ci --ignore-scripts --no-audit --no-fund
          npm run build:chrome
          npm run build:firefox
          npx tsc --noEmit
Observed: Both bundler builds pass, but tsc exits 2 with:
  TS2307 Cannot find module '~/backend/NativeMessaging' (src/backend/BackendProvider.ts)
  TS2322 manifest 'author' type incompatible (chrome and Firefox)
  TS2344/TS2305 type errors in node_modules/webext-bridge (incl. type-fest Jsonify)
Expected: Both builds and a separate TypeScript typecheck pass without masking errors.
Suggested fix for Codex: audit actual source import and compatible dependency/type
  versions; write targeted changes in an approved fork after owner license decision.
  Do not blanket-disable typechecking or silently skip library checking as a release fix.
~~~

## Reuse versus build — early matrix

| Component | Current recommendation | Additional evidence/gap |
| --- | --- | --- |
| Core download engine and desktop UI | **Reuse/adapt AB candidate** | Desktop compile, tests, dependency license scan, Windows packaging |
| Chrome browser bridge | **Reuse/adapt AB extension** | Security hardening, versioned handoff, browser installation test |
| Basic HLS detection | **Reuse existing extension logic first** | Verify with local, authorized HLS fixtures; no DRM bypass |
| Queue/schedule/history | **Validate source features before writing** | Controlled fixtures, restart recovery, UX inspection |
| Local conversion/transcoding | **Integrate FFmpeg later** | Binary/license flags, codec availability, sandboxing |
| Website | **Build original landing site or audit ReClip after scope decision** | Marketing-only vs local companion vs hosted service changes security and cost substantially |
| Optional source connectors | **Defer** | Permissions, site policies, package licenses and tests |
| Custom security tests and direct-download fixtures | **Build original tests for our acceptance gates** | M1/M2 work after base approval |

## Next ordered audit tasks

1. **A03/A05/A06:** resolve BLK-001 in a permitted environment, audit desktop dependency notices and run a narrowly scoped Gradle desktop build/tests with exact failure logs; do not provision paid infrastructure.
2. **A08/A10:** audit message validation and localhost API threat model; verify extension handoff against a locally running app with user-controlled file URLs.
3. **A11–A17:** pin/audit ReClip, MediaGrabber, HLS Downloader, FFmpeg, yt-dlp and alternative feature references. Do not mix incompatible-licensed source.
4. **A18–A21:** implement legal synthetic HTTP fixtures, establish baseline benchmarks and revise the feature matrix and architecture decision based on results.
5. Request owner decisions **G03–G06** and **G08** before any code import, public release, hosted deployment or paid workload.

## Copyable Codex continuation instruction

> Read AGENTS.md, docs/IMPLEMENTATION_CHECKLIST.md and docs/M0_AUDIT.md. Continue from A03/A05/A06 using the two pinned upstream SHAs above. Reproduce and fix BLK-001 (Gradle network/toolchain) in an authorized environment and investigate BLK-002 (extension TypeScript errors). Do not clone arbitrary HEAD or import upstream source into this project until the owner decides branding/license/base. First report exact desktop build/test commands, dependency-license risks and failures. Flag authenticated loopback/native pairing as mandatory. Update checked items only with evidence. No paid cloud/GPU or public deployments, and no unsupported YouTube/DRM functionality.

**Current product status:** The repo contains documentation and audit evidence, not a runnable Downloader application. Chrome extension build success is evidence about the **upstream candidate**, not our product.

## First original project code: local download fixture

The repository now includes [tools/fixtures/http_fixture.py](../tools/fixtures/http_fixture.py), a dependency-free loopback server with deterministic 16 KiB content, Range/206, unsatisfiable 416, a Range-disabled path and SHA-256 validation; see its [usage guide](../tools/fixtures/README.md). It is **test infrastructure**, not a downloader or imported third-party implementation.

**Initial baseline (13 November):** `python3 -m unittest discover -s tests -v` — **9 tests PASS** in 0.597 seconds on Linux. The fixture has since been extended; see the follow-up evidence below. Neither the fixture nor an upstream extension bundle is a usable desktop application.

## 15 November 2026 follow-up: source triage, security and original code

The [17-repository matrix](REUSE_DECISION_MATRIX.md) records an exact observed default-branch commit, build/source locations, root license declarations and an individual decision for each candidate. The two **conditional** primary recommendations remain AB Download Manager (68f0ea6e8ba5cbeb02c92342cd3bf7475378ae68) and its AB Browser Integration companion (bf6811dd8a3ee2b47b94d70e13c2c7e70be7be05). There is **no authorization or verified app build** yet. The [build-start plan](BUILD_START_PLAN.md) defines the incremental architecture, M0/M1/M2 gates and exact approvals needed.

### Reproducible follow-up commands and outcomes

| Location | Command / source observation | Result |
| --- | --- | --- |
| Downloader repo | `python3 -m unittest discover -s tests -v` | **PASS: 14/14** deterministic fixture tests, approximately 1.12 s, Python 3.12.14 on Linux |
| Downloader repo | `python3 -m compileall -q tools tests` | **PASS** |
| AB extension pinned checkout | `npm ci --ignore-scripts --no-audit --no-fund` | **PASS** with lockfile; 535 installed packages |
| AB extension pinned checkout | `npm run build:chrome` | **PASS**, Vite 452 modules, approximately 2.64 s |
| AB extension pinned checkout | `npm run build:firefox` | **PASS**, Vite 453 modules, approximately 2.64 s |
| AB extension pinned checkout | `./node_modules/.bin/tsc --noEmit` | **FAIL**, TS2307 missing NativeMessaging import, TS2322 manifest author mismatch, TS generic/type-fest issues (issue #5) |
| AB extension pinned checkout | `npm audit --omit=dev --audit-level=moderate --json` | **FAIL (exit 1): two high advisories**, lodash GHSA-r5fr-rjxr-66jc and zod range <4.6.6, from npm audit output; assess affected runtime paths and lockfile remediation in an approved fork. An advisory is not proof of exploitability. |
| AB desktop pinned checkout | `./gradlew --version` | **BLOCKED**: official Gradle 9.8 binary download encounters `java.net.SocketException: Network is unreachable` (issue #4); no desktop compile/test run |
| AB desktop pinned source | gradle/wrapper/gradle-wrapper.properties and gradle.properties | Wrapper **9.8.0**, `jvm.toolchain=25`; current probe JDK 21 does not satisfy requested toolchain. Validate available JDK 25 distribution in permitted environment. |

The original fixture now supports optional TLS with a caller-supplied certificate, verified HTTPS requests (including rejection of an untrusted certificate), matching/mismatched If-Range ETags, relative redirect, intentionally truncated response, and denial of excessively long Range offsets. It binds only to 127.0.0.1 and does not fetch user-provided URLs or disable certificate validation. A small [fixture-only GitHub Actions workflow](../.github/workflows/fixture-tests.yml) is added with pinned checkout/setup-python actions and read-only permissions; **the workflow is not yet proven by an observed hosted GitHub run**. M1 runtime integration and benchmarks remain undone.

### Security decisions to preserve

- **High:** upstream AB `apiEnabled=true` but `apiAuthEnabled=false` by default; integration `/add` may skip key enforcement and can feed silent-import flow. The local bridge must authenticate and authorize job-creating requests; loopback binding does not suffice. Native messaging is preferred for the first slice (issue #6).
- **High:** extension's broad `*://*/*`, cookies, webRequest, nativeMessaging and content-script access require privacy minimization and negative-origin tests before packaging.
- **Supply chain:** two high production-dependency advisories appeared in a pinned upstream npm audit. Preserve evidence and evaluate targeted upgrades without bypassing TypeScript checks.
- **Website:** ReClip's Flask backend runs submitted URLs via yt-dlp and keeps jobs in process memory. No adequate default hosted SSRF, authentication, quota or persistence guarantees were evident in inspected code; **reference its UX only**, pending an original safe design.
- **Licensing:** MediaGrabber's bundled Windows FFmpeg is identified as GPLv3 in its third-party notices; FFmpeg's LGPL/GPL behavior is build dependent. Gopeed, aria2, Cobalt, MeTube, Pinchflat, Tube Archivist and other GPL/AGPL examples are not silently importable into an unlicensed product.
- **Policy:** support user-owned/expressly permitted downloads, review browser-store requirements, and reject DRM/protected source circumvention. Do not promise general YouTube integration.

**Open work:** exact transitive SBOM and NOTICE inventory, full desktop Java 25 + Gradle boot/build/tests, extension typecheck repair in an owner-approved fork, authentic Chrome/native handoff, user decisions G03–G06/G08, and platform policy review. All remain unchecked in the [implementation checklist](IMPLEMENTATION_CHECKLIST.md).
