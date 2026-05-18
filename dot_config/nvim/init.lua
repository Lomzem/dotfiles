require("opts")
require("binds")

require("colorschemes")
require("autocmds")

require("vim._core.ui2").enable()

vim.pack.add({ "https://github.com/esmuellert/codediff.nvim" })
require("codediff").setup({
	diff = {
		ignore_trim_whitespace = true,
	},
})

vim.pack.add({ "https://github.com/nvim-tree/nvim-tree.lua" })
require("nvim-tree").setup()
vim.keymap.set("n", "<a-e>", "<cmd>NvimTreeToggle<cr>")

-- Source all in `lua/plugins`
local plugins_dir = vim.fs.joinpath(vim.api.nvim_get_runtime_file("lua/plugins", false)[1])
for name, type in vim.fs.dir(plugins_dir, { depth = math.huge }) do
	if type == "file" then
		local abspath = vim.fs.joinpath(plugins_dir, name)
		dofile(abspath)
	end
end

require("lsp")
