# Future analysis, recovery evidence and preserved work

Start with [the current audit](REPOSITORY_AUDIT.txt),
[the complete inventory](COMPLETE_FILE_INVENTORY.txt),
[the mapping](ORIGINAL_TO_NEW_PATH_MAPPING.txt), and
[the future vision](PROJECT_VISION_AND_FUTURE_ROADMAP.txt).
The starting commit for this pass is `7a7e2f6`.

- Root `.txt` reports: actual inventory, feature ownership, overlap decisions,
  security concerns, migration evidence, validation boundaries and handoff.
- `repository-inventory/`: machine-readable per-file content/dependency metadata,
  relationship graph, final catalogue and ignored/generated path inventory.
- `migration-records/`: exact original/active/retained path hashes and one-off
  migration provenance. Generator sources are not production entrypoints.
- `historical-implementations/7a7e2f6/`: exact originals of revised files.
- `incomplete-features/browser-extension/`: orphan imports-only backend stub;
  active dispatch remains in the browser application's Backend.ts.
- `reference-projects/mediagrabber/` and `reference-projects/reclip/`: intact
  alternative implementations, not active product services or workspaces.
- `prior-versions/0b2a1ad/` and `recovery-notes/`: earlier preserved documents,
  request scope and past audit evidence. These are historical, not current setup.
- `security-reports/pre-scope-change-logs/`: earlier observations, not proof of
  post-move behavior. The latest pass deliberately ran no tests.

No file was established as attacker-added merely because it was unfamiliar.
Current account security is unresolved. Review the security report before
adopting code: reference implementations contain known trust/resource concerns.
The directory name is not a sandbox. Do not include this tree in recursive
production imports, package workspaces, builds or deployment. Secrets must be
handled securely, not copied here. Preserve licenses and provenance.

The full exact-byte/Git preservation record is
[migration-records/preservation-manifest.json](migration-records/preservation-manifest.json).
