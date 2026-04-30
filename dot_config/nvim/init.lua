vim.pack.add({
    "https://github.com/catppuccin/nvim",
    "https://github.com/folke/snacks.nvim",
})

vim.cmd("colorscheme catppuccin-mocha")

require("opts")

require("snacks").setup({
    bigfile = { enabled = true },
    picker = { enabled = true },
})

-- contains plugin binds, therefore, must 
-- be **after** plugin setups
require("binds")
