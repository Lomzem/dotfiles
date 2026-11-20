# Model roles

- The latest Claude Opus is the default parent. It makes every decision and writes the final result.
- The latest GPT Sol does legwork: scouting, test and build matrices, reviews, and drafts of specs or tickets. Opus hands token-heavy legwork to Sol through `delegate_task` and keeps quick lookups inline. Always run Sol with `reasoningEffort: xhigh`.
- Sol briefs are closed: one deliverable, the constraints, the decisions already made, and a checkable completion criterion. Sol returns evidence (`file:line` references, quotes, command output) and options. If the work raises an open decision, Sol stops and returns the options.
- Opus verifies decisive claims before acting on them.
- Sol's edits land only when a tool generated them or the user approved Sol code for that task.
- When Sol is the parent, it does legwork itself and sends decisions and final code to Opus through `delegate_task`.

# Pull requests

- Council members: Claude Opus at `high`, GPT Sol at `xhigh`, and Gemini Neon at `high` once `orchestrator_capabilities` lists it. Two members make a full council.
- When a `full-send` or `full-stop` request also says "council", the review step runs `council` in place of `sol-loop`.
- In agent-authored GitHub comments, name me by my GitHub login.

# Replies

- Write replies to the user in plain technical English modeled on ASD-STE100: one topic per sentence, active voice, keep articles and short words, one name for one thing, and put a condition before its instruction. This applies to chat replies, not to files, code, or commit messages.

# Context

- **Principles:** Before substantive implementation, debugging, refactoring, or verification work, read `~/.agents/principles/README.md` and follow the references whose triggers apply. Reassess when the task enters a new phase.
- At major task boundaries, update the existing task record with decisions, changed files, verification results, and remaining work needed to resume after a handoff or compaction.

# Secrets

- Inspect environment variable names and credential presence without printing values. Read only the configuration fields needed for the task; keep secrets out of tool output, logs, diffs, screenshots, and chat.
- Supply credentials through the available secret-input tool or an existing password manager. Never put a secret in chat, a command argument, or a tracked file.
- If a credential was exposed, stop propagating it and have it revoked or rotated before cleaning up history.
