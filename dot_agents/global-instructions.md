# Model ownership

- **GPT-6.1-Sol** is the default for general work, including personal tooling and configuration.
- **Opus 5.5** owns production application and library architecture, API design, and implementation, plus all UI implementation, including personal tools and prototypes. Sol may review UI code; UI changes go to Opus.

# Delegation

- Use **GPT-6.1-Sol** for reviews and substantial fact-finding: documentation research, codebase scouting, dependency and tooling investigation, and log or test analysis. Opus delegates these investigations even when they arise during implementation. Keep quick lookups and short checks inline.
- Sol may turn approved decisions into specs and tickets. Opus resolves architecture and API decisions.
- Give each delegate one coherent deliverable, the relevant constraints and sources, and a checkable completion criterion. Return findings with evidence, changed files, checks, and unresolved questions as applicable. The parent verifies decisive claims and integrates the result.
- Work inline when the current model owns the task. Delegate independent work when it benefits from a separate context or review.
- Subagents complete their assigned work directly. Further delegation requires the parent's explicit authorization in the task brief.

# Pull requests

- **GPT-6.1-Sol** owns PR follow-through: CI triage, review coordination, and merging when shipping is part of the task and the repository's merge requirements are satisfied. Production and UI fixes remain with Opus.
- Before creating, taking over, or shipping a PR, read `~/.agents/PR-WORKFLOW.md`.

# Context

- Start with the current task and relevant files or document sections; expand when a dependency or unanswered question requires it.
- At major task boundaries, update the existing task record with decisions, changed files, verification results, and remaining work needed to resume after a handoff or compaction.

# Secrets

- Inspect environment variable names and credential presence without printing values. Read only the configuration fields needed for the task; keep secrets out of tool output, logs, diffs, screenshots, and chat.
- Supply credentials through the available secret-input tool or an existing password manager. Never ask for a secret in chat or put one in a command argument, tracked file, or example. Use clearly fake placeholders in examples.
- Before committing or pushing, run the repository's secret checks with full redaction. Resolve findings without bypassing hooks or adding broad exclusions. Report only the path, line, and rule. If a credential was exposed, stop propagating it and have it revoked or rotated before cleaning up history.
