# Legal, licensing, privacy and security guardrails

This is engineering guidance, **not legal advice**. Get appropriate professional review before releasing a paid product, distributing third-party binaries, or supporting a new platform.

## Platform permission boundaries

1. **YouTube terms:** Do not assume that being able to view a video grants a right to download it. Terms restrict reproducing/downloading content except where specifically allowed by the service, applicable law, or relevant permissions.
2. **YouTube API policies:** The YouTube API is not a general audiovisual download API. Its rules restrict downloading, caching and offline use without prior written approval.
3. **Chrome Web Store:** The store restricts extensions facilitating YouTube downloads; a self-installed development extension is **not** evidence that an extension is eligible for store publication.
4. **Copyright and authorization:** Support direct downloads/uploads and other sources only where the user has rights and the service permits the operation. Do not provide DRM, paywall, authentication, anti-bot or region-control bypass features.
5. **Consent and account access:** Never extract user cookies, browser credentials or private tokens without informed consent and an approved design; prefer platform-supported authentication and minimize data handling.

Official sources:

- https://www.youtube.com/t/terms
- https://developers.google.com/youtube/terms/developer-policies
- https://developer.chrome.com/docs/webstore/troubleshooting
- https://developer.chrome.com/docs/webstore/program-policies/malicious-and-prohibited
- https://support.google.com/youtube/answer/56100 (official download route for one's own uploads)

## License governance

Before using third-party code or shipping binaries:

- Record upstream source, commit, exact license, copyright holders, NOTICE and bundled dependencies.
- Generate an SBOM and preserve required license/attribution notices in source and releases.
- Inspect FFmpeg build flags/codecs carefully (LGPL versus GPL/nonfree configurations).
- Treat AGPL/GPL and other copyleft code as **reference only** unless the owner approves obligations and code-use design.
- Do not copy logos, product names, graphics, protected UI designs or documentation wholesale.
- Do not assume GPT/Codex-generated output is uniquely owned or free of third-party license issues.
- **The project owner has not chosen a license for original Downloader code.** Public visibility alone is not permission to reuse it commercially.

## Threat model: desktop and browser

| Threat | Requirement |
| --- | --- |
| Malicious website commands local helper | Pairing token/native messaging, strict origin/extension IDs, no wildcard CORS, user confirmation |
| Arbitrary filesystem access | Validate destination, canonicalize paths, limit writable directories |
| Unsafe source URL or redirect | Validate each hop, deny local/loopback/link-local/private/reserved endpoints and DNS rebinding |
| Untrusted downloaded filenames | Sanitize path separators, control characters, reserved names and collision behavior |
| Credential leakage | Secret store/OS keychain; redact logs; short-lived tokens; no cookie dumping |
| Malicious media file or playlist | Resource-limited workers, trusted FFmpeg, updates, timeouts and crash isolation |
| Unauthorized software updates | Signed builds, verified update metadata, rollback and safe release channels |
| Extension over-permission | Manifest V3, minimized host permissions, clear consent, automated permission review |
| Data loss | Atomic output rename, checksum, safe temporary-file handling, explicit cleanup |
| Supply-chain compromise | Pin/review dependencies, SBOM, vulnerability scanning, provenance and CI protection |

## Threat model: optional hosted services

- Block SSRF to cloud metadata, RFC1918, loopback, link-local, IPv6 internal and localhost hostnames.
- Validate redirects and DNS answers on every request; do not proxy privileged credentials.
- Restrict protocols, response size, download duration, concurrency, accepted content types and disk quota.
- Authenticate users; set per-user and global rate/cost limits; provide job expiry and media deletion.
- Never expose storage buckets or private media publicly by default.
- Make data retention, privacy policy, abuse handling and takedown contact available before launch.
- Prefer local processing to avoid paying for other users' bandwidth and to reduce privacy risks.

## Minimum verification before every release

- Rights/permissions and allowed-source checklist.
- Dependency and license scan; binary provenance.
- Secret scanning and browser permission diff.
- Tests for corrupted downloads, redirects, SSRF, malicious paths, retry storms and disk exhaustion.
- Clean-machine install/update/uninstall and browser-bridge abuse tests.
- Privacy text, security contact and third-party notices updated.

Do not deploy, publish a browser-store listing or claim copyright compliance until these gates are reviewed.
