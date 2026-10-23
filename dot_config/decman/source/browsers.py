"""Helium is the primary browser on this laptop."""

import decman
from decman.plugins import pacman


class BrowsersModule(decman.Module):
    def __init__(self) -> None:
        super().__init__("browsers")

    @pacman.packages
    def pkgs(self) -> set[str]:
        return {
            "helium-browser-bin",
        }
