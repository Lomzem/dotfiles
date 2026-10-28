"""Render a setup (wallpaper + palette + fonts) into every app and apply it atomically.

A setup is applied as one transaction: render everything into a staging
directory, preflight it, then replace each target file. If any write or setting
fails, every file and setting already changed is put back and the recorded
setup stays as it was. Live reloads happen only after a successful commit and
never restart an application.
"""

from __future__ import annotations

import base64
import configparser
import contextlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

import tomllib

from . import contrast, store
from .store import Paths, RiceError

TEMPLATES = store.LIB / "templates"
NOCTALIA_PALETTE = "Rice"
T3_THEME_ID = "rice"
PLACEHOLDER = re.compile(r"@@([a-z_]+)\.([a-z_]+)@@")
FONT_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9 ._+-]{0,63}")

# Keys rice owns in Noctalia's config. The Settings UI writes its own copy into
# ~/.local/state/noctalia/settings.toml, which would override rice.toml. `None`
# means every key in that table.
NOCTALIA_OWNED: dict[str, set[str] | None] = {
    "theme": None,
    "theme.templates": None,
    "shell": {"font_family", "settings_window_translucent"},
    "shell.panel": {"transparency_mode"},
    "bar.default": {"font_family", "radius", "margin_edge", "background_opacity"},
    "notification": {"background_opacity"},
    "osd": {"background_opacity"},
    "hooks": {"wallpaper_changed"},
}
KEY = re.compile(r"\s*([A-Za-z0-9_-]+)\s*=(.*)")
HEADER_PART = re.compile(r"""\s*(?:([A-Za-z0-9_-]+)|"((?:[^"\\]|\\.)*)"|'([^']*)')\s*""")


@dataclass
class Output:
    target: Path
    data: bytes | None
    mode: int = 0o600
    link: str | None = None


@dataclass
class Setting:
    """A non-file setting changed in the same transaction (with its undo)."""

    describe: str
    apply: Callable[[], None]
    undo: Callable[[], None]


@dataclass
class Plan:
    outputs: list[Output] = field(default_factory=list)
    settings: list[Setting] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


def template_targets(paths: Paths) -> list[tuple[str, Path]]:
    """Template file -> rendered target. Each entry is one app adapter."""
    c, d = paths.config, paths.data
    return [
        ("kitty.conf", c / "kitty/rice-theme.conf"),
        ("noctalia.toml", c / "noctalia/rice.toml"),
        ("niri.kdl", c / "niri/rice.kdl"),
        ("fuzzel.ini", c / "fuzzel/rice.ini"),
        ("zathura", c / "zathura/rice"),
        ("gtk3.css", c / "gtk-3.0/rice.css"),
        ("gtk4.css", c / "gtk-4.0/rice.css"),
        ("qt6ct-colors.conf", c / "qt6ct/colors/rice.conf"),
        ("qt6ct.conf", c / "qt6ct/qt6ct.conf"),
        ("yazi.toml", c / "yazi/flavors/rice.yazi/flavor.toml"),
        ("nvim.lua", c / "nvim/colors/rice.lua"),
        ("vesktop.css", c / "vesktop/themes/rice.theme.css"),
        ("fontconfig.conf", c / "fontconfig/conf.d/60-rice-fonts.conf"),
        ("helium.json", d / "rice/helium-theme/manifest.json"),
        ("helium-fonts.json", d / "rice/helium-fonts/fonts.json"),
        ("web-github.css", d / "rice/userstyles/github.user.css"),
        ("web-google.css", d / "rice/userstyles/google.user.css"),
        ("web-duckduckgo.css", d / "rice/userstyles/duckduckgo.user.css"),
        ("web-youtube.css", d / "rice/userstyles/youtube.user.css"),
        ("darkreader.json", d / "rice/userstyles/darkreader.patch.json"),
    ]


# ── Fonts ───────────────────────────────────────────────────────────────────


def installed_families() -> set[str]:
    result = store.run(["fc-list", ":", "family"])
    if result.returncode != 0:
        raise RiceError("fc-list failed; is fontconfig installed?")
    names: set[str] = set()
    for line in result.stdout.splitlines():
        names.update(part.strip().casefold() for part in line.split(","))
    return names


def check_font(name: str, families: set[str]) -> str:
    name = name.strip()
    if not FONT_NAME.fullmatch(name):
        raise RiceError(f"font name {name!r} has unsupported characters (letters, digits, space, . _ + -)")
    if name.casefold() not in families:
        raise RiceError(f"font {name!r} is not installed (fontconfig cannot find it); install it with decman first")
    return name


def font_settings(paths: Paths, fonts: dict[str, str]) -> list[Setting]:
    """Font preferences that live outside rendered files."""
    found = []
    gsettings = shutil.which("gsettings")
    if gsettings:
        for key, family in (
            ("font-name", fonts["interface"]),
            ("monospace-font-name", fonts["monospace"]),
        ):
            found.extend(_gsetting(gsettings, key, family))
    return found


def _gsetting(gsettings: str, key: str, family: str) -> list[Setting]:
    schema = "org.gnome.desktop.interface"
    current = store.run([gsettings, "get", schema, key])
    if current.returncode != 0:
        return []
    old = current.stdout.strip().strip("'")
    size = old.rsplit(" ", 1)[-1] if old.rsplit(" ", 1)[-1].replace(".", "", 1).isdigit() else "11"
    new = f"{family} {size}"
    if old == new:
        return []

    def put(value: str) -> Callable[[], None]:
        def apply() -> None:
            if store.run([gsettings, "set", schema, key, value]).returncode != 0:
                raise RiceError(f"gsettings could not set {key}")

        return apply

    return [Setting(f"GTK {key} = {new}", put(new), put(old))]


def _t3_fonts(path: Path, fonts: dict[str, str]) -> list[Output]:
    """Patch family choices only; preserve app sizes and unrelated client settings."""
    original = path.read_bytes()
    try:
        data = json.loads(original)
    except json.JSONDecodeError:
        return []
    wanted = {
        "fontFamilySans": fonts["interface"],
        "fontFamilyComposer": fonts["interface"],
        "fontFamilyCode": fonts["monospace"],
        "fontFamilyTerminal": fonts["monospace"],
    }
    if not isinstance(data, dict) or all(data.get(k) == v for k, v in wanted.items()):
        return []
    data.update(wanted)
    patched = (json.dumps(data, indent=2) + "\n").encode()
    return [Output(path, patched)]


# ── Rendering ───────────────────────────────────────────────────────────────


def _substitute(text: str, values: dict[str, dict[str, str]], source: str) -> str:
    def replace(match: re.Match[str]) -> str:
        group, key = match.groups()
        try:
            return values[group][key]
        except KeyError:
            raise RiceError(f"template {source} uses unknown placeholder {match.group(0)}") from None

    return PLACEHOLDER.sub(replace, text)


def _panel_mode(setup: dict) -> str:
    colors = setup["colors"]
    bound = store.backdrop_bound(Path(setup["wallpaper"]))
    roles = (
        "on_surface",
        "on_surface_variant",
        "primary",
        "secondary",
        "tertiary",
        "error",
    )
    # Noctalia v5 preset constants: floating glass=.55, glass cards=.65;
    # floating soft=.80, cards=.88. Foregrounds remain opaque.
    for mode, panel_alpha, card_alpha in (
        ("glass", 0.55, 0.65),
        ("soft", 0.80, 0.88),
        ("solid", 1.0, 1.0),
    ):
        if all(
            contrast.worst_ratio(contrast.rgb(colors[fg]), contrast.rgb(colors[bg]), alpha, bound) >= 4.5
            for bg, alpha in (
                ("surface", panel_alpha),
                ("surface_container", card_alpha),
            )
            for fg in roles
        ):
            return mode
    return "solid"


def _placeholders(paths: Paths, setup: dict, fonts: dict[str, str]) -> dict[str, dict[str, str]]:
    alpha = setup["alpha"]
    return {
        "path": {"config": str(paths.config), "home": str(paths.home)},
        "font": dict(fonts),
        "shell": {"mode": _panel_mode(setup)},
        "alpha": {k: f"{v:.2f}" for k, v in alpha.items()},
        "alpha_hex": {k: f"{round(v * 255):02x}" for k, v in alpha.items()},
        "alpha_pct": {k: str(round(v * 100)) for k, v in alpha.items()},
    }


def _render_templates(paths: Paths, setup: dict, fonts: dict[str, str], staging: Path) -> list[Output]:
    """Fonts and alpha are substituted first; Noctalia's template engine renders colours."""
    targets = [(name, target) for name, target in template_targets(paths) if (TEMPLATES / name).exists()]
    if not targets:
        return []
    values = _placeholders(paths, setup, fonts)
    tokens = staging / "tokens.json"
    tokens.write_text(json.dumps({"dark": setup["colors"], "light": setup["colors"]}))
    argv = ["noctalia", "theme", "--theme-json", str(tokens), "--default-mode", "dark"]
    rendered = []
    for index, (name, target) in enumerate(targets):
        source = staging / f"in-{index}"
        out = staging / f"out-{index}"
        source.write_text(_substitute((TEMPLATES / name).read_text(), values, name))
        argv += ["-r", f"{source}:{out}"]
        rendered.append((out, target))
    result = store.run_offline(argv)
    if result.returncode != 0:
        raise RiceError(f"noctalia template rendering failed: {(result.stderr or result.stdout).strip()}")
    outputs = []
    for out, target in rendered:
        if not out.exists():
            raise RiceError(f"noctalia did not render {target}")
        data = out.read_bytes()
        if target == paths.config / "qt6ct/qt6ct.conf" and target.is_file():
            data = _qt_preferences(target, data)
        outputs.append(Output(target, data))
    return outputs


class _QtConfig(configparser.ConfigParser):
    def optionxform(self, optionstr: str) -> str:
        return optionstr


def _qt_preferences(target: Path, rendered: bytes) -> bytes:
    """Merge the palette and font families without resetting QFont sizes or app settings."""

    def parse(text: str) -> configparser.ConfigParser:
        parser = _QtConfig(interpolation=None)
        parser.read_string(text)
        return parser

    try:
        original = target.read_text()
        existing, desired = parse(original), parse(rendered.decode())
    except (OSError, UnicodeError, configparser.Error) as error:
        raise RiceError(f"cannot safely merge Qt preferences at {target}: {error}") from error
    for section in ("Appearance", "Fonts"):
        if section not in existing:
            existing.add_section(section)
    for key in ("color_scheme_path", "custom_palette"):
        existing["Appearance"][key] = desired["Appearance"][key]
    for key in ("general", "fixed"):
        before = existing["Fonts"].get(key)
        replacement = desired["Fonts"][key]
        if before and "," in before:
            quote = '"' if before.startswith('"') and before.endswith('"') else ""
            value = before[1:-1] if quote else before
            family = replacement.strip('"').split(",", 1)[0]
            replacement = quote + family + "," + value.split(",", 1)[1] + quote
        existing["Fonts"][key] = replacement
    owned = {
        "Appearance": {key: existing["Appearance"][key] for key in ("color_scheme_path", "custom_palette")},
        "Fonts": {key: existing["Fonts"][key] for key in ("general", "fixed")},
    }
    # Preserve comments, formatting and every unowned line. This also makes a
    # second application byte-stable when its values have not changed.
    section, result = "", []

    def flush() -> None:
        values = owned.pop(section, {})
        if values and result and not result[-1].endswith("\n"):
            result.append("\n")
        for key, value in values.items():
            result.append(f"{key}={value}\n")

    for line in original.splitlines(keepends=True):
        header = re.fullmatch(r"\s*\[([^\]]+)\]\s*(?:[#;].*)?", line.rstrip("\n"))
        if header:
            flush()
            section = header.group(1)
        key = KEY.fullmatch(line.rstrip("\n")) if not header else None
        if key and key.group(1) in owned.get(section, {}):
            value = owned[section].pop(key.group(1))
            if key.group(2).strip() != value:
                line = f"{key.group(1)}={value}\n"
        result.append(line)
    flush()
    for section, values in owned.items():
        if values:
            result.append(f"\n[{section}]\n")
            result.extend(f"{key}={value}\n" for key, value in values.items())
    return "".join(result).encode()


def _noctalia_palette(colors: dict[str, str]) -> bytes:
    roles = {
        "mPrimary": "primary",
        "mOnPrimary": "on_primary",
        "mSecondary": "secondary",
        "mOnSecondary": "on_secondary",
        "mTertiary": "tertiary",
        "mOnTertiary": "on_tertiary",
        "mError": "error",
        "mOnError": "on_error",
        "mSurface": "surface",
        "mOnSurface": "on_surface",
        "mSurfaceVariant": "surface_container",
        "mOnSurfaceVariant": "on_surface_variant",
        "mOutline": "outline_variant",
        "mShadow": "shadow",
        "mHover": "hover",
        "mOnHover": "on_hover",
    }
    names = ("black", "red", "green", "yellow", "blue", "magenta", "cyan", "white")
    dark: dict[str, object] = {role: colors[token] for role, token in roles.items()}
    dark["terminal"] = {
        "background": colors["terminal_background"],
        "foreground": colors["terminal_foreground"],
        "cursor": colors["terminal_cursor"],
        "cursorText": colors["terminal_cursor_text"],
        "selectionBg": colors["terminal_selection_bg"],
        "selectionFg": colors["terminal_selection_fg"],
        "normal": {n: colors[f"terminal_normal_{n}"] for n in names},
        "bright": {n: colors[f"terminal_bright_{n}"] for n in names},
    }
    return (json.dumps({"dark": dark}, indent=2) + "\n").encode()


def _header(line: str) -> tuple[str, bool] | None:
    """`[a.b]` / `[[a.b]]` with bare, quoted or spaced parts -> ("a.b", is_array).

    Anything else (including continuation lines of a multi-line array) is None;
    `_strip_owned` re-parses its result, so a missed header cannot go unnoticed.
    """
    stripped = line.strip()
    array = stripped.startswith("[[")
    if not stripped.startswith("["):
        return None
    rest, parts = stripped[2 if array else 1 :], []
    while True:
        part = HEADER_PART.match(rest)
        if not part or not part.group(0).strip():
            return None
        bare, double, single = part.groups()
        parts.append(json.loads(f'"{double}"') if double is not None else bare if bare is not None else single)
        rest = rest[part.end() :]
        if not rest.startswith("."):
            break
        rest = rest[1:]
    close = "]]" if array else "]"
    tail = rest[len(close) :].strip()
    if not rest.startswith(close) or (tail and not tail.startswith("#")):
        return None
    return ".".join(parts), array


def _strip_owned(text: str) -> str:
    """Drop the single-line keys rice owns from a Noctalia settings.toml, keeping the rest.

    Every `[table]` and `[[array.table]]` header changes scope; array tables are
    never owned. The result is re-parsed and must equal the original minus rice's
    keys, otherwise nothing is changed and the user is asked to edit by hand.
    """
    owned_here: set[str] | None = set()
    table, kept = "", []
    for line in text.splitlines(keepends=True):
        header = _header(line)
        if header:
            table, array = header
            owned_here = set() if array or table not in NOCTALIA_OWNED else NOCTALIA_OWNED[table]
        key = None if header else KEY.fullmatch(line.rstrip("\n"))
        if key and (owned_here is None or key.group(1) in owned_here):
            value = key.group(2)
            if value.count("[") != value.count("]") or value.strip().startswith(('"""', "'''")):
                raise RiceError(f"cannot safely remove multi-line {table}.{key.group(1)} from Noctalia settings")
            continue
        kept.append(line)
    result = "".join(kept)
    if _without_owned(tomllib.loads(text)) != tomllib.loads(result):
        raise RiceError(
            "Noctalia settings.toml uses a layout rice cannot edit safely; "
            f"remove the keys rice owns ({', '.join(NOCTALIA_OWNED)}) from it by hand"
        )
    return result


def _without_owned(data: dict) -> dict:
    """`data` minus rice's keys; nested tables and arrays of tables are never owned."""
    data = json.loads(json.dumps(data))
    for name, owned in NOCTALIA_OWNED.items():
        section: object = data
        for part in name.split("."):
            section = section.get(part) if isinstance(section, dict) else None
        if not isinstance(section, dict):
            continue
        for key, value in list(section.items()):
            table = isinstance(value, dict) or (
                isinstance(value, list) and value and all(isinstance(v, dict) for v in value)
            )
            if (owned is None and not table) or (owned is not None and key in owned):
                del section[key]
    return data


def _noctalia_settings(paths: Paths) -> list[Output]:
    path = paths.state.parent / "noctalia/settings.toml"
    if not path.is_file():
        return []
    try:
        text = path.read_text()
        stripped = _strip_owned(text)
    except (UnicodeDecodeError, tomllib.TOMLDecodeError) as error:
        raise RiceError(f"cannot read {path}: {error}") from error
    return [] if stripped == text else [Output(path, stripped.encode())]


def _t3_theme(setup: dict) -> bytes:
    colors = setup["colors"]
    theme = {
        "version": 1,
        "name": f"Rice {setup['label']}"[:48],
        "appearance": "dark",
        "canvas": colors["surface"],
        "accent": colors["primary"],
    }
    return (json.dumps(theme, indent=2) + "\n").encode()


def plan(paths: Paths, setup: dict) -> Plan:
    fonts = store.settings(paths)["fonts"]
    result = Plan()
    with tempfile.TemporaryDirectory(prefix="rice-render-") as tmp:
        result.outputs = _render_templates(paths, setup, fonts, Path(tmp))
    result.outputs += [
        Output(
            paths.config / f"noctalia/palettes/{NOCTALIA_PALETTE}.json",
            _noctalia_palette(setup["colors"]),
        ),
        *_noctalia_settings(paths),
        Output(paths.home / f".t3/userdata/themes/{T3_THEME_ID}.json", _t3_theme(setup)),
    ]
    t3 = paths.home / ".t3/userdata/client-settings.json"
    if t3.is_file():
        result.outputs.extend(_t3_fonts(t3, fonts))
    vesktop = paths.config / "vesktop/settings/settings.json"
    if vesktop.is_file():
        data = store.read_json(vesktop)
        enabled = data.get("enabledThemes", [])
        if not isinstance(enabled, list) or any(not isinstance(item, str) for item in enabled):
            raise RiceError("Vesktop enabledThemes must be a list of theme filenames")
        if "rice.theme.css" not in enabled:
            data["enabledThemes"] = [*enabled, "rice.theme.css"]
            result.outputs.append(Output(vesktop, (json.dumps(data, indent=2) + "\n").encode()))
    result.settings = font_settings(paths, fonts)
    return result


# ── Transaction ─────────────────────────────────────────────────────────────


def _preflight(paths: Paths, outputs: list[Output]) -> None:
    for output in outputs:
        if output.data is None:
            continue
        if output.target.suffix == ".toml":
            try:
                tomllib.loads(output.data.decode())
            except (UnicodeDecodeError, tomllib.TOMLDecodeError) as error:
                raise RiceError(f"rendered {output.target} is not valid TOML: {error}") from error
        if output.target.suffix == ".json":
            try:
                json.loads(output.data)
            except json.JSONDecodeError as error:
                raise RiceError(f"rendered {output.target} is not valid JSON: {error}") from error
    niri_config = paths.config / "niri/config.kdl"
    if not niri_config.is_file() or not shutil.which("niri"):
        return
    niri_dir = niri_config.parent
    with tempfile.TemporaryDirectory(prefix="rice-niri-") as tmp:
        staged = Path(tmp)
        for item in niri_dir.glob("*.kdl"):
            shutil.copy(item, staged / item.name)
        for output in outputs:
            if output.target.parent == niri_dir:
                (staged / output.target.name).write_bytes(output.data or b"")
        result = store.run(["niri", "validate", "-c", str(staged / "config.kdl")])
        if result.returncode != 0:
            raise RiceError(f"niri rejected the new config: {(result.stderr or result.stdout).strip()}")


def _capture(path: Path) -> dict:
    if path.is_symlink():
        return {"path": str(path), "link": os.readlink(path)}
    if not path.exists():
        return {"path": str(path), "data": None}
    if not path.is_file():
        raise RiceError(f"{path} is not a regular file; move it away and retry")
    return {
        "path": str(path),
        "data": base64.b64encode(path.read_bytes()).decode(),
        "mode": path.stat().st_mode & 0o777,
    }


def _output(saved: dict) -> Output:
    data = saved.get("data")
    return Output(
        Path(saved["path"]),
        base64.b64decode(data) if data is not None else None,
        saved.get("mode", 0o600),
        saved.get("link"),
    )


def _write(output: Output) -> None:
    path = output.target
    if output.link is not None:
        path.unlink(missing_ok=True)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.symlink_to(output.link)
    elif output.data is None:
        path.unlink(missing_ok=True)
    else:
        store.write_atomic(path, output.data)
        path.chmod(output.mode)


def commit(paths: Paths, work: Plan, finish: Callable[[], None], recover: Callable[[], None]) -> None:
    """Commit files, preferences and required IPC together; undo all on failure."""
    _preflight(paths, work.outputs)
    try:
        backups = [_output(_capture(out.target)) for out in work.outputs]
    except RiceError as error:
        raise RiceError(f"apply preflight failed, previous setup kept: {error}") from error
    applied: list[Output] = []
    settings: list[Setting] = []
    try:
        for output, before in zip(work.outputs, backups):
            applied.append(before)
            _write(output)
        for setting in work.settings:
            settings.append(setting)
            setting.apply()
        finish()
    except BaseException as error:
        problems = []
        for setting in reversed(settings):
            try:
                setting.undo()
            except (OSError, RiceError, subprocess.SubprocessError) as undo_error:
                problems.append(str(undo_error))
        for before in reversed(applied):
            try:
                _write(before)
            except OSError as undo_error:
                problems.append(str(undo_error))
        try:
            recover()
        except RiceError as undo_error:
            problems.append(str(undo_error))
        if problems:
            raise RiceError(f"apply failed ({error}); recovery incomplete: {'; '.join(problems)}") from error
        if isinstance(error, (RiceError, OSError)):
            raise RiceError(f"apply failed, previous setup kept: {error}") from error
        raise


def _noctalia(args: list[str]) -> str:
    result = store.run(["noctalia", "msg", *args], timeout=10)
    if result.returncode:
        raise RiceError(f"Noctalia {' '.join(args[:1])} failed: {(result.stderr or result.stdout).strip()}")
    return result.stdout.strip()


def _kitty_reload() -> None:
    with contextlib.suppress(FileNotFoundError, subprocess.TimeoutExpired):
        subprocess.run(
            ["pkill", "-USR1", "-x", "kitty"],
            capture_output=True,
            check=False,
            timeout=5,
        )


def _reload(wallpaper: str | None) -> None:
    # Load new fonts/palette before wallpaper-set persists the shell's in-memory settings.
    _noctalia(["config-reload"])
    if wallpaper:
        _noctalia(["wallpaper-set", wallpaper])
    _noctalia(["config-reload"])
    _kitty_reload()


def _snapshot(paths: Paths, work: Plan, wallpaper: str) -> dict:
    preferences = {}
    if shutil.which("gsettings"):
        for key in ("font-name", "monospace-font-name"):
            result = store.run(["gsettings", "get", "org.gnome.desktop.interface", key])
            if result.returncode == 0:
                preferences[key] = result.stdout.strip().strip("'")
    saved = {
        "files": [_capture(o.target) for o in work.outputs],
        "gsettings": preferences,
    }
    path = paths.state / "backups" / (uuid.uuid4().hex + ".json")
    store.write_json(path, saved)
    return {
        "snapshot": str(path),
        "wallpaper": wallpaper,
        "label": "Desktop before rice",
        "palette": {"name": "Original desktop"},
        "preview": False,
    }


def restore(paths: Paths, state: dict) -> list[str]:
    previous = state.get("previous")
    if not previous:
        raise RiceError("there is no previous setup to restore")
    if "snapshot" not in previous:
        return apply(paths, previous, state)
    saved = store.read_json(Path(previous["snapshot"]))
    work = Plan(outputs=[_output(item) for item in saved["files"]])
    for key, value in saved["gsettings"].items():
        # _gsetting preserves sizes; pass the full saved value via an exact setter.
        current = store.run(["gsettings", "get", "org.gnome.desktop.interface", key]).stdout.strip().strip("'")

        def setter(v: str, k: str = key) -> None:
            result = store.run(["gsettings", "set", "org.gnome.desktop.interface", k, v])
            if result.returncode:
                raise RiceError(f"could not restore GTK {k}")

        work.settings.append(
            Setting(
                f"restore {key}",
                lambda v=value, put=setter: put(v),
                lambda v=current, put=setter: put(v),
            )
        )
    live = _noctalia(["wallpaper-get"])

    def finish() -> None:
        _reload(previous.get("wallpaper"))
        store.write_json(
            paths.state / "state.json",
            {**state, "current": None, "previous": state.get("current")},
        )

    commit(paths, work, finish, lambda: _reload(live))
    return ["Restored the desktop captured before the first rice preview/application."]


def apply(paths: Paths, setup: dict, state: dict) -> list[str]:
    """Apply one setup transactionally; repeated previews retain their original undo."""
    contrast.validate_palette(setup["colors"], setup["alpha"], set())
    rows = contrast.evaluate(setup["colors"], setup["alpha"], store.backdrop_bound(Path(setup["wallpaper"])))
    failed = contrast.failures(rows)
    if failed:
        raise RiceError("application refused: " + "; ".join(store.describe(row) for row in failed))
    live = _noctalia(["wallpaper-get"])
    work = plan(paths, setup)
    old = state.get("current")
    previous = state.get("previous") if old and old.get("preview") else old
    if not old and state.get("previous", {}) and "snapshot" in state["previous"]:
        previous = state["previous"]
    if not previous:
        previous = _snapshot(paths, work, live)

    if "snapshot" in previous:
        snapshot_path = Path(previous["snapshot"])
        saved = store.read_json(snapshot_path)
        captured = {item["path"] for item in saved["files"]}
        # Newly enabled adapters must remain reversible during a preview session.
        saved["files"].extend(_capture(out.target) for out in work.outputs if str(out.target) not in captured)
        store.write_json(snapshot_path, saved)

    def finish() -> None:
        _reload(setup["wallpaper"])
        images = {**state.get("images", {}), setup["sha256"]: setup["wallpaper"]}
        store.write_json(
            paths.state / "state.json", {**state, "current": setup, "previous": previous, "images": images}
        )

    commit(paths, work, finish, lambda: _reload(live or (old or {}).get("wallpaper")))
    return [setting.describe for setting in work.settings] + [
        "Kitty, Noctalia and Niri: reloaded",
        "Neovim: generated colors reload in sessions using rice",
        "Fuzzel, Zathura, Yazi, GTK and Qt: next launch; T3 font preferences: reopen app",
        "Helium: generated theme and font bridge load on next launch; Vesktop: Rice theme enabled",
    ]
