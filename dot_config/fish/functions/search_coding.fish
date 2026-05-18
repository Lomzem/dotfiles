function search_coding
    set choices \
        (fd --format {} -td . "$HOME/coding/" -d 1) \
        (fd --format {} -td . "$HOME/.local/share/chezmoi/dot_config/" -d 1)

    set selected (
        printf "%s\n" $choices |\
        sort -r | \
        fzf --delimiter '/' --with-nth -2..
    )

    if test -n $selected
        cd $selected
    end
end
