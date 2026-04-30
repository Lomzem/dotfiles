# Reload fish config
function so
    source $HOME/.config/fish/config.fish
    source $HOME/.config/fish/conf.d/*.fish
    source $HOME/.config/fish/functions/*.fish
end
