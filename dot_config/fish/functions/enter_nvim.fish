function enter_nvim
    if string match (jobs --command) "nvim"
        # nvim job is running in background, resume
        fg
    else
        nvim .
    end
end
