# Open-source landscape and reuse decisions

Snapshot researched on **13 November 2026**. Links, licenses, activity and features can change. **A complete dependency and provenance audit is required before code reuse or distribution.**

## Primary candidates: evaluate for actual integration

| Project | URL | Reported project license | Main value | Initial decision |
| --- | --- | --- | --- | --- |
| AB Download Manager | https://github.com/amir1376/ab-download-manager | Apache-2.0 | Kotlin Multiplatform/Compose desktop manager; acceleration, queues, scheduling | **Preferred desktop base, pending build/security audit** |
| AB browser integration | https://github.com/amir1376/ab-download-manager-browser-integration | Apache-2.0 | Existing extension/desktop handoff, Chrome/Firefox packaging | **Preferred extension base, pending audit** |
| ReClip | https://github.com/averygan/reclip | MIT | Lightweight Flask web media frontend; MP4/MP3, quality and batch | **Candidate website/UI implementation** |
| MediaGrabber | https://github.com/miroshArtem/MediaGrabber | MIT | Manifest V3 detection and native helper reference | **Evaluate selectively**; smaller project, assess tests/security |
| HLS Downloader | https://github.com/puemos/hls-downloader | MIT | Authorized HLS with local ffmpeg.wasm processing | **Evaluate selectively** |
| Parabolic | https://github.com/NickvisionApps/Parabolic | MIT | Desktop video/audio UX, formats and supported OS workflows | **Compare with AB; do not rebuild desktop twice** |
| FFmpeg | https://github.com/FFmpeg/FFmpeg | LGPL/GPL depending on configuration | Media transcoding, remuxing, codecs, metadata | **Use as dependency after binary/license review** |
| yt-dlp | https://github.com/yt-dlp/yt-dlp | Core Unlicense; bundled components differ | Site extractors, format/metadata handling | **Optional, permitted-source plugin only** |

## References: features and patterns, not automatic imports

| Project | URL | License note | What to study |
| --- | --- | --- | --- |
| Gopeed | https://github.com/GopeedLab/gopeed | GPL-3.0 | Cross-platform download engine, extension model, API, CLI, automation |
| Motrix | https://github.com/agalwood/Motrix | Main code MIT; bundled aria2 is GPL-licensed | Desktop UX, plugins, native messaging, SBOM |
| aria2 | https://github.com/aria2/aria2 | GPL-2.0 | Segmented transfers, resume, protocol support, JSON-RPC |
| Cobalt | https://github.com/imputnet/cobalt | AGPL-3.0 | Web UX and API separation |
| MeTube | https://github.com/alexta69/metube | AGPL-3.0 | Format options, queue, playlist/channel subscriptions |
| Pinchflat | https://github.com/kieraneglin/pinchflat | AGPL-3.0 | Download scheduling, media naming, user-defined automation |
| Tube Archivist | https://github.com/tubearchivist/tubearchivist | GPL-3.0 | Media library, search and organizational workflows |
| YoutubeDL-Material | https://github.com/Tzahi12345/YoutubeDL-Material | MIT | Full-stack UI and downloader service; audit older dependencies |
| yt-dlp-web-ui | https://github.com/marcopiovanello/yt-dlp-web-ui | GPL-3.0; archived October 2026 | RPC patterns only; not recommended as primary maintained base |

## Important distinction: source license versus product ownership

- The owner may control the repository, new original code, brand and deployment **without** acquiring exclusive copyright in upstream code.
- **MIT/Apache-2.0** are permissive but still require copyright notices and/or LICENSE/NOTICE preservation; inspect each dependency.
- **GPL/AGPL** often require source-availability obligations under distribution or network use; study as references unless the owner explicitly approves the relevant licensing model.
- FFmpeg builds vary in applicable license conditions; generated binaries, external codecs and nonfree flags must be reviewed.
- A separately installed program, embedded library, linked component and copied source code may create **different** obligations. Obtain appropriate legal review before commercial distribution.
- Branding and logos are independent of code licenses. Do not reuse third-party trademarks or UI assets as our own.

## Audit checklist and evidence format

For **each** adoption candidate:

1. Pin source URL, commit SHA/tag, commit date and maintainer status.
2. Read project license, CONTRIBUTING, NOTICE, third-party notices and build files.
3. Enumerate transitive dependency licenses, bundled executables and media codecs.
4. Identify known vulnerabilities, unsafe install scripts, open network listeners and insecure defaults.
5. Build from source in a clean environment and record exact command, OS, logs and artifacts.
6. Test relevant features with an authorized sample; verify what works instead of repeating README claims.
7. Estimate maintenance burden, compatibility and expected integration changes.
8. Record **reuse / adapt / reference only / reject**, with decision and reviewer.

Suggested report row:

| Component | Ref/commit | Build | License/SBOM | Verified features | Risks | Decision |
| --- | --- | --- | --- | --- | --- | --- |
| Example | To inspect | Not run | Pending | None verified | Pending | Undecided |

## Research sources

Primary project sources are the GitHub repositories above. Product benchmarks and policies are separately linked in [COMPETITOR_BENCHMARK.md](COMPETITOR_BENCHMARK.md) and [LEGAL_SECURITY.md](LEGAL_SECURITY.md).
