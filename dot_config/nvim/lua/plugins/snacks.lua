vim.pack.add({ "https://github.com/nvim-lua/plenary.nvim" })
vim.pack.add({ "https://github.com/folke/snacks.nvim" })
require("snacks").setup({
	bigfile = { enabled = true },
	picker = { enabled = true },
})
vim.keymap.set("n", "<c-p>", Snacks.picker.files)
vim.keymap.set("n", "<leader>ps", Snacks.picker.grep)
vim.keymap.set("n", "gm", Snacks.picker.lsp_symbols)
vim.keymap.set("n", "gM", Snacks.picker.lsp_workspace_symbols)
vim.keymap.set("n", "gd", Snacks.picker.lsp_definitions)
vim.keymap.set("n", "gr", Snacks.picker.lsp_references)
vim.keymap.set("n", "gp", Snacks.picker.diagnostics)
vim.keymap.set("n", "gh", Snacks.picker.help)
