---
name: research
description: Investigate a question against primary sources and return cited findings inline. Use when the user wants a topic researched, docs or API facts verified, or reading legwork delegated to a background agent.
---

Spin up a **background agent** to do the research, so you keep working while it reads. Start it with a fresh context window.

Its job:

1. Investigate the question against **primary sources** (official docs, source code, specs, first-party APIs), not a secondary write-up of them. Follow every claim back to the source that owns it.
2. Return the findings directly with a citation for every claim, and present them inline in chat.
3. When the prompt explicitly asks for a file, write a single cited Markdown file where the repo keeps such notes (or pick a sensible path and report where).
