vim.pack.add({
	"https://github.com/catppuccin/nvim",
	"https://github.com/folke/snacks.nvim",
})

vim.cmd("colorscheme catppuccin-mocha")

require("snacks").setup({
	bigfile = { enabled = true },
	picker = { enabled = true },
})


vim.g.mapleader = " "
vim.g.localleader = "\\"

vim.keymap.set("n", "<c-p>", Snacks.picker.files)
