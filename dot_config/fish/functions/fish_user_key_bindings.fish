function fish_user_key_bindings
    bind -M default ctrl-n enter_nvim
    bind -M insert ctrl-n enter_nvim

    bind -M default ctrl-f search_coding repaint
    bind -M insert ctrl-f search_coding repaint

    bind -M default alt-k up-or-search
    bind -M insert alt-k up-or-search
    bind -M default alt-j down-or-search
    bind -M insert alt-j down-or-search

    bind -M default ctrl-o canvastui repaint
    bind -M insert ctrl-o canvastui repaint
end
