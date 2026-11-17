package ir.amirab.downloader.connection

import com.sun.net.httpserver.HttpExchange
import com.sun.net.httpserver.HttpServer
import ir.amirab.downloader.connection.proxy.AutoConfigurableProxyProvider
import ir.amirab.downloader.connection.proxy.NoopSystemProxySelectorProvider
import ir.amirab.downloader.connection.proxy.ProxyStrategy
import ir.amirab.downloader.connection.proxy.ProxyStrategyProvider
import ir.amirab.downloader.downloaditem.http.HttpDownloadCredentials
import java.io.IOException
import java.net.InetSocketAddress
import java.security.MessageDigest
import java.util.concurrent.TimeUnit
import kotlin.test.AfterTest
import kotlin.test.BeforeTest
import kotlin.test.Test
import kotlin.test.assertContentEquals
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith
import kotlin.test.assertFalse
import kotlin.test.assertNotNull
import kotlin.test.assertTrue
import kotlinx.coroutines.runBlocking
import okhttp3.OkHttpClient
import okio.buffer

/** Real client/response reads against synthetic loopback endpoints; no external media. */
class HttpClientIntegrationTest {
    private val payload = ByteArray(16_384) { (it % 256).toByte() }
    private lateinit var server: HttpServer
    private lateinit var transport: OkHttpClient
    private lateinit var client: OkHttpHttpDownloaderClient
    @Volatile private var received = emptyMap<String, String>()

    @BeforeTest
    fun start() {
        server = HttpServer.create(InetSocketAddress("127.0.0.1", 0), 0)
        server.createContext("/") { exchange -> respond(exchange) }
        server.start()
        transport = OkHttpClient.Builder()
            .connectTimeout(5, TimeUnit.SECONDS)
            .readTimeout(5, TimeUnit.SECONDS)
            .build()
        client = OkHttpHttpDownloaderClient(
            transport,
            object : UserAgentProvider {
                override fun getUserAgent() = "DownloaderFixture/1.0"
            },
            object : ProxyStrategyProvider {
                override fun getProxyStrategyFor(url: String) = ProxyStrategy.Direct
            },
            NoopSystemProxySelectorProvider(),
            AutoConfigurableProxyProvider.NoOp(),
        )
    }

    @AfterTest
    fun stop() {
        server.stop(0)
        transport.connectionPool.evictAll()
        transport.dispatcher.executorService.shutdownNow()
    }

    private fun credentials(path: String = "/file.bin") = HttpDownloadCredentials(
        "http://127.0.0.1:${server.address.port}$path"
    )

    private fun respond(exchange: HttpExchange) {
        exchange.use { e ->
            received = e.requestHeaders.entries.associate { it.key.lowercase() to it.value.joinToString(",") }
            val path = e.requestURI.path
            if (path == "/redirect.bin") {
                e.responseHeaders.add("Location", "/file.bin")
                e.sendResponseHeaders(302, -1)
                return
            }
            if (path == "/auth.bin") {
                e.responseHeaders.add("WWW-Authenticate", "Basic realm=\"fixture\"")
                e.sendResponseHeaders(401, -1)
                return
            }
            e.responseHeaders.add("Content-Type", "application/octet-stream")
            e.responseHeaders.add("ETag", "\"fixture-v1\"")
            e.responseHeaders.add("Content-Disposition", "attachment; filename=\"fixture.bin\"")
            val range = e.requestHeaders.getFirst("Range")
            val match = range?.let { Regex("bytes=(\\d+)-(\\d*)").matchEntire(it) }
            var body = payload
            var status = 200
            if (match != null && path != "/no-range.bin") {
                val start = match.groupValues[1].toInt()
                if (start >= payload.size) {
                    e.responseHeaders.add("Content-Range", "bytes */${payload.size}")
                    e.sendResponseHeaders(416, -1)
                    return
                }
                val end = match.groupValues[2].toIntOrNull()?.coerceAtMost(payload.lastIndex) ?: payload.lastIndex
                body = payload.copyOfRange(start, end + 1)
                e.responseHeaders.add("Content-Range", "bytes $start-$end/${payload.size}")
                status = 206
            }
            e.sendResponseHeaders(status, body.size.toLong())
            if (path == "/drop.bin") {
                e.responseBody.write(body, 0, 2_048)
                // Deliberate declared-length mismatch: the client must reject truncation.
                runCatching { e.responseBody.close() }
            } else {
                e.responseBody.write(body)
            }
        }
    }

    @Test
    fun fullDownloadHasExpectedBytesAndHash(): Unit = runBlocking {
        client.connect(credentials(), null, null).use { connection ->
            assertEquals(200, connection.responseInfo.statusCode)
            assertEquals(payload.size.toLong(), connection.contentLength)
            val bytes = connection.source.buffer().readByteArray()
            assertContentEquals(payload, bytes)
            val hash = MessageDigest.getInstance("SHA-256").digest(bytes).joinToString("") { "%02x".format(it) }
            assertEquals("a1f259d4365ed4320c377ce26f5c8c56dcdc9a89e7b641bfd8eabfbbeac86654", hash)
        }
    }

    @Test
    fun rangeCarriesWholeSizeAndResumeCapability(): Unit = runBlocking {
        client.connect(credentials(), 0, 8191).use { connection ->
            assertEquals(206, connection.responseInfo.statusCode)
            assertEquals(8192L, connection.contentLength)
            assertEquals(16384L, connection.responseInfo.totalLength)
            assertTrue(connection.responseInfo.resumeSupport)
            assertContentEquals(payload.copyOfRange(0, 8192), connection.source.buffer().readByteArray())
        }
    }

    @Test
    fun partialResponsesReassembleWithoutCorruption(): Unit = runBlocking {
        val first = client.connect(credentials(), 0, 8191).use { it.source.buffer().readByteArray() }
        val last = client.connect(credentials(), 8192, null).use { it.source.buffer().readByteArray() }
        assertContentEquals(payload, first + last)
    }

    @Test
    fun ignoredRangeIsReportedAsFullResponse(): Unit = runBlocking {
        client.connect(credentials("/no-range.bin"), 8192, null).use { connection ->
            assertEquals(200, connection.responseInfo.statusCode)
            assertFalse(connection.responseInfo.resumeSupport)
            assertContentEquals(payload, connection.source.buffer().readByteArray())
        }
    }

    @Test
    fun redirectUsesFinalUrlAndPayload(): Unit = runBlocking {
        client.connect(credentials("/redirect.bin"), null, null).use { connection ->
            assertTrue(connection.responseInfo.requestUrl.endsWith("/file.bin"))
            assertContentEquals(payload, connection.source.buffer().readByteArray())
        }
    }

    @Test
    fun truncatedTransferRaisesInsteadOfReturningPartialSuccess() {
        assertFailsWith<IOException> {
            runBlocking {
                client.connect(credentials("/drop.bin"), null, null).use { it.source.buffer().readByteArray() }
            }
        }
    }

    @Test
    fun integrityHeadersOverrideCallerAndHostIsNotForwarded(): Unit = runBlocking {
        val request = credentials().copy(headers = mapOf("Accept-Encoding" to "gzip", "Host" to "wrong.invalid"))
        client.connect(request, null, null).use { it.source.buffer().readByteArray() }
        assertEquals("identity", received["accept-encoding"])
        assertEquals("127.0.0.1:${server.address.port}", received["host"])
    }

    @Test
    fun configuredDefaultUserAgentIsSent(): Unit = runBlocking {
        client.connect(credentials(), null, null).use { it.source.buffer().readByteArray() }
        assertEquals("DownloaderFixture/1.0", received["user-agent"])
    }

    @Test
    fun explicitUserAgentTakesPriority(): Unit = runBlocking {
        client.connect(credentials().copy(userAgent = "ExplicitFixture/2.0"), null, null).use {
            it.source.buffer().readByteArray()
        }
        assertEquals("ExplicitFixture/2.0", received["user-agent"])
    }

    @Test
    fun authenticationFailureIsVisibleToCaller(): Unit = runBlocking {
        val info = client.head(credentials("/auth.bin"), null, null)
        assertEquals(401, info.statusCode)
        assertTrue(info.requiresAuth)
        assertTrue(info.requireBasicAuth)
        assertFalse(info.isSuccessFul)
    }

    @Test
    fun unsatisfiableRangeIsNotReportedSuccessful(): Unit = runBlocking {
        val info = client.head(credentials(), 99_999, null)
        assertEquals(416, info.statusCode)
        assertFalse(info.isSuccessFul)
        assertNotNull(info.unsuccessFullException)
    }
}
