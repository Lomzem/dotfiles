"""rice: approved wallpaper palettes and fonts for the whole desktop."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from . import contrast, desktop, report, store
from .store import Paths, RiceError

NEEDS_REVIEW = 3


def _state(paths: Paths) -> dict:
    path = paths.state / "state.json"
    return store.read_json(path) if path.exists() else {}


def _public(setup: dict | None) -> dict | None:
    if not setup:
        return None
    return {k: v for k, v in setup.items() if k not in ("colors", "alpha")}


def _bound(setup_or_image: Path) -> contrast.Bound:
    return store.backdrop_bound(setup_or_image)


def _report(paths: Paths, palette: dict, status: str, bound: contrast.Bound | None = None) -> Path:
    rows = contrast.evaluate(palette["colors"], palette["alpha"], bound or store.draft_bound(palette))
    return report.write(paths.draft_dir(palette["sha256"]) / "report.html", palette, rows, status)


def _profile_setup(profile: dict, image: Path) -> dict:
    revision = store.current_revision(profile)
    return {
        "wallpaper": str(image),
        "sha256": profile["sha256"],
        "palette": {"name": profile["name"], "revision": revision["revision"]},
        "label": profile["name"],
        "colors": revision["colors"],
        "alpha": revision["alpha"],
        "preview": False,
    }


def _notify(summary: str, body: str) -> None:
    try:
        subprocess.run(
            ["notify-send", "-a", "rice", summary, body],
            capture_output=True,
            check=False,
            timeout=5,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass


def _ensure_draft(paths: Paths, image: Path) -> tuple[dict, Path, bool]:
    sha = store.image_sha(image)
    draft = store.load_draft(paths, sha)
    created = draft is None
    if draft is None:
        draft = store.create_draft(paths, image, None, None)
    return draft, _report(paths, draft, "draft, not approved"), created


def _validated_for(palette: dict, image: Path) -> None:
    """A palette may only be shown over a wallpaper it stays readable on."""
    rows = contrast.evaluate(palette["colors"], palette["alpha"], _bound(image))
    failed = contrast.failures(rows)
    if failed:
        raise RiceError(
            f"palette is not readable over {image.name}: "
            + "; ".join(store.describe(row) for row in failed)
            + ". Approve a palette for this wallpaper instead (rice select)."
        )


# ── Commands ────────────────────────────────────────────────────────────────


def cmd_draft(paths: Paths, args: argparse.Namespace) -> int:
    image = store.resolve_image(args.image)
    sha = store.image_sha(image)
    existing = store.load_draft(paths, sha)
    profile = store.load_profile(paths, sha)
    if existing and not args.regenerate:
        draft = existing
        print(f"Existing draft kept (use --regenerate for a new one): {draft['name']}")
    elif profile and not args.regenerate:
        draft = store.draft_from_profile(paths, profile, image)
        print(f"Draft created from approved {profile['name']} r{profile['current']} (no regeneration)")
    else:
        draft = store.create_draft(paths, image, args.scheme, args.name)
        print(f"Draft generated with {draft['generator']['version']} scheme {draft['generator']['scheme']}")
        if profile:
            print(f"Approved {profile['name']} r{profile['current']} stays active until you approve this draft")
    if args.name:
        draft["name"] = args.name
        store.save_draft(paths, draft)
    print(f"Report: {_report(paths, draft, 'draft, not approved')}")
    return 0


def _require_draft(paths: Paths, image: Path) -> dict:
    draft = store.load_draft(paths, store.image_sha(image))
    if draft is None:
        raise RiceError(f"no draft for {image}; run `rice draft {image}` first")
    draft["image"] = str(image)
    draft["bound"] = [list(c) for c in store.backdrop_bound(image)]
    return draft


def cmd_set(paths: Paths, args: argparse.Namespace) -> int:
    image = store.resolve_image(args.image)
    sha = store.image_sha(image)
    draft = store.load_draft(paths, sha)
    if draft is None:
        profile = store.load_profile(paths, sha)
        if profile is None:
            raise RiceError(f"no draft or approved palette for {image}; run `rice draft {image}` first")
        draft = store.draft_from_profile(paths, profile, image)
    store.edit_draft(draft, args.assignments)
    store.save_draft(paths, draft)
    rows = contrast.evaluate(draft["colors"], draft["alpha"], store.draft_bound(draft))
    failed = contrast.failures(rows)
    print(f"{len(failed)} of {len(rows)} checks fail")
    for row in failed:
        print(f"  {store.describe(row)}")
    print(f"Report: {_report(paths, draft, 'draft, not approved')}")
    return 0


def cmd_report(paths: Paths, args: argparse.Namespace) -> int:
    image = store.resolve_image(args.image)
    sha = store.image_sha(image)
    draft = store.load_draft(paths, sha)
    if draft is not None:
        palette, status = draft, "draft, not approved"
    else:
        profile = store.load_profile(paths, sha)
        if profile is None:
            raise RiceError(f"nothing to report for {image}; run `rice draft {image}`")
        revision = store.current_revision(profile)
        palette = {
            **revision,
            "name": profile["name"],
            "sha256": sha,
            "image": str(image),
        }
        status = f"approved r{revision['revision']}"
    rows = contrast.evaluate(palette["colors"], palette["alpha"], store.draft_bound(palette))
    path = report.write(paths.draft_dir(sha) / "report.html", palette, rows, status)
    if args.json:
        print(
            json.dumps(
                {
                    "status": status,
                    "report": str(path),
                    "coverage": contrast.COVERAGE,
                    "checks": rows,
                }
            )
        )
    else:
        print(f"{len(contrast.failures(rows))} of {len(rows)} checks fail. Report: {path}")
    return 0


def cmd_approve(paths: Paths, args: argparse.Namespace) -> int:
    image = store.resolve_image(args.image)
    draft = _require_draft(paths, image)
    profile = store.approve(paths, draft, args.name)
    print(f"Approved {profile['name']} r{profile['current']} -> {store.profile_path(paths, profile['sha256'])}")
    if args.apply:
        return _apply(paths, _profile_setup(profile, image))
    return 0


def _apply(paths: Paths, setup: dict) -> int:
    for note in desktop.apply(paths, setup, _state(paths)):
        print(f"  {note}")
    print(f"Applied {setup['label']}{' (preview)' if setup.get('preview') else ''} with {setup['wallpaper']}")
    return 0


def cmd_select(paths: Paths, args: argparse.Namespace) -> int:
    image = store.resolve_image(args.image)
    profile = store.load_profile(paths, store.image_sha(image))
    if profile is not None:
        return _apply(paths, _profile_setup(profile, image))
    draft, path, created = _ensure_draft(paths, image)
    verb = "Drafted" if created else "Draft awaiting review for"
    message = f"{verb} {draft['name']}; nothing applied. Review {path}, then `rice preview` or `rice approve`."
    print(message)
    _notify("rice: new wallpaper needs approval", message)
    return NEEDS_REVIEW


def cmd_preview(paths: Paths, args: argparse.Namespace) -> int:
    image = store.resolve_image(args.image)
    draft = _require_draft(paths, image)
    setup = {
        "wallpaper": str(image),
        "sha256": draft["sha256"],
        "palette": {"draft": draft["sha256"], "name": draft["name"]},
        "label": f"{draft['name']} draft",
        "colors": draft["colors"],
        "alpha": draft["alpha"],
        "preview": True,
    }
    code = _apply(paths, setup)
    print("Undo with `rice restore`.")
    return code


def cmd_restore(paths: Paths, args: argparse.Namespace) -> int:
    for note in desktop.restore(paths, _state(paths)):
        print(note)
    return 0


def cmd_wallpaper(paths: Paths, args: argparse.Namespace) -> int:
    image = store.resolve_image(args.image)
    current = _state(paths).get("current")
    if not current:
        raise RiceError("no palette is active yet; use `rice select` first")
    _validated_for(current, image)
    return _apply(paths, {**current, "wallpaper": str(image), "sha256": store.image_sha(image)})


def cmd_palette(paths: Paths, args: argparse.Namespace) -> int:
    current = _state(paths).get("current")
    if not current:
        raise RiceError("no wallpaper is active yet; use `rice select` first")
    profile = store.profile_by_name(paths, args.name)
    setup = _profile_setup(profile, Path(current["wallpaper"]))
    setup["sha256"] = current["sha256"]
    _validated_for(setup, Path(current["wallpaper"]))
    return _apply(paths, setup)


def cmd_reapply(paths: Paths, args: argparse.Namespace) -> int:
    current = _state(paths).get("current")
    if not current:
        raise RiceError("nothing applied yet; use `rice select`")
    state = _state(paths)
    for note in desktop.apply(paths, current, state):
        print(f"  {note}")
    # Re-rendering is not a new setup: keep the previous one restorable.
    store.write_json(paths.state / "state.json", state)
    print(f"Re-rendered {current['label']}")
    return 0


def cmd_darkreader(paths: Paths, args: argparse.Namespace) -> int:
    """Merge the active palette into an export; the extension imports the result."""
    source = Path(args.export).expanduser().resolve()
    target = Path(args.output).expanduser().resolve()
    if source == target or target.exists():
        raise RiceError("choose a new output file; the original Dark Reader export is kept")
    patch_path = paths.data / "rice/userstyles/darkreader.patch.json"
    if not patch_path.is_file():
        raise RiceError("run `rice reapply` before merging Dark Reader settings")
    try:
        exported = store.read_json(source)
        patch = store.read_json(patch_path)
    except OSError as error:
        raise RiceError(f"cannot read Dark Reader settings: {error.strerror}") from error
    if not isinstance(exported.get("theme"), dict) or not isinstance(exported.get("disabledFor"), list):
        raise RiceError("expected a full JSON export from Dark Reader Settings > Advanced")
    if not all(isinstance(site, str) for site in exported["disabledFor"]):
        raise RiceError("Dark Reader disabledFor must contain site names")
    exported["theme"].update(patch["theme"])
    exported["disabledFor"] = list(dict.fromkeys(exported["disabledFor"] + patch["disabledFor"]))
    for key in ("changeBrowserTheme", "detectDarkTheme"):
        exported[key] = patch[key]
    store.write_json(target, exported)
    print(f"Import in Dark Reader Settings > Advanced: {target}")
    return 0


def cmd_fonts(paths: Paths, args: argparse.Namespace) -> int:
    fonts = store.settings(paths)["fonts"]
    if args.pick:
        raw = store.run(["fc-list", ":", "family"])
        families = sorted(
            {
                part.strip()
                for line in raw.stdout.splitlines()
                for part in line.split(",")
                if desktop.FONT_NAME.fullmatch(part.strip())
            }
        )
        choices = []
        for title in ("Interface font", "Monospace font"):
            picked = store.run(["fuzzel", "--dmenu", "--prompt", title + ": "], input="\n".join(families))
            if picked.returncode:
                print("Font selection cancelled; nothing changed.")
                return 0
            choices.append(picked.stdout.strip())
        args.interface, args.monospace = choices
    if not args.interface and not args.monospace:
        print(json.dumps(fonts) if args.json else f"interface: {fonts['interface']}\nmonospace: {fonts['monospace']}")
        return 0
    families = desktop.installed_families()
    stored = store.read_json(paths.settings) if paths.settings.exists() else {}
    new_fonts = dict(stored.get("fonts", {}))
    if args.interface:
        new_fonts["interface"] = desktop.check_font(args.interface, families)
    if args.monospace:
        new_fonts["monospace"] = desktop.check_font(args.monospace, families)
    original = paths.settings.read_bytes() if paths.settings.exists() else None
    stored["fonts"] = new_fonts
    store.write_json(paths.settings, stored)
    current = _state(paths).get("current")
    if not current:
        print("Fonts saved; they apply with the next `rice select`.")
        return 0
    try:
        state = _state(paths)
        for note in desktop.apply(paths, current, state):
            print(f"  {note}")
        store.write_json(paths.state / "state.json", state)
    except RiceError:
        if original is None:
            paths.settings.unlink(missing_ok=True)
        else:
            store.write_atomic(paths.settings, original)
        raise
    merged = store.settings(paths)["fonts"]
    print(f"Fonts: interface {merged['interface']}, monospace {merged['monospace']}")
    print("Already-open Chromium/Electron windows (Helium, T3, Vesktop) pick up fonts when reopened.")
    return 0


def cmd_status(paths: Paths, args: argparse.Namespace) -> int:
    state = _state(paths)
    data = {
        "current": _public(state.get("current")),
        "previous": _public(state.get("previous")),
        "fonts": store.settings(paths)["fonts"],
    }
    if args.json:
        print(json.dumps(data))
        return 0
    current = data["current"]
    if not current:
        print("Nothing applied yet.")
    else:
        palette = current["palette"]
        kind = f"r{palette['revision']}" if "revision" in palette else "draft preview"
        print(f"Palette: {palette['name']} ({kind})\nWallpaper: {current['wallpaper']}")
    print(f"Fonts: {data['fonts']['interface']} / {data['fonts']['monospace']}")
    return 0


def _thumbnail(paths: Paths, image: Path, sha: str) -> str | None:
    thumb = paths.cache / "thumbs" / f"{sha}.jpg"
    if not thumb.exists():
        thumb.parent.mkdir(parents=True, exist_ok=True)
        result = store.run(
            [
                "magick",
                str(image) + "[0]",
                "-thumbnail",
                "384x216^",
                "-gravity",
                "center",
                "-extent",
                "384x216",
                str(thumb),
            ]
        )
        if result.returncode != 0:
            return None
    return str(thumb)


def cmd_list(paths: Paths, args: argparse.Namespace) -> int:
    current = _state(paths).get("current") or {}
    items = []
    for image in store.wallpapers(paths):
        sha = store.image_sha(image)
        profile = store.load_profile(paths, sha)
        draft = store.load_draft(paths, sha)
        items.append(
            {
                "path": str(image),
                "name": profile["name"] if profile else (draft["name"] if draft else image.stem),
                "status": "approved" if profile else ("draft" if draft else "new"),
                "draft": draft is not None,
                "current": current.get("sha256") == sha,
                "report": str(paths.draft_dir(sha) / "report.html") if draft else None,
                "thumbnail": _thumbnail(paths, image, sha) if args.thumbnails else None,
            }
        )
    named = [{"name": p["name"], "revision": p["current"], "sha256": p["sha256"]} for p in store.profiles(paths)]
    if args.json:
        print(json.dumps({"wallpapers": items, "palettes": named}))
        return 0
    for item in items:
        marker = "*" if item["current"] else " "
        print(f"{marker} {item['status']:<8} {item['name']:<24} {item['path']}")
    print("Approved palettes: " + (", ".join(p["name"] for p in named) or "none"))
    return 0


def cmd_hook(paths: Paths, args: argparse.Namespace) -> int:
    """Noctalia `wallpaper_changed` hook: route the stock picker through approval."""
    chosen = os.environ.get("NOCTALIA_WALLPAPER_PATH", "")
    if not chosen or not Path(chosen).is_file():
        return 0
    image = Path(chosen).resolve()
    current = _state(paths).get("current")
    if current and Path(current["wallpaper"]) == image:
        return 0
    profile = store.load_profile(paths, store.image_sha(image))
    if profile is not None:
        return _apply(paths, _profile_setup(profile, image))
    draft, path, _ = _ensure_draft(paths, image)
    if current:
        subprocess.run(
            ["noctalia", "msg", "wallpaper-set", current["wallpaper"]],
            capture_output=True,
            check=False,
        )
    message = f"{draft['name']} has no approved palette yet, so the wallpaper was put back. Review {path}."
    _notify("rice: wallpaper needs approval", message)
    print(message)
    return NEEDS_REVIEW


# ── Entry ───────────────────────────────────────────────────────────────────

LOCKED = {
    "draft",
    "set",
    "approve",
    "select",
    "preview",
    "restore",
    "wallpaper",
    "palette",
    "reapply",
    "fonts",
    "hook",
    "report",
}


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="rice", description=__doc__)
    sub = root.add_subparsers(dest="command", required=True, metavar="COMMAND")

    def command(name: str, handler, help: str) -> argparse.ArgumentParser:
        p = sub.add_parser(name, help=help, description=help)
        p.set_defaults(handler=handler)
        return p

    p = command("draft", cmd_draft, "Create or show a draft palette for an image")
    p.add_argument("image")
    p.add_argument(
        "--regenerate",
        action="store_true",
        help="run the generator again (approved palette is kept)",
    )
    p.add_argument("--scheme", help="Noctalia scheme, e.g. m3-content, m3-tonal-spot, vibrant")
    p.add_argument("--name")
    p = command("set", cmd_set, "Edit named colours or alpha in a draft")
    p.add_argument("image")
    p.add_argument("assignments", nargs="+", metavar="NAME=VALUE")
    p = command("report", cmd_report, "Write the swatch and contrast report")
    p.add_argument("image")
    p.add_argument("--json", action="store_true")
    p = command("approve", cmd_approve, "Approve a draft as a new immutable revision")
    p.add_argument("image")
    p.add_argument("--name")
    p.add_argument("--apply", action="store_true", help="apply it right away")
    p = command("select", cmd_select, "Apply an approved wallpaper, or draft an unknown one")
    p.add_argument("image")
    p = command("preview", cmd_preview, "Apply a draft temporarily (undo with restore)")
    p.add_argument("image")
    command("restore", cmd_restore, "Go back to the previous setup")
    p = command("wallpaper", cmd_wallpaper, "Change only the wallpaper, keeping the palette")
    p.add_argument("image")
    p = command(
        "palette",
        cmd_palette,
        "Apply a named approved palette to the current wallpaper",
    )
    p.add_argument("name")
    command("reapply", cmd_reapply, "Re-render the current setup (after editing templates)")
    p = command("darkreader", cmd_darkreader, "Merge the active palette into a Dark Reader settings export")
    p.add_argument("export", help="JSON exported from Dark Reader Settings > Advanced")
    p.add_argument("--output", required=True, help="new JSON file to import; existing files are never overwritten")
    p = command(
        "fonts",
        cmd_fonts,
        "Show or change the interface and monospace fonts everywhere",
    )
    p.add_argument("--pick", action="store_true", help="choose both fonts graphically with Fuzzel")
    p.add_argument("--interface", metavar="FAMILY")
    p.add_argument("--monospace", metavar="FAMILY")
    p.add_argument("--json", action="store_true")
    p = command("status", cmd_status, "Show the current setup")
    p.add_argument("--json", action="store_true")
    p = command("list", cmd_list, "List wallpapers and approved palettes")
    p.add_argument("--json", action="store_true")
    p.add_argument("--thumbnails", action="store_true", help="also create thumbnails")
    p = command("hook", cmd_hook, "Noctalia hook entry point")
    p.add_argument("event", choices=["wallpaper-changed"])
    return root


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    paths = Paths.from_env()
    try:
        if args.command in LOCKED:
            with store.locked(paths):
                return args.handler(paths, args)
        return args.handler(paths, args)
    except (RiceError, contrast.PaletteError) as error:
        print(f"rice: {error}", file=sys.stderr)
        return 1
