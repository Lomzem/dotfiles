# This file is not sourced automatically by config.fish
# Intended to be manually ran **once** to set long-term variables.
# Usage:
# On first fish install, run `source $HOME/.config/fish/universal.fish`

fish_add_path $HOME/.local/bin

set -Ux LESS '-R --use-color -Dd+r$Du+b'

set -Ux EDITOR nvim
set -Ux VISUAL nvim
set -Ux MANPAGER "nvim +Man!"

set -Ux CANVAS_URL "https://canvas.csuchico.edu"

# Colors for `fd`
set -Ux LS_COLORS (dircolors | head -n 1 | cut --characters 11-)

set -Ux FZF_DEFAULT_OPTS "
  --bind='ctrl-l:accept'
  --style full
  --height=~65%
  --layout=reverse
  --border=none
  --prompt='❯ '
  --pointer=''
  --marker=''
  --scrollbar=''
  --highlight-line
  --cycle
  --color='
    fg:-1,fg+:-1,bg:-1,bg+:black
    hl:cyan,hl+:bright-cyan
    border:bright-black,separator:bright-black,scrollbar:bright-black
    label:-1,query:-1
    prompt:yellow,pointer:green,marker:yellow
    spinner:yellow,info:bright-black
    header:cyan,gutter:-1
  '
"
