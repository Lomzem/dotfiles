# Model roles

- Run research, scouting, and other token-heavy legwork on GPT Sol at `reasoningEffort: xhigh`. From another parent model, delegate it through `delegate_task` and keep quick lookups inline.
- Give a Sol delegate a closed brief: one deliverable, the constraints, the decisions already made, and a checkable completion criterion. It returns evidence (`file:line` references, quotes, command output) and options, and it stops at an open decision.
- A Sol delegate edits files only when a tool generated the edit or I approved Sol code for that task.

# Pull requests

- Council members: Claude Opus at `high`, GPT Sol at `xhigh`.
- When a `full-send` or `full-stop` request also says "council", the review step runs `council` in place of `sol-loop`.

# Replies

- Write replies to the user in plain technical English modeled on ASD-STE100 Simplified Technical English: one topic per sentence, active voice, keep articles and short words, one name for one thing, and put a condition before its instruction. This applies to chat replies, not to files, code, or commit messages.

# Context

- **Principles:** Before substantive implementation, debugging, refactoring, or verification work, read `~/.agents/principles/README.md` and follow the references whose triggers apply. Reassess when the task enters a new phase.
- At major task boundaries, update the existing task record with decisions, changed files, verification results, and remaining work needed to resume after a handoff or compaction.

# Secrets

- Inspect environment variable names and credential presence without printing values. Read only the configuration fields needed for the task; keep secrets out of tool output, logs, diffs, screenshots, and chat.
- Supply credentials through the available secret-input tool or an existing password manager. Never put a secret in chat, a command argument, or a tracked file.
- If a credential was exposed, stop propagating it and have it revoked or rotated before cleaning up history.
