"""Boot, AMD firmware, networking, and package management."""

import decman
from decman.plugins import aur, pacman


class BaseModule(decman.Module):
    def __init__(self) -> None:
        super().__init__("base")

    @pacman.packages
    def pkgs(self) -> set[str]:
        return {
            "amd-ucode",
            "archlinux-keyring",
            "base",
            "base-devel",
            "bash",
            "bluez",
            "bluez-libs",
            "bluez-utils",
            "chaotic-keyring",
            "chaotic-mirrorlist",
            "fuse2",
            "grub",
            "libxcrypt",
            "linux",
            "linux-firmware",
            "linux-headers",
            "networkmanager",
            "openssh",
            "reflector",
            "systemd",
            "yay",  # Manual fallback alongside decman.
        }

    @aur.packages
    def aurpkgs(self) -> set[str]:
        return {
            "decman",
        }
