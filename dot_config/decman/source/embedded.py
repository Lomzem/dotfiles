"""ARM and Espressif development tools installed on this laptop."""

import decman
from decman.plugins import pacman


class EmbeddedModule(decman.Module):
    def __init__(self) -> None:
        super().__init__("embedded")

    @pacman.packages
    def pkgs(self) -> set[str]:
        return {
            "arm-none-eabi-gcc",
            "arm-none-eabi-newlib",
            "esp-generate",
            "espflash",
            "espup",
            "openocd",
        }
