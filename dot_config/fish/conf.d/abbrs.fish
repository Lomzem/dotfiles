abbr --add cdt cd (mktemp --directory)
abbr --add cl clear
abbr --add cls clear
abbr --add cz chezmoi
abbr --add fs "kitten choose-fonts --config-file-name=$HOME/.config/kitty/font.conf && python $HOME/.config/kitty/copy_font.py $HOME/.config/kitty/font.conf && touch $HOME/.config/kitty/font.conf"
abbr --add m make
abbr --add mdt "nvim (mktemp --suffix=.md) -c 'setlocal autowriteall'"
abbr --add oc opencode .
abbr --add pso source .venv/bin/activate.fish
abbr --add r readlink -f
abbr --add rs sudo reboot now
abbr --add s yay -Ss
abbr --add sd sudo shutdown now
abbr --add stow stow --dir=$HOME/dotfiles --target=$HOME --no-folding .
abbr --add stow stow --dir=$HOME/dotfiles --target=$HOME --no-folding .
abbr --add upd 'sudo pacman -Syu --noconfirm && yay -Syu --noconfirm'
abbr --add vpn sudo gpclient --fix-openssl connect vpn-gw.csuchico.edu

abbr --add --position anywhere -- Noc --noconfirm
abbr --add --position anywhere C '| wl-copy'
abbr --add --position anywhere X '| xargs -I {}'
abbr --add p wl-paste

# zoxide
abbr --add z cd

abbr --add n nvim
abbr --add nv "cd $HOME/.local/share/chezmoi/dot_config/nvim && nvim ."

# git
abbr --add g git
abbr --add gA git add -A
abbr --add ga git add .
abbr --add gc git commit
abbr --add gco git checkout
abbr --add gp git pull
abbr --add gph git push
abbr --add gs git status
abbr --add jp 'git add . && git commit -m "Just push 😝" && git push'
