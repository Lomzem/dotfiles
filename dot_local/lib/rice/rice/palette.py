from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from . import contrast, store
from .store import Paths, RiceError

_ANSI = {
    "black": "black (normal: a background shade; bright: comments, muted text)",
    "red": "red: errors, deletions (must stay red)",
    "green": "green: success, additions (must stay green)",
    "yellow": "yellow: warnings, changes (must stay yellow)",
    "blue": "blue",
    "magenta": "magenta",
    "cyan": "cyan",
    "white": "white",
}
ANSI = tuple(_ANSI)

COLORS: dict[str, str] = {
    "background": "window background of GTK/Qt apps, Neovim floats, websites",
    "on_background": "text on `background`",
    "surface": "translucent panels: Noctalia bar, popups, notifications, Fuzzel, Discord",
    "on_surface": "main text on panels and cards",
    "on_surface_variant": "muted/secondary text on panels and cards",
    "surface_variant": "alternate rows, inactive tabs, Qt base",
    "surface_container_lowest": "deepest inset areas (code blocks, sunken fields)",
    "surface_container_low": "low cards and sidebars",
    "surface_container": "cards and controls drawn on panels",
    "surface_container_high": "raised cards, menus, hovered rows",
    "surface_container_highest": "highest raised areas (dialogs, selected rows)",
    "primary": "main accent: focus rings, links, Fuzzel matches, Niri focus border",
    "on_primary": "text on `primary` (selected items, primary buttons)",
    "primary_container": "tinted selection background",
    "on_primary_container": "text on `primary_container`",
    "secondary": "secondary accent (secondary buttons, Qt highlights)",
    "on_secondary": "text on `secondary`",
    "secondary_container": "tinted chips and toggles",
    "on_secondary_container": "text on `secondary_container`",
    "tertiary": "third accent (badges, highlights)",
    "on_tertiary": "text on `tertiary`",
    "tertiary_container": "GTK warning background",
    "on_tertiary_container": "text on `tertiary_container`",
    "error": "error indicators and text (must stay red)",
    "on_error": "text on `error`",
    "hover": "hovered item background in Noctalia",
    "on_hover": "text on `hover`",
    "outline": "borders and dividers",
    "outline_variant": "subtle borders, Noctalia outlines",
    "shadow": "drop shadows",
    "terminal_background": "Kitty background (shown at the terminal opacity), Neovim, Yazi",
    "terminal_foreground": "normal terminal text",
    "terminal_cursor": "terminal cursor",
    "terminal_cursor_text": "text under the terminal cursor",
    "terminal_selection_bg": "selected terminal text background",
    "terminal_selection_fg": "selected terminal text",
    **{f"terminal_{tone}_{name}": f"ANSI {tone} {text}" for tone in ("normal", "bright") for name, text in _ANSI.items()},
}

OPACITY: dict[str, str] = {
    "panels": "how solid `surface` panels are over the wallpaper, from 0.3 to 1.0: the Noctalia bar, "
    "notifications and OSD, Fuzzel and Discord",
    "terminal": "how solid `terminal_background` is over the wallpaper in Kitty, from 0.3 to 1.0",
}

@dataclass
class Palette:
    colors: dict[str, str]
    opacity: dict[str, float]
    source: Literal["file", "approved", "generated"]
    revision: int | None = None
    corrections: list[str] | None = None

    @property
    def alpha(self) -> dict[str, float]:
        return {"panel": self.opacity["panels"], "terminal": self.opacity["terminal"]}


class PaletteFileError(RiceError):

    def __init__(self, path: Path, problems: list[str]) -> None:
        super().__init__(f"{path} cannot be used: " + "; ".join(problems))
        self.path = path
        self.problems = problems


def file_path(paths: Paths, name: str) -> Path:
    return paths.config / "rice" / "palettes" / f"{name}.json"


def _opacity(alpha: dict[str, float]) -> dict[str, float]:
    return {"panels": alpha["panel"], "terminal": alpha["terminal"]}


def load(paths: Paths, name: str, image: Path, bound: contrast.Bound) -> Palette:
    path = file_path(paths, name)
    profile = store.load_profile(paths, store.image_sha(image))
    revision = store.current_revision(profile) if profile else None
    defaults = _opacity(revision["alpha"]) if revision else _opacity(contrast.DEFAULT_ALPHA)
    if path.exists() or path.is_symlink():
        return parse_file(path, defaults)
    if revision:
        return Palette({name: revision["colors"][name] for name in COLORS}, defaults, "approved", revision["revision"])
    colors = store.generate(image, store.settings(paths)["scheme"])
    store.semantic_terminal(colors)
    contrast.validate_palette(colors, contrast.DEFAULT_ALPHA, set(COLORS))
    colors = {name: colors[name] for name in COLORS}
    alpha = dict(contrast.DEFAULT_ALPHA)
    corrections = contrast.correct(colors, alpha, bound)
    return Palette(colors, _opacity(alpha), "generated", corrections=corrections)


def parse_file(path: Path, default_opacity: dict[str, float]) -> Palette:
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as error:
        raise PaletteFileError(path, [f"not valid JSON: {error}"]) from error
    except (OSError, UnicodeError) as error:
        raise PaletteFileError(path, [str(error)]) from error
    shape = 'expected {"colors": {NAME: "#rrggbb", ...}, "opacity": {"panels": N, "terminal": N}}'
    if not isinstance(data, dict) or not isinstance(data.get("colors"), dict):
        raise PaletteFileError(path, [shape])
    if not isinstance(data.get("opacity", {}), dict):
        raise PaletteFileError(path, [f"opacity must be an object; {shape}"])
    colors, opacity = data["colors"], {**default_opacity, **data.get("opacity", {})}
    problems = []
    extra = sorted(set(data) - {"colors", "opacity"})
    if extra:
        problems.append(f"unknown keys: {', '.join(extra)}; {shape}")
    missing = [name for name in COLORS if name not in colors]
    if missing:
        problems.append(f"missing colors: {', '.join(missing)}")
    unknown = sorted(set(colors) - COLORS.keys())
    if unknown:
        problems.append(f"unknown colors (not used by any app): {', '.join(unknown)}")
    for name, value in colors.items():
        if name in COLORS and not (isinstance(value, str) and contrast.HEX.fullmatch(value.lower())):
            problems.append(f"{name} must be a #rrggbb color, got {value!r}")
    unknown_opacity = sorted(set(opacity) - OPACITY.keys())
    if unknown_opacity:
        problems.append(f"unknown opacity: {', '.join(unknown_opacity)} (use {', '.join(OPACITY)})")
    for name in OPACITY:
        value = opacity.get(name)
        ok = (
            isinstance(value, (int, float))
            and not isinstance(value, bool)
            and contrast.ALPHA_LIMITS[0] <= value <= contrast.ALPHA_LIMITS[1]
        )
        if not ok:
            problems.append(f"opacity.{name} must be a number from 0.3 to 1.0, got {value!r}")
    if problems:
        raise PaletteFileError(path, problems)
    return Palette(
        colors={name: colors[name].lower() for name in COLORS},
        opacity={name: float(opacity[name]) for name in OPACITY},
        source="file",
    )
