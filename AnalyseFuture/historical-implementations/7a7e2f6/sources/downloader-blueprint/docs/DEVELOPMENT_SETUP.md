# Development and verification guide

**As of the 15 November 2026 M0 audit, there is no user-facing application to run here.** The original HTTP/HTTPS fixture and automated tests are runnable. The upstream candidates are not yet imported.

## Minimum prerequisites for initial audit

- Git and GitHub access.
- A clean disposable development environment for building unfamiliar upstream code.
- JDK/Gradle tooling appropriate for [AB Download Manager](https://github.com/amir1376/ab-download-manager).
- Node.js/npm for [AB Browser Integration](https://github.com/amir1376/ab-download-manager-browser-integration).
- FFmpeg only for **permitted test media** during the later media milestone.
- Windows/Chrome test access for the first end-to-end bridge; use Windows CI runners if developing from Linux cloud.

Avoid installing arbitrary scripts as administrator or executing unchecked third-party CI secrets. Read build files first, pin dependency versions and use standard package checks.

## Getting the project docs

~~~
git clone https://github.com/rejoansardar620-lang/Downloader-.git
cd Downloader-
~~~

Read in order: README.md, AGENTS.md, docs/START_HERE.md, docs/FEATURE_MATRIX.md, docs/LEGAL_SECURITY.md, docs/ROADMAP.md.

## Upstream audit worktrees (do not import yet)

Research candidates in separate, isolated directories. The repository links and initial priorities are listed in [REFERENCE_REPOSITORIES.md](REFERENCE_REPOSITORIES.md).

For AB Download Manager, the upstream README documents a Gradle release task:

~~~
./gradlew createReleaseFolderForCi
~~~

The upstream browser integration documents:

~~~
npm install
npm run pack:chrome
npm run pack:firefox
~~~

**These are upstream instructions, not commands already run in this repository.** Verify JDK requirements, dependencies, scripts, network policy and expected outputs first.

## First integration test (proposed)

The first synthetic [loopback HTTP fixture](../tools/fixtures/README.md) is implemented. From the repository root, run:

~~~sh
python3 -m unittest discover -s tests -v
python3 -m tools.fixtures.http_fixture --port 8765
~~~

Use `http://127.0.0.1:8765/file.bin` for Range-aware tests and `/no-range.bin` to test safe full restart. The fixture has **14 passing tests** covering Range/If-Range, redirects, truncated transfers and certificate-validated HTTPS. It supports optional caller-supplied TLS cert/key (see its own README); no desktop downloader has consumed it. The following desktop-to-browser end-to-end test remains proposed.

1. Serve a small openly redistributable test file from a controlled HTTPS endpoint that supports Range requests.
2. Download to a user-selected temporary directory.
3. Compare SHA-256 hash with the fixture.
4. Interrupt the connection and restart/resume.
5. Send the same job through the Chrome extension and local bridge.
6. Attempt a malicious/unauthorized cross-origin bridge request and verify rejection.
7. Record commands, OS/browser versions, pass/fail outcomes and screenshots where useful.

Use synthetic or clearly licensed media; do **not** use arbitrary YouTube videos as default automated tests.

## When code is introduced

Every module should document:

- Installation and commands for Linux/Windows/macOS where supported.
- Local build/test/lint/typecheck commands and expected output.
- Environment variable examples without secrets.
- Test fixture licensing and storage limits.
- Runtime/debugging/telemetry behavior.
- Extension IDs, native messaging registration, endpoint binding and pairing.
- CI job links and release artifact provenance.

## CI recommendations

| Stage | Initial check |
| --- | --- |
| PR (fixture only, implemented) | Python unittest/compileall; pinned GitHub actions, no secrets or external media |
| PR (future app) | Formatting, static analysis, unit tests, secrets, dependency/license review |
| Integration (future) | Local HTTP/HTTPS fixture, job lifecycle, cross-origin bridge security |
| Browser (future) | Build Chrome MV3 and smoke-test supported browser |
| Desktop (future) | Linux build + Windows CI build; separate signed release job |
| Release (future) | SBOM, third-party notices, artifacts, hashes, signature/rollback checks |

Use dependency caching and run narrow checks during development. A full multi-OS release build should run at milestone gates, not after every documentation change.

## Current verification status

- GitHub repository: planning/docs and original fixture plus initial test workflow; **no application implemented**.
- Desktop build: **blocked** at Gradle 9.8 bootstrap by release-asset network restriction; upstream source specifies JDK 25 toolchain. See [issue #4](https://github.com/rejoansardar620-lang/Downloader-/issues/4).
- Extension (isolated upstream clone): **Chrome and Firefox bundle builds PASS**, standalone TypeScript **FAILS**. See [issue #5](https://github.com/rejoansardar620-lang/Downloader-/issues/5).
- Browser integration: **not attempted end-to-end**; upstream unauthenticated-by-default HTTP API is a release blocker. See [issue #6](https://github.com/rejoansardar620-lang/Downloader-/issues/6).
- Cloud deployment: **not attempted**.
- Tests: **14/14 local Python fixture tests PASS**; upstream desktop tests not run; new GitHub Actions workflow not yet verified on GitHub.

See [BUILD_START_PLAN.md](BUILD_START_PLAN.md) and [REUSE_DECISION_MATRIX.md](REUSE_DECISION_MATRIX.md) before importing or rewriting source.
