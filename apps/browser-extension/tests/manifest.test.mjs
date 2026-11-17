import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import vm from 'node:vm';
import test from 'node:test';
import ts from 'typescript';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const metadata = JSON.parse(readFileSync(path.join(root, 'package.json')));
const cache = new Map();

// Only the pure manifest builder and its shared metadata module are evaluated;
// no browser globals, background workers, URLs or native host are contacted.
function loadBuilder(file) {
    if (cache.has(file)) return cache.get(file);
    const source = readFileSync(path.join(root, 'src/manifest', file), 'utf8');
    const compiled = ts.transpileModule(source, {
        // Vite exposes imported JSON as the default export; emulate that
        // interop while evaluating the pure builders in CommonJS.
        compilerOptions: {module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022, esModuleInterop: true},
    }).outputText;
    const exports = {};
    const require = name => {
        if (name === '../../package.json') return metadata;
        if (name === './shared') return loadBuilder('shared.ts');
        throw new Error(`Unexpected manifest dependency: ${name}`);
    };
    vm.runInNewContext(compiled, {exports, require}, {filename: file});
    cache.set(file, exports);
    return exports;
}

test('Chrome builder emits MV3 service-worker and host permissions', () => {
    const manifest = loadBuilder('manifest.chrome.ts').getManifestForChrome();
    assert.equal(manifest.manifest_version, 3);
    assert.equal(manifest.background.service_worker, 'src/entrypoint/Background.ts');
    assert.equal(manifest.background.scripts, undefined);
    assert.equal(manifest.action.default_popup, 'src/entrypoint/BrowserAction/index.html');
    assert.ok(manifest.host_permissions.includes('*://*/*'));
    assert.ok(!manifest.permissions.includes('webRequestBlocking'));
});

test('Firefox builder emits MV2 scripts and its browser ID', () => {
    const manifest = loadBuilder('manifest.firefox.ts').getManifestForFirefox();
    assert.equal(manifest.manifest_version, 2);
    assert.equal(manifest.background.scripts[0], 'src/entrypoint/Background.ts');
    assert.equal(manifest.background.service_worker, undefined);
    assert.equal(manifest.browser_specific_settings.gecko.id, 'firefox-integration@abdownloadmanager.com');
    assert.ok(manifest.permissions.includes('webRequestBlocking'));
});

test('both manifests retain supplied author, metadata and existing source assets', () => {
    for (const [file, name] of [['manifest.chrome.ts', 'getManifestForChrome'], ['manifest.firefox.ts', 'getManifestForFirefox']]) {
        const manifest = loadBuilder(file)[name]();
        assert.equal(manifest.author, metadata.author);
        assert.equal(typeof manifest.author, 'string');
        assert.equal(manifest.name, metadata.displayName);
        assert.equal(manifest.version, metadata.version);
        readFileSync(path.join(root, 'public', manifest.icons[128]));
        readFileSync(path.join(root, manifest.options_ui.page));
        for (const item of manifest.content_scripts) for (const script of item.js) readFileSync(path.join(root, script));
    }
});
