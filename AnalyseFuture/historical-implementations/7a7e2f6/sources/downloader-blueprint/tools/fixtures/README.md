# Deterministic direct-download fixture (M0/M1)

The server is **our original implementation**, independent of candidate upstream applications. It provides a small HTTP test target for the Downloader desktop engine and browser handoff. It never fetches outside URLs, accesses local files, or processes real user videos.

## Start

From repository root, with Python 3.10+:

~~~sh
python3 -m tools.fixtures.http_fixture --port 8765
~~~

The server binds **only to 127.0.0.1**. A port of `0` assigns an available loopback port. Run tests:

~~~sh
python3 -m unittest discover -s tests -v
~~~

The test suite generates a temporary self-signed certificate with the local
OpenSSL CLI and tests real HTTPS with certificate verification **enabled**.
The temporary certificate and key are removed when tests finish.
For a manual HTTPS run, supply your own local test certificate and key:

~~~sh
python3 -m tools.fixtures.http_fixture --port 8765 \
    --tls-cert /path/to/test-cert.pem --tls-key /path/to/test-key.pem
~~~

The HTTPS client must trust that specific test certificate. Never disable
TLS verification globally to make a test pass.

| URL | Behavior | Expected |
| --- | --- | --- |
| `/file.bin` | Fixed 16 KiB binary payload | HTTP 200, `Accept-Ranges: bytes`, deterministic SHA-256 |
| `/file.bin` with `Range: bytes=0-8191` | First half | HTTP 206 + correct `Content-Range` |
| `/file.bin` with `Range: bytes=8192-` | Second half | HTTP 206; concatenate pieces to obtain exact payload hash |
| `/file.bin` with `Range: bytes=99999-` | Invalid offset | HTTP 416 + `Content-Range: bytes */16384` |
| `/no-range.bin` | Deliberately ignores Range | HTTP 200, full body; a downloader must restart safely |
| `/health` | Readiness | HTTP 200 `ok` |
| Any unknown URL | No external proxy | HTTP 404 |

Additional controlled test endpoints and behaviors:

- /file.bin with a matching If-Range ETag: 206 partial resume.
- /file.bin with a stale If-Range ETag: 200 full response (restart).
- /drop.bin: connection closes after 2048 bytes of a declared 16 KiB response; the client must report a truncated transfer.
- /redirect.bin: 302 with a local Location header pointing to /file.bin.

When M1 imports the approved engine, use these endpoints for direct, interrupted/resumed, invalid-range, redirect, TLS and integrity tests. The fixture supports only single byte ranges and local redirects. It does not model authenticated remote sources, bandwidth throttling, HLS/DASH, multirange replies or full crash/restart behavior.

CI is defined in .github/workflows/fixture-tests.yml. It runs for relevant pull requests or on manual invocation, with no GPU or hosted downloader deployment. Passing these tests does not prove the future desktop app works.
