---
name: visual-report
description: Deliver a report as an interactive, self-contained HTML page rendered in T3 Code. Use when reporting back research findings, an explanation, a comparison, or an implementation summary. Quick answers and status updates stay as text.
---

# Visual report

A **report** is one Svelte project in a report directory under `~/.local/share/visual-report/reports/`. Its export is one self-contained HTML file that works offline. The report directory keeps the editable source, so you or a later agent can revise the report.

## Steps

### 1. Create the report

```sh
bun ~/.agents/skills/visual-report/scripts/new-report.ts <kebab-slug> "<Title>"
```

The last line of output is the report directory. To revise a report, edit its existing directory instead.

### 2. Write the report

The report is `src/lib/report/Report.svelte`. Its title is in `src/lib/report/meta.ts`. The shell around it gives the page its `<h1>`, the skip link, the `<main>` landmark, and the theme switch. Dark is the default theme.

Design each report for its content. Choose the structure, the visuals, and the interactions that make this subject clear. Add interaction where the reader explores: filters, comparisons, toggles between views, step-throughs, or simulations. A static section is correct for a fact the reader only reads.

- Write each heading as a plain label for its content: "Cache hit rate by region". Start each section with its content. A report has no subtitles, taglines, slogans, or lead-in lines under the title or a heading.
- Lay out sections with headings, whitespace, and dividers. Use a card only for one item in a set that the reader compares side by side.
- Build from semantic HTML and the components in `src/lib/components/`. Write custom SVG or HTML for visuals. Put a pattern the report repeats in a new component there.
- Use the theme color tokens (`bg-muted`, `text-muted-foreground`, `fill-chart-1`). They keep contrast at WCAG 2.2 AA in both themes.
- Make each section work from 320 CSS pixels wide up to desktop width.
- Give every control a visible label and a keyboard path. Give every chart a text equivalent, such as a table or a summary sentence.
- Import images and data files, so the export inlines them. You send the whole export inline to `html_render`, so keep it small: write the UI yourself instead of adding a UI or chart library.

Write `tests/report.spec.ts` with one test per interaction the report offers. Each test proves the interaction through the page, as the reader uses it. The step is done when every section has its content and every interaction has a test.

### 3. Edit the prose

Apply every rule in [`unslop`](../unslop/SKILL.md) to all report text. Technical text (procedures, system behavior, specifications, and failure analysis) also follows ASD-STE100 Simplified Technical English. Read [STE100.md](STE100.md) for those rules.

### 4. Preview in T3 Code

Run `bun run export`, then `bun run serve` in the background. Open the report with T3 Code's preview tools at `{kind: "environment-port", port: 4173}`. If calls on a visible tab time out, open a background tab with `open: false`. Inspect the report with `preview_snapshot` (with `includeImage`) in these states:

- Desktop width, dark theme and light theme.
- The `iphone-se` preset.
- Each interaction, operated by keyboard.

If `preview_snapshot` times out, run `bun run screenshots` and read the PNG files it prints. Use `preview_click` and `preview_evaluate` for the interactions. Fix each defect you see, then export again. The preview is done when every state reads clearly and nothing overlaps, clips, or scrolls sideways. Before you stop the server, get the render height at the reply width: resize to `freeform` 728 × 800, then evaluate `document.documentElement.scrollHeight`.

### 5. Commit

Commit all changes in the report directory. The pre-commit hook in `lefthook.yml` runs the gate. Fix each failure and commit again. The step is done when the commit lands. A commit made with `--no-verify` skips the gate and does not count.

### 6. Render and reply

Read `<report directory>/<report directory name>.html` in pages of 60 lines, using the `offset` and `limit` of the Read tool, until you hold every line. Pass the full contents to `html_render`, with the height from step 4. In your reply, give the absolute path of that HTML file as a link. Add only what the page does not say.
