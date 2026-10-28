"""Seam: draft -> approve -> reuse without regeneration, keyed by image content."""

import json
import shutil
import unittest

from harness import Desktop


class ApprovedProfiles(unittest.TestCase):
    def setUp(self) -> None:
        self.desktop = Desktop()
        self.addCleanup(self.desktop.close)

    def t3_theme(self) -> dict:
        return json.loads((self.desktop.home / ".t3/userdata/themes/rice.json").read_text())

    def test_renamed_image_reuses_approved_palette_without_regenerating(self) -> None:
        desk = self.desktop
        image = desk.image("mitsuha.png", (24, 32, 72))

        desk.rice("draft", image)
        desk.rice("set", image, "primary=#7dd3fc")
        desk.rice("approve", image, "--name", "Mitsuha")
        generated = desk.generator_runs()

        renamed = image.with_name("renamed-copy.png")
        shutil.copy(image, renamed)
        image.unlink()
        desk.rice("select", renamed)

        self.assertEqual(desk.generator_runs(), generated)
        self.assertEqual(self.t3_theme()["accent"], "#7dd3fc")
        status = desk.json("status")
        self.assertEqual(status["current"]["palette"], {"name": "Mitsuha", "revision": 1})
        self.assertEqual(status["current"]["wallpaper"], str(renamed))
        self.assertIn(str(renamed), [item["path"] for item in desk.json("list")["wallpapers"]])

    def test_regenerated_draft_does_not_replace_approved_palette_until_approved(
        self,
    ) -> None:
        desk = self.desktop
        image = desk.image("mitsuha.png", (24, 32, 72))
        desk.rice("draft", image)
        desk.rice("set", image, "primary=#7dd3fc")
        desk.rice("approve", image, "--name", "Mitsuha")

        desk.rice("draft", image, "--regenerate")
        desk.rice("set", image, "primary=#a5b4fc")
        desk.rice("select", image)
        self.assertEqual(self.t3_theme()["accent"], "#7dd3fc")

        desk.rice("approve", image)
        desk.rice("select", image)
        self.assertEqual(self.t3_theme()["accent"], "#a5b4fc")
        self.assertEqual(
            desk.json("status")["current"]["palette"],
            {"name": "Mitsuha", "revision": 2},
        )

    def test_unknown_image_is_drafted_and_nothing_is_applied(self) -> None:
        desk = self.desktop
        image = desk.image("new.png", (200, 180, 160))

        result = desk.rice("select", image, check=False)

        self.assertEqual(result.returncode, 3, result.stderr)
        self.assertFalse((desk.home / ".t3/userdata/themes/rice.json").exists())
        self.assertIsNone(desk.json("status")["current"])
        listed = desk.json("list")["wallpapers"]
        self.assertEqual([(w["path"], w["status"]) for w in listed], [(str(image), "draft")])
