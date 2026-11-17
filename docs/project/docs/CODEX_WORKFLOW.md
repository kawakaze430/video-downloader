# Codex Cloud workflow: build efficiently

The owner intends to use GPT-6 Astra/Codex Cloud where available. Model access, task allowances, network access and GitHub permissions depend on the selected environment.

## Start in the correct repository

1. Connect GitHub to Codex and grant access to **rejoansardar620-lang/Downloader-**.
2. Create/select a Codex Cloud environment containing this repository.
3. Configure required development tools, dependency caches and only the network domains genuinely needed.
4. Give Codex a **single bounded milestone**, not "build every feature".
5. Inspect its diff, tests, risks and billable cloud dependencies before approving further work.
6. Commit/push important work. A new cloud task may not inherit uncommitted changes from an earlier task.

Official overview: https://help.openai.com/en/articles/20001545-using-codex-cloud

## First prompt: audit only

~~~text
You are the lead engineer for Downloader.
Read README.md, AGENTS.md, docs/START_HERE.md,
docs/PRODUCT_VISION.md, docs/FEATURE_MATRIX.md,
docs/REFERENCE_REPOSITORIES.md, docs/ARCHITECTURE.md,
docs/ROADMAP.md, docs/LEGAL_SECURITY.md and docs/DECISIONS.md.

GOAL: Build a reliable commercial-quality desktop-first download
manager, browser companion and optional authorized media web UI.
Minimize coding time, compute costs and duplicated functionality.

THIS TASK IS M0 ONLY. DO NOT BUILD THE ENTIRE PRODUCT.

Audit AB Download Manager and AB Browser Integration first.
Compare ReClip, MediaGrabber, HLS Downloader, Parabolic and the
other repositories in docs/REFERENCE_REPOSITORIES.md as needed.

For each candidate:
- Pin the exact commit and read license/third-party notices.
- Check actual source and existing tests, not README alone.
- Build in a safe isolated environment if feasible.
- Record framework, supported platforms, license obligations,
  dependencies, maintenance and security risks.
- Map requested features to verified upstream / partial / missing.
- Keep local repository status distinct from upstream capabilities.
- Propose a single smallest Windows + Chrome HTTPS direct-file
  download vertical slice with measurable acceptance tests.

Update the audit report and docs/DECISIONS.md with proposed choices.
Report every command run and whether it passed or was blocked.
Do not copy upstream code, deploy, buy services or expose secrets.
Stop after M0 and request owner approval for M1.
~~~

## Follow-up prompt for an approved implementation milestone

~~~text
Implement only milestone [M1/M2/etc] from docs/ROADMAP.md,
using the owner-approved ADRs in docs/DECISIONS.md.

First inspect existing source/tests and list what is reusable.
Preserve licenses/notices and maintain clear module boundaries.
Do not build features already functioning in the chosen base.
Add deterministic tests with authorized fixtures, then run the
relevant build and security checks.

Update docs/FEATURE_MATRIX.md with only verified results.
Provide diff summary, test commands/results, unresolved blockers,
security and licensing changes, and a short next-step recommendation.
Stop at the milestone boundary.
~~~

## Anti-waste rules

| Bad pattern | Better instruction |
| --- | --- |
| "Build the whole competitor now" | One milestone with 3–6 measurable acceptance criteria |
| Reimplement queues already in AB | Audit and adapt existing queue APIs |
| Import 10 repositories in one commit | Pin and assess, then import minimal reviewed components |
| Run full video compatibility on every change | Offline fixture tests; bounded scheduled compatibility tests |
| Switch from Kotlin to Tauri without evidence | Build the existing desktop base first, then compare costs |
| Claim everything works because it compiles | Validate behavior end-to-end on supported OS/browser |
| Rebuild all platforms on every tiny edit | Targeted tests first, full CI at release gates |
| Pay for servers before product validation | Local-first architecture, hosting only after approval |

## Reporting format expected from Codex

1. **Outcome:** what is now demonstrably usable?
2. **Changed files:** bounded list.
3. **Feature status:** verified complete / partial / blocked / not started.
4. **Checks:** commands, environment, outcomes and limitations.
5. **Licenses/security:** new dependencies or risks.
6. **Next milestone:** one proposed bounded task.

## Boundaries

- Do not bypass DRM, paywalls, account protections, YouTube/Chrome policies or unauthorized source restrictions.
- Do not harvest browser cookies or repackage third-party source without authorization/license review.
- Do not use hidden credentials, create paid resources, or publish releases without the owner's approval.
- Do not obscure failures: a network-blocked test is **blocked**, not passed.
