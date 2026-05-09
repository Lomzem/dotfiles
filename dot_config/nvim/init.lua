require("opts")
require("binds")

require("colorschemes")

-- Source all in `lua/plugins`
local plugins_dir = vim.fs.joinpath(vim.api.nvim_get_runtime_file("lua/plugins", false)[1])
for name, type in vim.fs.dir(plugins_dir, { depth = math.huge }) do
	if type == "file" then
		local abspath = vim.fs.joinpath(plugins_dir, name)
		dofile(abspath)
	end
end

require("lsp")
