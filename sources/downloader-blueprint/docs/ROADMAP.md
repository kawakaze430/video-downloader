# Roadmap with release gates

The milestones below are **planned**, not completed. Every milestone ends with a reviewable commit/PR, commands run, test evidence and updated feature status. Do not merge all upstream projects at once.

## M0 — Audit, choices and legal foundation (first task)

**Outputs:** build/license/dependency/security reports for AB desktop + browser integration and alternative candidates; feature coverage matrix; verified sample test assets; proposed architecture; explicit owner decisions on license and branding.

**Exit gate:** One primary base chosen with evidence, license obligations documented, initial OS/browser chosen, risk register reviewed. **No implementation rewrite yet.**

## M1 — First working desktop vertical slice (P0)

**Scope:** Build selected desktop foundation; download an authorized HTTPS file, show progress, pause/resume where supported, retry, checksum verification, restart recovery, safe filename handling.

**Exit gate:** Reproducible clean install/build; automated local integration tests; no corruption on interrupted transfer; actual output hash matches fixture.

## M2 — Browser handoff and packaging (P0)

**Scope:** Build selected browser companion; context menu and download capture; pair with desktop; authenticated job handoff; status feedback; browser permissions review.

**Exit gate:** Chrome-to-desktop demo succeeds; malicious webpage cannot trigger unauthorized local action; extension package generated; permission inventory documented.

## M3 — Owned-media processing (P1)

**Scope:** FFmpeg probing, audio extraction, MP4/MKV/WebM, non-DRM HLS/DASH from permitted test sources, subtitles, batch media processing, cancellation and resource limits.

**Exit gate:** Deterministic sample fixtures pass; audio/video sync and metadata verified; media failures do not hang UI; shipped FFmpeg binary license recorded.

## M4 — Website experience (P1)

**Scope:** Product site, download/install guides, optional upload-based converter or rights-reviewed direct URL workflow, clear privacy/terms, accessibility.

**Exit gate:** Security review (SSRF, quotas, uploads, retention), responsive usability tests and documented hosting cost; public deployment only by owner approval.

## M5 — Production-ready release (P1)

**Scope:** CI for supported OS/browser, signed installers and updates, telemetry opt-in, privacy-safe crash reports, localization, release notes, rollback plan, SBOM, security disclosures.

**Exit gate:** Clean-machine installation and update tests, accepted security findings, release checklist and support docs.

## M6 — Competitive expansion (P2)

**Possible scope:** Plugin SDK, CLI/API, scheduled subscriptions for permitted sources, advanced file sorting, remote jobs, mobile companion, AI-assisted indexing of owned media.

**Exit gate:** Product usage and support evidence justify each major feature. No automatic commitment to cloud cost.

## How to prevent credit waste

For every milestone, maintain this compact progress table in the issue/PR:

| Feature | Upstream status | Local status | Evidence | Next work |
| --- | --- | --- | --- | --- |
| Example: queue | Found in AB docs | Not implemented here | No local test | Audit source/build |

Rules:

1. Complete M0 before choosing a large rewrite.
2. Work on one milestone and a few acceptance criteria per task.
3. Run relevant existing tests before adding new code.
4. Reuse verified packages, keep dependency caches and avoid live-network media tests in every build.
5. Stop for a decision if a license, platform-policy or material architecture blocker appears.
6. Do not report or advertise a release until its exit gate is satisfied.
