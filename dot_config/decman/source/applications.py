"""Documents, creative applications, media, and chat."""

import decman
from decman.plugins import pacman


class ApplicationsModule(decman.Module):
    def __init__(self) -> None:
        super().__init__("applications")

    @pacman.packages
    def pkgs(self) -> set[str]:
        return {
            "ffmpeg",
            "imagemagick",
            "mpv",
            "musescore",
            "obs-studio",
            "pandoc-bin",
            "typst",
            "vesktop",
            "zathura",
            "zathura-pdf-mupdf",
        }
