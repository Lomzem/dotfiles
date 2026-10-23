"""Container, Jellyfin media server, and Nix packages; no service state changes."""

import decman
from decman.plugins import pacman


class ServicesModule(decman.Module):
    def __init__(self) -> None:
        super().__init__("services")

    @pacman.packages
    def pkgs(self) -> set[str]:
        return {
            "docker",
            "docker-compose",
            "jellyfin-server",
            "jellyfin-web",
            "nix",
        }
