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
- Import images and data files, so the export inlines them. Keep the tool payload small: write the UI yourself instead of adding a UI or chart library.
- Use ordinary outbound `<a href="https://…">` links for citations. Assets must work offline. Never hide URLs in JavaScript variables to evade export validation; fix the asset or the validator.

Write `tests/report.spec.ts` with one test per interaction the report offers. Each test proves the interaction through the page, as the reader uses it. The step is done when every section has its content and every interaction has a test.

### 3. Edit the prose

Apply every rule in [`unslop`](../unslop/SKILL.md) to all report text. Technical text (procedures, system behavior, specifications, and failure analysis) also follows ASD-STE100 Simplified Technical English. Read [STE100.md](STE100.md) for those rules.

### 4. Preview in T3 Code

Run `bun run export`, then `bun run serve` in the background. Call `preview_status`, then open the report at `{kind: "environment-port", port: 4173}` if needed. After each `preview_resize`, use `preview_evaluate` to read `({width: window.innerWidth, height: window.innerHeight})`. Continue only if these match the requested dimensions. Inspect with `preview_snapshot` (with `includeImage`) in these states:

- 1280 pixels wide, dark theme and light theme.
- 375 and 320 pixels wide.
- Each interaction, operated by keyboard.

If collaborative preview fails, a snapshot times out, or dimensions differ, switch immediately to `html_preview`; do not retry the failing preview path. Transfer the export as in step 6. Preview at explicit widths 1280, 728, 375, and 320 in both themes. Set the report's theme explicitly: remove the export's `class="dark"` for a light preview; `appearance` alone does not toggle that class. Verify keyboard interactions with `bun run test`; use `bun run screenshots` for additional captures. Fix each defect, then export again. The preview is done when every state reads clearly and nothing overlaps, clips, or scrolls sideways.

### 5. Commit

Commit all changes in the report directory. The pre-commit hook in `lefthook.yml` runs the gate. Fix each failure and commit again. The step is done when the commit lands. A commit made with `--no-verify` skips the gate and does not count.

### 6. Render and reply

Transfer `<report directory>/<report directory name>.html` through code orchestration, without reading or re-emitting its contents through the model. In Codex `functions.exec`, read it as JSON through `exec_command`, parse the output into a variable, and pass that variable directly to the HTML tools. For example (substitute the absolute path):

```js
const file = await tools.exec_command({
  cmd: `python3 -c 'import json,pathlib; print(json.dumps(pathlib.Path("/absolute/report.html").read_text()))'`,
  max_output_tokens: 100000,
});
if (file.exit_code !== 0) throw new Error('Cannot read report');
const html = JSON.parse(file.output); // Truncated output fails here.
const preview = await tools.mcp__t3_code__html_preview({ html, width: 728 });
// Inspect only the preview image and metadata; keep html out of tool output.
```

Preview the final export at 728 pixels wide, then call `html_render` from code with the same `html` variable and `height` set to the preview's `contentHeight`, clamped to 80–2000. Print only metadata and images from these calls. If the runtime cannot transfer a file through code, report that limitation instead of copying compiled HTML into context. In your reply, link the absolute HTML path. Add only what the page does not say.
