# Proposed architecture (design, not implementation)

> **Draft.** The initial implementation has not been chosen or imported. Confirm feasibility with source inspection before making framework-specific commitments.

## Core approach

**Desktop first, local by default, one final project repository.** The desktop engine owns download jobs and writes files locally. The browser extension only discovers authorized links and sends authenticated, explicit user-initiated jobs. Media processing is a separate component using FFmpeg for supported files. The website begins as a product presence and expands to a secure optional web service later.

~~~mermaid
flowchart TD
  Extension["Browser companion"] -->|"paired request"| Bridge["Local authenticated API"]
  Desktop["Desktop UI"] --> Engine["Download/job engine"]
  Bridge --> Engine
  Engine --> Files["Local storage + history"]
  Engine --> Media["Media processor"]
  Web["Optional web app"] --> Hosted["Isolated hosted API/queue"]
  Hosted --> Media
~~~

The local engine should not depend on the hosted service to download direct files. The hosted API must not accept arbitrary unrestricted URLs.

## Preferred first baseline

- **Desktop:** Investigate AB Download Manager (Kotlin Multiplatform/Compose) **as-is** before choosing a rewrite.
- **Extension:** Investigate AB Browser Integration and its native/localhost handoff.
- **Web UI:** Evaluate ReClip separately. It is **not** already integrated into AB.
- **Media processor:** Wrap trusted FFmpeg invocation with argument arrays, timeouts, resource limits, job cancellation and sanitized metadata.
- **Source plugins:** Permissioned adapters for explicitly supported sources; never assume raw media downloads are permitted merely because yt-dlp offers an extractor.
- **Persistence:** First reuse the chosen desktop application's storage. Add PostgreSQL/Redis only if a later hosted service genuinely needs them.

**Avoid premature stack conflict:** Earlier research considered Next.js/FastAPI/Tauri for a greenfield product. The newer AB foundation is Kotlin, and preserving that tested code is the current preferred experiment. A framework rewrite requires evidence that integration is more costly than migration.

## Domain boundaries

| Module | Owns | Does not own |
| --- | --- | --- |
| Download engine | Transfers, resume/retry, concurrency, state, integrity | Scraping sites, UI rendering |
| Browser extension | User intent, permitted URL discovery, secure handoff | Secret storage, FFmpeg execution, arbitrary filesystem paths |
| Local bridge | Pairing, auth, rate limits, state/read-only APIs | Open unauthenticated public access |
| Media processor | Local file conversions, media probing, safe output handling | Source rights decisions or browser cookie extraction |
| Source connector | Rights-reviewed metadata/source resolution | Privilege escalation, DRM circumvention |
| Web service (later) | Quotas, auth, bounded jobs, cleanup, abuse protection | Unrestricted server-side URL fetching |

## Job contract (proposed)

A job should carry at least:

| Field | Meaning |
| --- | --- |
| id | Stable UUID |
| source_kind | direct_url, local_file, or approved_connector |
| source | Safe reference, not a secret-bearing URL in persistent logs |
| destination | Validated, user-selected destination |
| format_profile | Explicit conversion/quality options or original |
| created_at / updated_at | Time tracking |
| status | Lifecycle state |
| bytes_done / bytes_total | Progress, total may be unknown |
| checksum | Optional integrity expectation |
| retry_count / error_code | Recovery and user messaging |
| provenance | Originating UI, permission decision and source adapter version |

Proposed lifecycle:

~~~mermaid
stateDiagram-v2
  [*] --> Queued
  Queued --> Resolving
  Resolving --> Downloading
  Downloading --> Verifying
  Verifying --> Processing
  Verifying --> Complete
  Processing --> Complete
  Downloading --> Paused
  Paused --> Queued
  Resolving --> Failed
  Downloading --> Failed
  Verifying --> Failed
  Processing --> Failed
  Failed --> Queued: retry
  Queued --> Cancelled
  Downloading --> Cancelled
  Complete --> [*]
  Cancelled --> [*]
~~~

Workers must be idempotent where feasible; interrupted jobs must persist recoverable state. Successful completion means output is committed safely and integrity requirements passed, not just that a network transfer ended.

## Extension-to-desktop security contract

1. The user explicitly selects a URL or initiates a permitted capture.
2. Companion checks allowed origins and authenticates to a paired local helper; no wildcard CORS.
3. Helper validates URL scheme and destination, enforces limits and creates one job.
4. Extension receives a job ID and polls/subscribes to permitted progress fields.
5. Credentials and sensitive request headers remain local and are never echoed to logs or remote websites.

Prefer native messaging or a well-secured loopback bridge after auditing AB's existing protocol; do **not** design a privileged localhost API open to arbitrary tabs.

## Future monorepo layout (illustrative)

~~~
apps/
  desktop/             # selected existing desktop foundation
  extension/           # companion browser integration
  web/                 # optional website
components/
  media-processor/     # local FFmpeg wrapper
  source-connectors/   # rights-reviewed adapters
contracts/             # API schema, versioning, generated clients
tests/
  fixtures/            # small redistributable test files
  integration/
docs/
infrastructure/        # only when needed for hosting
~~~

The folder structure can change after the audit; keep integration **interfaces stable and documented**, not rigidly fixed directory names.
