---
name: ship-pr
description: "Ship work through a GitHub PR: open or update it, monitor CodeRabbit and CI, merge behind the approval gate, and finish any required release. Use when asked to ship, open, babysit, or merge a PR, or to release."
---

# Ship PR

Take the work from wherever it stands (local branch or existing PR) to the **endpoint** the user asked for, and stop there. "Open a PR" ends once the PR is open; "merge" ends at the verified merge. A full "ship" request includes any required release. Honor authorization already given in the thread; loading this skill grants none by itself.

Per global routing, application-code fixes and design decisions go to Opus.

## Workflow

1. **Orient.** Identify the repo, intended base, branch, and any existing PR. Leave unrelated work as it is, and integrate other branches or worktrees only when asked.
2. **Prepare.** Commit the relevant changes and run the repo's CI checks locally where feasible.
3. **Push.** Push, then update the matching open PR or open one against the base. Write the body with the `pr` skill when available.
4. **Review.** Judge each CodeRabbit or human finding on its merit: fix real defects and reply with reasoning to the rest. A fix is settled when the reviewer or CI confirms it on the new head.
5. **Merge** once the gate holds, using the repo's merge method pinned to the SHA you checked.
6. **Release** only as the repo's policy requires, reusing any version, tag, or release its automation already made, and confirm the post-merge and tag workflows succeed.

## The gate

Evaluate on the current head SHA, again after every push:

- CodeRabbit explicitly approved this exact SHA. Approval of an older head, no review, or a paused or rate-limited CodeRabbit fails.
- Required checks pass.
- No changes-requested review or open blocking finding remains.
- Branch protection and rulesets are satisfied.

Merge through the gate only, never by admin override, dismissed reviews, or bypassing auto-merge.

## Waiting

Use the host's PR-watch tools when present. In T3 Code only the parent thread watches: a delegated child waiting on an open PR returns a checkpoint, and the parent links and watches the PR, then ends its turn. The watch ends at merge, so post-merge and tag workflows use bounded CLI waits on exact run IDs, as does a plain terminal.

When a wait outlasts the run or a permission blocks progress, stop with a **checkpoint**: head SHA, gate status, pending run IDs, the blocker, and the next action. A checkpoint is pending, not done. On resume, recheck those runs and any existing release artifacts before acting.

## Report

PR link and endpoint reached, then as applicable the merge commit, release, post-merge CI results, and blockers.
