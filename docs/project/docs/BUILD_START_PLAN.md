# Build-start plan — verified M0 foundation, then M1 and M2

**Audit date:** 15 November 2026. **Status:** M0 in progress, not yet approved for importing third-party application code.

## 1. What actually exists in our repository

The inspected local checkout initially pointed at main commit **3509d5158630416b656508e2fe35a57265148752** with a clean worktree. No integrated desktop application, extension, media processor or website exists in this repository. Files consist of project documents, issue/PR templates, and an original Python HTTP fixture and test suite. This task adds **original fixture functionality and a small test workflow**, not an application release.

| Area | Existing state | Direct evidence |
| --- | --- | --- |
| Product plan/feature inventory | Detailed but proposed | README, PRODUCT_VISION, FEATURE_MATRIX, ROADMAP |
| License/brand/platform | Owner decisions missing | DECISIONS ADR-009/010/011 and checklist G03–G06 |
| Original runtime source | Python loopback HTTP fixture only | tools/fixtures/http_fixture.py |
| Automated tests | Baseline 9 tests passed before edits; expanded to **14 passing** | python3 -m unittest discover -s tests -v |
| HTTPS test route | Added to fixture, using caller-supplied cert/key and ephemeral cert generation in tests | create_server(... certfile, keyfile), HTTPSFixtureTests |
| Controlled failure handling | Added If-Range, abrupt EOF and relative redirect | fixture endpoints/tests |
| CI | New minimal Python fixture workflow, not full app CI | .github/workflows/fixture-tests.yml |
| Desktop executable / Chrome-to-app demonstration | **Not implemented** | No app source imported; no Windows install evidence |
| Cloud/service/backend | **Not implemented** | No deployment, credentials or paid resources |

### Current repository tree (conceptual)

~~~
.github/
  ISSUE_TEMPLATE/
  PULL_REQUEST_TEMPLATE.md
  workflows/fixture-tests.yml       # new, tests only
docs/
  ... existing vision, security, audit, checklist ...
  REUSE_DECISION_MATRIX.md           # 17-candidate evidence and selections
  BUILD_START_PLAN.md                # this document
tools/
  fixtures/http_fixture.py          # existing and extended original code
  fixtures/README.md
tests/
  test_http_fixture.py              # original tests, extended
README.md  AGENTS.md  CONTRIBUTING.md  SECURITY.md
~~~

Do not create empty apps/desktop, apps/extension, packages or a new job engine solely to imitate a future monorepo. Preserve the selected AB layout in an **approved fork or pinned subtree** when adoption is authorized. We can place it under an app-level boundary later without renaming every Kotlin module.

## 2. Foundation recommendation

Select exactly two primary upstream projects, conditionally:

1. [AB Download Manager](https://github.com/amir1376/ab-download-manager) at **68f0ea6e8ba5cbeb02c92342cd3bf7475378ae68**, for Kotlin desktop engine, queue, persistence, UI and native host.
2. [AB Browser Integration](https://github.com/amir1376/ab-download-manager-browser-integration) at **bf6811dd8a3ee2b47b94d70e13c2c7e70be7be05**, for MV3 Chrome, Firefox, existing request protocol and browser UX.

Why: a designed integration already exists, the engine has implementation evidence (not merely README claims), and both roots declare Apache-2.0. The alternative Parabolic uses C#/.NET 10 + yt-dlp workflows rather than AB's general direct-file engine; Gopeed uses Go/Flutter under GPL-3.0; Motrix uses Electron/aria2 with extra licensing/runtime concerns. ReClip's current Flask backend accepts arbitrary URLs and is unsuitable as a public service without major SSRF/auth/resource controls.

Evidence for all 17, commit pins and reasons are in [REUSE_DECISION_MATRIX.md](REUSE_DECISION_MATRIX.md). This selection is **not an authorization to copy source code**.

## 3. Proposed desktop-first architecture

~~~mermaid
flowchart TD
    B["Chrome user action"] --> E["Extension background"]
    E --> N["Native messaging host"]
    N --> C["Desktop integration controller"]
    U["Desktop UI"] --> C
    C --> J["AB job/queue engine"]
    J --> D["Persisted jobs and download parts"]
    J --> F["User-approved local files"]
    F --> V["Integrity checks and safe finalize"]
~~~

Existing native messaging manifests already restrict the Chrome extension origin and Firefox extension ID. **Keep that boundary.** The desktop integration handler currently supports both GUI import and a separately authenticated headless API. A browser-originated request must be treated as untrusted input even when native messaging authenticated the extension.

**Local HTTP bridge:** The upstream server binds 127.0.0.1 and skips authentication when its optional auth setting is disabled; default is disabled. The extension currently prioritizes HTTP fallback unless native messaging is already connected. For our intended release, require authenticated, version-aware pairing for *every* job-creating route, and prefer native messaging for the first slice. Either remove the unauthenticated HTTP fallback or make it independently secure. See issue #6.

**Not in the first slice:** hosted conversion, Redis, PostgreSQL, arbitrary remote job control, AI features, public source extractors and billing. None is needed to prove local file reliability.

### Proposed job lifecycle

~~~mermaid
stateDiagram-v2
  [*] --> Queued
  Queued --> Resolving
  Resolving --> Downloading
  Downloading --> Paused
  Paused --> Queued
  Downloading --> Verifying
  Verifying --> Complete
  Resolving --> Failed
  Downloading --> Failed
  Verifying --> Failed
  Failed --> Queued: bounded retry
  Queued --> Cancelled
  Downloading --> Cancelled
  Complete --> [*]
  Cancelled --> [*]
~~~

**Compatibility rule:** AB already has download/job/queue model classes and a native messaging request protocol. The first implementation should **adapt its existing shapes**, not create a competing engine or prematurely assert that a newly imagined JSON format is implemented. Before B02, define the smallest version/feature negotiation and compatibility tests around the existing message shapes.

**New bridge validation rules to implement after adoption approval:**

- Only the pinned, user-installed extension ID may invoke native actions; parse a bounded JSON message, reject unknown actions and schema-invalid inputs.
- Require user intent, preferably a GUI confirmation for the first authorized direct URL. Reject silently submitted jobs absent an explicit opt-in and authenticated pairing.
- Restrict HTTP fallback by strong tokens, origin/Host checking, short timeouts, replay controls and no wildcard CORS; consider disabling it entirely for beta.
- Validate allowed URL schemes and redirects, avoid private/loopback fetches when proxying arbitrary remote URLs, and never accept an untrusted absolute destination path.
- Sanitize filenames, handle collisions and disk-full/permissions errors, cap concurrency and retries, and never log cookies, Authorization headers or private links.
- Persist job state before acknowledging creation; success requires complete/verified output rather than only an HTTP 200 response.

## 4. M0 exit work — explicit order

| Order | Task / checklist | Acceptance and evidence | Current status |
| --- | --- | --- | --- |
| 1 | Check upstream provenance A01/A07 | Exact commit and declared root license; verify no surprise branch switch | **PASS** for both pins |
| 2 | Inspect engine/queue/bridge source A02/A04/A08 | Reuse map with code paths; separately identify tests not yet run | **PARTIAL**, source evidence found, runtime unverified |
| 3 | Desktop JDK/Gradle setup A05 | Gradle 9.8 boots; JDK 25 toolchain available; exact desktop task succeeds | **BLOCKED** on official release-asset egress, issue #4 |
| 4 | Desktop tests A06 | Targeted Kotlin/desktop tests run with results; controlled file transfer | **NOT RUN**; upstream test suites to enumerate |
| 5 | Extension bundling and types A09 | npm ci, Chrome/Firefox builds, tsc all pass | **PARTIAL**: builds PASS, typecheck FAIL, issue #5 |
| 6 | Bridge threat model A08/A10 | Native protocol and HTTP rules documented; negative test plan | **PARTIAL**, design/issue #6, no runtime handoff |
| 7 | 15 alternatives A11–A17 | Source triage, exact branch pins, root licenses and dependency risk list | **PARTIAL**, documented in reuse matrix; no full SBOM/build |
| 8 | Fixture-based benchmark A18 | Controlled HTTPS/Range/error cases and actual app throughput/integrity data | **PARTIAL**: fixture tests PASS, app not available |
| 9 | Reuse matrix and decision A19–A21 | One pair recommended; owner explicitly approves decisions | **RECOMMENDED**, owner signoff pending |

Desktop bootstrap: with Linux/OpenJDK 21, running ./gradlew --version in the pinned upstream tree still fails with java.net.SocketException: Network is unreachable. Direct curl reaches services.gradle.org but its Gradle 9.8 binary redirect to GitHub release assets is not permitted from this environment. Do not lower TLS integrity, use untrusted mirrors, or mark the desktop build as passing. The root gradle.properties separately specifies jvm.toolchain=25, so **JDK 25 is another prerequisite to verify**.

Extension reproducible checks:

~~~sh
npm ci --ignore-scripts --no-audit --no-fund
npm run build:chrome
npm run build:firefox
./node_modules/.bin/tsc --noEmit
~~~

The first three **PASS** with the pinned lockfile. TypeScript **FAILS**: src/backend/BackendProvider.ts references a missing NativeMessaging module; Manifest author type mismatch; webext-bridge declaration errors including its type-fest Jsonify import. The branch builds are **not proof of type safety or runtime compatibility**. Fix only in an owner-approved fork, with targeted, non-suppressive changes.

## 5. M1 smallest working desktop slice — after owner approval

1. Select a fork/subtree strategy that retains AB upstream provenance and Apache-2.0 notices. Record original commit and any changes.
2. Reproduce a clean desktop build (Linux first; Windows 11 target) with exact JDK/Gradle/Android-disabled configuration. Keep existing modules and DB implementation.
3. Use our Python fixture's local HTTPS endpoint with a trusted temporary test cert. The app must download a known SHA-256 file to a user-approved directory.
4. Test actual progress (bytes/speed), pause/resume (Range+If-Range), retry after truncated response, cancellation, 302 redirect and no-range safe restart.
5. Test filename/path validation, collision, disk-full behavior, finite retries and failure messages.
6. Kill/restart app and verify persisted partial state and safe output finalization; compare SHA-256.
7. Add focused integration tests for each scenario, document clean-build commands and update the checklist only where behavior passed.

**M1 gate:** reproducible Windows 11 binary, authorized HTTPS file download with real progress, verified output checksum, safe cancellation/recovery and no required internet video source.

## 6. M2 smallest secure browser slice — after M1 and owner approval

1. Fork the pinned AB extension without reimplementing its existing popup/context-menu code.
2. Fix TypeScript errors, package MV3 Chrome and document exact compatible extension/desktop versions.
3. Pair the browser to the native host with registered extension ID, bounded messages and explicit user action.
4. Send one permitted HTTPS fixture job and observe desktop acknowledgement and progress.
5. Reject unknown extension IDs, forged origins, unauthenticated localhost HTTP requests and malicious paths.
6. Review broad host/cookie/webRequest permissions; minimize them without falsely claiming those features work.
7. Add Chrome install/reload/update smoke test on Windows 11. Do not claim Chrome Web Store eligibility without a policy review.

**M2 gate:** one user action creates exactly one authenticated desktop job; negative tests fail closed; no unauthorized YouTube or protected media features.

## 7. Owner approvals required before imports/releases

1. **G03:** public product name, identity and trademark/logo policy.
2. **G04:** original-code license (open-source or proprietary), distribution and contributor terms.
3. **G05:** first target Windows 11 + Chrome (recommended); secondary OS/browser priorities.
4. **G06:** scope: authorized direct downloads first, media tools later, optional web service later.
5. **G08:** CI/cloud usage budget and whether public Actions PR checks may run.
6. **Gate M0:** approve the exact two upstream commits and Apache-2.0/third-party notice strategy after dependency audit.
7. **ADR-014:** content source/rights policy and public store/distribution constraints.

Until those decisions are recorded, do not import the full upstream app, claim ownership of third-party code, publish a product, or create paid resources.

## 8. Cost-conscious continuation prompt

> Continue M0 for Downloader using docs/REUSE_DECISION_MATRIX.md, docs/BUILD_START_PLAN.md and docs/M0_AUDIT.md. Resolve issue #4 only via an environment with permitted verified Gradle 9.8 and JDK 25 binaries; otherwise record the exact blocker. Resolve issue #5 in an approved isolated upstream fork, without hiding TS errors. Harden the protocol described in issue #6 only after owner decisions. Preserve the current original Python fixture, run its 14 tests, and review the manual/PR fixture CI. Do not deploy or import GPL/AGPL code, and do not claim M1/M2 done without a real Windows + Chrome integration test.

**Definition of progress:** new code, tests, measured results and durable audit evidence. A passing upstream extension build alone does not make our Downloader application runnable.
