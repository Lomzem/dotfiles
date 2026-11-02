# pstack verification skills for Claude Code and Codex

Researched 2026-11-02. Scope: selectively reuse verification workflows with shared user skills in `~/.agents/skills`, exposed through `~/.claude/skills` and `~/.codex/skills`; no Cursor, Grok, or full pstack installation.

## Recommendation

Cherry-pick **create-verification-skill** and its feature-map examples first. Add **maintain-verification-skill** if maintaining a project feature map will be useful. Neither skill requires Cursor, Grok, a specific model, pstack model configuration, poteto-mode, MCP servers, or the plugin machinery. They are Markdown instructions; their substantive dependencies are access to the target repository, a runnable application, and tools capable of driving its real surface. Maintenance additionally requires parallel read-only source agents and a live verification pass. These conclusions follow from the complete [generator][create] and [maintenance][maintain] instructions, rather than the full-stack README's model-routing defaults.

Adapt their output paths and maintenance shipping policy before installation. Keep the generator's requirement to execute the generated instructions, the feature map, isolation, doctor checks, observable evidence, and cleanup. These make the pair more useful than a generic “run tests before finishing” rule. No skills were installed or edited during this investigation.

## Source snapshot and inventory

Primary source: `cursor/plugins`, checked out read-only in a temporary directory at **`ae5650febf4320793844c12c4adaa937f417f8da`**, repository commit date **2026-10-31T17:10:38-07:00**. This is the inspected repository snapshot, not a claim that each skill changed on that date. All links below pin that snapshot.

Minimum useful copy:

| Upstream file | Purpose |
| --- | --- |
| `pstack/skills/create-verification-skill/SKILL.md` | Repository investigation and verified skill generation |
| `pstack/skills/create-verification-skill/references/feature-map-example/README.md` | Index, preconditions, proof conventions, feature contract |
| `…/feature-map-example/create-note.md` | Worked mutation, cancellation, persistence and CLI example |
| `…/feature-map-example/search.md` | Worked multi-entry-point search example |
| `pstack/skills/maintain-verification-skill/SKILL.md` | Optional upkeep workflow; no companion files |
| `pstack/LICENSE` | MIT copyright and permission notice |

The example commands (`control-notes`, `notes`, port 4173) describe a fictional worked example, **not software to install**. The generator must replace them with commands and selectors discovered in the target repository. Preserve the relative reference-directory layout. [Feature-map examples][examples], [generator][create].

Licensing: pstack has an [MIT license][license], copyright 2026 Lauren Tan. Copies or substantial portions must retain its copyright and permission notice. Retain the complete license beside the vendored material or in an explicitly associated attribution file; record the upstream revision and local adaptations so future updates can be reviewed.

## Actual dependencies

| Component | Required by these workflows? | Reason |
| --- | --- | --- |
| Cursor paths | Adaptation required | Generator writes `.cursor/skills/verify-<app>/`; maintainer searches there “usually.” |
| Cursor/Grok/model rule | No | Neither selected skill names a model or reads a model rule. |
| Full pstack/setup-pstack | No | Setup only offers verification generation as an optional later step. |
| Browser/CDP, Playwright, tmux/PTY, HTTP tooling | Depends on project | Prefer existing harnesses; choose tools for the actual app surface. No one harness is universally required. |
| Subagent support | Maintenance: yes, as written | One concurrent read-only source reader per feature; coordinator alone drives the app. Generator does not demand delegation. |
| Git hosting/PR tool | Changed maintenance run: yes, as written | Its `changed` outcome explicitly requires one PR; `clean` and `blocked` require none. |
| Scheduling/automation | No | Generator suggests a cadence only if asked; maintenance is a manual workflow. |
| Other verification skill | Maintenance: yes | Requires an existing launch/drive skill with feature map; stops if absent. |

Sources: [create][create], [maintain][maintain], [setup-pstack][setup]. A project can still be blocked by missing authentication, seed data, supported OS, external service access, or the inability to isolate instances; the instructions require reporting these limits, not claiming success.

## Adaptations for the shared skill directory

1. **Separate reusable generators from project outputs.** Store the reusable pair under the established `dot_agents/skills` source / `~/.agents/skills` installation. Generate each project's `verify-<app>` in that project's `.agents/skills`, with a project-local `.claude/skills` link if needed by that project's Claude setup. The existing *global* symlinks do not expose arbitrary project-local directories. Choose and verify the project discovery arrangement before generating output; do not put every project's private launch instructions into the global skills directory.
2. **Replace all `.cursor/skills` output/discovery paths**, including feature-map creation paths. Update maintenance's target search to the chosen shared project location and existing project conventions. Keep names/frontmatter intact unless deliberately renaming both folders and invocation references.
3. **Resolve invocation metadata per harness.** Retain Claude Code's `disable-model-invocation: true`. For Codex, add `agents/openai.yaml` with `policy.allow_implicit_invocation: false`; its official [skills documentation](https://learn.chatgpt.com/docs/build-skills) specifies `.agents/skills`, symlink support, and explicit `$skill` / `/skills` invocation. Keep standalone names rather than plugin-prefixed `/pstack:…` commands.
4. **Use available tools and existing model ownership.** Maintenance specifies agent responsibilities, not literal Cursor tool fields or model IDs. Translate to Claude/Codex agent mechanisms and follow this repository's Sol fact-finding / Opus implementation ownership. If parallel agents are unavailable, explicitly adapt to sequential source reading; that is a local change to the prescribed workflow.
5. **Change maintenance's shipping contract if PRs are unwanted.** Make `changed` mean locally reviewed, proven corrections, with PR creation only when requested. Otherwise the untouched workflow directs the agent to create a PR. When shipping is authorized, follow `~/.agents/PR-WORKFLOW.md` first.

The upstream [Claude adapter][adapter] confirms path and tool mapping, but targets a complete plugin. Its generated [Claude skill][generated] merely inserts an adapter-reading paragraph; it retains `.cursor` paths in the body. Copying that version alone adds a missing relative adapter dependency. Prefer the raw pair with small explicit local adaptations over importing the whole adapter. The [generation script][generation] documents exactly how these wrappers are produced. No Codex adapter appears in the inspected `harness/pstack` tree.

## Side effects and boundaries

Generation writes skill files, may produce executable helpers, launches and drives the app, mutates fixture data, captures evidence, and tears down its instances. It also says to fix a broken startup first **or report it precisely**, so narrow this to reporting unless product fixes are authorized. The examples are not a sandbox: the generated skill must establish disposable data/profiles, owned ports and processes, safe credentials, and an artifact location before executing real user paths. [Generator][create], [examples][examples].

Preserve upstream's explicit safeguards: no double-driving shared instances; never kill by process name; verify dry-run effects instead of trusting the flag; retain proof through teardown; clean failed iterations too. External messages, purchases, production data writes or network side effects remain real when driving the real app. This user's secret-handling rules apply to captured logs, screenshots, response bodies and helper arguments as well as chat output.

Maintenance confines edits to the verification directory and reports product regressions separately. Its source agents must never drive or edit; the coordinator serializes live interactions, rechecks health after surprises, and exercises every feature. A clean source review alone cannot produce `clean`. Feature-level live coverage also should not be overstated as exhaustive coverage of every entry point or possible input. [Maintenance][maintain].

## Relevant siblings: useful ideas, separate scope

- [Prove It Works][prove] reinforces checking the real artifact and keeping repeatable proof. Optional; the selected generator already states the central evidence contract.
- [Build the Lever][lever] motivates a reusable control CLI. Optional; its broader codemod/delegation rules are unnecessary baggage for this cherry-pick.
- [Create Formal Verification Skill][formal] and [Maintain Formal Verification Skill][formal-maintain] address code-linked invariants, models, bounds and drift, rather than app journeys. Skip initially. The formal generator explicitly requires `/statechart` when it selects TLA+, introducing a real conditional sibling dependency absent from ordinary verification generation.
- The [verification guide][guide] explains the pair but is supporting reading, not a runtime requirement. Full setup and model routing solve a larger problem than this request.

## Verification and remaining decisions

Read both complete skills, all three feature-map references, MIT license, README installation sections, setup's optional offers, both formal-verification siblings, the two principles, Claude adapter, generated Claude generator and harness generation logic. No existing research-note directory convention was found, so this note uses `docs/research/`. No application was launched and no installation or skill behavior was tested.

Before implementation, detect the existing project skill layout and choose local-only versus PR-based maintenance outcomes. A suitable shared layout is `.agents/skills/verify-X` plus a relative `.claude/skills/verify-X` symlink, preserving existing arrangements. These do not block adopting the underlying workflow.

[create]: https://github.com/cursor/plugins/blob/ae5650febf4320793844c12c4adaa937f417f8da/pstack/skills/create-verification-skill/SKILL.md
[maintain]: https://github.com/cursor/plugins/blob/ae5650febf4320793844c12c4adaa937f417f8da/pstack/skills/maintain-verification-skill/SKILL.md
[examples]: https://github.com/cursor/plugins/tree/ae5650febf4320793844c12c4adaa937f417f8da/pstack/skills/create-verification-skill/references/feature-map-example
[license]: https://github.com/cursor/plugins/blob/ae5650febf4320793844c12c4adaa937f417f8da/pstack/LICENSE
[setup]: https://github.com/cursor/plugins/blob/ae5650febf4320793844c12c4adaa937f417f8da/pstack/skills/setup-pstack/SKILL.md
[adapter]: https://github.com/cursor/plugins/blob/ae5650febf4320793844c12c4adaa937f417f8da/pstack/docs/harness/claude-code.md
[generated]: https://github.com/cursor/plugins/blob/ae5650febf4320793844c12c4adaa937f417f8da/harness/pstack/claude-code/skills/create-verification-skill/SKILL.md
[generation]: https://github.com/cursor/plugins/blob/ae5650febf4320793844c12c4adaa937f417f8da/scripts/generate-pstack-harness-trees.mjs
[prove]: https://github.com/cursor/plugins/blob/ae5650febf4320793844c12c4adaa937f417f8da/pstack/skills/principle-prove-it-works/SKILL.md
[lever]: https://github.com/cursor/plugins/blob/ae5650febf4320793844c12c4adaa937f417f8da/pstack/skills/principle-build-the-lever/SKILL.md
[formal]: https://github.com/cursor/plugins/blob/ae5650febf4320793844c12c4adaa937f417f8da/pstack/skills/create-formal-verification-skill/SKILL.md
[formal-maintain]: https://github.com/cursor/plugins/blob/ae5650febf4320793844c12c4adaa937f417f8da/pstack/skills/maintain-formal-verification-skill/SKILL.md
[guide]: https://github.com/cursor/plugins/blob/ae5650febf4320793844c12c4adaa937f417f8da/pstack/docs/guide/06-verify-and-ship.md

## Installation follow-up — 2026-11-02

Installed the adapted pair from `dot_agents/skills/{create-verification-skill,maintain-verification-skill}` to `~/.agents/skills` with a scoped `chezmoi apply`. Included all three creator references, per-skill MIT licenses, pinned provenance, and Codex manual-invocation metadata. Generated project skills use `.agents/skills`, with relative Claude discovery links, existing-layout preservation and checks against writes escaping through symlinks. Maintenance leaves proven corrections locally unless PR shipping is requested, uses Sol source readers within available agent limits, and documents sequential reading when delegation is unavailable.

Verification: parsed YAML frontmatter and invocation policy; checked local Markdown links, license bytes and absence of Cursor paths in skill instructions; confirmed the documented relative link in a disposable directory; compared all 11 installed files byte-for-byte with source; verified both Claude/Codex discovery paths resolve to the installed files; scoped post-apply `chezmoi diff` and `git diff --check` were clean. The generic skill validator rejects the Claude-specific `disable-model-invocation` extension, so metadata was checked directly rather than removing the supported field. No application-specific skill has been generated or exercised yet. No commit or PR was created. Next use: invoke the creator in the target application repository.
