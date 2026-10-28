"""Where rice keeps settings, approved profiles, drafts and desktop state.

Approved profiles are configuration (chezmoi tracks them). Drafts, reports,
backups and the current/previous setup are disposable state.
"""

from __future__ import annotations

import colorsys
import contextlib
import datetime
import fcntl
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import time
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

from . import contrast

SCHEMA = 1
LIB = Path(__file__).resolve().parent.parent
DEFAULT_SETTINGS = {
    "fonts": {"interface": "Geist", "monospace": "GeistMono Nerd Font"},
    "scheme": "m3-content",
    "wallpaper_dirs": ["~/.local/share/wallpapers"],
}
# Semantic ANSI hues keep red/yellow/green meaningful whatever the wallpaper.
SEMANTIC_ANSI = {"red": 355.0, "yellow": 45.0, "green": 135.0}
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif", ".avif", ".jxl"}


class RiceError(Exception):
    """A user-facing failure; the message says what to do next."""


def now() -> str:
    return datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds")


def _xdg(env: dict[str, str], name: str, fallback: str) -> Path:
    value = env.get(name)
    return Path(value) if value else Path(env["HOME"]) / fallback


@dataclass(frozen=True)
class Paths:
    home: Path
    config: Path
    state: Path
    cache: Path
    data: Path

    @classmethod
    def from_env(cls, env: dict[str, str] | None = None) -> Paths:
        env = dict(os.environ if env is None else env)
        return cls(
            home=Path(env["HOME"]),
            config=_xdg(env, "XDG_CONFIG_HOME", ".config"),
            state=_xdg(env, "XDG_STATE_HOME", ".local/state") / "rice",
            cache=_xdg(env, "XDG_CACHE_HOME", ".cache") / "rice",
            data=_xdg(env, "XDG_DATA_HOME", ".local/share"),
        )

    @property
    def profiles(self) -> Path:
        return self.config / "rice" / "profiles"

    @property
    def settings(self) -> Path:
        return self.config / "rice" / "settings.json"

    def draft_dir(self, sha: str) -> Path:
        return self.state / "drafts" / sha


def write_atomic(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.")
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
        os.replace(tmp, path)
    except BaseException:
        with contextlib.suppress(FileNotFoundError):
            os.unlink(tmp)
        raise


def write_json(path: Path, value: object) -> None:
    write_atomic(path, (json.dumps(value, indent=2, sort_keys=False) + "\n").encode())


def read_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text())
    except json.JSONDecodeError as error:
        raise RiceError(f"{path} is not valid JSON: {error}") from error
    if not isinstance(value, dict):
        raise RiceError(f"{path} must contain a JSON object")
    return value


@contextlib.contextmanager
def locked(paths: Paths, timeout: float = 60.0) -> Iterator[None]:
    """Serialise every command that changes profiles, drafts or the desktop."""
    paths.state.mkdir(parents=True, exist_ok=True)
    with open(paths.state / "lock", "w") as handle:
        deadline = time.monotonic() + timeout
        while True:
            try:
                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() > deadline:
                    raise RiceError("another rice command is still running") from None
                time.sleep(0.1)
        try:
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


def settings(paths: Paths) -> dict:
    merged = json.loads(json.dumps(DEFAULT_SETTINGS))
    if paths.settings.exists():
        stored = read_json(paths.settings)
        for key, value in stored.items():
            if isinstance(value, dict) and isinstance(merged.get(key), dict):
                merged[key].update(value)
            else:
                merged[key] = value
    return merged


def image_sha(image: Path) -> str:
    digest = hashlib.sha256()
    try:
        with open(image, "rb") as handle:
            for block in iter(lambda: handle.read(1 << 20), b""):
                digest.update(block)
    except OSError as error:
        raise RiceError(f"cannot read image {image}: {error.strerror}") from error
    return digest.hexdigest()


def resolve_image(value: str | Path) -> Path:
    image = Path(value).expanduser()
    if not image.is_file():
        raise RiceError(f"no such image: {image}")
    return image.resolve()


def run(argv: list[str], timeout: float = 60.0, **kwargs) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(argv, capture_output=True, text=True, check=False, timeout=timeout, **kwargs)
    except FileNotFoundError as error:
        raise RiceError(f"{argv[0]} is not installed") from error
    except subprocess.TimeoutExpired as error:
        raise RiceError(f"`{' '.join(argv[:3])}` did not finish within {timeout:g}s") from error


def run_offline(argv: list[str]) -> subprocess.CompletedProcess[str]:
    """Run a generator/renderer in a throwaway HOME.

    `noctalia theme` loads (and migrates in place) the user's Noctalia config even
    when it only renders files, so it must never see the real one.
    """
    with tempfile.TemporaryDirectory(prefix="rice-offline-") as tmp:
        env = {k: v for k, v in os.environ.items() if not k.startswith("XDG_") and k != "HOME"}
        env.update(
            HOME=tmp,
            XDG_CONFIG_HOME=f"{tmp}/config",
            XDG_STATE_HOME=f"{tmp}/state",
            XDG_CACHE_HOME=f"{tmp}/cache",
        )
        return run(argv, env=env, cwd=tmp)


def backdrop_bound(image: Path) -> contrast.Bound:
    """Exact per-channel min/max over every pixel of every frame.

    Blurring and cropping only mix wallpaper pixels, so whatever the compositor
    shows behind a translucent surface stays inside this box. Any transparency
    exposes an unknown fill, so such images get the black-white bound.
    """
    try:
        result = subprocess.run(
            ["magick", str(image), "-depth", "8", "rgba:-"],
            capture_output=True,
            check=False,
            timeout=120,
        )
    except FileNotFoundError as error:
        raise RiceError("ImageMagick (magick) is required to sample the wallpaper") from error
    except subprocess.TimeoutExpired as error:
        raise RiceError(f"ImageMagick took too long to read {image}") from error
    data = result.stdout
    if result.returncode != 0 or not data or len(data) % 4:
        raise RiceError(f"ImageMagick could not read {image}: {result.stderr.decode(errors='replace').strip()}")
    if min(data[3::4]) < 255:
        return contrast.BLACK_WHITE
    channels = [data[i::4] for i in range(3)]
    low = tuple(float(min(c)) for c in channels)
    high = tuple(float(max(c)) for c in channels)
    return (low, high)  # type: ignore[return-value]


def generator_version() -> str:
    result = run_offline(["noctalia", "--version"])
    return result.stdout.strip() or "unknown"


def generate(image: Path, scheme: str) -> dict[str, str]:
    """Run Noctalia's native palette generator (dark variant, flattened tokens)."""
    with tempfile.TemporaryDirectory(prefix="rice-gen-") as tmp:
        out = Path(tmp) / "tokens.json"
        result = run_offline(
            [
                "noctalia",
                "theme",
                str(image),
                "--scheme",
                scheme,
                "--dark",
                "-o",
                str(out),
            ]
        )
        if result.returncode != 0 or not out.exists():
            raise RiceError(f"noctalia theme failed for {image}: {(result.stderr or result.stdout).strip()}")
        tokens = json.loads(out.read_text())
    if not isinstance(tokens, dict) or "primary" not in tokens:
        raise RiceError("noctalia theme returned an unexpected token map")
    return {k: v.lower() for k, v in tokens.items()}


def _hls_hex(hue: float, lightness: float, saturation: float) -> str:
    r, g, b = colorsys.hls_to_rgb(hue / 360.0, lightness, saturation)
    return contrast.hex_of((r * 255.0, g * 255.0, b * 255.0))


def semantic_terminal(colors: dict[str, str]) -> None:
    """Generator ANSI colours follow the wallpaper; red/yellow/green must keep their meaning."""
    for name, hue in SEMANTIC_ANSI.items():
        colors[f"terminal_normal_{name}"] = _hls_hex(hue, 0.68, 0.62)
        colors[f"terminal_bright_{name}"] = _hls_hex(hue, 0.78, 0.70)


# ── Drafts ──────────────────────────────────────────────────────────────────


def draft_path(paths: Paths, sha: str) -> Path:
    return paths.draft_dir(sha) / "draft.json"


def load_draft(paths: Paths, sha: str) -> dict | None:
    path = draft_path(paths, sha)
    return read_json(path) if path.exists() else None


def create_draft(paths: Paths, image: Path, scheme: str | None, name: str | None) -> dict:
    sha = image_sha(image)
    scheme = scheme or settings(paths)["scheme"]
    tokens = generate(image, scheme)
    colors = dict(tokens)
    semantic_terminal(colors)
    alpha = dict(contrast.DEFAULT_ALPHA)
    bound = backdrop_bound(image)
    corrections = contrast.correct(colors, alpha, bound)
    profile = load_profile(paths, sha)
    draft = {
        "schema": SCHEMA,
        "sha256": sha,
        "image": str(image),
        "name": name or (profile["name"] if profile else image.stem.replace("-", " ").replace("_", " ").title()),
        "created": now(),
        "base_revision": profile["current"] if profile else None,
        "generator": {
            "tool": "noctalia",
            "version": generator_version(),
            "scheme": scheme,
            "mode": "dark",
        },
        "generated": tokens,
        "colors": colors,
        "alpha": alpha,
        "bound": [list(bound[0]), list(bound[1])],
        "corrections": corrections,
        "edits": {},
    }
    save_draft(paths, draft)
    return draft


def draft_from_profile(paths: Paths, profile: dict, image: Path) -> dict:
    """Edit an approved palette without regenerating it."""
    revision = current_revision(profile)
    draft = {key: json.loads(json.dumps(value)) for key, value in revision.items() if key != "revision"}
    draft.update(
        schema=SCHEMA,
        sha256=profile["sha256"],
        image=str(image),
        name=profile["name"],
        created=now(),
        base_revision=revision["revision"],
        corrections=[],
    )
    draft.pop("approved", None)
    save_draft(paths, draft)
    return draft


def save_draft(paths: Paths, draft: dict) -> None:
    contrast.validate_palette(draft["colors"], draft["alpha"], set(draft["generated"]))
    write_json(draft_path(paths, draft["sha256"]), draft)


def edit_draft(draft: dict, assignments: list[str]) -> None:
    for assignment in assignments:
        key, sep, value = assignment.partition("=")
        key, value = key.strip(), value.strip()
        if not sep or not key:
            raise RiceError(f"expected name=value, got {assignment!r}")
        if key.startswith("alpha."):
            name = key.removeprefix("alpha.")
            if name not in contrast.DEFAULT_ALPHA:
                raise RiceError(f"unknown alpha {name!r}; use one of {', '.join(contrast.DEFAULT_ALPHA)}")
            try:
                number = float(value)
            except ValueError:
                raise RiceError(f"{key} must be a number") from None
            draft["alpha"][name] = number
            draft["edits"][key] = number
        else:
            if key not in draft["colors"]:
                raise RiceError(f"unknown colour {key!r}; see the report for editable names")
            if not contrast.HEX.match(value.lower()):
                raise RiceError(f"{key} must be #rrggbb, got {value!r}")
            draft["colors"][key] = draft["edits"][key] = value.lower()
    contrast.validate_palette(draft["colors"], draft["alpha"], set(draft["generated"]))


def draft_bound(draft: dict) -> contrast.Bound:
    low, high = draft["bound"]
    return (tuple(low), tuple(high))  # type: ignore[return-value]


# ── Approved profiles ───────────────────────────────────────────────────────


def profile_path(paths: Paths, sha: str) -> Path:
    return paths.profiles / f"{sha}.json"


def load_profile(paths: Paths, sha: str) -> dict | None:
    path = profile_path(paths, sha)
    return read_json(path) if path.exists() else None


def current_revision(profile: dict) -> dict:
    for revision in profile["revisions"]:
        if revision["revision"] == profile["current"]:
            return revision
    raise RiceError(f"profile {profile['name']} has no revision {profile['current']}")


def approve(paths: Paths, draft: dict, name: str | None) -> dict:
    rows = contrast.evaluate(draft["colors"], draft["alpha"], draft_bound(draft))
    failed = contrast.failures(rows)
    if failed:
        listed = "; ".join(describe(row) for row in failed)
        raise RiceError(f"approval refused, {len(failed)} check(s) fail: {listed}")
    name = name or draft["name"]
    _check_name(paths, name, draft["sha256"])
    profile = load_profile(paths, draft["sha256"]) or {
        "schema": SCHEMA,
        "sha256": draft["sha256"],
        "name": name,
        "current": 0,
        "revisions": [],
    }
    number = max((r["revision"] for r in profile["revisions"]), default=0) + 1
    profile["revisions"].append(
        {
            "revision": number,
            "approved": now(),
            "source_name": Path(draft["image"]).name,
            "image": draft["image"],
            "generator": draft["generator"],
            "generated": draft["generated"],
            "colors": draft["colors"],
            "alpha": draft["alpha"],
            "bound": draft["bound"],
            "edits": draft["edits"],
        }
    )
    profile["name"] = name
    profile["current"] = number
    write_json(profile_path(paths, draft["sha256"]), profile)
    draft_path(paths, draft["sha256"]).unlink()
    return profile


def _check_name(paths: Paths, name: str, sha: str) -> None:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9 _.-]{0,47}", name):
        raise RiceError("profile names use letters, digits, spaces, '.', '_' or '-' (max 48)")
    for other in profiles(paths):
        if other["sha256"] != sha and other["name"].casefold() == name.casefold():
            raise RiceError(f"profile name {name!r} is already used by another wallpaper")


def profiles(paths: Paths) -> list[dict]:
    if not paths.profiles.is_dir():
        return []
    return [read_json(path) for path in sorted(paths.profiles.glob("*.json"))]


def profile_by_name(paths: Paths, name: str) -> dict:
    for profile in profiles(paths):
        if profile["name"].casefold() == name.casefold():
            return profile
    raise RiceError(f"no approved palette named {name!r}; see `rice list`")


def describe(row: dict) -> str:
    if row["kind"] == "hue":
        return f"{row['role']} (hue {row['hue']})"
    return f"{row['role']} {row['fg']}/{row['bg']} {row['ratio']}:1 < {row['minimum']}:1"


def wallpapers(paths: Paths) -> list[Path]:
    """Images in the configured wallpaper directories plus any with a profile or draft."""
    found: dict[Path, None] = {}
    for directory in settings(paths)["wallpaper_dirs"]:
        root = Path(directory).expanduser()
        if root.is_dir():
            for path in sorted(root.rglob("*")):
                if path.suffix.lower() in IMAGE_SUFFIXES and path.is_file():
                    found[path.resolve()] = None
    for draft_file in sorted((paths.state / "drafts").glob("*/draft.json")):
        image = Path(read_json(draft_file)["image"])
        if image.is_file():
            found[image] = None
    for profile in profiles(paths):
        image = Path(current_revision(profile).get("image", ""))
        if image.is_file():
            found[image.resolve()] = None
    state_file = paths.state / "state.json"
    if state_file.exists():
        for value in read_json(state_file).get("images", {}).values():
            image = Path(value)
            if image.is_file():
                found[image.resolve()] = None
    return list(found)


def remove_tree(path: Path) -> None:
    shutil.rmtree(path, ignore_errors=True)
