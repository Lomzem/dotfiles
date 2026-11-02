# Boundary and proof guide

## Boundary and cost

Prove caller-visible behavior through its production owner with fixed external
I/O fixtures and independent expected values. Prefer focused integration tests
and independent unit contracts over mocked internal decisions or whole-product
boots. Name the credible regression and what the test cannot prove.

Work in vertical slices: failing behavior, coherent repair, passing proof.
Regressions must fail on the original defect rather than fixture setup. Report
unavailable baseline proof. Refactor under green tests and preserve distinct
contracts when consolidating coverage.

Measure changed test files with the repository’s focused runner; report wall
time and material cost changes. Apply its time and coverage budgets. A slow test
needs a contract that a cheaper boundary cannot prove. Keep distinct end-to-end
and live contracts in the repository’s designated tier.

Use controlled clocks, isolated state, and managed ports. Await observable
completion rather than sleeps or action returns. Reuse appropriate suite-level
fixtures, release owned resources, and repair shared-state leaks at their owner.
Keep credentials and real user data out of fixtures and captures.

## Proof policy

Read root and scoped agent instructions, test scripts, and CI routing before
choosing commands. Use the target repository’s runner and required gates.

- Prove the changed contract through focused owner and sibling tests; run relevant
  type, lint, format, and build checks when the change requires them.
- For removed source inspections, exercise the owning executable or dry-run path.
- Use CI for broad proof where the repository workflow supports it. Complete
  required local gates before handoff; report unavailable checks and coverage gaps.
- Preserve the checkout while a test run is active. Isolate concurrent runs’
  state and caches, or run serially.
- Reproduce failures at the original boundary and order before isolating them.
  Classify product defects, fixture failures, and environment failures with
  evidence. Repeat checks when inputs change, a failure needs diagnosis, or a
  named risk remains.
- Documentation-only changes need relevant link/format checks and
  `git diff --check`; runtime tests add no proof for prose alone.

Validation does not grant commit, push, merge, or publication authority. Follow
the task’s authorization and repository workflow for those actions.
