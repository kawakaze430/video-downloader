# Local validation

Run from this package:

```sh
npm ci --ignore-scripts
npm test
npm run build
npm run pack:chrome
npm run pack:firefox
```

`npm test` checks the complete source tree and compile-only message contracts
with `strict: true` and `skipLibCheck: false`, then runs Node tests of the
manifest builders and declaration-preparation guard. It does not contact a
website, inspect cookies or connect to a desktop native host.

## Published type compatibility

The locked `webext-bridge@6.0.1` bundle omits its `type-fest@2` declaration
dependency, constrains endpoint message IDs differently from `ProtocolMap`,
and tries to infer original generic parameters through non-invertible
`Jsonify<T>` types. Its no-payload defaults also contradict strict null checking.
The app now declares the intended type-fest version explicitly.

`scripts/prepare-types.mjs` repairs only the exact reviewed `.d.ts` files. It
checks dependency versions and original/patched hashes, fails on unexpected
content, and is idempotent. It reads branded payload/return properties directly,
keeps command IDs and payloads closed, and represents undefined requests.
Compile-time negative examples fail if these guarantees are weakened.
Runtime JavaScript and the native messaging protocol remain unchanged.

The shared manifest type from `@types/chrome@0.0.321` is used by the Vite plugin
for both browsers. Its author property omits Firefox's supported string form
(present in `webextension-polyfill`'s `Manifest.ManifestBase`). The declaration
repair adds that specific form while preserving object authors and every
other manifest field. Generated manifests retain the original author metadata.

Preparation runs explicitly before type checks, so frozen installations with
`--ignore-scripts` work. Dependency upgrades must review/update these patches;
they are not silently accepted. Once upstream declarations are repaired, remove
the compatibility step after the same positive/negative checks pass.

Bundle/package success verifies generated files, not browser permissions,
desktop pairing, download correctness or live platform support. Those need
separate browser/native-host integration checks.
