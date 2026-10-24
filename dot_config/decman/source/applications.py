"""Documents, creative applications, media, and chat."""

from pathlib import Path

import decman
from decman.plugins import aur, pacman


class ApplicationsModule(decman.Module):
    def __init__(self) -> None:
        super().__init__("applications")

    @aur.custom_packages
    def custom_packages(self) -> set[aur.CustomPackage]:
        return {
            aur.CustomPackage(
                pkgname="dictus-bin",
                pkgbuild_directory=str(
                    Path(__file__).resolve().parents[1] / "packages" / "dictus-bin"
                ),
            )
        }

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
