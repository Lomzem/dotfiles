"""Fonts installed on this laptop."""

import decman
from decman.plugins import aur, pacman


class FontsModule(decman.Module):
    def __init__(self) -> None:
        super().__init__("fonts")

    @pacman.packages
    def pkgs(self) -> set[str]:
        return {
            "inter-font",
            "noto-fonts",
            "noto-fonts-emoji",
            "otf-geist-mono-nerd",
            "ttf-jetbrains-mono-nerd",
            "ttf-lilex-nerd",
        }

    @aur.packages
    def aurpkgs(self) -> set[str]:
        return {
            "otf-apple-sf-pro",
            "ttf-geist-variable",
            "ttf-rubik-vf",
        }
