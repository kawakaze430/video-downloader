# Contributing to Downloader

Thanks for helping create a reliable, privacy-conscious download manager. The project is currently **documentation-first**: architecture and candidate repositories exist, but application code has not yet been imported or validated.

## Before your first contribution

1. Read [the quick start](docs/START_HERE.md), [vision](docs/PRODUCT_VISION.md), [feature matrix](docs/FEATURE_MATRIX.md) and [legal/security requirements](docs/LEGAL_SECURITY.md).
2. Check [open decisions](docs/DECISIONS.md) and the [roadmap](docs/ROADMAP.md).
3. Open or select an issue describing a narrow outcome. Avoid duplicate work and giant PRs.
4. For proposed upstream code, provide the exact repository, commit/tag, license, dependency tree and preservation requirements.
5. Discuss nontrivial changes to architecture, licenses, distribution or network behavior before implementation.

## Current contribution opportunities

- Verify reference-repository licenses, recent activity and dependency security.
- Build a feature coverage matrix from **actual source inspection and test results**.
- Identify usable direct-download fixtures with explicit redistribution/test permission.
- Design the protocol for extension-to-desktop job handoff.
- Improve security and acceptance criteria.
- Propose the initial CI matrix (Linux analysis/build, Windows packaging, browser smoke tests).

After the owner decides the software license and contribution policy, implementation issues can be opened for the first vertical slice.

## Pull request checklist

- [ ] Linked issue and succinct problem statement.
- [ ] Single focused change; unrelated user changes preserved.
- [ ] Clear distinction between implemented, tested and proposed behavior.
- [ ] Tests/documentation updated, commands and results reported.
- [ ] New dependencies justified with license, security and maintenance notes.
- [ ] No secrets, session data, unapproved binaries, media archives or generated downloads.
- [ ] No DRM, paywall, access-control or rights circumvention.
- [ ] License and provenance information supplied for any imported upstream code.

## Engineering conventions (provisional)

- Keep browser, desktop, web and engine modules independent with versioned API contracts.
- Prefer typed interfaces, explicit errors, dependency injection and deterministic tests.
- Handle cancellation, retry, resume and crash recovery as first-class state transitions.
- Include an end-user recovery message with each operational failure.
- Do not add a dependency solely to avoid writing a few lines of simple code; conversely, do not rewrite mature infrastructure.
- Use existing formatting and testing scripts once a chosen base repository is imported.

## Licensing and ownership

**Project license and contribution terms are not yet selected.** Do not assume public visibility means permissive licensing. Contributors retain rights unless an applicable license/contribution agreement says otherwise. Open issues and documentation suggestions are welcome; contact the maintainer before submitting substantial application code or copying third-party components.

## Vulnerability reporting

Do not publish exploit details, credentials or sensitive reproduction data in public issues. Use GitHub's private vulnerability reporting/security advisory mechanism if enabled, or contact the repository owner privately first.

## Proposed PR template

See [.github/PULL_REQUEST_TEMPLATE.md](.github/PULL_REQUEST_TEMPLATE.md). Be factual: never mark a feature ready because it works only in an upstream repository.
