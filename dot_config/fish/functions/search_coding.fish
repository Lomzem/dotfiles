function search_coding
    set choices \
        (fd --format {} -td . "$HOME/coding/" -d 1) \
        (fd --format {} -td . "$HOME/dotfiles/.config/" -d 1) \
        (fd --format {} -td . "$HOME/coding/csci581-ml" -d 1) \
        (fd --format {} -td . "$HOME/coding/csci515-compilers" -d 1) \
        (fd --format {} -td . "$HOME/coding/csci411-alg" -d 1) \
        "$HOME/.config/nvim" \
        "$HOME/dotfiles/.local/bin/custom-scripts" \
        "$HOME/dotfiles/.local/bin/custom-scripts/bookmarks" \
        "$HOME/dotfiles/.local/share/colorschemes"

    set selected (
        printf "%s\n" $choices |\
        sort -r | \
        fzf --delimiter '/' --with-nth -2..
    )

    if test -n $selected
        cd $selected
    end
end
