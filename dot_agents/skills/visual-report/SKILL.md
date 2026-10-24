---
name: visual-report
description: Deliver a report as an interactive, self-contained HTML page rendered in T3 Code. Use when reporting back research findings, an explanation, a comparison, or an implementation summary. Quick answers and status updates stay as text.
---

# Visual report

A **report** is one Svelte project under `~/.local/share/visual-report/reports/`. Its export is one self-contained HTML file that works offline. The project keeps the editable source, so you or a later agent can revise the report.

## Steps

### 1. Create the project

```sh
bun ~/.agents/skills/visual-report/scripts/new-report.ts <kebab-slug> "<Title>"
```

The last line of output is the report directory. To revise a report, edit its existing directory instead.

### 2. Write the report

The report is `src/lib/report/Report.svelte`. Its title is in `src/lib/report/meta.ts`. The shell around it gives the page its `<h1>`, the skip link, the `<main>` landmark, and the theme switch. Dark is the default theme.

Design each report for its content. Choose the structure, the visuals, and the interactions that make this subject clear. Add interaction where the reader explores: filters, comparisons, toggles between views, step-throughs, or simulations. A static section is correct for a fact the reader only reads.

- Build from the shadcn-svelte components in `src/lib/components/ui/`. Add others with `bunx shadcn-svelte@latest add <name>`. Write custom SVG or HTML for visuals that no component gives.
- Use the theme color tokens (`bg-card`, `text-muted-foreground`, `fill-chart-1`). They keep contrast at WCAG 2.2 AA in both themes.
- Make each section work from 320 CSS pixels wide up to desktop width.
- Give every control a visible label and a keyboard path. Give every chart a text equivalent, such as a table or a summary sentence.
- Import images and data files, so the export inlines them. Each kilobyte of the export is a cost when you render it, so add a dependency only when the report uses it.

Write `tests/report.spec.ts` with one test per interaction the report offers. Each test proves the interaction through the page, as the reader uses it.

### 3. Edit the prose

Apply every rule in [`unslop`](../unslop/SKILL.md) to all report text. Technical text (procedures, system behavior, specifications, and failure analysis) also follows ASD-STE100 Simplified Technical English. Read [STE100.md](STE100.md) for those rules.

### 4. Preview in T3 Code

Run `bun run export`, then `bun run serve` in the background. Open the report with T3 Code's preview tools at `{kind: "environment-port", port: 4173}`. Inspect it with `preview_snapshot` (with `includeImage`) in these states:

- Desktop width, dark theme and light theme.
- The `iphone-se` preset.
- Each interaction, operated by keyboard.

Fix each defect you see, then export again. The preview is done when every state reads clearly and nothing overlaps, clips, or scrolls sideways. Before you stop the server, get the render height at the reply width: resize to `freeform` 728 × 800, then evaluate `document.documentElement.scrollHeight`.

### 5. Commit

Commit all changes in the report directory. The pre-commit hook runs the gate: formatting, ESLint with `@shadcn/lint`, type checks, the export, and the Playwright tests (offline load, themes, keyboard, axe WCAG 2.2 AA, and reflow). Fix each failure and commit again. The step is done when the commit lands. A commit made with `--no-verify` skips the gate and does not count.

### 6. Render and reply

Read `<report dir>/<report dir name>.html` and pass its full contents to `html_render`, with the height from step 4. In your reply, give the absolute path of that HTML file as a link. Add only what the page does not say.
