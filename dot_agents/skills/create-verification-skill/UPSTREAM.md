# Upstream

Adapted from [pstack/create-verification-skill](https://github.com/cursor/plugins/tree/ae5650febf4320793844c12c4adaa937f417f8da/pstack/skills/create-verification-skill) at commit `ae5650febf4320793844c12c4adaa937f417f8da`. Copyright 2026 Lauren Tan; see [LICENSE](LICENSE).

Local adaptations: shared project paths and Claude discovery links, preserving existing layouts and checking symlink destinations; manual invocation for Claude Code and Codex; repository model ownership; startup failures reported unless fixes are authorized; maintenance command names for both tools.

Invoke in Claude Code with `/create-verification-skill` or in Codex with `$create-verification-skill`. These reusable skills live globally; generated verification skills belong in the target repository.
