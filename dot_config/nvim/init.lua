require("opts")

vim.pack.add({ "https://github.com/catppuccin/nvim" })

vim.cmd("colorscheme catppuccin-mocha")

require("lsp")

vim.pack.add({ "https://github.com/folke/snacks.nvim" })
require("snacks").setup({
	bigfile = { enabled = true },
	picker = { enabled = true },
})

-- contains plugin binds, therefore, must
-- be **after** plugin setups
require("binds")
