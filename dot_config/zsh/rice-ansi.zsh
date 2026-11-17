if [[ ${TERM_PROGRAM:-} == t3code ]]; then
    typeset -g _rice_ansi_file="${XDG_DATA_HOME:-$HOME/.local/share}/rice/ansi-colors" _rice_ansi_shown
    _rice_ansi_show() {
        if [[ ! -r $_rice_ansi_file ]]; then
            [[ -n $_rice_ansi_shown ]] || return 0
            printf '\033]104;0;1;2;3;4;5;6;7;8;9;10;11;12;13;14;15\033\\'
            _rice_ansi_shown=
            return
        fi
        local colors="$(<$_rice_ansi_file)"
        [[ $colors == $_rice_ansi_shown ]] && return 0
        _rice_ansi_shown=$colors
        print -rn -- $colors
    }
    _rice_ansi_show
    autoload -Uz add-zsh-hook
    add-zsh-hook precmd _rice_ansi_show
fi
