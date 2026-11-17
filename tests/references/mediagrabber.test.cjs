const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const root = process.env.MEDIA_GRABBER_VALIDATION_ROOT || path.resolve(__dirname, '../../AnalyseFuture/reference-projects/mediagrabber');
const ts = require(path.join(root, 'node_modules/typescript'));
// Only the reviewed pure parser/quality/RPC modules are loaded. Native host,
// installer, downloader, browser hooks and live network code are never started.
function loadSource(relative) {
  const filename = path.join(root, relative);
  const compiled = ts.transpileModule(fs.readFileSync(filename, 'utf8'), {
    compilerOptions: {module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022},
    fileName: filename,
  });
  const loaded = {exports: {}};
  new Function('exports', 'require', 'module', '__filename', '__dirname', compiled.outputText)(
    loaded.exports, require, loaded, filename, path.dirname(filename));
  return loaded.exports;
}
const {M3U8ParserWrapper:HLS} = loadSource('extension/src/lib/m3u8-parser.ts');
const {DashParserWrapper:DASH} = loadSource('extension/src/lib/dash-parser.ts');
const quality = loadSource('extension/src/lib/quality-utils.ts');
const {RpcProtocol} = loadSource('coapp/src/rpc.ts');
const base='https://example.invalid/owned/master.m3u8';
const master=`#EXTM3U
#EXT-X-MEDIA:TYPE=AUDIO,GROUP-ID="a",NAME="English",LANGUAGE="en",DEFAULT=YES,URI="audio/en.m3u8"
#EXT-X-STREAM-INF:BANDWIDTH=1500000,RESOLUTION=1280x720,CODECS="avc1.4d401f",AUDIO="a"
720/index.m3u8
#EXT-X-STREAM-INF:BANDWIDTH=5000000,RESOLUTION=1920x1080,CODECS="avc1.4d4028",AUDIO="a"
1080/index.m3u8`;
function mpd(attrs='contentType="video"',rep='id="v1" bandwidth="5000000" width="1920" height="1080"',extra='') {
 return `<MPD mediaPresentationDuration="PT1H2M3.5S"><Period><AdaptationSet ${attrs}>${extra}<Representation ${rep}/></AdaptationSet></Period></MPD>`;
}
test('HLS master resolves variants and sorts by bandwidth',()=>{const p=HLS.parse(master,base);assert.equal(p.type,'master');assert.deepEqual(p.variants.map(v=>v.height),[1080,720]);assert.equal(p.variants[0].url,'https://example.invalid/owned/1080/index.m3u8');});
test('HLS alternate audio metadata and child URL',()=>{const p=HLS.parse(master,base);assert.equal(p.mediaRenditions[0].language,'en');assert.equal(p.mediaRenditions[0].default,true);assert.ok(p.childUrls.includes('https://example.invalid/owned/audio/en.m3u8'));});
test('HLS media resolves segments and sums duration',()=>{const p=HLS.parse('#EXTM3U\n#EXT-X-TARGETDURATION:8\n#EXTINF:3.5,\none.ts\n#EXTINF:4.25,\ntwo.ts',base);assert.equal(p.type,'media');assert.equal(p.duration,7.75);assert.deepEqual(p.segments,['https://example.invalid/owned/one.ts','https://example.invalid/owned/two.ts']);});
test('HLS repeated identical variant metadata deduplicates',()=>{const p=HLS.parse('#EXTM3U\n#EXT-X-STREAM-INF:BANDWIDTH=100,RESOLUTION=640x360\na.m3u8\n#EXT-X-STREAM-INF:BANDWIDTH=100,RESOLUTION=640x360\nb.m3u8',base);assert.equal(p.variants.length,1);});
test('HLS invalid input yields no variants or segments',()=>{const p=HLS.parse('not a manifest',base);assert.deepEqual(p.variants,[]);assert.deepEqual(p.segments,[]);});
test('HLS fetch reports HTTP error instead of parsing it',async()=>{const original=global.fetch;global.fetch=async()=>({ok:false,status:403});try{await assert.rejects(HLS.fetchAndParse(base),/HTTP 403/);}finally{global.fetch=original;}});
test('DASH parses video dimensions and bandwidth',()=>{const p=DASH.parse(mpd(),base);assert.equal(p.variants.length,1);assert.equal(p.variants[0].height,1080);assert.equal(p.variants[0].bandwidth,5000000);});
test('DASH parses subtitle BaseURL and language',()=>{const p=DASH.parse('<MPD><Period><AdaptationSet contentType="text" mimeType="text/vtt" lang="en"><BaseURL>sub/en.vtt</BaseURL></AdaptationSet></Period></MPD>',base);assert.deepEqual(p.subtitleTracks,[{url:'https://example.invalid/owned/sub/en.vtt',lang:'en',mimeType:'text/vtt'}]);});
test('DASH marks protected adaptation set',()=>{const p=DASH.parse(mpd(undefined,undefined,'<ContentProtection schemeIdUri="urn:example:protected"/>'),base);assert.equal(p.variants[0].encrypted,true);});
test('DASH parses ISO duration with hours/minutes/fractional seconds',()=>{assert.equal(DASH.parse(mpd(),base).duration,3723.5);});
test('DASH invalid input yields no variants',()=>{assert.deepEqual(DASH.parse('not XML',base).variants,[]);});
test('DASH accepts standard XML single-quoted attributes',()=>{const p=DASH.parse("<MPD mediaPresentationDuration='PT4S'><Period><AdaptationSet contentType='video'><Representation bandwidth='800000' height='360' width='640'/></AdaptationSet></Period></MPD>",base);assert.equal(p.variants.length,1);assert.equal(p.variants[0].height,360);assert.equal(p.duration,4);});
test('quality labels use declared dimensions',()=>{assert.equal(quality.getQualityLabel(1080),'1080p');assert.equal(quality.getQualityLabel(2160),'4K');assert.equal(quality.getQualityLabel(),'Unknown');});
test('duration formatting handles hours',()=>{assert.equal(quality.formatDuration(3723),'1:02:03');assert.equal(quality.formatDuration(75),'1:15');});
test('bandwidth formatting handles Mbps and Kbps',()=>{assert.equal(quality.formatBandwidth(1500000),'1.5 Mbps');assert.equal(quality.formatBandwidth(500000),'500 Kbps');});
test('quality conversion deduplicates repeated input and sorts',()=>{const p=quality.toQualityInfo([{height:720,bitrate:1000,url:'a'},{height:1080,bitrate:4000,url:'b'},{height:720,bitrate:1000,url:'duplicate'}]);assert.equal(p.length,2);assert.equal(p[0].height,1080);assert.equal(p[1].bandwidth,1000000);});
test('quality deduplication keeps one label',()=>{const p=quality.deduplicateQualities([{label:'720p',bandwidth:1000,url:'a'},{label:'720p',bandwidth:900,url:'b'}]);assert.equal(p.length,1);assert.equal(p[0].url,'a');});
test('quality selection handles empty/best/worst',()=>{const values=[{bandwidth:4000,url:'high'},{bandwidth:1000,url:'low'}];assert.equal(quality.selectQuality([],'best'),null);assert.equal(quality.selectQuality(values,'best').url,'high');assert.equal(quality.selectQuality(values,'worst').url,'low');});
test('RPC rejects calls before connection',async()=>{await assert.rejects(new RpcProtocol().call('not-connected'),/not connected/);});
test('RPC request and successful reply correlate',async()=>{const rpc=new RpcProtocol();let sent;rpc.setPost(m=>{sent=m;});const value=rpc.call('sum',2,3);assert.equal(sent.type,'weh#rpc');assert.deepEqual(sent._args,[2,3]);rpc.receive({type:'weh#rpc',_reply:sent._request,_result:5});assert.equal(await value,5);});
test('RPC error reply rejects correlated call',async()=>{const rpc=new RpcProtocol();let sent;rpc.setPost(m=>{sent=m;});const value=rpc.call('fail');rpc.receive({type:'weh#rpc',_reply:sent._request,_error:'synthetic failure'});await assert.rejects(value,/synthetic failure/);});
test('RPC dispatches handler and replies',async()=>{const rpc=new RpcProtocol();let resolve;const reply=new Promise(r=>{resolve=r;});rpc.setPost(resolve);rpc.listen({sum:(a,b)=>a+b});rpc.receive({type:'weh#rpc',_request:17,_method:'sum',_args:[2,3]});assert.deepEqual(await reply,{type:'weh#rpc',_reply:17,_result:5});});
test('RPC unknown method reports error',async()=>{const rpc=new RpcProtocol();let resolve;const reply=new Promise(r=>{resolve=r;});rpc.setPost(resolve);rpc.receive({type:'weh#rpc',_request:18,_method:'missing'});const p=await reply;assert.equal(p._reply,18);assert.match(p._error,/not a function/);});
test('RPC unknown reply is safely ignored',()=>{assert.doesNotThrow(()=>new RpcProtocol().receive({type:'weh#rpc',_reply:999,_result:'ignored'}));});
