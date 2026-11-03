# Sources and maintenance

Adapted on 2026-11-02 from the 22 corresponding `principle-<name>/SKILL.md` files in [cursor/plugins pstack](https://github.com/cursor/plugins/tree/main/pstack/skills), fetched from `main`. This is a local adaptation, not an automatically synchronized upstream installation. The original material is copyright 2026 Lauren Tan, under the [MIT license](LICENSE).

The filenames map directly to upstream names. For example, `build-the-lever.md` comes from `pstack/skills/principle-build-the-lever/SKILL.md`. `exhaust-the-design-space` and `never-block-on-the-human` are outside this selection.

Local adaptations:

- Plain references and one routing index replace per-principle skills and invocation metadata. The manual `principles` skill reads this same index.
- Internal cross-references use local Markdown paths. Unbundled pstack workflow dependencies use existing project tooling and evidence artifacts.
- Foundational scaffolding and subtraction stay within the actual task. First-principles redesign is a design lens for choosing a scoped implementation.
- Reader load judges boundaries by the complexity they hide. A single caller is not sufficient reason to inline a boundary.
- Boundary validation preserves checks for invariants not established by types; semantic branding targets plausible value mixups.
- Outcome-oriented work preserves live installations and verifies delivery boundaries. Sequencing establishes a baseline without mandating a rebase or separately landing a failing test.
- Root-cause work preserves legitimate explanatory comments. Experience prototypes answer an actual uncertainty.
- Context management follows the user's existing model ownership and delegation rules.

Compare future upstream changes with these adaptations before merging them. Matt Pocock skills remain independent and untouched by this layer.
