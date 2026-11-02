# Upstream

Adapted from [pstack/maintain-verification-skill](https://github.com/cursor/plugins/tree/ae5650febf4320793844c12c4adaa937f417f8da/pstack/skills/maintain-verification-skill) at commit `ae5650febf4320793844c12c4adaa937f417f8da`. Copyright 2026 Lauren Tan; see [LICENSE](LICENSE).

Local adaptations: shared project discovery with symlink deduplication; manual invocation for Claude Code and Codex; source readers follow model ownership and agent limits, with a documented sequential fallback; corrections remain local unless PR shipping is requested.

Invoke in Claude Code with `/maintain-verification-skill` or in Codex with `$maintain-verification-skill`. These reusable skills live globally; generated verification skills belong in the target repository.
