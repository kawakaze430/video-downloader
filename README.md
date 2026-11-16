# video-downloader

One repository for the intended download-manager project. The five supplied
archives are now extracted under `sources/` with their original contents and
licenses preserved. The ZIP files remain at the root as source backups.

| Directory | Supplied source | Languages / tools |
| --- | --- | --- |
| `sources/downloader-blueprint/` | Downloader planning documents and deterministic download fixture | Python 3.10+, OpenSSL for HTTPS tests |
| `sources/ab-download-manager/` | Desktop download manager candidate | Kotlin, Gradle, JVM |
| `sources/ab-browser-integration/` | AB browser extension candidate | TypeScript, React, npm, Vite |
| `sources/mediagrabber/` | MediaGrabber browser extension and native companion | TypeScript, Node.js, npm |
| `sources/reclip/` | ReClip web downloader reference | Python, Flask, HTML/CSS/JavaScript |

This change organizes source snapshots. It does not connect the applications,
combine their features, select a product license, or migrate languages. Each
component keeps its own build files and documentation. Archive hashes and file
counts are recorded in [sources/archives.json](sources/archives.json).

## Verified fixture workflow

```sh
cd sources/downloader-blueprint
python3 -m unittest discover -s tests -v
python3 -m tools.fixtures.http_fixture --port 8765
```

The fixture is a local synthetic download target, not the complete product.
See its [documentation](sources/downloader-blueprint/tools/fixtures/README.md).

## Languages

One product can contain several languages. A desktop app, browser extension,
and companion process can exchange structured messages while retaining their
existing implementations. A shared protocol would need to be designed and
tested in a separately approved integration task.

A single-language approach is also possible, but converting the Kotlin desktop
or Python applications to TypeScript would require substantial rewriting.
Browser extension code still needs JavaScript output, and FFmpeg remains an
external media-processing tool. No language migration has been selected or
started. Wait for the owner's direction before integration or migration.

## Source licenses

AB Download Manager and its browser integration include Apache-2.0 licenses.
MediaGrabber and ReClip include MIT licenses. The Downloader blueprint supplies
no root LICENSE; none has been invented here. Keep component notices intact.
