require("opts")
require("binds")

vim.pack.add({ "https://github.com/catppuccin/nvim" })

vim.cmd("colorscheme catppuccin-mocha")

require("lsp")

vim.pack.add({ "https://github.com/folke/snacks.nvim" })
require("snacks").setup({
	bigfile = { enabled = true },
	picker = { enabled = true },
})
vim.keymap.set("n", "<c-p>", Snacks.picker.files)

vim.pack.add({ "https://github.com/Wansmer/treesj" })
require("treesj").setup({
	use_default_keymaps = false,
})
vim.keymap.set("n", "<leader>j", require("treesj").toggle)

vim.pack.add({ "https://github.com/nvim-mini/mini.ai", "https://github.com/nvim-mini/mini.move" })
require("mini.move").setup({
	mappings = {
		-- Visual mode
		down = "J",
		up = "K",
		-- Normal mode
		line_down = "<m-j>",
		line_up = "<m-k>",
	},
})
