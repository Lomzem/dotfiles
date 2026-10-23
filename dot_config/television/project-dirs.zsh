#!/usr/bin/env zsh
emulate -LR zsh

{
  # Immediate project directories, including symlinks to directories.
  for dir in "$HOME"/proj/*(N-/); do
    print -r -- "$dir"
  done

  # Only immediate managed config directories, using their live paths.
  chezmoi managed --include dirs --path-style absolute "$HOME/.config" |
    while IFS= read -r dir; do
      [[ "${dir:h}" == "$HOME/.config" && -d "$dir" ]] && print -r -- "$dir"
    done
} | LC_ALL=C sort -u
