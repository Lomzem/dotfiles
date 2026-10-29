"""Seam: `rice select` -> the installed Television config rendered by real `tv` in Kitty's palette."""

import fcntl
import os
import re
import select
import shutil
import struct
import subprocess
import termios
import time
import unittest
from pathlib import Path

from harness import REPO, Desktop

ROWS, COLS = 20, 100
SGR_FG = {**{30 + n: n for n in range(8)}, **{90 + n: 8 + n for n in range(8)}}
SGR_BG = {**{40 + n: n for n in range(8)}, **{100 + n: 8 + n for n in range(8)}}


def kitty_palette(conf: Path) -> dict[str, str]:
    pairs = re.findall(r"^(color\d+|foreground|background)\s+(#[0-9a-f]{6})$", conf.read_text(), re.M | re.I)
    return dict(pairs)


def wcag(a: str, b: str) -> float:
    def lum(colour: str) -> float:
        c = [int(colour[i : i + 2], 16) / 255 for i in (1, 3, 5)]
        r, g, b = (x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    high, low = sorted((lum(a), lum(b)), reverse=True)
    return (high + 0.05) / (low + 0.05)


def screen(output: str, palette: dict[str, str]) -> dict[tuple[int, int], tuple[str, str, str]]:
    """Cells (row, col) -> (char, fg, bg) for the absolute-positioned SGR stream ratatui writes."""
    cells: dict[tuple[int, int], tuple[str, str, str]] = {}
    row = col = 0
    fg, bg = palette["foreground"], palette["background"]
    for m in re.finditer(r"\x1b\[([0-9;?]*)([A-Za-z])|\x1b[^\[]|([^\x1b\r\n])", output):
        if m[3] is not None:
            cells[(row, col)] = (m[3], fg, bg)
            col += 1
        elif m[2] == "H":
            pos = [int(x or 1) for x in (m[1] or "1;1").split(";")] + [1]
            row, col = pos[0] - 1, pos[1] - 1
        elif m[2] == "m":
            codes = [int(x or 0) for x in (m[1] or "0").split(";")]
            i = 0
            while i < len(codes):
                code = codes[i]
                if code in (0, 39):
                    fg = palette["foreground"]
                if code in (0, 49):
                    bg = palette["background"]
                if code in SGR_FG:
                    fg = palette[f"color{SGR_FG[code]}"]
                if code in SGR_BG:
                    bg = palette[f"color{SGR_BG[code]}"]
                if code in (38, 48):
                    if codes[i + 1] == 5:
                        colour, i = palette[f"color{codes[i + 2]}"], i + 2
                    else:
                        colour, i = "#{:02x}{:02x}{:02x}".format(*codes[i + 2 : i + 5]), i + 4
                    fg, bg = (colour, bg) if code == 38 else (fg, colour)
                i += 1
    return cells


@unittest.skipUnless(shutil.which("tv"), "Television is not installed")
class Television(unittest.TestCase):
    def setUp(self) -> None:
        desk = self.desktop = Desktop()
        self.addCleanup(desk.close)
        night = desk.image("night.png", (20, 24, 60))
        desk.rice("draft", night)
        desk.rice("approve", night, "--name", "Night")
        desk.rice("select", night)
        installed = desk.config / "television/config.toml"
        installed.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(REPO / "dot_config/television/config.toml", installed)

    def render(self) -> str:
        """Run the installed config in a pseudo-terminal until the first frame settles."""
        leader, follower = os.openpty()
        fcntl.ioctl(follower, termios.TIOCSWINSZ, struct.pack("HHHH", ROWS, COLS, 0, 0))
        env = {**self.desktop.env, "PATH": os.environ["PATH"], "TERM": "xterm-256color"}
        argv = ["tv", "--source-command", "printf 'alpha\\nbeta\\n'", "--no-sort", "--no-remote"]
        proc = subprocess.Popen(argv, stdin=follower, stdout=follower, stderr=follower, env=env, start_new_session=True)
        os.close(follower)
        output, deadline = b"", time.monotonic() + 3
        try:
            while time.monotonic() < deadline:
                if select.select([leader], [], [], 0.1)[0]:
                    try:
                        output += os.read(leader, 65536)
                    except OSError:
                        break
        finally:
            proc.kill()
            proc.wait()
            os.close(leader)
        return output.decode("utf-8", "replace")

    def test_selected_result_is_readable_in_the_rice_terminal_palette(self) -> None:
        palette = kitty_palette(self.desktop.config / "kitty/rice-theme.conf")
        cells = screen(self.render(), palette)
        lines = {r: "".join(cells.get((r, c), " ")[0] for c in range(COLS)) for r in range(ROWS)}
        row = next((r for r, text in lines.items() if "alpha" in text), None)
        self.assertIsNotNone(row, f"tv did not render the results:\n" + "\n".join(lines.values()))
        start = lines[row].index("alpha")
        for col in range(start, start + len("alpha")):
            _, fg, bg = cells[(row, col)]
            self.assertGreaterEqual(wcag(fg, bg), 4.5, f"selected text {fg} on {bg}")


if __name__ == "__main__":
    unittest.main()
