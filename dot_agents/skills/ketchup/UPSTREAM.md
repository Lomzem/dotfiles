# Upstream

Adapted from [cursor/plugins — pstack/ketchup](https://github.com/cursor/plugins/blob/6ea74587e384e1a8035c09ae33a46fe3f881eb9b/pstack/skills/ketchup/SKILL.md), revision `6ea74587e384e1a8035c09ae33a46fe3f881eb9b`, retrieved 2026-11-03. The upstream MIT notice is preserved in [LICENSE](LICENSE).

Local changes: Shortened the human-facing description; made the catch-up window invocation-neutral; inlined the plain-language voice; replaced the optional /visualize skill with available plotting tools; added a terminal media fallback. Retained Claude Code manual invocation and added Codex `policy.allow_implicit_invocation: false`. Shared source: `dot_agents/skills/ketchup`; installation: `~/.agents/skills/ketchup`.

Invoke with `/ketchup` in Claude Code, or `$ketchup` / the skills picker in Codex. No Cursor plugin or model configuration is required.
