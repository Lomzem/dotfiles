"""The check, edit and use workflow for wallpaper names and paths."""

from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
from pathlib import Path

from . import contrast, desktop, palette, preview, store
from .palette import PaletteFileError
from .store import Paths, RiceError


def _tilde(path: Path | str) -> str:
    text, home = str(path), str(Path.home())
    return "~" + text[len(home) :] if text == home or text.startswith(home + "/") else text


def _describe(row: dict) -> str:
    if row["kind"] == "hue":
        family = contrast.SEMANTIC_ROLES[row["fg"]]
        low, high = contrast.SEMANTIC_HUES[family]
        return f"{row['role']}: hue is {row['hue']}, needs {low:g}-{high:g}"
    where = " over the wallpaper" if row.get("alpha") else ""
    return f"{row['role']}: {row['fg']} on {row['bg']}{where} is {row['ratio']}:1, needs {row['minimum']:g}:1"


def _failure(row: dict, colors: dict[str, str], alpha: dict[str, float], bound: contrast.Bound) -> dict:
    public = dict(row)
    surface = public.pop("alpha", None)
    if surface:
        public["opacity"] = "panels" if surface == "panel" else surface
    return {**public, "message": _describe(row), "fix": contrast.suggest(row, colors, alpha, bound)}


def _check_report(paths: Paths, name: str, image: Path) -> dict:
    report: dict = {"wallpaper": name, "image": str(image), "palette_file": str(palette.file_path(paths, name))}
    bound = store.backdrop_bound(image)
    try:
        chosen = palette.load(paths, name, image, bound)
    except PaletteFileError as error:
        return {
            **report,
            "ok": False,
            "source": "file",
            "problems": error.problems,
            "failures": [],
            "names": palette.COLORS,
            "opacity_names": palette.OPACITY,
            "palette": None,
            "preview": None,
        }
    rows = contrast.evaluate(chosen.colors, chosen.alpha, bound)
    failed = [
        _failure(row, chosen.colors, chosen.alpha, bound)
        for row in contrast.failures(rows)
    ]
    return {
        **report,
        "ok": not failed,
        "source": chosen.source,
        "problems": [],
        "failures": failed,
        "checked": len(rows),
        "coverage": contrast.COVERAGE,
        "corrections": chosen.corrections or [],
        "names": palette.COLORS,
        "opacity_names": palette.OPACITY,
        "palette": {"colors": chosen.colors, "opacity": chosen.opacity},
        "preview": str(preview.render(paths, name, image, chosen)),
    }


def _fix_text(fix: dict) -> str:
    changes = {**fix.get("set", {}), **{f"opacity.{k}": v for k, v in fix.get("opacity", {}).items()}}
    if not changes:
        return str(fix["result"])
    result = fix["result"]
    measured = f"{result}:1" if isinstance(result, float) else result
    return ", ".join(f"{key} -> {value}" for key, value in changes.items()) + f" ({measured})"


def _show_check(paths: Paths, name: str, image: Path) -> bool:
    report = _check_report(paths, name, image)
    file = _tilde(report["palette_file"])
    source = f"palette file {file}" if report["source"] == "file" else report["source"] + " palette"
    print(f"{name}: {source}")
    if report["problems"]:
        print("✗ The palette file cannot be checked:")
        for problem in report["problems"]:
            print(f"  {problem}")
        print(f"`rice check {name} --json` lists every allowed name and what it controls.")
        return False
    if report["ok"]:
        print(f"✓ All {report['checked']} checks pass.")
    else:
        print(f"✗ {len(report['failures'])} of {report['checked']} checks fail:")
        for row in report["failures"]:
            print(f"  {row['message']}")
            print(f"    fix: {_fix_text(row['fix'])}")
    print(f"Preview: {_tilde(report['preview'])}")
    return report["ok"]


def cmd_check(paths: Paths, args: argparse.Namespace) -> int:
    name, image = store.named_wallpaper(paths, args.wallpaper)
    if args.json:
        report = _check_report(paths, name, image)
        print(json.dumps(report, indent=2))
        return 0 if report["ok"] else 1
    ok = _show_check(paths, name, image)
    if not ok:
        print(f"Run `rice edit {name}` to apply the fixes.")
    elif not palette.file_path(paths, name).exists():
        print(f"Run `rice edit {name}` to start a palette file from it.")
    return 0 if ok else 1


def setup(paths: Paths, name: str, image: Path) -> dict:
    sha = store.image_sha(image)
    chosen = palette.load(paths, name, image, store.backdrop_bound(image))
    reference = {"name": name, "source": chosen.source}
    if chosen.revision is not None:
        reference["revision"] = chosen.revision
    return {
        "wallpaper": str(image),
        "sha256": sha,
        "palette": reference,
        "label": name,
        "colors": chosen.colors,
        "alpha": chosen.alpha,
        "preview": False,
    }


def _use(paths: Paths, name: str, image: Path) -> None:
    try:
        selected = setup(paths, name, image)
        state = store.state(paths)
        notes = desktop.apply(paths, selected, state, preserve_previous=selected == state.get("current"))
    except RiceError as error:
        raise RiceError(f"{error}\nRun `rice check {shlex.quote(name)}` to inspect the palette.") from error
    print(f"Applied {name} ({selected['palette']['source']} palette)")
    for note in notes:
        print(f"  {note}")


def cmd_use(paths: Paths, args: argparse.Namespace) -> int:
    _use(paths, *store.named_wallpaper(paths, args.wallpaper))
    return 0


def _edit(path: Path) -> None:
    try:
        editor = shlex.split(os.environ.get("VISUAL") or os.environ.get("EDITOR") or "vi")
    except ValueError as error:
        raise RiceError(f"invalid VISUAL or EDITOR: {error}") from error
    if not editor:
        raise RiceError("set VISUAL or EDITOR to an editor command")
    try:
        result = subprocess.run([*editor, str(path)], check=False)
    except OSError as error:
        raise RiceError(f"cannot start the editor {editor[0]}; set VISUAL or EDITOR") from error
    if result.returncode:
        raise RiceError(f"the editor exited with status {result.returncode}; nothing applied")


def _again() -> bool:
    if not sys.stdin.isatty():
        return False
    try:
        answer = input("Edit again? [Y/n] ")
    except EOFError:
        return False
    return answer.strip().lower() in ("", "y", "yes")


def cmd_edit(paths: Paths, args: argparse.Namespace) -> int:
    name, image = store.named_wallpaper(paths, args.wallpaper)
    path = palette.file_path(paths, name)
    drafted = not (path.exists() or path.is_symlink())
    if drafted:
        starting = palette.load(paths, name, image, store.backdrop_bound(image))
        store.write_json(path, {"colors": starting.colors, "opacity": starting.opacity})
        print(f"Started {_tilde(path)} from the {starting.source} palette.")
    try:
        _edit(path)
    except RiceError:
        if drafted:
            path.unlink(missing_ok=True)
        raise
    while not _show_check(paths, name, image):
        if not _again():
            print(f"Kept {_tilde(path)}; nothing applied. Run `rice edit {name}` to continue.")
            return 1
        _edit(path)
    _use(paths, name, image)
    return 0
