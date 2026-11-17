from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from . import contrast, store
from .palette import ANSI, COLORS, Palette
from .store import Paths, RiceError

WIDTH, HEIGHT, STRIP = 1280, 560, 48


def _font(family: str) -> str:
    result = store.run(["fc-match", "-f", "%{file}", family])
    return result.stdout.strip() if result.returncode == 0 and result.stdout.strip() else family


def _rgba(value: str, alpha: float) -> str:
    r, g, b = contrast.rgb(value)
    return f"rgba({r},{g},{b},{alpha:.3f})"


class _Canvas:
    def __init__(self, colors: dict[str, str]) -> None:
        self.colors = colors
        self.argv: list[str] = []

    def box(self, fill: str, x0: int, y0: int, x1: int, y1: int, radius: int = 12) -> None:
        self.argv += ["-fill", fill, "-draw", f"roundrectangle {x0},{y0} {x1},{y1} {radius},{radius}"]

    def text(self, font: str, size: int, color: str, x: int, y: int, words: str) -> None:
        self.argv += ["-font", font, "-pointsize", str(size), "-fill", self.colors[color]]
        self.argv += ["-annotate", f"+{x}+{y}", words.replace("%", "%%")]


def render(paths: Paths, name: str, image: Path, palette: Palette) -> Path:
    colors, opacity = palette.colors, palette.opacity
    fonts = store.settings(paths)["fonts"]
    sans, mono = _font(fonts["interface"]), _font(fonts["monospace"])
    c = _Canvas(colors)

    c.box(_rgba(colors["surface"], opacity["panels"]), 32, 32, 620, 528, 18)
    c.text(sans, 30, "on_surface", 64, 88, "Panel text")
    c.text(sans, 20, "on_surface_variant", 64, 124, "Muted text on the panel")
    c.text(sans, 20, "primary", 64, 158, "Accent and match text")
    c.text(sans, 20, "error", 380, 158, "Error")
    c.box(colors["surface_container"], 56, 184, 596, 268)
    c.text(sans, 20, "on_surface", 80, 220, "Text on a card")
    c.text(sans, 16, "on_surface_variant", 80, 248, "Muted text on a card")
    c.box(colors["primary"], 452, 206, 572, 246, 20)
    c.text(sans, 18, "on_primary", 474, 233, "Selected")
    for row, (bg, fg, label) in enumerate(
        (
            ("primary_container", "on_primary_container", "Tinted selection"),
            ("secondary_container", "on_secondary_container", "Chip / toggle"),
            ("hover", "on_hover", "Hovered row"),
            ("tertiary_container", "on_tertiary_container", "Warning"),
        )
    ):
        y = 288 + row * 56
        c.box(colors[bg], 56, y, 596, y + 44, 10)
        c.text(sans, 18, fg, 80, y + 29, label)
    for col, (bg, fg) in enumerate((("secondary", "on_secondary"), ("tertiary", "on_tertiary"), ("error", "on_error"))):
        x = 360 + col * 80
        c.box(colors[bg], x, 60, x + 70, 90, 8)
        c.text(sans, 12, fg, x + 5, 80, bg.capitalize())

    c.box(_rgba(colors["terminal_background"], opacity["terminal"]), 652, 32, 1248, 528, 18)
    c.text(mono, 18, "terminal_foreground", 680, 76, f"~ $ rice check {name}")
    c.text(mono, 18, "terminal_bright_black", 680, 106, "# comments use bright black")
    for row, tone in enumerate(("normal", "bright")):
        for col, color in enumerate(ANSI[1:]):
            c.text(mono, 16, f"terminal_{tone}_{color}", 680 + col * 78, 146 + row * 30, color)
    c.text(mono, 18, "terminal_normal_red", 680, 226, "- removed line")
    c.text(mono, 18, "terminal_normal_green", 680, 256, "+ added line")
    c.text(mono, 18, "terminal_normal_yellow", 680, 286, "~ changed line")
    c.box(colors["terminal_selection_bg"], 676, 306, 940, 336, 4)
    c.text(mono, 18, "terminal_selection_fg", 680, 328, "selected text")
    c.text(mono, 18, "terminal_foreground", 680, 366, "cursor here")
    c.box(colors["terminal_cursor"], 806, 348, 818, 372, 1)
    c.text(mono, 18, "terminal_cursor_text", 807, 366, "e")
    c.box(colors["outline"], 680, 400, 1220, 402, 0)
    c.box(colors["outline_variant"], 680, 420, 1220, 422, 0)

    width = WIDTH / len(COLORS)
    for index, color in enumerate(COLORS):
        x0 = round(index * width)
        c.argv += ["-fill", colors[color], "-draw", f"rectangle {x0},{HEIGHT} {round(x0 + width)},{HEIGHT + STRIP}"]

    out = paths.cache / "check" / f"{name}.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix="rice-preview-", dir=out.parent) as tmp:
        staged = Path(tmp) / "preview.png"
        result = store.run(
            [
                "magick",
                f"{image}[0]",
                "-resize",
                f"{WIDTH}x{HEIGHT}^",
                "-gravity",
                "center",
                "-extent",
                f"{WIDTH}x{HEIGHT}",
                "-gravity",
                "northwest",
                "-background",
                "black",
                "-extent",
                f"{WIDTH}x{HEIGHT + STRIP}",
                "+gravity",
                *c.argv,
                str(staged),
            ],
            timeout=120,
        )
        if result.returncode != 0:
            raise RiceError(f"ImageMagick could not draw the preview: {result.stderr.strip()}")
        staged.replace(out)
    return out
