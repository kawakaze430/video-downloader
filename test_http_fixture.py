"""Standard-library regression checks for the download test server."""

import hashlib
import http.client
import shutil
import ssl
import subprocess
import tempfile
import threading
import unittest
from pathlib import Path

from tools.fixtures.http_fixture import (
    PAYLOAD,
    PAYLOAD_SHA256,
    create_server,
    parse_single_range,
)


class RangeParserTests(unittest.TestCase):
    def test_ranges(self):
        self.assertEqual(parse_single_range("bytes=0-10", 100), (0, 10))
        self.assertEqual(parse_single_range("bytes=20-", 100), (20, 99))
        self.assertEqual(parse_single_range("bytes=-5", 100), (95, 99))
        self.assertEqual(parse_single_range("bytes=-200", 100), (0, 99))
        self.assertEqual(parse_single_range("bytes=90-500", 100), (90, 99))

    def test_invalid_ranges(self):
        for header in ("bytes=-0", "bytes=-", "bytes=5-4", "bytes=100-", "bytes=0-1,3-4", "items=0-5", "bytes=" + "9" * 300 + "-"):
            with self.subTest(header=header):
                self.assertIsNone(parse_single_range(header, 100))


class DownloadFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = create_server(0)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=3)

    def request(self, path, headers=None, method="GET"):
        connection = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=3)
        try:
            connection.request(method, path, headers=headers or {})
            response = connection.getresponse()
            return response.status, dict(response.getheaders()), response.read()
        finally:
            connection.close()

    def test_full_download_and_sha256(self):
        status, headers, body = self.request("/file.bin")
        self.assertEqual(status, 200)
        self.assertEqual(headers["Accept-Ranges"], "bytes")
        self.assertEqual(len(body), 16384)
        self.assertEqual(body, PAYLOAD)
        self.assertEqual(hashlib.sha256(body).hexdigest(), PAYLOAD_SHA256)

    def test_partial_download_reassembles_without_corruption(self):
        first = self.request("/file.bin", {"Range": "bytes=0-8191"})
        second = self.request("/file.bin", {"Range": "bytes=8192-"})
        self.assertEqual((first[0], second[0]), (206, 206))
        self.assertEqual(first[1]["Content-Range"], "bytes 0-8191/16384")
        self.assertEqual(second[1]["Content-Range"], "bytes 8192-16383/16384")
        self.assertEqual(hashlib.sha256(first[2] + second[2]).hexdigest(), PAYLOAD_SHA256)

    def test_suffix_range(self):
        status, headers, body = self.request("/file.bin", {"Range": "bytes=-8"})
        self.assertEqual(status, 206)
        self.assertEqual(headers["Content-Range"], "bytes 16376-16383/16384")
        self.assertEqual(body, PAYLOAD[-8:])

    def test_if_range_etag(self):
        _, headers, _ = self.request("/file.bin", method="HEAD")
        etag = headers["ETag"]
        matching = self.request("/file.bin", {"Range": "bytes=0-10", "If-Range": etag})
        mismatch = self.request("/file.bin", {"Range": "bytes=0-10", "If-Range": '"changed"'})
        self.assertEqual((matching[0], matching[2]), (206, PAYLOAD[:11]))
        self.assertEqual((mismatch[0], mismatch[2]), (200, PAYLOAD))

    def test_unsatisfiable_range(self):
        status, headers, body = self.request("/file.bin", {"Range": "bytes=99999-"})
        self.assertEqual(status, 416)
        self.assertEqual(headers["Content-Range"], "bytes */16384")
        self.assertEqual(body, b"")

    def test_no_range_endpoint_ignores_range(self):
        status, headers, body = self.request("/no-range.bin", {"Range": "bytes=1-2"})
        self.assertEqual(status, 200)
        self.assertEqual(headers["Accept-Ranges"], "none")
        self.assertEqual(body, PAYLOAD)

    def test_head_and_health(self):
        status, headers, body = self.request("/file.bin", method="HEAD")
        self.assertEqual(status, 200)
        self.assertEqual(int(headers["Content-Length"]), 16384)
        self.assertEqual(body, b"")
        health_status, _, health_body = self.request("/health")
        self.assertEqual((health_status, health_body), (200, b"ok"))

    def test_unknown_path_not_a_proxy(self):
        status, _, body = self.request("/https://example.com/private")
        self.assertEqual((status, body), (404, b"not found"))

    def test_local_redirect(self):
        status, headers, body = self.request("/redirect.bin")
        self.assertEqual((status, headers["Location"], body), (302, "/file.bin", b""))

    def test_truncated_response_is_detectable(self):
        with self.assertRaises(http.client.IncompleteRead):
            self.request("/drop.bin")


class HTTPSFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if shutil.which("openssl") is None:
            raise unittest.SkipTest("OpenSSL CLI unavailable; TLS test requires local certificate generation")
        cls.temp = tempfile.TemporaryDirectory(prefix="downloader-tls-fixture-")
        cert = Path(cls.temp.name) / "fixture.crt"
        key = Path(cls.temp.name) / "fixture.key"
        try:
            subprocess.run(
                [
                    "openssl", "req", "-x509", "-newkey", "rsa:2048",
                    "-nodes", "-keyout", str(key), "-out", str(cert),
                    "-days", "1", "-subj", "/CN=localhost",
                    "-addext", "subjectAltName=DNS:localhost,IP:127.0.0.1",
                ],
                check=True,
                capture_output=True,
                timeout=15,
            )
            cls.cert = cert
            cls.server = create_server(0, cert, key)
            cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
            cls.thread.start()
        except Exception:
            cls.temp.cleanup()
            raise

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=3)
        cls.temp.cleanup()

    def test_verified_https_full_and_partial_download(self):
        context = ssl.create_default_context(cafile=str(self.cert))
        for range_header, expected_status, expected in [
            (None, 200, PAYLOAD),
            ("bytes=2048-", 206, PAYLOAD[2048:]),
        ]:
            with self.subTest(range_header=range_header):
                conn = http.client.HTTPSConnection(
                    "127.0.0.1", self.server.server_port,
                    context=context, timeout=3,
                )
                try:
                    headers = {"Range": range_header} if range_header else {}
                    conn.request("GET", "/file.bin", headers=headers)
                    response = conn.getresponse()
                    self.assertEqual(response.status, expected_status)
                    self.assertEqual(response.read(), expected)
                finally:
                    conn.close()

    def test_untrusted_certificate_rejected(self):
        conn = http.client.HTTPSConnection(
            "127.0.0.1", self.server.server_port,
            context=ssl.create_default_context(), timeout=3,
        )
        try:
            with self.assertRaises(ssl.SSLCertVerificationError):
                conn.request("GET", "/file.bin")
                conn.getresponse()
        finally:
            conn.close()


if __name__ == "__main__":
    unittest.main()
