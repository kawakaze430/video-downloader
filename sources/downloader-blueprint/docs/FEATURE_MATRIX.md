# Master feature inventory and acceptance criteria

This is the feature backlog for the intended competitive product. **All application features listed below remain NOT IMPLEMENTED in this repository as of 15 November 2026.** Separately, the repo includes an original deterministic HTTP/HTTPS fixture with 14 passing tests and a fixture-only CI workflow. Neither makes the app features complete. A named upstream library is a candidate to evaluate, **not proof** that our product implements the feature. See the [17-source evidence matrix](REUSE_DECISION_MATRIX.md) and [M0 execution report](BUILD_START_PLAN.md).

Legend: **P0** required for first beta; **P1** important for a competitive 1.x product; **P2** later differentiation. Acceptance criteria below are proposed and may be refined after audit.

## A. Desktop download manager

| ID | Feature | Priority | Candidate | Acceptance target |
| --- | --- | --- | --- | --- |
| D01 | HTTPS direct-file downloads | P0 | AB Download Manager | Download a permitted test file with matching SHA-256 |
| D02 | Real progress, ETA and speed | P0 | AB Download Manager | UI reflects actual transferred bytes; handles unknown length |
| D03 | Pause/resume | P0 | AB Download Manager | Range-capable source resumes without corrupting output; otherwise safe restart |
| D04 | Retry and recovery | P0 | AB Download Manager | Simulated disconnect/restart preserves recoverable job state |
| D05 | Cancel and cleanup | P0 | AB Download Manager | Job cancels without orphaned worker or unsafe partial files |
| D06 | Download queue and concurrency cap | P0 | AB Download Manager | Configured concurrency and fair scheduling enforced |
| D07 | Safe filename/path handling | P0 | AB Download Manager + validation | No traversal, unexpected overwrite or reserved-name failure |
| D08 | Integrity/checksum validation | P0 | AB Download Manager / own adapter | Invalid hash reported; file not marked successful |
| D09 | Segmented transfer when supported | P1 | AB Download Manager | No duplicated bytes; compare with single connection fairly |
| D10 | Scheduling and speed limits | P1 | AB Download Manager | Jobs start at intended local time; limits measured |
| D11 | Download categories, search and history | P1 | AB Download Manager | History survives restart and can be searched |
| D12 | Proxy and network settings | P1 | AB Download Manager | Explicit configured proxy works, credentials remain protected |
| D13 | Bulk link intake, deduplication | P1 | ReClip / AB | Repeated URLs detected; deliberate duplicates still possible |
| D14 | Import/export of job lists | P2 | Design needed | Versioned format with invalid data handled safely |
| D15 | CLI, local REST API | P2 | Gopeed/Motrix reference | Authenticated, versioned and documented API |

## B. Browser companion

| ID | Feature | Priority | Candidate | Acceptance target |
| --- | --- | --- | --- | --- |
| B01 | Desktop handoff for direct downloads | P0 | AB Browser Integration | User click creates exactly one authenticated desktop job |
| B02 | Popup and right-click controls | P0 | AB Browser Integration | Works on supported Chrome/Edge version |
| B03 | Safe native messaging/pairing | P0 | AB integration + security work | Arbitrary page cannot command local helper |
| B04 | Active job progress | P1 | AB integration / adapter | Popup reflects state from desktop engine |
| B05 | Supported direct media detection | P1 | MediaGrabber | Correct media listed with user-initiated action |
| B06 | Authorized non-DRM HLS/DASH | P1 | HLS Downloader | Tested with owned sample stream and correct audio/video |
| B07 | Firefox extension support | P1 | AB integration | Package and smoke-test in supported Firefox |
| B08 | Fine-grained host permissions | P0 | Manifest V3 | Minimum requested permissions justified and reviewed |
| B09 | Optional remote target | P2 | Gopeed reference | Secure pairing, explicit consent and no open control port |

## C. Media conversion and organization

| ID | Feature | Priority | Candidate | Acceptance target |
| --- | --- | --- | --- | --- |
| M01 | Import user-owned local video/audio | P1 | New media module | File processed offline without uploading by default |
| M02 | MP4/MKV/WebM remux where compatible | P1 | FFmpeg | Container conversion plays with synchronized audio |
| M03 | MP3/M4A/FLAC/WAV/Opus extraction | P1 | FFmpeg | Metadata/sample duration checked; lossless output not mislabeled |
| M04 | Video compression and presets | P1 | FFmpeg | Actual output codec/quality/size displayed |
| M05 | Trim/merge permitted media | P1 | FFmpeg | Audio stays synchronized; invalid edits fail safely |
| M06 | Subtitle import/export | P1 | FFmpeg / media metadata | Supported SRT/VTT conversions tested |
| M07 | Audio-track and language selection | P1 | FFmpeg | Selected track matches requested language when metadata exists |
| M08 | Batch conversion queue | P1 | Shared jobs | Job failures do not corrupt remaining jobs |
| M09 | Available 4K/8K processing | P1 | FFmpeg | No false promise of native 8K when source is lower quality |
| M10 | Metadata and media library | P2 | Parabolic/Tube Archivist reference | Search, thumbnails, duplicate handling, privacy |
| M11 | AI transcription and tagging | P2 | Unselected | Opt-in, privacy and cost disclosures; measurable value |
| M12 | Site-specific connector architecture | P1 | yt-dlp optional | Explicit allowlist/rights review and connector regression tests |

## D. Website, platform and release engineering

| ID | Feature | Priority | Candidate | Acceptance target |
| --- | --- | --- | --- | --- |
| W01 | Public product/installation website | P1 | New site / existing marketing pattern | Accessible and mobile responsive |
| W02 | Uploaded media conversion | P1 | Original hardened service/FFmpeg; ReClip UX reference | Size/format limits, authenticated cleanup and valid output |
| W03 | Permitted direct URL job UI | P1 | Original hardened design; ReClip UX reference | SSRF-safe URL checks, explicit quotas, progress |
| W04 | Cloud/server-side queue | P2 | Redis/worker candidate | Bounded resource use, cancellation and TTL cleanup |
| W05 | User accounts and billing | P2 | Not selected | Only after privacy policy and business model approval |
| P01 | Reproducible developer builds | P0 | AB build + extension tooling | Fresh environment builds without private dependencies |
| P02 | Automated unit/integration tests | P0 | Project-specific | Core state machine, security cases, extension bridge covered |
| P03 | Signed release and installer | P1 | Existing packager | Install/update/uninstall tested on supported OS |
| P04 | Auto-updates and rollback strategy | P1 | Existing updater | Signature verification and controlled release channels |
| P05 | Dependency/license SBOM | P0 | Standard tooling | All shipped dependencies and licenses documented |
| P06 | Privacy-safe logs and diagnostics | P0 | New/shared | No credentials, cookies or private URLs in logs |
| P07 | Localization and accessibility | P1 | App i18n tooling | Keyboard navigation, labels, contrast, locale correctness |
| P08 | Plugin SDK and marketplace | P2 | Motrix/Gopeed reference | Signed plugins, sandbox, granular permissions |

## Release gates

- **P0 beta:** One supported desktop OS and Chrome, authenticated handoff, reliable authorized HTTPS file download, integrity/recovery tests, license audit and build/release docs.
- **P1 commercial-quality candidate:** media processing, supported HLS/DASH, quality/format selection, better UX, localization, signed updates and supported website workflows.
- **P2 expansion:** automation APIs, mobile/remote access, optional AI, advanced plugins and cloud services.

## Tracking rule

When code arrives, add columns or an issue-linked manifest for **local implementation status**, **last verified commit**, **test command**, **platform** and **evidence**. Never change an item to "Done" solely because the upstream README mentions it.
