---
name: sol
description: Run this thread and all delegated work on GPT Sol only.
disable-model-invocation: true
---

This thread is in Sol-only mode. Sol-only mode replaces the Opus roles in the global instructions.

- GPT Sol does all the work and makes every judgment, including recommendations and final answers.
- Delegate only to GPT Sol. Start each brief with: "Sol-only mode: you own all judgments and results. Delegate only to GPT Sol." A child does not see this skill.
- If a judgment needs Opus, ask the user first.
