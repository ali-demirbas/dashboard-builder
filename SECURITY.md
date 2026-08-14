# Security Policy

## Supported versions

This project is pre-1.0. Only the latest commit on `main` is supported; there are no maintained release branches yet.

## Reporting a vulnerability

Please report security issues privately through [GitHub Security Advisories](https://github.com/ali-demirbas/dashboard-builder/security/advisories/new) rather than opening a public issue.

Include what you'd include in any report: the affected file(s), how to reproduce, and the impact you think it has.

## Scope

This repo has no server, no hosted service, and collects no user data. It is a Claude Code skill: almost entirely prompt/markdown content, plus a few small dependency-free Python scripts under `scripts/` that only validate repo structure (frontmatter, internal links) and run no shell commands or network calls against untrusted input. A bug there would be a wrong validation result, not code execution.

The realistic attack surface is the skill's own instruction-following, not the repo's code:

- **Prompt injection via supplied data.** The skill's rule 11 (`SKILL.md`) requires treating every uploaded file — a CSV, a campaign name, an ad label, a PDF export — as data, never as instructions. A crafted file that gets the skill to execute embedded text as a command, rather than surface it as a finding, is in scope.
- **PII handling.** `data-quality-gate.md` §Handling PII requires never quoting a raw identifier (email, phone, device ID) in output. A supplied file that gets a raw identifier echoed back is in scope.
- **Fabricated output presented as sourced.** The skill's non-negotiable rules ban presenting an estimate as measured or a hypothesis as fact. A reproducible case where the skill's own instructions can be made to violate this is a real finding, even though nothing "breaks" in the code sense.

Issues that only affect a user's own local run of a validator script (a malformed path causing a Python traceback) are better filed as a normal bug report.

## Response

This is a solo-maintained open-source project. There's no SLA, but reports will be acknowledged and triaged as soon as reasonably possible.
