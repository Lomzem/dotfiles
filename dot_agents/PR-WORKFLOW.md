# Pull request workflow

Use the repository's instructions to determine required checks, reviewers, merge method, and whether the task includes merging. GPT-6.1-Sol coordinates PR follow-through; route production application, library, and UI changes to Opus under the global ownership rules.

## Prepare

1. Identify the PR's current head SHA and the repository's deterministic checks from its scripts and CI configuration. Run the applicable local checks and fix failures before requesting external review.
2. Create or update the PR as a draft while preparing it. For repositories using CodeRabbit, keep its automatic reviews disabled or paused during implementation and CI repair. When configuring the repository, merge this setting into its existing `.coderabbit.yaml`:

   ```yaml
   reviews:
     auto_review:
       enabled: false
   ```

   Preserve other review settings. Check for label or description-keyword opt-ins that could still trigger reviews. Draft status alone does not stop an explicit manual review.
3. Wait for all applicable deterministic CI checks to pass on the current head. Missing, pending, or failing required checks leave the PR pending. Complete any required internal review before requesting CodeRabbit.

## Review and repair

1. Once the checks pass, request CodeRabbit with `@coderabbitai review` when the repository requires it. Request one review for the prepared revision; batch related fixes and pushes to conserve the allowance, especially on public repositories.
2. Read the completed review and assess every finding. Fix valid issues or reply with evidence explaining why a change is unnecessary. Blocking findings remain pending until resolved under the repository's review policy.
3. After changes, rerun the applicable checks, wait for CI on the new head, then request one incremental review. Use a full review only when recovery or coverage requires starting over.
4. Treat a rate-limited, skipped, failed, or incomplete CodeRabbit review as pending, never approval. Read the reported availability time, keep the PR unmerged, and retry when reviews are available. A passing or neutral CodeRabbit check alone does not establish that a review happened. Resolving threads or asking for approval does not substitute for review.

## Monitor and merge

- Use the platform's event-driven PR watcher for waits. Delegated workers return the PR URL, head SHA, check and review state, and remaining work to their parent; the parent owns monitoring.
- On new results, address the actionable findings, update the PR, and resume monitoring if requirements remain pending. Keep review requests tied to prepared revisions rather than repeated attempts while a review or rate limit is pending.
- When merging is included in the task, merge only after the current head has all required checks passing and the repository's required approvals. Where CodeRabbit approval is required, verify a completed review and its explicit approval covering that head; stale approval or a rate-limit status leaves the gate unmet.
- Use the repository's merge method, verify that the PR merged into the intended base branch, and report the PR URL and resulting commit. PR delivery is complete when the authorized merge is verified; review-only work is complete when findings and outstanding gates are reported.

## CodeRabbit reference

- [Automatic review controls](https://docs.coderabbit.ai/configuration/auto-review)
- [Review commands](https://docs.coderabbit.ai/guides/commands)
- [Status checks, including skipped and rate-limited reviews](https://docs.coderabbit.ai/pr-reviews/status-check)
- [Rate limits and reducing unnecessary reviews](https://docs.coderabbit.ai/management/rate-limits)
