import assert from 'node:assert/strict';
import {readFileSync, writeFileSync, mkdirSync, mkdtempSync, copyFileSync, rmSync} from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
import test from 'node:test';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const files = [
    'webext-bridge/package.json', '@types/chrome/package.json', 'type-fest/package.json',
    ...['background', 'content-script', 'devtools', 'options', 'popup', 'window', 'types-248b79c4'].map(name => `webext-bridge/dist/${name}.d.ts`),
    '@types/chrome/index.d.ts',
];

function fixture(t) {
    const dir = mkdtempSync(path.join(os.tmpdir(), 'browser-types-'));
    t.after(() => rmSync(dir, {recursive: true, force: true}));
    mkdirSync(path.join(dir, 'scripts'));
    copyFileSync(path.join(root, 'scripts/prepare-types.mjs'), path.join(dir, 'scripts/prepare-types.mjs'));
    for (const name of files) {
        const target = path.join(dir, 'node_modules', name);
        mkdirSync(path.dirname(target), {recursive: true});
        copyFileSync(path.join(root, 'node_modules', name), target);
    }
    return dir;
}

function prepare(dir) {
    return spawnSync(process.execPath, [path.join(dir, 'scripts/prepare-types.mjs')], {encoding: 'utf8'});
}

test('preparing the already-patched declarations is idempotent', t => {
    const dir = fixture(t);
    const before = readFileSync(path.join(dir, 'node_modules/webext-bridge/dist/background.d.ts'), 'utf8');
    const result = prepare(dir);
    assert.equal(result.status, 0, result.stderr);
    assert.match(result.stdout, /0 files prepared/);
    assert.equal(readFileSync(path.join(dir, 'node_modules/webext-bridge/dist/background.d.ts'), 'utf8'), before);
});

test('unexpected declaration edits fail before any patch is written', t => {
    const dir = fixture(t);
    const target = path.join(dir, 'node_modules/webext-bridge/dist/background.d.ts');
    writeFileSync(target, readFileSync(target, 'utf8').replace('messageID: K', 'messageID: string'));
    const result = prepare(dir);
    assert.notEqual(result.status, 0);
    assert.match(result.stderr, /Modified compatibility declarations/);
});

test('an unreviewed dependency version is rejected', t => {
    const dir = fixture(t);
    const target = path.join(dir, 'node_modules/webext-bridge/package.json');
    const pkg = JSON.parse(readFileSync(target));
    pkg.version = '6.0.2';
    writeFileSync(target, JSON.stringify(pkg));
    const result = prepare(dir);
    assert.notEqual(result.status, 0);
    assert.match(result.stderr, /expected 6\.0\.1/);
});
