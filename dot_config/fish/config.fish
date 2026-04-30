if status is-interactive
    fish_vi_key_bindings insert

    # Better cd
    zoxide init fish --cmd cd | source

    # Prompt
    starship init fish | source

    # History
    atuin init fish | source
end
