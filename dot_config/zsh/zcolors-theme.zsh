color () {
	print -nr - $'\e['"${(vj.;.)color[(I)(${(~j.|.)@})]}m"
}
lscolor () {
	print -nr - $'\e['${ls_colors[(R)$1=*]#$1=}m
}
	if whence -p less > /dev/null && (( ${${=$( less -V )}[2]} >= 581 ))
	then
		export -UT LESS less ' '
		less+=(--use-color '-DSkY$DPWb') 
	fi
	autoload -Uz add-zsh-hook
	zcolors.precmd () {
		unfunction -m zcolors.\*
		add-zsh-hook -d precmd zcolors.precmd
		zmodload -F zsh/parameter p:saliases
		ls_colors+=('*.'${(@k)^saliases}"=$lscolors[sg]") 
	}
	add-zsh-hook precmd zcolors.precmd
export GREP_COLOR='103;30'
export GREP_COLORS='mt=103;30'
export -UT LS_COLORS ls_colors=( '' 'cd=33;01' 'st=34' 'no=00' 'bd=103;30' 'ln=36' 'su=91' 'ex=92' 'tw=44;37' 'or=31' 'fi=37' 'di=94' 'sg=93' 'ow=44;97' 'pi=33' '*.zwc=90' 'so=35' 'mi=90' '*.DS_Store=90' )
export LSCOLORS=ExgxfxdxCxadDxBxDxheHe
typeset -g ZSH_AUTOSUGGEST_HIGHLIGHT_STYLE='fg=8'
typeset -g -A ZSH_HIGHLIGHT_STYLES=( [arg0]='fg=10' [assign]='fg=6' [autodirectory]='fg=12' [back-dollar-quoted-argument]='fg=6' [back-double-quoted-argument]='fg=6' [back-quoted-argument]='' [back-quoted-argument-delimiter]='fg=5' [bracket-error]='fg=1' [bracket-level-1]='fg=5' [bracket-level-2]='fg=5' [bracket-level-3]='fg=5' [bracket-level-4]='fg=5' [bracket-level-5]='fg=5' [builtins]='fg=10' [command-substitution]='' [command-substitution-delimiter]='fg=5' [commandseparator]='fg=3' [comment]='fg=8' [cursor-matchingbracket]='fg=0,bg=11' [default]='' [dollar-double-quoted-argument]='fg=6' [dollar-quoted-argument]='fg=11' [double-hyphen-option]='fg=11' [double-quoted-argument]='fg=11' [global-alias]='fg=6' [globbing]='fg=7,bg=4' [history-expansion]='fg=6' [named-fd]='fg=3,bold' [numeric-fd]='fg=3,bold' [path]='fg=12' [path_pathseparator]='fg=7' [path_prefix]='fg=4' [path_prefix_pathseparator]='fg=8' [precommand]='fg=9' [process-substitution]='' [process-substitution-delimiter]='fg=5' [rc-quote]='fg=6' [redirection]='fg=3' [reserved-word]='fg=9' [single-hyphen-option]='fg=11' [single-quoted-argument]='fg=11' [suffix-alias]='fg=11' [unknown-token]='fg=1' )
typeset -g -A color=( [00]=none [01]=bold [02]=faint [03]=italic [04]=underline [05]=blink [07]=reverse [08]=conceal [100]=bg-brightblack [101]=bg-brightred [102]=bg-brightgreen [103]=bg-brightyellow [104]=bg-brightblue [105]=bg-brightmagenta [106]=bg-brightcyan [107]=bg-brightwhite [22]=normal [23]=no-italic [24]=no-underline [25]=no-blink [27]=no-reverse [28]=no-conceal [30]=black [31]=red [32]=green [33]=yellow [34]=blue [35]=magenta [36]=cyan [37]=white [39]=default [40]=bg-black [41]=bg-red [42]=bg-green [43]=bg-yellow [44]=bg-blue [45]=bg-magenta [46]=bg-cyan [47]=bg-white [49]=bg-default [90]=brightblack [91]=brightred [92]=brightgreen [93]=brightyellow [94]=brightblue [95]=brightmagenta [96]=brightcyan [97]=brightwhite [bg-black]=40 [bg-blue]=44 [bg-brightblack]=100 [bg-brightblue]=104 [bg-brightcyan]=106 [bg-brightgreen]=102 [bg-brightmagenta]=105 [bg-brightred]=101 [bg-brightwhite]=107 [bg-brightyellow]=103 [bg-cyan]=46 [bg-default]=49 [bg-green]=42 [bg-magenta]=45 [bg-red]=41 [bg-white]=47 [bg-yellow]=43 [black]=30 [blink]=05 [blue]=34 [bold]=01 [brightblack]=90 [brightblue]=94 [brightcyan]=96 [brightgreen]=92 [brightmagenta]=95 [brightred]=91 [brightwhite]=97 [brightyellow]=93 [conceal]=08 [cyan]=36 [default]=39 [dim]=02 [faint]=02 [fg-black]=30 [fg-blue]=34 [fg-brightblack]=90 [fg-brightblue]=94 [fg-brightcyan]=96 [fg-brightgreen]=92 [fg-brightmagenta]=95 [fg-brightred]=91 [fg-brightwhite]=97 [fg-brightyellow]=93 [fg-cyan]=36 [fg-default]=39 [fg-gray]=30 [fg-green]=32 [fg-grey]=30 [fg-magenta]=35 [fg-red]=31 [fg-white]=37 [fg-yellow]=33 [green]=32 [italic]=03 [magenta]=35 [no-blink]=25 [no-conceal]=28 [no-italic]=23 [no-reverse]=27 [no-underline]=24 [none]=00 [normal]=22 [red]=31 [reverse]=07 [underline]=04 [white]=37 [yellow]=33 )
typeset -g -A zcolor=( ['*.DS_Store']=90 ['*.zwc']=90 [bd]='103;30' [cd]='33;01' [di]=94 [ex]=92 [fi]=37 [ln]=36 [mi]=90 [no]=00 [or]=31 [ow]='44;97' [pi]=33 [sg]=93 [so]=35 [st]=34 [su]=91 [tw]='44;37' )
typeset -g -a zle_highlight=( 'special:fg=6' 'region:fg=15,bg=4' 'paste:fg=15,bg=4' 'isearch:fg=0,bg=11' 'suffix:fg=15,bg=4' )
zstyle ':completion:*:default' list-colors '(events)=(|-)<->(#b)(*)=00=90' '(history-lines)=[[:space:]]#(#b)(<->) *=00=90' '(*(branch|head)*~*remote*)=(#b)(*[^ ]~*  *|)[ ]#(*)=00=94=90' '(aliases|builtins|executables|functions|commands)=(#b)(*[^ ]~*  *|)[ ]#(*)=00=92=90' '(named-directories)=(#b)(*[^ ]~*  *|)[ ]#(*)=00=94=90' '(suffix-aliases)=(#b)(*[^ ]~*  *|)[ ]#(*)=00=93=90' '(*commit*~*-tag)=(#b)(*[^ ]~*  *|)[ ]#(*)=00=33=90' '(options)=(#b)(*[^ ]~*  *|)[ ]#(*)=00=93=90' '(*-tag*~*commit*)=(#b)(*[^ ]~*  *|)[ ]#(*)=00=35=90' '(*local*~*director*)=(#b)(*[^ ]~*  *|)[ ]#(*)=00=94=90' '(*remote*~*(branch|head)*)=(#b)(*[^ ]~*  *|)[ ]#(*)=00=36=90' '(file-descriptors)=(#b)(*[^ ]~*  *|)[ ]#(*)=00=33;01=90' '(global-aliases|modifiers|parameters)=(#b)(*[^ ]~*  *|)[ ]#(*)=00=36=90' '(glob(flags|quals))=(#b)(*[^ ]~*  *|)[ ]#(*)=00=44;37=90' '(reserved-words)=(#b)(*[^ ]~*  *|)[ ]#(*)=00=91=90' '(*~*(directories|files|expansions))=(*[^ ]~*  *|)[ ]#(#b)(*)=00=90' 'no=00' 'st=34' 'cd=33;01' 'ex=92' 'su=91' 'ln=36' 'bd=103;30' 'fi=37' 'or=31' 'tw=44;37' 'sg=93' 'di=94' 'ow=44;97' 'pi=33' 'mi=90' 'so=35' '*.zwc=90' '*.DS_Store=90' 'tc=37' 'sp=00' 'sa=93' 'ma=44;97' $'lc=\C-[[00;' 'rc=m'
zstyle ':completion:*' group-name ''
zstyle ':completion:*' list-separator ' '
