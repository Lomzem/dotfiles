"""Editors, programming languages, build tools, and AI coding tools."""

import decman
from decman.plugins import aur, pacman


class DevelopmentModule(decman.Module):
    def __init__(self) -> None:
        super().__init__("development")

    @pacman.packages
    def pkgs(self) -> set[str]:
        return {
            "binutils",
            "bun",
            "clang",
            "cloc",
            "cmake",
            "code",
            "gdb",
            "git",
            "git-filter-repo",
            "git-lfs",
            "github-cli",
            "gitleaks",
            "go",
            "hyperfine",
            "jujutsu",
            "just",
            "lazygit",
            "lld",
            "lua",
            "neovim",
            "npm",
            "openai-codex",
            "pnpm",
            "python",
            "python-pip",
            "ruff",
            "rustup",
            "typescript",
            "uv",
        }

    @aur.packages
    def aurpkgs(self) -> set[str]:
        return {
            "cppman",
        }
