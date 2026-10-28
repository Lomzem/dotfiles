"""Seam: contrast validation through the public commands, including composited transparency.

Expected ratios are published WebAIM values, not computed by the code under test:
#ffffff on #777777 is 4.48:1 and #ffffff on #666666 is 5.74:1. A #000000 panel at
alpha 0.533 over a white wallpaper composites to #777777, at 0.6 to #666666.
"""

import unittest

from harness import Desktop


class ContrastGate(unittest.TestCase):
    def setUp(self) -> None:
        self.desktop = Desktop()
        self.addCleanup(self.desktop.close)
        self.image = self.desktop.image("white.png", (255, 255, 255))
        self.desktop.rice("draft", self.image)

    def panel_text(self) -> dict:
        checks = self.desktop.json("report", self.image)["checks"]
        return next(row for row in checks if row["role"] == "text on panel")

    def assert_refused(self, reason: str) -> None:
        result = self.desktop.rice("approve", self.image, "--name", "White", check=False)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn(reason, result.stderr)
        self.assertEqual(self.desktop.json("list")["palettes"], [])

    def test_translucent_panel_is_judged_over_the_wallpaper_not_opaque(self) -> None:
        self.desktop.rice(
            "set",
            self.image,
            "surface=#000000",
            "on_surface=#ffffff",
            "alpha.panel=0.533",
        )

        row = self.panel_text()
        self.assertAlmostEqual(row["opaque"], 21.0, places=2)
        self.assertAlmostEqual(row["ratio"], 4.48, delta=0.02)
        self.assertFalse(row["ok"])
        self.assert_refused("text on panel")

        self.desktop.rice("set", self.image, "alpha.panel=0.6")
        self.assertAlmostEqual(self.panel_text()["ratio"], 5.74, delta=0.02)

        self.desktop.rice("set", self.image, "alpha.panel=1")
        self.desktop.rice("approve", self.image, "--name", "White")
        self.assertEqual([p["name"] for p in self.desktop.json("list")["palettes"]], ["White"])

    def test_one_bright_pixel_bounds_the_backdrop(self) -> None:
        """Navy wallpaper with a single white pixel: the panel can sit over that pixel."""
        image = self.desktop.image(
            "navy-star.png",
            (12, 16, 40),
            size=(640, 360),
            spot=(321, 77, (255, 255, 255)),
        )
        self.desktop.rice("draft", image)
        self.desktop.rice("set", image, "surface=#000000", "on_surface=#ffffff", "alpha.panel=0.533")

        checks = self.desktop.json("report", image)["checks"]
        row = next(row for row in checks if row["role"] == "text on panel")
        self.assertAlmostEqual(row["ratio"], 4.48, delta=0.02)
        self.assertFalse(row["ok"])

    def test_all_controlled_card_surfaces_are_checked(self) -> None:
        self.desktop.rice("set", self.image, "surface_container_high=#ffffff")
        self.assert_refused("omnibox")

    def test_fuzzel_accent_text_requires_text_contrast_when_translucent(self) -> None:
        self.desktop.rice(
            "set",
            self.image,
            "surface=#000000",
            "surface_variant=#000000",
            "primary=#aaaaaa",
            "on_primary=#000000",
            "alpha.panel=0.74",
        )
        self.assert_refused("Fuzzel prompt and match text")

    def test_semantic_red_must_stay_red(self) -> None:
        self.desktop.rice("set", self.image, "terminal_normal_red=#60a5fa")
        self.assert_refused("terminal_normal_red stays red")

    def test_malformed_values_are_rejected(self) -> None:
        for assignment in (
            "primary=#12345",
            "primary=red",
            "alpha.panel=nan",
            "alpha.panel=2",
        ):
            with self.subTest(assignment):
                result = self.desktop.rice("set", self.image, assignment, check=False)
                self.assertEqual(result.returncode, 1, result.stdout)
