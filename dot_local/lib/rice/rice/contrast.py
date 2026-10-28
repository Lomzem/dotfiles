"""Colour validation, WCAG contrast checks and automatic corrections.

This module is independent of the palette generator. It reads a palette (named
`#rrggbb` colours plus surface alpha values) and a backdrop bound (per-channel
min/max of the wallpaper) and decides whether every controlled pair is readable.

WCAG 2.x AA thresholds are used: 4.5:1 for text, 3:1 for meaningful UI
indicators. A translucent surface is composited over every colour the backdrop
box can produce; its worst luminance sits on one of the two box corners, so the
check is exact for the bound it is given.
"""

from __future__ import annotations

import colorsys
import math
import re
from dataclasses import dataclass

TEXT = 4.5
UI = 3.0

HEX = re.compile(r"^#[0-9a-f]{6}$")

# Surfaces drawn with a translucent background, keyed by palette alpha name.
ALPHA_LIMITS = (0.3, 1.0)
DEFAULT_ALPHA = {"panel": 0.82, "terminal": 0.82}

Rgb = tuple[float, float, float]
Bound = tuple[Rgb, Rgb]  # darkest and brightest backdrop corner

BLACK_WHITE: Bound = ((0.0, 0.0, 0.0), (255.0, 255.0, 255.0))


@dataclass(frozen=True)
class Pair:
    fg: str
    bg: str
    minimum: float
    role: str
    alpha: str | None = None  # name of the alpha that makes `bg` translucent


ANSI = ("red", "green", "yellow", "blue", "magenta", "cyan", "white")

PAIRS: tuple[Pair, ...] = (
    # Shell surfaces (Noctalia bar, panels, notifications, Fuzzel) over the wallpaper.
    Pair("on_surface", "surface", TEXT, "text on panel", "panel"),
    Pair("on_surface_variant", "surface", TEXT, "muted text on panel", "panel"),
    Pair("primary", "surface", TEXT, "Fuzzel prompt and match text", "panel"),
    Pair("error", "surface", UI, "error indicator on panel", "panel"),
    # Opaque controls drawn on top of the panel.
    Pair("on_surface", "surface_container", TEXT, "text on card"),
    Pair("on_surface_variant", "surface_container", TEXT, "muted text on card"),
    Pair("primary", "surface_container", UI, "accent indicator on card"),
    Pair("on_primary", "primary", TEXT, "selected item text"),
    Pair("on_secondary", "secondary", TEXT, "secondary button text"),
    Pair("on_tertiary", "tertiary", TEXT, "tertiary button text"),
    Pair("on_error", "error", TEXT, "error button text"),
    Pair("on_primary_container", "primary_container", TEXT, "tinted selection text"),
    Pair("on_secondary_container", "secondary_container", TEXT, "tinted chip text"),
    Pair("on_hover", "hover", TEXT, "hovered item text"),
    # Terminal (Kitty, and Neovim, Yazi and Zsh through the ANSI palette).
    Pair("terminal_foreground", "terminal_background", TEXT, "terminal text", "terminal"),
    Pair("terminal_cursor", "terminal_background", UI, "terminal cursor", "terminal"),
    Pair("terminal_cursor_text", "terminal_cursor", TEXT, "text under cursor"),
    Pair("terminal_selection_fg", "terminal_selection_bg", TEXT, "selected terminal text"),
    *(
        Pair(
            f"terminal_{tone}_{name}",
            "terminal_background",
            TEXT,
            f"ANSI {tone} {name}",
            "terminal",
        )
        for tone in ("normal", "bright")
        for name in ANSI
    ),
    Pair(
        "terminal_bright_black",
        "terminal_background",
        TEXT,
        "ANSI bright black (comments)",
        "terminal",
    ),
)

# Adapter contract: every text role actually used on a surface must stay readable.
# These surfaces cover GTK/Qt, Chromium chrome, Vesktop, shell cards and terminal
# editor popups/cursorline. This is deliberately stronger than a single UI pair.
SURFACES = (
    "background",
    "surface",
    "surface_variant",
    "surface_container_lowest",
    "surface_container_low",
    "surface_container",
    "surface_container_high",
    "surface_container_highest",
)
TEXT_ROLES = (
    "on_background",
    "on_surface",
    "on_surface_variant",
    "primary",
    "secondary",
    "tertiary",
    "error",
    "terminal_foreground",
    "terminal_bright_black",
    *(f"terminal_{tone}_{name}" for tone in ("normal", "bright") for name in ANSI),
)
PAIRS += tuple(
    Pair(fg, bg, TEXT, f"{fg} on {bg} (editor, shell, GTK, browser omnibox)")
    for bg in SURFACES
    for fg in TEXT_ROLES
    if not any(p.fg == fg and p.bg == bg and p.minimum >= TEXT and p.alpha is None for p in PAIRS)
)
PAIRS += tuple(
    Pair(fg, "surface", TEXT, f"{fg} on translucent Discord background", "panel")
    for fg in ("error", "terminal_normal_green", "terminal_normal_yellow")
    if not any(p.fg == fg and p.bg == "surface" and p.minimum >= TEXT and p.alpha == "panel" for p in PAIRS)
)
PAIRS += tuple(
    Pair(fg, "terminal_background", TEXT, f"{fg} transparent editor text", "terminal")
    for fg in TEXT_ROLES
    if not any(
        p.fg == fg and p.bg == "terminal_background" and p.minimum >= TEXT and p.alpha == "terminal" for p in PAIRS
    )
)
PAIRS += (
    Pair("on_tertiary_container", "tertiary_container", TEXT, "GTK warning text"),
    Pair("terminal_background", "terminal_normal_green", TEXT, "Yazi copied count"),
    Pair("terminal_background", "terminal_normal_red", TEXT, "Yazi cut count"),
    Pair("terminal_background", "terminal_normal_yellow", TEXT, "Neovim changed text"),
)

# Hue ranges (degrees) that keep semantic colours recognisable.
SEMANTIC_HUES = {
    "red": (340.0, 25.0),
    "yellow": (35.0, 70.0),
    "green": (85.0, 165.0),
}
SEMANTIC_ROLES = {
    "error": "red",
    "terminal_normal_red": "red",
    "terminal_bright_red": "red",
    "terminal_normal_yellow": "yellow",
    "terminal_bright_yellow": "yellow",
    "terminal_normal_green": "green",
    "terminal_bright_green": "green",
}

COVERAGE = (
    "Checked: the listed shell, card, selection, hover, terminal, cursor, selection and "
    "ANSI pairs. Translucent panel and terminal backgrounds are composited over the "
    "wallpaper bound (full-resolution extrema over every frame). Not checked: ANSI normal black (a background colour), "
    "decorative outlines, the fixed whole-window opacity of Helium/T3, and any colours "
    "chosen by applications, websites or documents themselves."
)


class PaletteError(ValueError):
    pass


def rgb(value: str) -> Rgb:
    return (int(value[1:3], 16), int(value[3:5], 16), int(value[5:7], 16))


def hex_of(color: Rgb) -> str:
    return "#" + "".join(f"{round(min(255.0, max(0.0, c))):02x}" for c in color)


def luminance(color: Rgb) -> float:
    def channel(c: float) -> float:
        c = c / 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = color
    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)


def ratio(a: Rgb, b: Rgb) -> float:
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def composite(top: Rgb, alpha: float, below: Rgb) -> Rgb:
    return tuple(alpha * t + (1.0 - alpha) * b for t, b in zip(top, below))  # type: ignore[return-value]


def worst_ratio(fg: Rgb, bg: Rgb, alpha: float, bound: Bound) -> float:
    """Lowest contrast of `fg` over `bg` at `alpha` composited on any backdrop in `bound`."""
    if alpha >= 1.0:
        return ratio(fg, bg)
    dark = luminance(composite(bg, alpha, bound[0]))
    light = luminance(composite(bg, alpha, bound[1]))
    text = luminance(fg)
    if dark <= text <= light:
        return 1.0
    nearest = light if text > light else dark
    hi, lo = max(text, nearest), min(text, nearest)
    return (hi + 0.05) / (lo + 0.05)


def hue(value: str) -> float:
    r, g, b = (c / 255.0 for c in rgb(value))
    h, _, _ = colorsys.rgb_to_hls(r, g, b)
    return h * 360.0


def in_hue_range(degrees: float, span: tuple[float, float]) -> bool:
    low, high = span
    return low <= degrees <= high if low <= high else degrees >= low or degrees <= high


def validate_palette(colors: object, alpha: object, required: set[str]) -> None:
    """Reject malformed palettes before any contrast or rendering work."""
    if not isinstance(colors, dict) or not isinstance(alpha, dict):
        raise PaletteError("palette must contain 'colors' and 'alpha' objects")
    missing = sorted(required - colors.keys())
    if missing:
        raise PaletteError(f"palette is missing colours: {', '.join(missing)}")
    for name, value in colors.items():
        if not isinstance(name, str) or not re.fullmatch(r"[a-z][a-z0-9_]{0,63}", name):
            raise PaletteError(f"invalid colour name: {name!r}")
        if not isinstance(value, str) or not HEX.match(value):
            raise PaletteError(f"{name} must be a lowercase #rrggbb colour, got {value!r}")
    for name in DEFAULT_ALPHA:
        value = alpha.get(name)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise PaletteError(f"alpha.{name} must be a finite number")
        if not ALPHA_LIMITS[0] <= value <= ALPHA_LIMITS[1]:
            raise PaletteError(f"alpha.{name} must be between {ALPHA_LIMITS[0]} and {ALPHA_LIMITS[1]}")
    unknown = sorted(set(alpha) - DEFAULT_ALPHA.keys())
    if unknown:
        raise PaletteError(f"unknown alpha values: {', '.join(unknown)}")


def _surface_alpha(value: float) -> float:
    # Fuzzel uses an 8-bit RGBA alpha; use the less opaque of byte/native forms.
    return min(value, round(value * 255) / 255)


def evaluate(colors: dict[str, str], alpha: dict[str, float], bound: Bound) -> list[dict]:
    """Every controlled pair and semantic hue with its measured result."""
    rows = []
    for pair in PAIRS:
        level = _surface_alpha(alpha[pair.alpha]) if pair.alpha else 1.0
        fg, bg = rgb(colors[pair.fg]), rgb(colors[pair.bg])
        measured = worst_ratio(fg, bg, level, bound)
        rows.append(
            {
                "kind": "contrast",
                "role": pair.role,
                "fg": pair.fg,
                "bg": pair.bg,
                "alpha": pair.alpha,
                "minimum": pair.minimum,
                "opaque": round(ratio(fg, bg), 2),
                "ratio": round(measured, 2),
                "black_white": round(worst_ratio(fg, bg, level, BLACK_WHITE), 2),
                "ok": measured >= pair.minimum,
            }
        )
    for name, family in SEMANTIC_ROLES.items():
        degrees = hue(colors[name])
        rows.append(
            {
                "kind": "hue",
                "role": f"{name} stays {family}",
                "fg": name,
                "hue": round(degrees),
                "ok": in_hue_range(degrees, SEMANTIC_HUES[family]),
            }
        )
    return rows


def failures(rows: list[dict]) -> list[dict]:
    return [row for row in rows if not row["ok"]]


def _with_lightness(value: str, lightness: float) -> str:
    r, g, b = (c / 255.0 for c in rgb(value))
    h, _, s = colorsys.rgb_to_hls(r, g, b)
    nr, ng, nb = colorsys.hls_to_rgb(h, min(1.0, max(0.0, lightness)), s)
    return hex_of((nr * 255.0, ng * 255.0, nb * 255.0))


def _lightness(value: str) -> float:
    r, g, b = (c / 255.0 for c in rgb(value))
    return colorsys.rgb_to_hls(r, g, b)[1]


def _fix_foreground(fg: str, bg: str, minimum: float) -> str | None:
    """Move `fg` lightness away from `bg` (hue kept) until the opaque pair passes."""
    target = minimum + 0.1
    away = 1.0 if luminance(rgb(bg)) < 0.18 else -1.0
    for direction in (away, -away):
        start = _lightness(fg)
        for step in range(101):
            candidate = _with_lightness(fg, start + direction * step / 100.0)
            if ratio(rgb(candidate), rgb(bg)) >= target:
                return candidate
    return None


def correct(colors: dict[str, str], alpha: dict[str, float], bound: Bound) -> list[str]:
    """Fix failing pairs in place: correct luminance first, then raise surface alpha.

    Returns a human-readable log of every change.
    """
    changes: list[str] = []
    for _ in range(4):
        changed = False
        for pair in PAIRS:
            fg, bg = colors[pair.fg], colors[pair.bg]
            if ratio(rgb(fg), rgb(bg)) >= pair.minimum:
                continue
            fixed = _fix_foreground(fg, bg, pair.minimum)
            if fixed and fixed != fg:
                colors[pair.fg] = fixed
                changes.append(f"{pair.fg}: {fg} -> {fixed} ({pair.role})")
                changed = True
        if not changed:
            break
    for name in sorted(alpha):
        pairs = [p for p in PAIRS if p.alpha == name]
        start = alpha[name]
        level = start
        while level < 1.0 and any(
            worst_ratio(rgb(colors[p.fg]), rgb(colors[p.bg]), _surface_alpha(level), bound) < p.minimum for p in pairs
        ):
            level = min(1.0, round(level + 0.01, 2))
        if level != start:
            alpha[name] = level
            changes.append(f"alpha.{name}: {start} -> {level} (readable over the wallpaper)")
    return changes
