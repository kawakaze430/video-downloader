# Complete ordered implementation checklist

**Project:** Downloader — independently branded desktop-first download manager, browser companion and authorized media-processing product.

**Last checked:** 15 November 2026. See the [updated engineering audit](M0_AUDIT.md), [17-source matrix](REUSE_DECISION_MATRIX.md) and [build-start plan](BUILD_START_PLAN.md) for exact pins, build evidence, security findings and continuation instructions.

**Status rule:** Checked items have evidence in this repository or a linked issue/PR. All other items are **not verified**. A feature present in an upstream repository is not yet implemented here.

**Execution order:** Complete each gate before starting the next milestone. The project owner may re-prioritize tasks, but record the decision first. Refer to [feature IDs](FEATURE_MATRIX.md), [roadmap](ROADMAP.md), [AGENTS.md](../AGENTS.md), and [security requirements](LEGAL_SECURITY.md).

## 0. Governance and project setup — BLOCKING DECISIONS

- [x] G00: Create GitHub repository with initial documentation and contributor instructions — [bootstrap commit](https://github.com/rejoansardar620-lang/Downloader-/commit/51022e8f6440c3dabba46179c5642a7c8c3d3a3e).
- [x] G01: Write vision, competitor benchmarks, architecture proposal, roadmap, and feature matrix.
- [x] G02: Add AGENTS.md, CONTRIBUTING.md, SECURITY.md, issue/PR templates and initial M0 issues.
- [ ] G03: Owner chooses **product name**, logo policy, trademark review and public project description.
- [ ] G04: Owner decides **software license and contribution terms** before accepting significant third-party or contributor code. Do not silently choose one.
- [ ] G05: Owner approves initial target **Windows 11 + Chrome** (recommended); set secondary OS/browser priorities.
- [ ] G06: Owner confirms initial product scope: desktop-first authorized direct downloads, then media tools, then web service.
- [ ] G07: Define versioning, issue labels, branch protection and PR review ownership.
- [ ] G08: Set an explicit cost ceiling for Codex/CI/cloud testing and deployment.

**Gate G:** Decisions G03–G06 documented in [DECISIONS.md](DECISIONS.md) by the owner. Auditing can proceed before this gate; code imports and public releases cannot.

## 1. M0 — Research, audits and reuse decision (first engineering milestone)

### 1A. Desktop and extension foundations

- [x] A01: Pin exact upstream commit SHA/tag for [AB Download Manager](https://github.com/amir1376/ab-download-manager) — [audit](M0_AUDIT.md) pins `68f0ea6e8ba5cbeb02c92342cd3bf7475378ae68`.
- [ ] A02: Inspect desktop source modules, build scripts, supported OS matrix and configuration.
- [ ] A03: Audit Apache-2.0 obligations and all transitive dependencies, including bundled native tools.
- [ ] A04: Determine existing download features by **source + tests**: D01–D12.
- [ ] A05: Build AB desktop in an isolated environment; record JDK, Gradle command, OS and actual result.
- [ ] A06: Run upstream tests; classify pass/fail/blocked and investigate critical failures.
- [x] A07: Pin exact upstream commit SHA/tag for [AB Browser Integration](https://github.com/amir1376/ab-download-manager-browser-integration) — [audit](M0_AUDIT.md) pins `bf6811dd8a3ee2b47b94d70e13c2c7e70be7be05`.
- [ ] A08: Audit extension permissions, Manifest V3 compatibility, browser store restrictions and native messaging/localhost security.
- [ ] A09: Build extension packages and run available tests; record evidence — Chrome MV3 and Firefox bundler builds PASS; standalone `tsc --noEmit` FAIL; browser installation and package verification remain. See [audit](M0_AUDIT.md), [blocker #5](https://github.com/rejoansardar620-lang/Downloader-/issues/5).
- [ ] A10: Validate the existing desktop-to-extension protocol, or document a safe adaptation strategy.

### 1B. Media, website and alternatives

- [ ] A11: Pin and audit [ReClip](https://github.com/averygan/reclip) (website). Verify actual batch, format and quality behavior.
- [ ] A12: Pin and audit [MediaGrabber](https://github.com/miroshArtem/MediaGrabber) and [HLS Downloader](https://github.com/puemos/hls-downloader) (extension/media security).
- [ ] A13: Assess [Parabolic](https://github.com/NickvisionApps/Parabolic) versus AB: supported platforms, build quality, and reuse costs.
- [ ] A14: Audit FFmpeg executable build/license and allowable code paths for supported media-processing features.
- [ ] A15: Audit yt-dlp and bundled license requirements for **optional** use on authorized sources only.
- [ ] A16: Study Gopeed, Motrix/aria2, Cobalt, MeTube and Tube Archivist for **feature ideas only**, unless their source license is explicitly approved.
- [ ] A17: Create a dependency/license/SBOM risk register with exact source commits and NOTICE obligations.
- [ ] A18: Benchmark baseline binaries with controlled legal fixtures; record CPU/RAM, resume reliability and integrity rather than marketing speed claims — [HTTP/HTTPS fixture](../tools/fixtures/README.md) has 14 passing local tests, including interruption/redirect/If-Range; **no application benchmark**.
- [ ] A19: Produce a **build vs reuse matrix** for every P0/P1 feature, including cost/risk of integration.
- [ ] A20: Compare one-core/one-extension architecture to greenfield rewrite. Recommend a single base with evidence.
- [ ] A21: Update DECISIONS.md and FEATURE_MATRIX.md with **verified**, not presumed, results.

**Gate M0:** Owner approves a base/extension, software license path, exact pinned upstream commits, first fixture and M1 acceptance criteria. No broad repository merger.

## 2. M1 — Local download engine / first runnable product (P0)

- [ ] D01: Import or integrate only approved, pinned upstream source and preserve attribution/NOTICE.
- [ ] D02: Create the maintainable repository/module structure without breaking upstream history or tests.
- [ ] D03: Establish hermetic/reproducible developer environment and build scripts.
- [ ] D04: Add small, explicitly redistributable HTTPS fixtures (including Range-capable and Range-disabled servers) — original [HTTP/optional HTTPS loopback fixture](../tools/fixtures/README.md) and unit tests implemented; full application integration and controlled remote HTTPS validation pending.
- [ ] D05: Implement/verify direct HTTPS download to user-approved local directory.
- [ ] D06: Show real bytes, progress, unknown-length support, speed and errors.
- [ ] D07: Implement/verify pause/resume where HTTP Range is supported; safe restart otherwise.
- [ ] D08: Implement/verify retry, backoff, cancellation and partial-file cleanup.
- [ ] D09: Implement/verify bounded concurrent jobs, queue order and prioritization.
- [ ] D10: Implement/verify safe filenames, collision policy, disk-full behavior and path validation.
- [ ] D11: Implement/verify file integrity check and atomic finalization.
- [ ] D12: Persist job history and recover from network failure, app crash and restart.
- [ ] D13: Add unit tests for state transitions, redirects, retries, corruption and cancellation.
- [ ] D14: Run real desktop application with a test fixture; capture reproducible test evidence.
- [ ] D15: Document build, run, debug, uninstall and known limitations.

**Gate M1:** Clean Windows build and successful authorized transfer with verified SHA-256. Interruption, cancellation and recovery tests pass. No YouTube-dependent demo.

## 3. M2 — Browser extension and secure desktop handoff (P0)

- [ ] B01: Reuse approved AB Browser Integration source/architecture rather than duplicating its core functions.
- [ ] B02: Define versioned extension-to-desktop request/response schema and compatibility checks.
- [ ] B03: Implement/verify native messaging or tightly authenticated loopback pairing.
- [ ] B04: Block untrusted origins, malicious tabs, arbitrary file paths and unauthorized local commands.
- [ ] B05: Support user-triggered context-menu and normal permitted file-download capture.
- [ ] B06: Expose accurate job status, errors and cancellation to the extension.
- [ ] B07: Minimize host permissions, extension IDs and data collection; add a privacy declaration.
- [ ] B08: Package Chrome MV3 and test install/reload/update in an isolated browser profile.
- [ ] B09: Add security tests for replay, origin confusion, native host discovery, token leakage and CORS abuse.
- [ ] B10: Review Chrome Web Store policy **before** publication; no unauthorized YouTube functionality.

**Gate M2:** Chrome handoff creates one authenticated job, UI progress updates, and malicious page tests fail closed. Package is verified; store listing remains separate.

## 4. M3 — Media processing, subtitles and permitted streams (P1)

- [ ] M01: Safely ingest user-owned local video/audio without automatic cloud upload.
- [ ] M02: Select approved FFmpeg binaries/build flags and ship required notices.
- [ ] M03: Probe metadata and offer only actually supported formats/resolutions.
- [ ] M04: Convert/remux MP4, MKV and WebM; validate playable output.
- [ ] M05: Extract/convert MP3, M4A, FLAC, WAV and Opus.
- [ ] M06: Support audio track/language and SRT/VTT subtitle handling with correct sync.
- [ ] M07: Support trim, merge, compression and simple presets on owned assets.
- [ ] M08: Add bounded batch processing, cancel, timeout, disk quota and temp cleanup.
- [ ] M09: Process authorized non-DRM HLS/DASH fixtures; no DRM or authentication bypass.
- [ ] M10: Add format-specific regression fixtures and playback/integrity checks.
- [ ] M11: Introduce optional rights-reviewed source connectors only after policy/security approval.
- [ ] M12: Report unsupported or protected sources clearly and without speculative workarounds.

**Gate M3:** All supported media fixtures pass; transcodes are bounded, outputs playable, metadata honest and license notices shipped.

## 5. M4 — Website and optional hosted processing (P1)

- [ ] W01: Build a unique accessible product website, download links, feature descriptions and support docs.
- [ ] W02: Decide whether website is marketing-only, local companion UI, or hosted converter (owner approval).
- [ ] W03: Reuse/adapt ReClip only after license/security audit and interface definition.
- [ ] W04: Implement secure upload ingestion for user-owned files if hosted conversion is approved.
- [ ] W05: Restrict direct URL schemes, redirects, DNS and private networks to prevent SSRF.
- [ ] W06: Set per-job time, size, CPU, RAM, disk, bandwidth and concurrency limits.
- [ ] W07: Require appropriate authentication/quotas; protect stored media and downloads.
- [ ] W08: Delete temporary assets by retention policy, with clear privacy notice.
- [ ] W09: Add backend integration tests, abuse tests and cost monitoring.
- [ ] W10: Deploy publicly only with owner approval, legal review and verified infrastructure costs.

**Gate M4:** Secure, accessible web flow with documented retention, observed cost and no open file-fetch proxy.

## 6. M5 — Quality, security and production distribution (P1)

- [ ] P01: Establish GitHub Actions: lint/typecheck/unit/integration for approved components.
- [ ] P02: Add Windows desktop, Chrome, and secondary OS/browser release build matrix.
- [ ] P03: Implement proper versioning, changelog, release notes and rollback strategy.
- [ ] P04: Sign desktop binaries and verify download/update signatures.
- [ ] P05: Generate SBOM, dependency licenses and third-party notices for each package.
- [ ] P06: Test clean install, upgrade, downgrade protections and uninstall on target OS.
- [ ] P07: Perform dependency scanning, secrets scanning, SAST and permission review.
- [ ] P08: Run crash/restart, network outage, storage exhaustion and memory tests.
- [ ] P09: Improve accessibility, keyboard navigation and localization.
- [ ] P10: Create privacy/terms/support/security reporting pages and disclosure process.
- [ ] P11: Publish release artifacts only with permission, packaging checks and user-facing documentation.
- [ ] P12: Collect opt-in usability feedback and correct beta-blocking defects.

**Gate M5:** Reproducible signed release that meets quality, security and legal/distribution standards.

## 7. M6 — Competitive product expansion (P2, AFTER beta)

- [ ] X01: Advanced scheduling, templates, categories and deduplicated download history.
- [ ] X02: API/CLI and opt-in automation with authenticated tokens.
- [ ] X03: Secure plugin SDK, sandbox and permissions model.
- [ ] X04: Advanced archive/media organization and search.
- [ ] X05: Mobile companion and remote management with user pairing and cost controls.
- [ ] X06: Optional local AI transcription/tagging on user-owned media with opt-in processing.
- [ ] X07: Performance comparisons against IDM/4K competitors using fair test methodology.
- [ ] X08: Monetization decision, product analytics, distribution/support operations.

**Gate M6:** Each feature must have demand evidence, explicit business/maintenance cost, a security plan and tests.

## Blocker and handoff protocol

When something is blocked, Codex or a developer must provide:

~~~text
Task ID:
Milestone:
Exact command and environment:
Observed error/output:
Expected result:
Steps already tried:
Security/license impact:
Suggested next action:
Owner decision or credential required?:
~~~

Mark the task **BLOCKED** in the issue or PR. Do not mark blocked work complete; do not bypass permissions or import conflicting code. An unrelated milestone can continue only if it does not depend on the blocked task.

## Progress summary

| Milestone | State | Evidence |
| --- | --- | --- |
| G: governance | PARTIAL | Initial documents exist; product license/name require owner decision |
| M0: repo/architecture/license audit | IN PROGRESS | [Updated audit](M0_AUDIT.md): 17 source candidates triaged, exactly two foundations recommended, both upstream extension builds PASS, 14 fixture tests PASS; Gradle bootstrap, extension types, transitive SBOM and owner decisions remain BLOCKED |
| M1: desktop runtime | NOT STARTED | No application source imported; only a preparatory HTTP fixture exists |
| M2: browser handoff | NOT STARTED | No extension source imported |
| M3: media processing | NOT STARTED | No FFmpeg integration |
| M4: website | NOT STARTED | No website implementation |
| M5: production release | NOT STARTED | Initial fixture-only PR/manual CI exists locally, but no app CI, installers or release pipeline |
| M6: expansion | NOT STARTED | Backlog only |

**Next action:** Unblock A05/A06 with an authorized Gradle 9.8/JDK 25 setup; finish A03 dependency/NOTICE scan and A09 TypeScript repair in an approved upstream fork; verify native protocol security A08/A10. The 17-candidate source triage is documented, but each unchecked audit item still requires its stated full acceptance evidence. Resolve G03–G06 before importing or rewriting desktop/extension source.
