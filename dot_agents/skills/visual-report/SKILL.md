---
name: visual-report
description: Visual reports as self-contained HTML files. Use for research findings, explanations, comparisons, or implementation summaries; keep quick answers and status updates as text.
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

**Visualize:** Reach for a chart or diagram when a trend, comparison, distribution, flow, or structure would become clearer visually.

Design each report for its content. Choose the structure, the visuals, and the interactions that make this subject clear. Add interaction where the reader explores: filters, comparisons, toggles between views, step-throughs, or simulations. A static section is correct for a fact the reader only reads.

- Write each heading as a plain label for its content: "Cache hit rate by region". Put the section content directly beneath its heading.
- Lay out sections with headings, whitespace, and dividers. Use a card only for one item in a set that the reader compares side by side.
- **Components:** Build the report UI with [shadcn-svelte](https://www.shadcn-svelte.com/docs/cli) components and semantic HTML. In the report directory, initialize with `npx shadcn-svelte@latest init` when `components.json` is absent, then add the components you need with `npx shadcn-svelte@latest add <component>`. Match the report's existing import aliases and theme stylesheet when configuring the CLI. Keep shared report patterns in `src/lib/components/`; use custom SVG or HTML for visuals.
- Use the theme color tokens (`bg-muted`, `text-muted-foreground`, `fill-chart-1`). They keep contrast at WCAG 2.2 AA in both themes.
- Make each section work from 320 CSS pixels wide up to desktop width.
- Give every control a visible label and a keyboard path. Give every chart a text equivalent, such as a table or a summary sentence.
- Import images and data files, so the export inlines them. Bundle component dependencies into the export.
- Use ordinary outbound `<a href="https://…">` links for citations. Keep assets local and repair asset or validator defects so export validation can verify offline use.

Write `tests/report.spec.ts` with one test per interaction the report offers. Each test proves the interaction through the page, as the reader uses it. The step is done when every section has its content and every interaction has a test.

### 3. Edit the prose

Apply every rule in [`unslop`](../unslop/SKILL.md) to all report text. Technical text (procedures, system behavior, specifications, and failure analysis) also follows ASD-STE100 Simplified Technical English. Read [STE100.md](STE100.md) for those rules.

### 4. Verify the export

**Lint:** Run `bun run lint` in the report directory and fix each diagnostic. The template runs [shadcn-lint (`@shadcn/lint`)](https://github.com/shadcn-ui/lint) through ESLint, configured in `eslint.config.js`. To run that check directly, use `bunx eslint . --max-warnings 0`.

Run `bun run export` and `bun run test` to verify the exported file and its interactions. For visual inspection, run `bun run serve` in the background, then `bun run screenshots` and inspect the saved images. Add captures as needed to cover:

- 1280 pixels wide in dark and light themes.
- 375 and 320 pixels wide.
- Each interaction's visible states, with keyboard behavior covered by the interaction tests.

Fix defects and repeat the affected checks. Verification is complete when the checks pass and every inspected state reads clearly, with content fitting its viewport.

### 5. Commit

Commit all changes in the report directory. The pre-commit hook in `lefthook.yml` runs the gate. Fix each failure and commit again. The step is done when the commit lands. Keep the pre-commit hook enabled so the commit proves the gate passed.

### 6. Deliver the file

Link the absolute path to `<report directory>/<report directory name>.html` in your reply so the user can click the file and open it in their own browser. Add only what the page does not say. Delivery is complete when the verified export exists and the reply links it.

**Optional inline rendering:** For an extra preview in T3 Code, follow [INLINE-RENDERING.md](INLINE-RENDERING.md).
