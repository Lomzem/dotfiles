"""T3 Code and the Tailscale transport required for its remote access."""

import decman
from decman.plugins import aur, pacman


class T3CodeModule(decman.Module):
    def __init__(self) -> None:
        super().__init__("t3code")

    @pacman.packages
    def pkgs(self) -> set[str]:
        return {"tailscale"}

    @aur.packages
    def aurpkgs(self) -> set[str]:
        return {"t3code-nightly-bin"}
