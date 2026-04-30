function pac
    if test -z "$argv"
        echo "Usage: pac [command]"
        return 1
    end

    set first "-$argv[1]"
    sudo pacman $first $argv[2..]
end
