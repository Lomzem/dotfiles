vim.pack.add({ "https://github.com/mikavilpas/yazi.nvim" })
vim.keymap.set("n", "<leader>pv", require("yazi").yazi)

vim.pack.add({ "https://github.com/stevearc/oil.nvim" })
require("oil").setup({
	view_options = {
		show_hidden = true,
	},
	keymaps = {
		["<C-s>"] = { false, desc = "Oil Save" },
		["<C-p>"] = function()
			Snacks.picker.files()
		end,
	},
})
