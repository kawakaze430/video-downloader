"""Loopback-only HTTP fixture for permitted direct-download and Range tests.

No external downloads, user media, pip dependencies, or remote network access.
The payload is a deterministic 16 KiB byte sequence generated in memory.

Run:
    python3 -m tools.fixtures.http_fixture --port 8765

URLs:
    http://127.0.0.1:8765/file.bin       (supports one HTTP byte range)
    http://127.0.0.1:8765/no-range.bin   (ignores Range; always returns 200)
    http://127.0.0.1:8765/health
"""

from __future__ import annotations

import argparse
import hashlib
import re
import ssl
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

PAYLOAD = bytes(range(256)) * 64
PAYLOAD_SHA256 = hashlib.sha256(PAYLOAD).hexdigest()
_RANGE_PATTERN = re.compile(r"^bytes=(\d*)-(\d*)$")


def parse_single_range(value: str, size: int) -> tuple[int, int] | None:
    """Parse an inclusive HTTP byte range; return None when not satisfiable.

    Multipart ranges are intentionally unsupported to keep acceptance tests
    unambiguous. Open-ended and suffix byte ranges are supported.
    """
    match = _RANGE_PATTERN.fullmatch(value.strip())
    if match is None or size <= 0:
        return None

    first, last = match.groups()
    # Huge integers must not crash a request handler or consume arbitrary CPU.
    if len(first) > 20 or len(last) > 20:
        return None
    if not first and not last:
        return None
    if first:
        start = int(first)
        end = min(int(last), size - 1) if last else size - 1
        if start >= size or end < start:
            return None
        return start, end

    suffix = int(last)
    if suffix == 0:
        return None
    return max(0, size - suffix), size - 1


class FixtureRequestHandler(BaseHTTPRequestHandler):
    """Serve only three known paths, with no filesystem or proxy access."""

    protocol_version = "HTTP/1.1"

    def log_message(self, format: str, *args: object) -> None:
        # Tests must be quiet and never log authorization/cookie headers.
        return

    def do_GET(self) -> None:  # noqa: N802 — http.server API
        self._respond(include_body=True)

    def do_HEAD(self) -> None:  # noqa: N802 — http.server API
        self._respond(include_body=False)

    def _respond(self, include_body: bool) -> None:
        path = urlsplit(self.path).path
        if path == "/health":
            self._send(200, b"ok", include_body=include_body)
            return
        if path == "/redirect.bin":
            self._send(302, b"", {"Location": "/file.bin"}, include_body)
            return
        if path == "/drop.bin":
            # Send only part of a declared response. Downloaders must detect
            # truncation and retry; an HTTP 200 alone is not success.
            self.send_response(200)
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Length", str(len(PAYLOAD)))
            self.send_header("Connection", "close")
            self.end_headers()
            if include_body:
                self.wfile.write(PAYLOAD[:2048])
                self.wfile.flush()
            self.close_connection = True
            return
        if path not in ("/file.bin", "/no-range.bin"):
            self._send(404, b"not found", include_body=include_body)
            return

        supports_ranges = path == "/file.bin"
        headers = {
            "Content-Type": "application/octet-stream",
            "Content-Disposition": 'attachment; filename="fixture.bin"',
            "Accept-Ranges": "bytes" if supports_ranges else "none",
            "ETag": f'"{PAYLOAD_SHA256}"',
            "Cache-Control": "no-store",
        }

        range_header = self.headers.get("Range") if supports_ranges else None
        # When an If-Range validator differs, HTTP specifies sending the
        # complete representation rather than a partial one.
        if range_header is not None and self.headers.get("If-Range") not in (None, headers["ETag"]):
            range_header = None
        if range_header is not None:
            bounds = parse_single_range(range_header, len(PAYLOAD))
            if bounds is None:
                headers["Content-Range"] = f"bytes */{len(PAYLOAD)}"
                self._send(416, b"", headers, include_body)
                return
            start, end = bounds
            headers["Content-Range"] = f"bytes {start}-{end}/{len(PAYLOAD)}"
            self._send(206, PAYLOAD[start : end + 1], headers, include_body)
            return

        self._send(200, PAYLOAD, headers, include_body)

    def _send(
        self,
        status: int,
        body: bytes,
        headers: dict[str, str] | None = None,
        include_body: bool = True,
    ) -> None:
        self.send_response(status)
        self.send_header("Content-Length", str(len(body)))
        for key, value in (headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        if include_body:
            self.wfile.write(body)


def create_server(
    port: int,
    certfile: Path | None = None,
    keyfile: Path | None = None,
) -> ThreadingHTTPServer:
    """Create a loopback-only fixture; optionally enable real TLS.

    Certificates are caller-supplied (tests generate ephemeral certs).
    This function never disables TLS verification for clients.
    """
    if (certfile is None) != (keyfile is None):
        raise ValueError("certfile and keyfile must be supplied together")
    server = ThreadingHTTPServer(("127.0.0.1", port), FixtureRequestHandler)
    server.daemon_threads = True
    if certfile is not None and keyfile is not None:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        try:
            context.load_cert_chain(certfile=str(certfile), keyfile=str(keyfile))
            server.socket = context.wrap_socket(server.socket, server_side=True)
        except Exception:
            server.server_close()
            raise
    return server


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8765, help="Loopback port (0 for any free port)")
    parser.add_argument("--tls-cert", type=Path, help="PEM certificate for optional HTTPS")
    parser.add_argument("--tls-key", type=Path, help="PEM private key for optional HTTPS")
    args = parser.parse_args()
    if not 0 <= args.port <= 65535:
        parser.error("port must be in 0..65535")
    if bool(args.tls_cert) != bool(args.tls_key):
        parser.error("--tls-cert and --tls-key must be provided together")
    server = create_server(args.port, args.tls_cert, args.tls_key)
    scheme = "https" if args.tls_cert else "http"
    print(f"Fixture: {scheme}://127.0.0.1:{server.server_port}/file.bin", flush=True)
    print(f"SHA-256: {PAYLOAD_SHA256}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
