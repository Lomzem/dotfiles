require("opts")

vim.pack.add({
    "https://github.com/catppuccin/nvim",
    "https://github.com/folke/snacks.nvim",
    "https://github.com/neovim/nvim-lspconfig",
})

vim.cmd("colorscheme catppuccin-mocha")

require("lsp")

require("snacks").setup({
    bigfile = { enabled = true },
    picker = { enabled = true },
})

-- contains plugin binds, therefore, must 
-- be **after** plugin setups
require("binds")
