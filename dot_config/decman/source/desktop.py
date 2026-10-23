"""Niri desktop, Wayland tools, AMD graphics, and audio."""

import decman
from decman.plugins import aur, pacman


class DesktopModule(decman.Module):
    def __init__(self) -> None:
        super().__init__("desktop")

    @pacman.packages
    def pkgs(self) -> set[str]:
        return {
            "alsa-plugins",
            "alsa-utils",
            "archlinux-xdg-menu",
            "bibata-cursor-theme",
            "bluetui",
            "brightnessctl",
            "feh",  # Preferred image previewer.
            "fuzzel",
            "gnome-keyring",  # Matches the configured Secret portal backend.
            "grim",
            "gtk-layer-shell",
            "hyprpicker",  # Super+Alt+P picks a color and copies its hex value.
            "matugen",
            "mesa",
            "niri-git",
            "noctalia",
            "nwg-look",
            "pipewire",
            "pipewire-alsa",
            "pipewire-pulse",
            "playerctl",  # Used by the Niri media key bindings.
            "power-profiles-daemon",
            "pulsemixer",
            "slurp",
            "vulkan-icd-loader",
            "vulkan-radeon",
            "wev",
            "wireplumber",
            "wl-clipboard",
            "wtype",
            "xdg-desktop-portal-gnome",
            "xdg-desktop-portal-gtk",
            "xdg-desktop-portal-hyprland",  # Also provides niri-git's portal dependency.
            "xdg-desktop-portal-wlr",
            "xdotool",  # X11/Xwayland automation fallback; not native Wayland.
            "xwayland-satellite",
        }

    @aur.packages
    def aurpkgs(self) -> set[str]:
        return {
            "portty-bin",
        }
