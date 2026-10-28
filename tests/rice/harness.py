"""Run the public `rice` command against a disposable HOME.

Only process boundaries are faked: desktop IPC (noctalia msg, niri, pkill,
gsettings, notify-send). Palette generation still runs the real
`noctalia theme`, and image sampling still runs the real ImageMagick.
"""

import json
import shutil
import struct
import subprocess
import tempfile
import zlib
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RICE = REPO / "dot_local" / "bin" / "executable_rice"
REAL_NOCTALIA = shutil.which("noctalia") or "/usr/bin/noctalia"

FAKE_TOOL = """#!/bin/sh
printf '%s\\n' "$(basename "$0") $*" >> "$RICE_TEST_LOG"
{body}
"""

FAKES = {
    # Generation is real; only desktop IPC is recorded.
    "noctalia": """case "$1" in theme|--version) exec {real} "$@";; esac
case "$2" in
 wallpaper-get) if [ -f "$RICE_TEST_WALLPAPER" ]; then cat "$RICE_TEST_WALLPAPER"; fi;;
 wallpaper-set) printf '%s' "$3" > "$RICE_TEST_WALLPAPER";;
esac
exit 0""",
    "niri": "exit 0",
    "pkill": "exit 0",
    "notify-send": "exit 0",
    "gsettings": 'if [ "$1" = get ]; then echo "\'Rubik 11\'"; fi\nexit 0',
}


def png(
    path: Path,
    rgb: tuple[int, int, int],
    size: tuple[int, int] = (64, 36),
    spot: tuple[int, int, tuple[int, int, int]] | None = None,
) -> Path:
    """Write a solid-colour PNG with the standard library, optionally with one odd pixel at (x, y)."""
    width, height = size
    rows = [bytearray(bytes(rgb) * width) for _ in range(height)]
    if spot:
        x, y, colour = spot
        rows[y][x * 3 : x * 3 + 3] = bytes(colour)
    raw = b"".join(b"\x00" + bytes(row) for row in rows)

    def chunk(kind: bytes, data: bytes) -> bytes:
        body = kind + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body))

    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b"")
    )
    return path


class Desktop:
    """A temporary HOME with XDG directories and fake desktop IPC."""

    def __init__(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="rice-test-")
        self.root = Path(self._tmp.name)
        self.home = self.root / "home"
        self.config = self.home / ".config"
        self.state = self.home / ".local" / "state"
        self.log = self.root / "calls.log"
        bin_dir = self.root / "bin"
        for directory in (self.config, self.state, bin_dir):
            directory.mkdir(parents=True)
        self.log.touch()
        for name, body in FAKES.items():
            tool = bin_dir / name
            tool.write_text(FAKE_TOOL.format(body=body.format(real=REAL_NOCTALIA)))
            tool.chmod(0o755)
        self.env = {
            "HOME": str(self.home),
            "XDG_CONFIG_HOME": str(self.config),
            "XDG_STATE_HOME": str(self.state),
            "XDG_CACHE_HOME": str(self.home / ".cache"),
            "XDG_DATA_HOME": str(self.home / ".local" / "share"),
            "PATH": f"{bin_dir}:/usr/bin:/bin",
            "RICE_TEST_LOG": str(self.log),
            "RICE_TEST_WALLPAPER": str(self.root / "wallpaper"),
            "LANG": "C.UTF-8",
            "DBUS_SESSION_BUS_ADDRESS": "unix:path=/nonexistent",
        }

    def close(self) -> None:
        self._tmp.cleanup()

    def image(self, name: str, rgb: tuple[int, int, int], **kwargs) -> Path:
        return png(self.home / "Pictures" / name, rgb, **kwargs)

    def rice(self, *args: str | Path, check: bool = True) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            ["python3", "-I", str(RICE), *map(str, args)],
            check=False,
            env=self.env,
            capture_output=True,
            text=True,
            timeout=120,
        )
        if check and result.returncode != 0:
            raise AssertionError(
                f"rice {' '.join(map(str, args))} exited {result.returncode}\n"
                f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
            )
        return result

    def json(self, *args: str | Path) -> dict:
        return json.loads(self.rice(*args, "--json").stdout)

    def calls(self, tool: str) -> list[str]:
        return [line for line in self.log.read_text().splitlines() if line.split(" ", 1)[0] == tool]

    def generator_runs(self) -> int:
        """Palette generations: `noctalia theme <image>` without --theme-json."""
        return sum(
            1 for line in self.calls("noctalia") if line.startswith("noctalia theme") and "--theme-json" not in line
        )
