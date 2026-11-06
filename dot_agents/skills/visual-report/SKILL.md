---
name: visual-report
description: Visual reports as self-contained HTML files. Use for research findings, explanations, comparisons, or implementation summaries; keep quick answers and status updates as text.
---

# Visual report

A **report** is one Svelte project under `~/.local/share/visual-report/reports/`. Its editable source stays in the report directory; its deliverable is one self-contained HTML file that works offline.

Use `bun` for scripts and dependencies, and `bunx` for package CLIs.

## 1. Create or reopen

For a new report:

```sh
bun ~/.agents/skills/visual-report/scripts/new-report.ts <kebab-slug> "<Title>"
```

The last output line is the report directory. For revisions, edit the existing directory. Continue when the report directory is identified and ready to edit.

## 2. Plan the design

For a new report or visual redesign, read [frontend-design](../frontend-design/SKILL.md) and follow its plan, review, build, and critique process. Ground the identity in the subject, audience, and reading task. For other revisions, preserve the established identity.

Record the reviewed plan in `DESIGN.md`: palette and typography, layout, why they fit the content, and the visual choice that gives the report its personality. Map the palette to semantic tokens in `src/app.css` with light and dark values; keep category and status meanings consistent between themes. Choose chart colors for their data roles. Bundle custom fonts locally.

Read [ACCESSIBILITY.md](ACCESSIBILITY.md) before building or changing visuals or controls, and use its inspection checklist during verification.

Continue when `DESIGN.md` explains the design choices and defines both themes for implementation.

## 3. Write the report

Edit `src/lib/report/Report.svelte` and its title in `src/lib/report/meta.ts`. The shell supplies the `<h1>`, skip link, `<main>`, and theme switch. Dark is the default theme.

Let the subject determine length, sections, visuals, and export size. Visualize trends, comparisons, distributions, flows, and structures when doing so improves understanding. Add interaction where the reader explores; use static content for facts the reader only reads.

- Use plain content labels for headings, with the content directly beneath them.
- Organize sections with headings, whitespace, and dividers. Reserve cards for items compared side by side.
- Put status, category, version, and count labels in sentences, table columns, or beside values.
- Build with the template's shadcn-svelte controls and semantic HTML. Add needed controls with `bunx shadcn-svelte@latest add <component>`, preserving the existing aliases and theme. Keep shared patterns in `src/lib/components/`; use custom SVG or HTML for visuals.
- Use semantic color tokens. Import images, fonts, and data so the export bundles its assets. Use ordinary outbound links for citations.

Replace the sample tests in `tests/report.spec.ts` with reader-facing tests for the report's interactions, including keyboard operation. Keep the shared export and shell checks.

Continue when every section has its content, every interaction has behavioral coverage, and the accessibility requirements are implemented.

## 4. Edit the prose

Apply [unslop](../unslop/SKILL.md) to all report text. For procedures, system behavior, specifications, or failure analysis, also read [STE100.md](STE100.md). Continue when all applicable rules have been applied.

## 5. Verify and critique

Run `bun run verify` in the report directory. It owns the ordered automated checks and baseline screenshots of the exported file. For an existing report that predates `verify`, use its recorded verification workflow; migrate its template only when requested. Fix failures and rerun the affected checks.

Inspect the screenshots and any additional captures needed for the report's interaction states. Complete the manual checks in [ACCESSIBILITY.md](ACCESSIBILITY.md). Record the checked color pairs and ratios, manual results, and visual critique in `DESIGN.md`. Confirm the report still expresses the planned identity after fixes.

A passing automated gate proves its checks passed; visual clarity, design fit, and the manual accessibility checks require direct inspection. Continue when the gate passes, every inspected state reads clearly at its viewport, and `DESIGN.md` contains the inspection evidence.

## 6. Commit

Commit all report changes with the pre-commit hook enabled. The hook uses the same automated verification path. Resolve failures and retry. Continue when the commit lands.

## 7. Deliver

Link the absolute path to `<report directory>/<report directory name>.html` in your reply. Add only what the page does not say. Delivery is complete when the verified export exists and the reply links it.

For an additional T3 Code preview after the file is ready, use [INLINE-RENDERING.md](INLINE-RENDERING.md). Preview availability or failure does not block file delivery or require report changes.
