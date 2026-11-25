# Upstream

Adapted from [pstack/no-comments](https://github.com/cursor/plugins/blob/2f87c854fe3e2fcda44ca86b46ede35aad3c46b7/pstack/skills/no-comments/SKILL.md) and its [comment-sicko reviewer](https://github.com/cursor/plugins/blob/2f87c854fe3e2fcda44ca86b46ede35aad3c46b7/pstack/agents/comment-sicko.md) at commit `2f87c854fe3e2fcda44ca86b46ede35aad3c46b7`. The upstream MIT notice is in [LICENSE](LICENSE).

The shared skill uses a read-only Sol review in T3 Code. The caller validates findings and makes edits. The skill uses local engineering principles in place of Cursor commands and keeps genuine constraint comments until verified enforcement replaces them.

Invoke with `/no-comments` in Claude Code, `$no-comments` in Codex, or `/no-comments` in Antigravity. All three load the shared user skill from `~/.agents/skills/no-comments`.
