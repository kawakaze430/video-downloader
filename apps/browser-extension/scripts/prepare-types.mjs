// Compatibility fixes for exact published declaration defects. Runtime JS is
// untouched. npm ci --ignore-scripts is supported: typecheck invokes this step.
import {createHash} from 'node:crypto';
import {readFileSync, writeFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import path from 'node:path';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const hash = text => createHash('sha256').update(text).digest('hex');
const patchedHashes = {
    '997e36c3c7b522f5a6f659a8f0f83e67bc9b446b6f2e9e2e03dc99ecce4c507d': '85f67a666ad908f49321cfdaaecccfd2026bb83eaf00ee2a5507a15e7f4a13eb',
    '827da0b7725082864cb36bffad6ec3432aea80bd20852238a6b09c5b910f6043': '145dedab435aaaf19dc272db90d7696316c57f8209dd136ed3b59d5f68cb8075',
    '0cda72163975bcbebee86e0406a25cf914b206c61c68f8acdabc6e24a22a2333': '8ffc3d043678e1f0177b7b309ec616ee89b4dcecf2c8b82d7ff0db466874d183',
    '66a9f535fcb5144226deb42e40a0da202f2fd39adf15f79e8d90a0b09986eb73': 'c99254f292a2ec14037de3a1c7fa4694bdebe9af6b863963d4c53eaa00639b17',
    '80e9454038ed30c7a25eb35197aa12973898dc2b78e0938cfbce75432b7baa4d': 'cc9a2e7162bf7bf6fe5cfe8a90ccd82a6d11698554debe43e02fe162c1ef897f',
};

function version(name, expected) {
    const actual = JSON.parse(readFileSync(path.join(root, 'node_modules', name, 'package.json'))).version;
    if (actual !== expected) throw new Error(`Review declaration compatibility for ${name}@${actual}; expected ${expected}`);
}

function replaceOnce(text, before, after) {
    if (text.split(before).length !== 2) throw new Error(`Expected one declaration fragment: ${before}`);
    return text.replace(before, after);
}

const changes = [];
function patch(relative, originalHash, transform) {
    const file = path.join(root, 'node_modules', relative);
    const current = readFileSync(file, 'utf8');
    if (hash(current) === originalHash) {
        const transformed = transform(current);
        if (hash(transformed) !== patchedHashes[originalHash]) throw new Error(`Unexpected patch result for ${relative}`);
        changes.push([file, transformed]);
        return;
    }
    // Idempotency only accepts the exact expected transformed declaration.
    const marker = '// ab-download-manager declaration compatibility v1\n';
    if (!current.startsWith(marker)) throw new Error(`Unexpected declarations in ${relative}; reinstall with npm ci --ignore-scripts`);
    const original = current.slice(marker.length);
    // The pinned expected hash is external to node_modules and cannot be
    // bypassed by rewriting the declaration's self-description.
    const suffix = /\n\/\* original-sha256: ([a-f0-9]{64}); patched-sha256: ([a-f0-9]{64}) \*\/\n$/;
    const match = original.match(suffix);
    if (!match || match[1] !== originalHash || match[2] !== patchedHashes[originalHash]
        || hash(original.replace(suffix, '')) !== patchedHashes[originalHash]) {
        throw new Error(`Modified compatibility declarations in ${relative}; reinstall with npm ci --ignore-scripts`);
    }
}

version('webext-bridge', '6.0.1');
version('@types/chrome', '0.0.321');
version('type-fest', '2.19.0');

const contexts = {
    'background.d.ts': '997e36c3c7b522f5a6f659a8f0f83e67bc9b446b6f2e9e2e03dc99ecce4c507d',
    'content-script.d.ts': '827da0b7725082864cb36bffad6ec3432aea80bd20852238a6b09c5b910f6043',
    'devtools.d.ts': '997e36c3c7b522f5a6f659a8f0f83e67bc9b446b6f2e9e2e03dc99ecce4c507d',
    'options.d.ts': '997e36c3c7b522f5a6f659a8f0f83e67bc9b446b6f2e9e2e03dc99ecce4c507d',
    'popup.d.ts': '997e36c3c7b522f5a6f659a8f0f83e67bc9b446b6f2e9e2e03dc99ecce4c507d',
    'window.d.ts': '0cda72163975bcbebee86e0406a25cf914b206c61c68f8acdabc6e24a22a2333',
};

for (const [file, digest] of Object.entries(contexts)) {
    patch(`webext-bridge/dist/${file}`, digest, text => {
        text = replaceOnce(text, "import { G as GetDataType,", "import { b as DataTypeKey, G as GetDataType,");
        if ((text.match(/K extends string = string/g) ?? []).length !== 2) throw new Error(`Unexpected endpoint declarations: ${file}`);
        return text.replaceAll('K extends string = string', 'K extends DataTypeKey = DataTypeKey');
    });
}

patch('webext-bridge/dist/types-248b79c4.d.ts', '66a9f535fcb5144226deb42e40a0da202f2fd39adf15f79e8d90a0b09986eb73', text => {
    text = replaceOnce(text, "import { JsonValue, Jsonify } from 'type-fest';", "import { JsonValue, Jsonify } from 'type-fest';\ntype JsonData<T> = T extends undefined ? undefined : Jsonify<T>;");
    text = replaceOnce(text, 'interface BridgeMessage<T extends JsonValue>', 'interface BridgeMessage<T extends JsonValue | undefined>');
    text = replaceOnce(text, 'OnMessageCallback<T extends JsonValue,', 'OnMessageCallback<T extends JsonValue | undefined,');
    text = replaceOnce(text, 'data: Jsonify<Data>;', 'data: JsonData<Data>;');
    text = replaceOnce(text, 'return: Jsonify<Return>;', 'return: JsonData<Return>;');
    text = replaceOnce(text,
        "declare type GetDataType<K extends DataTypeKey, Fallback extends JsonValue = undefined> = K extends keyof ProtocolMap ? ProtocolMap[K] extends (...args: infer Args) => any ? Args['length'] extends 0 ? undefined : Args[0] : ProtocolMap[K] extends ProtocolWithReturn<infer Data, any> ? Data : ProtocolMap[K] : Fallback;",
        "declare type GetDataType<K extends DataTypeKey, Fallback extends JsonValue | undefined = undefined> = K extends keyof ProtocolMap ? ProtocolMap[K] extends (...args: infer Args) => any ? Args['length'] extends 0 ? undefined : JsonData<Args[0]> : ProtocolMap[K] extends { [ProtocolWithReturnSymbol]: true; data: infer Data } ? JsonData<Data> : JsonData<ProtocolMap[K]> : Fallback;");
    return replaceOnce(text,
        'declare type GetReturnType<K extends DataTypeKey, Fallback extends JsonValue = undefined> = K extends keyof ProtocolMap ? ProtocolMap[K] extends (...args: any[]) => infer R ? R : ProtocolMap[K] extends ProtocolWithReturn<any, infer Return> ? Return : void : Fallback;',
        'declare type GetReturnType<K extends DataTypeKey, Fallback extends JsonValue | undefined = undefined> = K extends keyof ProtocolMap ? ProtocolMap[K] extends (...args: any[]) => infer R ? JsonData<R> : ProtocolMap[K] extends { [ProtocolWithReturnSymbol]: true; return: infer Return } ? JsonData<Return> : void : Fallback;');
});

// Firefox's author schema is a string (as declared by webextension-polyfill).
// @types/chrome is also used by the Vite plugin for Firefox manifests, so its
// common base must represent that supported variant without losing other keys.
patch('@types/chrome/index.d.ts', '80e9454038ed30c7a25eb35197aa12973898dc2b78e0938cfbce75432b7baa4d', text => replaceOnce(text,
    'author?: {\n                email: string;\n            } | undefined;',
    'author?: string | {\n                email: string;\n            } | undefined;'));

// Validate every precondition before changing any file.
for (const [file, transformed] of changes) {
    const originalHash = hash(readFileSync(file, 'utf8'));
    writeFileSync(file, '// ab-download-manager declaration compatibility v1\n' + transformed
        + `\n/* original-sha256: ${originalHash}; patched-sha256: ${hash(transformed)} */\n`);
}
console.log(`Declaration compatibility ready (${changes.length} files prepared; runtime JS unchanged).`);
