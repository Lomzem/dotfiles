---
name: no-comments
description: Review a scoped diff for unnecessary comments, fix the causes they explain, and preserve real constraints. Use only on an explicit no-comments request.
disable-model-invocation: true
---

# No comments

Run this workflow only when the user explicitly invokes `no-comments`.

## Scope

Use the files or diff the user names. Otherwise review the changed lines since the merge base with the branch's base, using `main` if no base is known. Include staged and unstaged changes. Read surrounding code for evidence and keep all edits within the agreed scope.

## Review

Start a fresh, read-only comment review. In T3 Code, use the user's Sol routing through `delegate_task` with `reasoningEffort: xhigh`. Give the reviewer the fixed scope, the rules below, and a request for file and line references, proposed deletions, refactor targets, and evidence for keeps. If delegation is unavailable, apply the same rules yourself and report that you reviewed inline.

- Delete narration that repeats the code, decorative headings, dead commented-out code, and stale rationale.
- Keep legal notices, public API contracts, formatter directives, and concise explanations of proven external constraints that code cannot express. Keep issue or RFC links that supply evidence for such constraints.
- Look up each lint or type suppression in scope. A suppression for a style-only or faulty rule can stay when the reason still applies. Flag suppressions that mask correctness or safety checks for a code fix.
- Trace the affected symbol or call before judging warnings such as `IMPORTANT` or `do not remove`. When a comment explains surprising behavior in code you can change, name the smallest refactor that would make the behavior clear. Keep evidence of genuine constraints until the code or another check can enforce them.

## Apply

1. Check the review against the scoped diff and the rules above. Reject unsupported findings and scope escapes. If a delegated report fails these checks, rerun the review once with the specific failure. If the second report fails, leave its findings open and report why.
2. Apply accepted deletions directly. For workarounds and correctness suppressions, trace the cause and fix it before removing the comment or suppression. If the fix changes the design, sketch the smallest coherent change first. Use the relevant references in [Engineering principles](../../principles/README.md). Leave out-of-scope fixes open.
3. For a genuine constraint that needs new enforcement, propose the cheapest suitable type check, runtime check, test, or lint rule. Add it only with the caller's approval, including prior approval on unattended runs. Remove the comment after verifying the enforcement. If the constraint stays open, keep the comment and report it.
4. Recheck the scoped diff for protected comments and unrelated edits. Run checks relevant to any code fix. Report the comment deletion count, review reruns, fixes, enforcement added or proposed, and open work.
