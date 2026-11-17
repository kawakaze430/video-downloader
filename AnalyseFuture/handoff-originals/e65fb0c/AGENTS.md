# Working agreement

- Work only on the task the owner requests. Ask before adding features, integrating components, migrating languages, or changing product architecture.
- Use this existing checkout. Do not create another worktree unless asked.
- Work directly on `main`. Do not create feature branches or pull requests.
- While actively making changes, commit completed, reviewable progress at least every five minutes. Push those commits to `origin/main` to protect against workspace loss. Do not make empty commits or force-push; report any blocked push promptly.
- Preserve existing user edits, original archives, third-party licenses, notices, and component instructions.
- This repository holds several source snapshots for one intended product. Extraction does not mean their features are integrated or working together. Do not claim integration without testing it.
- Keep build outputs, downloaded dependencies, credentials, and user media out of commits.
- Read each component's `AGENTS.md` and setup documentation before changing its code.
- Current owner instruction authorizes working on and testing all components. Run relevant dependency, type, build, unit and functional checks safely; the earlier no-test restriction applied only to the completed restructuring pass. Keep verified, failed, blocked and unrun outcomes distinct.
- Read PROJECT_STRUCTURE.md for ownership. Keep Gradle and npm package internals together; do not sort implementation files merely by extension.
- AnalyseFuture contains preserved history, reference implementations, reports and the canonical future vision. Never include it in recursive production workspaces, imports, packaging, or deployment.
