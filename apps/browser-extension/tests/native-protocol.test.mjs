import assert from 'node:assert/strict';
import {webcrypto} from 'node:crypto';
import {readFileSync} from 'node:fs';
import {createRequire} from 'node:module';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import vm from 'node:vm';
import test from 'node:test';
import ts from 'typescript';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const requirePackage = createRequire(import.meta.url);
const cache = new Map();
const modules = {
    '~/backend/BackendError': 'src/backend/BackendError.ts',
    '~/utils/Zod': 'src/utils/Zod.ts',
};

function load(file) {
    if (cache.has(file)) return cache.get(file);
    const source = readFileSync(path.join(root, file), 'utf8');
    const output = ts.transpileModule(source, {
        compilerOptions: {module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022},
    }).outputText;
    const exports = {};
    const require = name => {
        if (name === 'zod') return requirePackage(name);
        if (modules[name]) return load(modules[name]);
        throw new Error(`Unexpected native-protocol dependency: ${name}`);
    };
    vm.runInNewContext(output, {exports, require, crypto: webcrypto}, {filename: file});
    cache.set(file, exports);
    return exports;
}

const protocol = load('src/backend/nativemessaging/NativeMessagingProtocol.ts');
const errors = load('src/backend/BackendError.ts');
const message = (overrides = {}) => ({
    id: 'N_fixture',
    content: {action: 'add', isError: false, payload: '{"accepted":true}'},
    ...overrides,
});

test('native message validator accepts the existing wire envelope', () => {
    assert.equal(protocol.isNativeMessagingMessage(message()), true);
    assert.equal(protocol.isNativeMessagingMessage(message({content: {action: null, isError: false, payload: ''}})), true);
});

test('native validator rejects malformed envelopes before processing', () => {
    for (const invalid of [null, [], {}, {id: 2}, message({content: null}),
        message({content: {action: 'add', isError: 'false', payload: '{}'}}),
        message({content: {action: 'add', isError: false, payload: {accepted: true}}})]) {
        assert.equal(protocol.isNativeMessagingMessage(invalid), false);
    }
});

test('successful responses preserve the actual content', () => {
    const value = message();
    assert.equal(protocol.processResponseOrThrow(value), value.content);
});

test('native errors are decoded to the typed backend error', () => {
    const value = message({content: {action: null, isError: true,
        payload: JSON.stringify({errorType: 'ValidationError', message: 'Bad fixture URL'})}});
    assert.throws(() => protocol.processResponseOrThrow(value), error => {
        assert.ok(error instanceof errors.NativeMessagingApiError);
        assert.equal(error.getBackendErrorType(), 'ValidationError');
        assert.equal(error.getBackendErrorMessage(), 'Bad fixture URL');
        return true;
    });
});

test('malformed error JSON produces an explicit unknown backend error', () => {
    const error = protocol.decodeError(message({content: {action: null, isError: true, payload: '{bad json'}}));
    assert.ok(error instanceof errors.NativeMessagingApiError);
    assert.equal(error.getBackendErrorType(), null);
    assert.equal(error.getBackendErrorMessage(), null);
});

test('error fields with the wrong shape are handled safely', () => {
    const error = protocol.decodeError(message({content: {action: null, isError: true,
        payload: JSON.stringify({errorType: 12, message: ['not a string']})}}));
    assert.equal(error.getBackendErrorType(), null);
    assert.equal(error.getBackendErrorMessage(), null);
});

test('message IDs are unique browser-prefixed UUIDs with distinct native routing', () => {
    const first = protocol.generateMessageId();
    const second = protocol.generateMessageId();
    assert.match(first, /^B_[0-9a-f-]{36}$/);
    assert.notEqual(first, second);
    assert.equal(protocol.isMessageIdFromBrowser(first), true);
    assert.equal(protocol.isMessageIdFromNative(first), false);
    assert.equal(protocol.isMessageIdFromNative('N_fixture'), true);
    assert.equal(protocol.isMessageIdFromBrowser('N_fixture'), false);
});
