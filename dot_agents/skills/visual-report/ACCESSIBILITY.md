# Report accessibility

Use these requirements when building visuals and controls, then inspect the exported report against the checklist. Record manual evidence in the report's `DESIGN.md`.

## Build

- Support widths from 320 CSS pixels to desktop without clipping or horizontal page scrolling.
- Give every control a visible label, a keyboard path, and a visible, unobscured focus indicator.
- Give each chart a text equivalent, such as a table or a summary sentence.
- Pair meaningful color with visible labels, shapes, patterns, or line styles. Underline inline links.
- Respect reduced motion.
- Use semantic color tokens in both themes, including muted text, chart labels, and hover, focus, and selected states. Tokens alone do not establish contrast.

## Inspect

The automated gate checks the exported file and captures the baseline viewports. Inspect desktop at 1280 pixels in dark and light themes, plus 375 and 320 pixels. Add captures for the report's visible interaction states. Operate controls by keyboard; check focus and zoom/reflow directly.

Measure actual foreground/background pairs, including transparency, in both themes:

| Content | Minimum contrast |
| --- | --- |
| Normal text | 4.5:1 |
| Large text: at least 24 CSS px, or about 18.67 CSS px when bold | 3:1 |
| Meaningful chart marks and visual cues identifying controls or states, including author-styled focus indicators | 3:1 against adjacent colors |

Decorative dividers may remain subtle. The thresholds follow [WCAG text contrast](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html) and [non-text contrast](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html).

Use automated accessibility results alongside manual inspection of SVG/canvas contrast, visible alternatives to color, keyboard focus, zoom/reflow, and reduced motion. Automated results alone do not establish WCAG conformance.

The inspection is complete when every inspected state fits its viewport and reads clearly, and `DESIGN.md` records the checked pairs and ratios, manual results, and remaining limitations. Fix defects and repeat the affected checks before delivery.
