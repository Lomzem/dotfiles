"""Self-contained HTML report: named swatches and every contrast check."""

from __future__ import annotations

import html
from pathlib import Path

from . import contrast

STYLE = """
body{font:14px/1.45 system-ui,sans-serif;margin:2rem;background:#14161c;color:#e8e8ee}
h1,h2{font-weight:600}code{font-family:ui-monospace,monospace}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:.6rem}
.sw{border-radius:10px;overflow:hidden;background:#1f222b}
.sw div{height:52px}.sw p{margin:.3rem .5rem;font-size:12px;word-break:break-all}
table{border-collapse:collapse;width:100%;margin-top:.5rem}
td,th{padding:.35rem .5rem;border-bottom:1px solid #2c3040;text-align:left;vertical-align:middle}
.ok{color:#7ee2a0}.bad{color:#ff8f8f;font-weight:600}
.sample{padding:.3rem .6rem;border-radius:6px;white-space:nowrap}
.note{color:#b8bccb;max-width:70rem}
"""


def _sample(fg: str, bg: str, alpha: float | None) -> str:
    background = bg
    if alpha is not None and alpha < 1:
        r, g, b = contrast.rgb(bg)
        background = f"rgba({r},{g},{b},{alpha:.2f})"
    return f'<span class="sample" style="color:{fg};background:{background}">Sample Aa 123</span>'


def write(path: Path, palette: dict, rows: list[dict], status: str) -> Path:
    colors, alpha = palette["colors"], palette["alpha"]
    failed = contrast.failures(rows)
    e = html.escape
    swatches = "".join(
        f'<div class="sw"><div style="background:{v}"></div><p><code>{e(k)}</code><br>{v}</p></div>'
        for k, v in sorted(colors.items())
    )
    checks = []
    for row in rows:
        verdict = '<span class="ok">pass</span>' if row["ok"] else '<span class="bad">FAIL</span>'
        if row["kind"] == "hue":
            checks.append(
                f"<tr><td>{verdict}</td><td>{e(row['role'])}</td><td><code>{e(row['fg'])}</code></td>"
                f"<td colspan=4>hue {row['hue']}°</td></tr>"
            )
            continue
        level = alpha[row["alpha"]] if row["alpha"] else None
        checks.append(
            f"<tr><td>{verdict}</td><td>{e(row['role'])}</td>"
            f"<td><code>{e(row['fg'])}</code> on <code>{e(row['bg'])}</code>"
            f"{f' (alpha.{row['alpha']} {level:.2f})' if level is not None else ''}</td>"
            f"<td>{_sample(colors[row['fg']], colors[row['bg']], level)}</td>"
            f"<td>{row['ratio']}:1 (min {row['minimum']}:1)</td>"
            f"<td>{row['opaque']}:1</td><td>{row['black_white']}:1</td></tr>"
        )
    corrections = palette.get("corrections") or []
    corrected = (
        "<h2>Automatic corrections</h2><ul>" + "".join(f"<li><code>{e(c)}</code></li>" for c in corrections) + "</ul>"
        if corrections
        else ""
    )
    alphas = ", ".join(f"<code>alpha.{k} = {v:.2f}</code>" for k, v in sorted(alpha.items()))
    generator = palette.get("generator", {})
    document = f"""<!doctype html><html lang="en"><meta charset="utf-8">
<title>rice: {e(palette["name"])}</title><style>{STYLE}</style>
<h1>{e(palette["name"])} <small>({e(status)})</small></h1>
<p class="note">Image <code>{e(palette["image"])}</code><br>SHA-256 <code>{e(palette["sha256"])}</code><br>
Generator {e(str(generator.get("version", "?")))}, scheme <code>{e(str(generator.get("scheme", "?")))}</code>.
Surface alpha: {alphas}.</p>
<p class="{"bad" if failed else "ok"}">{len(failed)} of {len(rows)} checks fail.</p>
<p class="note">Edit a colour with <code>rice set {e(palette["image"])} NAME=#rrggbb</code> or an alpha with
<code>alpha.panel=0.9</code>, then approve with <code>rice approve</code>. Approval is refused while any check fails.</p>
<h2>Checks (WCAG AA: text 4.5:1, UI indicators 3:1)</h2>
<p class="note">Columns: measured worst case over this wallpaper, the same pair fully opaque, and the
worst case over any backdrop from black to white. {e(contrast.COVERAGE)}</p>
<table><tr><th></th><th>Role</th><th>Pair</th><th>Sample</th><th>Wallpaper</th><th>Opaque</th><th>Black–white</th></tr>
{"".join(checks)}</table>{corrected}
<h2>Named colours</h2><div class="grid">{swatches}</div></html>
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(document)
    return path
