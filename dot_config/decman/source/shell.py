"""Zsh, terminals, dotfiles, and command-line utilities."""

import decman
from decman.plugins import pacman


class ShellModule(decman.Module):
    def __init__(self) -> None:
        super().__init__("shell")

    @pacman.packages
    def pkgs(self) -> set[str]:
        return {
            "acpi",
            "aria2",
            "atuin",
            "bat",
            "chezmoi",
            "croc",
            "curl",
            "dash",
            "difftastic",
            "dust",
            "eza",
            "fastfetch",
            "fd",
            "fzf",
            "htop",
            "ijq",
            "inetutils",
            "jq",
            "kitty",
            "man-db",
            "man-pages",
            "openbsd-netcat",
            "ouch",
            "pdfgrep",
            "powertop",
            "qpdf",
            "qrencode",
            "rclone",
            "ripgrep",
            "starship",
            "tealdeer",
            "television",
            "tmux",
            "unzip",
            "wget",
            "yazi",
            "zoxide",
            "zsh",
            "zsh-antidote",
        }
