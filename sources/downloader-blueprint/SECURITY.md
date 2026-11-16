# Security policy

This repository is currently a **planning/documentation project**, with no published application build. Security-sensitive issues may still arise in future implementation work or dependencies.

## Reporting a vulnerability

Do **not** publish proof-of-concept exploits, private tokens, user files or personal information in a public issue.

Prefer GitHub private vulnerability reporting or a GitHub Security Advisory if the owner enables it. Otherwise, contact the repository owner privately through their GitHub profile and request a secure reporting channel. The project has no designated security email or response-time SLA yet.

## Engineering policy

All contributors should read [legal and security guardrails](docs/LEGAL_SECURITY.md). In particular, local desktop bridges, native messaging, untrusted URLs, redirect handling, FFmpeg inputs, browser permissions and supply-chain dependencies require careful review.

Only report tested security behavior; no features have been security-audited in this repository at its documentation bootstrap.
