// Compile-only assertions. tsc reports unused @ts-expect-error annotations if
// a compatibility change accidentally widens the protocol to arbitrary data.
import {onMessage, sendMessage} from "webext-bridge/background";
import type {DownloadRequestHeaders} from "~/interfaces/DownloadRequestItem";
import type {Runtime} from "webextension-polyfill";

const reachability: Promise<boolean> = sendMessage("test_http_port", 15151, "background");
const native: Promise<boolean> = sendMessage("test_native_messaging", undefined, "background");
const headers: Promise<(DownloadRequestHeaders | null)[]> = sendMessage("get_headers", ["https://example.com/file.bin"], "background");
const platform: Promise<Runtime.PlatformInfo> = sendMessage("get_platform", undefined, "background");
void [reachability, native, headers, platform];

onMessage("test_http_port", message => {
    const port: number = message.data;
    return port > 0;
});
onMessage("test_native_messaging", message => {
    const noPayload: undefined = message.data;
    return noPayload === undefined;
});

// @ts-expect-error Unknown commands must not cross the bridge.
sendMessage("unregistered_command", null, "background");
// @ts-expect-error The HTTP-port request carries a number, not text.
sendMessage("test_http_port", "15151", "background");
// @ts-expect-error Header requests carry a list of URL strings.
sendMessage("get_headers", [42], "background");
// @ts-expect-error No-payload commands must reject arbitrary data.
sendMessage("test_native_messaging", {unexpected: true}, "background");
// @ts-expect-error HTTP-port handlers must return a boolean.
onMessage("test_http_port", () => "yes");
// @ts-expect-error Return values must not be widened to an unrelated scalar.
const wrongResult: Promise<string> = sendMessage("test_http_port", 15151, "background");
void wrongResult;
