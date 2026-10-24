# Laptop decman configuration

Decman manages this laptop's packages. Chezmoi manages its dotfiles.

Edit package sets in `source/`. Repository packages, including Chaotic-AUR,
go in `pkgs`; foreign packages go in `aurpkgs`. `source/t3code.py` keeps
T3 Code and Tailscale together.

Dictus uses the local `packages/dictus-bin/PKGBUILD`, declared with
`aur.custom_packages` in `source/applications.py`. Decman builds it and pacman
owns the installed files. To update it, bump `pkgver`, reset `pkgrel` to 1,
and replace `sha256sums` with the checksum from the matching upstream release.

Decman removes packages outside these declarations, including unused optional
dependencies.

Preview changes, then apply. Applying also upgrades system and AUR packages.

```sh
cd ~/.config/decman
sudo decman --dry-run --source "$PWD/source.py"
sudo decman --source "$PWD/source.py"
```

Check the Python configuration and save edits to chezmoi:

```sh
uv sync --locked
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked basedpyright
chezmoi add ~/.config/decman
```

The dotfiles repo ignores `.venv`, bytecode, caches, and nested Git metadata.
