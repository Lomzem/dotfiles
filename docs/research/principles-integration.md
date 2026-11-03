# Personal principles integration

Implemented and applied 2026-11-02. User approved the combined 22-principle set and an automatically reached router plus a manual command. Full pstack orchestration and its two remaining principles are outside scope. Matt Pocock skills are untouched. Later instruction: use Sol for this work; no further Opus work.

## Decisions and changed files

- `dot_agents/principles/README.md` routes concrete task conditions to 22 plain references. Agents read matching leaves in full and reassess at phase boundaries. Existing authorization, model ownership, repository rules, and specific task instructions retain precedence.
- `dot_agents/principles/*.md` contains locally adapted pstack principles. `SOURCES.md` records upstream provenance and adaptations; `LICENSE` retains the MIT notice. These are independently maintained references, not upstream Matt skill patches.
- One pointer in `dot_agents/global-instructions.md` enables automatic routing for substantive implementation, debugging, refactoring, and verification.
- `dot_agents/skills/principles/SKILL.md` forces a fresh router pass, including inspection of work already done. Claude uses `/principles`; Codex uses `$principles`. Claude's manual flag and Codex's `agents/openai.yaml` policy keep this manual entry point separate from the automatic pointer.
- `dot_agents/principles/check.py` is a retained structural verification tool, runnable in source or after installation.

## Verification

- Compared affected source and live files using `chezmoi diff`; global instructions had no pre-existing live divergence. Applied only the reviewed global instructions and two new directories. Final affected-path diff is empty.
- `python3 ~/.agents/principles/check.py` passes: 22 references, router coverage, local links, shared pointer, and both manual policies.
- Disposable negative controls confirm the checker rejects a missing reference and an incorrect Codex manual policy.
- Both harness instruction symlinks and both skill-directory symlinks resolve to the intended shared installed files.
- Sol review found two rules lost with upstream frontmatter removal. Restored the migration rule and structural-lesson rule in their reference bodies, then reapplied and rechecked.
- A read-only Claude harness smoke check followed its loaded global pointer, read the index and six relevant references for interrupted migrations and performance claims, and produced the expected evidence-oriented plan. This completed before the user prohibited Opus; no further Opus work was started.
- `git diff --check` passes. Existing upstream skill files have no changes.

## Limits and remaining work

Instruction-driven routing is not a deterministic hook. The smoke check establishes one Claude execution, not universal compliance. The explicit slash-command menu was not exercised, and a separate fresh Codex behavior run was not performed; Codex paths and invocation policy were verified structurally. New sessions should discover the new manual command.

## Shipping

User requested committing and pushing this integration on 2026-11-02, then settling the T3 conversation. Pre-shipping verification passed the principles checker, whitespace check, and fully redacted Gitleaks scans of the working tree and all local Git history. Repository pre-commit and pre-push hooks remain enabled. Git history records the resulting commit; remote push status is checked after shipping.
