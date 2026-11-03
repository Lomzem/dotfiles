---
name: visual-report
description: Visual reports as self-contained HTML files. Use for research findings, explanations, comparisons, or implementation summaries; keep quick answers and status updates as text.
---

# Visual report

A **report** is one Svelte project in a report directory under `~/.local/share/visual-report/reports/`. Its export is one self-contained HTML file that works offline. The report directory keeps the editable source, so you or a later agent can revise the report.

Use `bun` to run scripts and manage dependencies, and `bunx` to run package CLIs.

## Steps

### 1. Create the report

```sh
bun ~/.agents/skills/visual-report/scripts/new-report.ts <kebab-slug> "<Title>"
```

The last line of output is the report directory. To revise a report, edit its existing directory instead.

### 2. Design the report

For a new report or a visual redesign, read [`frontend-design`](../frontend-design/SKILL.md) and follow its plan, review, build, and critique process. Ground each report's identity in its subject, audience, and reading task. The template's neutral palette is a starting point for implementation; choose the report's palette and typography deliberately.

Record the reviewed plan in `DESIGN.md` in the report directory, including why its choices fit the content and which visual choice gives this report its personality. When revising a report, preserve its established identity unless the brief calls for a redesign.

Map the chosen palette to the semantic tokens in `src/app.css`, with separate light and dark values. Keep category and status meanings consistent across themes. Choose chart colors for their data roles, such as categories, ordered values, or divergence. Carry the identity through the report shell, controls, and visuals. Bundle any custom fonts locally so typography survives offline export.

This step is done when the plan explains why this design fits this subject and defines both themes for implementation.

### 3. Write the report

The report is `src/lib/report/Report.svelte`. Its title is in `src/lib/report/meta.ts`. The shell around it gives the page its `<h1>`, the skip link, the `<main>` landmark, and the theme switch. Dark is the default theme.

**Visualize:** Reach for a chart or diagram when a trend, comparison, distribution, flow, or structure would become clearer visually.

Let the content determine report length, section count, and export size. Design each report for its content. Choose the structure, the visuals, and the interactions that make this subject clear. Add interaction where the reader explores: filters, comparisons, toggles between views, step-throughs, or simulations. A static section is correct for a fact the reader only reads.

- Write each heading as a plain label for its content: "Cache hit rate by region". Put the section content directly beneath its heading.
- Lay out sections with headings, whitespace, and dividers. Use a card only for one item in a set that the reader compares side by side.
- Write status, category, version, and count labels as plain text: a word in the sentence, a table column, or a label beside its value.
- **Components:** Build the report UI with [shadcn-svelte](https://www.shadcn-svelte.com/docs/cli) components and semantic HTML. In the report directory, initialize with `bunx shadcn-svelte@latest init` when `components.json` is absent, then add the components you need with `bunx shadcn-svelte@latest add <component>`. Match the report's existing import aliases and theme stylesheet when configuring the CLI. Keep shared report patterns in `src/lib/components/`; use custom SVG or HTML for visuals.
- Use the report's semantic color tokens (`bg-muted`, `text-muted-foreground`, `fill-chart-1`). Verify their rendered combinations against WCAG 2.2 AA in both themes, including muted text, chart labels, and hover, focus, and selected states.
- Make each section work from 320 CSS pixels wide up to desktop width.
- Give every control a visible label and a keyboard path. Give every chart a text equivalent, such as a table or a summary sentence.
- Pair color with visible labels, shapes, patterns, or line styles wherever it conveys meaning. Underline inline links. Keep focus indicators visible and unobscured, and respect reduced motion.
- Import images and data files, so the export inlines them. Bundle component dependencies into the export.
- Use ordinary outbound `<a href="https://…">` links for citations. Keep assets local and repair asset or validator defects so export validation can verify offline use.

Write `tests/report.spec.ts` with one test per interaction the report offers. Each test proves the interaction through the page, as the reader uses it. The step is done when every section has its content and every interaction has a test.

### 4. Edit the prose

Apply every rule in [`unslop`](../unslop/SKILL.md) to all report text. For technical text (procedures, system behavior, specifications, and failure analysis), read the clarity guidance adapted from ASD-STE100 in [STE100.md](STE100.md).

### 5. Verify the export

**Lint:** Run `bun run lint` in the report directory and fix each diagnostic. The template runs [shadcn-lint (`@shadcn/lint`)](https://github.com/shadcn-ui/lint) through ESLint, configured in `eslint.config.js`. To run that check directly, use `bunx eslint . --max-warnings 0`.

Run `bun run export` and `bun run test` to verify the exported file and its interactions. For visual inspection, run `bun run serve` in the background, then `bun run screenshots` and inspect the saved images. Add captures as needed to cover:

- 1280 pixels wide in dark and light themes.
- 375 and 320 pixels wide.
- Each interaction's visible states, with keyboard behavior covered by the interaction tests.

Check actual foreground/background pairs, including transparency, in both themes. Require [4.5:1 for normal text and 3:1 for large text](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html). Large text is at least 24 CSS pixels, or about 18.67 CSS pixels when bold. Require [3:1 against adjacent colors](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html) for meaningful chart marks and visual cues needed to identify controls and states, including author-styled focus indicators. Decorative dividers can remain subtle.

Use the automated accessibility results alongside manual checks of SVG/canvas contrast, visible alternatives to color, keyboard focus, zoom/reflow, and reduced motion. Automated checks alone do not establish WCAG conformance. Record the checked color pairs and ratios, manual results, and visual critique in `DESIGN.md`. Confirm the report still expresses the planned identity after accessibility fixes.

Fix defects and repeat the affected checks. Verification is complete when the checks pass, every inspected state reads clearly with content fitting its viewport, and the design record contains the accessibility evidence.

### 6. Commit

Commit all changes in the report directory. The pre-commit hook in `lefthook.yml` runs the gate. Fix each failure and commit again. The step is done when the commit lands. Keep the pre-commit hook enabled so the commit proves the gate passed.

### 7. Deliver the file

Link the absolute path to `<report directory>/<report directory name>.html` in your reply so the user can click the file and open it in their own browser. Add only what the page does not say. Delivery is complete when the verified export exists and the reply links it.

**Stretch goal — inline preview:** The HTML file is the deliverable. After the verified file is ready, you may add a T3 Code preview using [INLINE-RENDERING.md](INLINE-RENDERING.md). Preview availability or failure does not block delivery or require changes to the report.
