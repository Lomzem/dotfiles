# Model ownership

- **GPT-6.1-Sol** is the default for general work, including personal tooling and configuration.
- **Opus 5.5** owns production application and library architecture, API design, and implementation, plus all UI implementation, including personal tools and prototypes. Sol may review UI code; UI changes go to Opus.

# Delegation

- Use **GPT-6.1-Sol** for reviews and substantial fact-finding: documentation research, codebase scouting, dependency and tooling investigation, and log or test analysis. Opus delegates these investigations even when they arise during implementation. Keep quick lookups and short checks inline.
- Sol may turn approved decisions into specs and tickets. Opus resolves architecture and API decisions.
- Give each delegate one coherent deliverable, the relevant constraints and sources, and a checkable completion criterion. Return findings with evidence, changed files, checks, and unresolved questions as applicable. The parent verifies decisive claims and integrates the result.
- Work inline when the current model owns the task. Delegate independent work when it benefits from a separate context or review.
- Subagents complete their assigned work directly. Further delegation requires the parent's explicit authorization in the task brief.

# Context

- Start with the current task and relevant files or document sections; expand when a dependency or unanswered question requires it.
- At major task boundaries, update the existing task record with decisions, changed files, verification results, and remaining work needed to resume after a handoff or compaction.
