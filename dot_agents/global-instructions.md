# Model ownership

- **GPT-6.1-Sol** is the default for general work, including personal tooling and configuration.
- **Opus 5.5** owns production application and library code: architecture, API design, and implementation.
- **UI implementation belongs exclusively to Opus 5.5**, including UI in personal tools and prototypes. Sol must delegate all UI implementation and changes to Opus; Sol may review UI code but must not edit it.

# Delegation

Use **GPT-6.1-Sol** for delegated reviews, codebase scouting, research, and other investigative work.

Work inline when the current model owns the task. Delegate when another model is required, or when an independent task benefits from parallel work or a separate context. Keep routine lookups and small tasks inline.

Subagents complete their assigned work directly. They may delegate further only when the parent agent explicitly authorizes it in their task brief.
