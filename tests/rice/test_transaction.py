"""Seam: preview -> apply -> restore, and a failed apply keeps the previous setup."""

import configparser
import json
import unittest
from pathlib import Path

import tomllib
from harness import FAKE_TOOL, FAKES, REAL_NOCTALIA, Desktop


class Transactions(unittest.TestCase):
    def setUp(self) -> None:
        desk = self.desktop = Desktop()
        self.addCleanup(desk.close)
        self.night = desk.image("night.png", (20, 24, 60))
        self.dusk = desk.image("dusk.png", (90, 40, 30))
        for image, name in ((self.night, "Night"), (self.dusk, "Dusk")):
            desk.rice("draft", image)
            desk.rice("approve", image, "--name", name)
        desk.rice("select", self.night)
        self.applied = self.files()

    def files(self) -> dict[Path, bytes]:
        home = self.desktop.home
        roots = (home / ".config", home / ".t3", home / ".local/share/rice")
        return {p: p.read_bytes() for root in roots if root.exists() for p in sorted(root.rglob("*")) if p.is_file()}

    def current(self) -> dict:
        return self.desktop.json("status")["current"]

    def test_preview_then_restore_returns_byte_identical_setup(self) -> None:
        desk = self.desktop
        desk.rice("draft", self.dusk, "--regenerate")
        desk.rice("set", self.dusk, "primary=#f0abfc")

        desk.rice("preview", self.dusk)
        self.assertNotEqual(self.files(), self.applied)
        self.assertTrue(self.current()["preview"])
        self.assertEqual(self.current()["wallpaper"], str(self.dusk))

        desk.rice("restore")
        self.assertEqual(self.files(), self.applied)
        self.assertEqual(self.current()["palette"], {"name": "Night", "revision": 1})
        self.assertIn(f"noctalia msg wallpaper-set {self.night}", desk.calls("noctalia"))

    def test_failed_apply_rolls_back_every_write(self) -> None:
        desk = self.desktop
        before, status = self.files(), self.current()
        blocker = desk.home / ".t3/userdata/themes/rice.json"  # written last
        blocker.unlink()
        blocker.mkdir()
        del before[blocker]

        result = desk.rice("select", self.dusk, check=False)

        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("previous setup kept", result.stderr)
        self.assertEqual(self.files(), before)
        self.assertEqual(self.current(), status)

    def test_failed_wallpaper_ipc_keeps_files_and_current_setup(self) -> None:
        desk = self.desktop
        before, status = self.files(), self.current()
        tool = desk.root / "bin/noctalia"
        body = (
            'if [ "$2" = wallpaper-set ] && [ "$3" = "'
            + str(self.dusk)
            + '" ]; then exit 9; fi\n'
            + FAKES["noctalia"].format(real=REAL_NOCTALIA)
        )
        tool.write_text(FAKE_TOOL.format(body=body))
        result = desk.rice("select", self.dusk, check=False)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(self.files(), before)
        self.assertEqual(self.current(), status)

    def test_reload_failure_restores_the_live_wallpaper(self) -> None:
        desk = self.desktop
        before, status = self.files(), self.current()
        tool = desk.root / "bin/noctalia"
        marker = desk.root / "reload-failed"
        failure = (
            'if [ "$2" = config-reload ] && [ ! -f "'
            + str(marker)
            + '" ]; then touch "'
            + str(marker)
            + '"; exit 9; fi\n'
        )
        tool.write_text(FAKE_TOOL.format(body=failure + FAKES["noctalia"].format(real=REAL_NOCTALIA)))
        result = desk.rice("select", self.dusk, check=False)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(self.files(), before)
        self.assertEqual(self.current(), status)
        self.assertEqual((desk.root / "wallpaper").read_text(), str(self.night))

    def test_qt_sizes_and_unrelated_preferences_survive_theme_switch(self) -> None:
        desk = self.desktop
        settings = desk.config / "qt6ct/qt6ct.conf"
        settings.write_text(
            '[Fonts]\ngeneral="Inter,17,-1,5,400"\nfixed="Lilex Nerd Font,15,-1,5,400"\n'
            "[Interface]\ndouble_click_interval=550\n[Appearance]\nicon_theme=MyIcons\n"
        )
        desk.rice("select", self.dusk)
        result = configparser.ConfigParser(interpolation=None)
        result.read(settings)
        self.assertEqual(result["Fonts"]["general"], '"Geist,17,-1,5,400"')
        self.assertEqual(result["Fonts"]["fixed"], '"GeistMono Nerd Font,15,-1,5,400"')
        self.assertEqual(result["Interface"]["double_click_interval"], "550")
        self.assertEqual(result["Appearance"]["icon_theme"], "MyIcons")

    def test_noctalia_settings_keep_array_tables_after_owned_table(self) -> None:
        desk = self.desktop
        settings = desk.state / "noctalia/settings.toml"
        settings.parent.mkdir(parents=True, exist_ok=True)
        settings.write_text(
            "[theme]\n"
            'mode = "dark"\n'
            "\n"
            "[[plugins.source]]\n"
            'kind = "path"\n'
            'location = "/plugins"\n'
            'name = "rice"\n'
            "\n"
            '[ "bar" . "default" ]\n'
            "radius = 4\n"
            'position = "top"\n'
        )

        desk.rice("select", self.dusk)

        kept = tomllib.loads(settings.read_text())
        self.assertNotIn("config_version", kept)  # rendering must not migrate the user's file
        self.assertEqual(kept["theme"], {})
        self.assertEqual(
            kept["plugins"]["source"],
            [{"kind": "path", "location": "/plugins", "name": "rice"}],
        )
        self.assertEqual(kept["bar"]["default"], {"position": "top"})


class FirstPreview(unittest.TestCase):
    def test_vesktop_preview_preserves_preferences_and_restore_recovers_original(self) -> None:
        desk = Desktop()
        self.addCleanup(desk.close)
        image = desk.image("night.png", (20, 24, 60))
        settings = desk.config / "vesktop/settings/settings.json"
        settings.parent.mkdir(parents=True)
        original = {
            "enabledThemes": ["personal.theme.css"],
            "transparent": False,
            "plugins": {"Example": {"enabled": True}},
            "useQuickCss": True,
        }
        before = (json.dumps(original, indent=4) + "\n").encode()
        settings.write_bytes(before)

        desk.rice("draft", image)
        desk.rice("preview", image)

        applied = json.loads(settings.read_bytes())
        self.assertTrue(applied["transparent"])
        self.assertEqual(applied["enabledThemes"], ["personal.theme.css", "rice.theme.css"])
        self.assertEqual(applied["plugins"], original["plugins"])
        self.assertTrue(applied["useQuickCss"])
        desk.rice("restore")
        self.assertEqual(settings.read_bytes(), before)

    def test_repeated_first_previews_restore_existing_desktop(self) -> None:
        desk = Desktop()
        self.addCleanup(desk.close)
        original = desk.config / "kitty/rice-theme.conf"
        original.parent.mkdir(parents=True)
        original.write_text("# existing user theme\n")
        before = original.read_bytes()
        for name, rgb in (("night.png", (20, 24, 60)), ("dusk.png", (90, 40, 30))):
            image = desk.image(name, rgb)
            desk.rice("draft", image)
            desk.rice("preview", image)
        desk.rice("restore")
        self.assertEqual(original.read_bytes(), before)
        self.assertFalse((desk.config / "fuzzel/rice.ini").exists())
        self.assertIsNone(desk.json("status")["current"])


if __name__ == "__main__":
    unittest.main()
