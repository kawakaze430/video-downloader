# Working agreement

- Work only on the task the owner requests. Ask before adding features, integrating components, migrating languages, or changing product architecture.
- Use this existing checkout. Do not create another worktree unless asked.
- Work directly on `main`. Do not create feature branches or pull requests.
- While actively making changes, commit completed, reviewable progress at least every five minutes. Push those commits to `origin/main` to protect against workspace loss. Do not make empty commits or force-push; report any blocked push promptly.
- Preserve existing user edits, original archives, third-party licenses, notices, and component instructions.
- This repository holds several source snapshots for one intended product. Extraction does not mean their features are integrated or working together. Do not claim integration without testing it.
- Keep build outputs, downloaded dependencies, credentials, and user media out of commits.
- Read each component's `AGENTS.md` and setup documentation before changing its code.
- Current owner-authorized recovery scope covers the complete repository and reference repairs. Do not run tests, builds, dependency installs, or application startup during this structure-only pass. A later explicit owner instruction can authorize validation.
- Read PROJECT_STRUCTURE.md for ownership. Keep Gradle and npm package internals together; do not sort implementation files merely by extension.
- AnalyseFuture contains preserved history, reference implementations, reports and the canonical future vision. Never include it in recursive production workspaces, imports, packaging, or deployment.
