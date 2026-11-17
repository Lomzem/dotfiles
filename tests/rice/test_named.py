"""Exercise the named wallpaper workflow through the public CLI."""

import json
import shutil
import subprocess
import unittest
from pathlib import Path

from harness import Desktop, REPO


class NamedWallpapers(unittest.TestCase):
    def setUp(self) -> None:
        self.desktop = Desktop()
        self.addCleanup(self.desktop.close)
        directory = self.desktop.home / ".local/share/wallpapers"
        directory.mkdir(parents=True)
        self.image = directory / "mitsuha.jpeg"
        shutil.copyfile(REPO / "mitsuha.jpeg", self.image)
        self.palette_file = self.desktop.config / "rice/palettes/mitsuha.json"

    def test_overview_and_completion_find_wallpapers(self) -> None:
        self.assertIn("check NAME|PATH", self.desktop.rice().stdout)
        self.assertEqual(self.desktop.rice("complete", "wallpapers").stdout.splitlines(), ["mitsuha"])
        alias = self.image.with_name("alias.jpeg")
        alias.symlink_to(self.image)
        self.assertIn("alias", self.desktop.rice("list").stdout)
        report = self.desktop.json("check", "alias")
        self.assertEqual(report["image"], str(alias))
        self.assertEqual(Path(report["palette_file"]).stem, "alias")

    def test_duplicate_names_are_reported(self) -> None:
        other = self.desktop.image("mitsuha.png", (30, 40, 60))
        result = self.desktop.rice("check", other, check=False)
        self.assertEqual(result.returncode, 1)
        self.assertIn("rename one", result.stderr)
        self.assertIn(str(other), result.stderr)
        self.assertIn(str(self.image), result.stderr)

    def test_approved_profile_checks_with_local_opacity_and_renders_preview(self) -> None:
        profiles = self.desktop.config / "rice/profiles"
        profiles.mkdir(parents=True)
        profile = next((REPO / "dot_config/rice/profiles").glob("*.json"))
        approved = json.loads(profile.read_text())
        for revision in approved["revisions"]:
            revision["image"] = str(self.image)
        (profiles / profile.name.removeprefix("private_")).write_text(json.dumps(approved))
        report = self.desktop.json("check", "mitsuha")
        self.assertTrue(report["ok"], report["failures"])
        self.assertEqual(report["source"], "approved")
        self.assertEqual(report["palette"]["opacity"], {"panels": 0.82, "terminal": 0.82})
        self.assertEqual(Path(report["preview"]).read_bytes()[:8], b"\x89PNG\r\n\x1a\n")
        self.assertEqual(self.desktop.generator_runs(), 0)
        self.assertIsNone(self.desktop.json("status")["current"])

    def test_check_suggests_fixes_and_use_refuses_unreadable_palette(self) -> None:
        palette = self.desktop.json("check", "mitsuha")["palette"]
        palette["colors"]["on_surface"] = "#4a4a4a"
        self.palette_file.parent.mkdir(parents=True)
        self.palette_file.write_text(json.dumps(palette))

        report = json.loads(self.desktop.rice("check", "mitsuha", "--json", check=False).stdout)
        self.assertFalse(report["ok"])
        panel = next(row for row in report["failures"] if row["role"] == "text on panel")
        self.assertEqual(panel["opacity"], "panels")
        result = self.desktop.rice("use", "mitsuha", check=False)
        self.assertEqual(result.returncode, 1)
        self.assertFalse(any(" msg " in call for call in self.desktop.calls("noctalia")))
        self.assertIsNone(self.desktop.json("status")["current"])

        palette["colors"].update(panel["fix"].get("set", {}))
        palette["opacity"].update(panel["fix"].get("opacity", {}))
        self.palette_file.write_text(json.dumps(palette))
        report = json.loads(self.desktop.rice("check", "mitsuha", "--json", check=False).stdout)
        self.assertFalse(any(row["role"] == "text on panel" for row in report["failures"]))

    def test_edit_applies_palette_and_reapply_preserves_restore(self) -> None:
        self.desktop.env["VISUAL"] = "true"
        self.desktop.rice("edit", "mitsuha")
        self.assertEqual(self.desktop.json("status")["current"]["wallpaper"], str(self.image))
        palette = json.loads(self.palette_file.read_text())
        palette["opacity"]["terminal"] = 1
        self.palette_file.write_text(json.dumps(palette))
        self.desktop.rice("reapply")
        kitty = self.desktop.config / "kitty/rice-theme.conf"
        self.assertIn("background_opacity 1.0", kitty.read_text())
        self.desktop.rice("restore")
        self.assertFalse(kitty.exists())

    def test_editor_failure_removes_new_palette(self) -> None:
        self.desktop.env["VISUAL"] = "false"
        result = self.desktop.rice("edit", "mitsuha", check=False)
        self.assertEqual(result.returncode, 1)
        self.assertFalse(self.palette_file.exists())
        self.assertIsNone(self.desktop.json("status")["current"])

    def test_t3_theme_and_terminal_follow_rice_and_restore(self) -> None:
        userdata = self.desktop.home / ".t3/userdata"
        userdata.mkdir(parents=True)
        preferences = userdata / "settings.json"
        preferences.write_text('{"defaultTheme": "personal"}\n')
        theme = userdata / "themes/rice.json"
        image = theme.with_suffix(".jpg")
        ansi = self.desktop.home / ".local/share/rice/ansi-colors"
        report = self.desktop.json("check", "mitsuha")
        colors = report["palette"]["colors"]
        self.desktop.rice("use", "mitsuha")
        published = json.loads(theme.read_text())
        self.assertEqual(published["colors"]["messageForeground"], colors["on_surface"])
        self.assertIn("--theme-background-image", published["css"])
        self.assertEqual(image.read_bytes(), self.image.read_bytes())
        self.assertEqual(json.loads(preferences.read_text()), {"defaultTheme": "personal"})

        hook = REPO / "dot_config/zsh/rice-ansi.zsh"
        env = {**self.desktop.env, "TERM_PROGRAM": "t3code"}
        kitty = subprocess.run(
            ["zsh", "-fc", 'source "$1"', "rice-test", str(hook)],
            env={**env, "TERM_PROGRAM": "kitty"}, check=True, capture_output=True,
        )
        self.assertEqual(kitty.stdout, b"")
        command = [
            "zsh", "-fc",
            'source "$1"; source "$1"; '
            '[[ ${precmd_functions[(I)_rice_ansi_show]} == 1 ]] || exit 1; '
            'python3 "$2" restore >/dev/null || exit; _rice_ansi_show; _rice_ansi_show',
            "rice-test", str(hook), str(REPO / "dot_local/bin/executable_rice"),
        ]
        payload = ansi.read_bytes()
        self.assertIn(f"\x1b]4;1;{colors['terminal_normal_red']}\x1b\\".encode(), payload)
        self.assertEqual(payload.count(b"\x1b]4;"), 16)
        result = subprocess.run(command, env=env, check=True, capture_output=True)
        reset = b"\x1b]104;" + b";".join(str(n).encode() for n in range(16)) + b"\x1b\\"
        self.assertEqual(result.stdout, payload + reset)
        self.assertFalse(theme.exists())
        self.assertFalse(image.exists())
        self.assertFalse(ansi.exists())
