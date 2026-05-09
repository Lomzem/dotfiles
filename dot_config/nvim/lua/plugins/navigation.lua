vim.pack.add({ "https://github.com/folke/flash.nvim" })
require("flash").setup({
	modes = {
		char = {
			label = { exclude = "hjklviardcCxDIA" },
			autohide = true,
			highlight = { backdrop = false },
			char_actions = function(motion)
				return {
					[";"] = "next", -- set to `right` to always go right
					[","] = "prev", -- set to `left` to always go left
					-- clever-f style
					[motion:lower()] = nil,
					[motion:upper()] = nil,
				}
			end,
		},
	},
})

vim.pack.add({ "https://github.com/smoka7/hop.nvim" })
require("hop").setup({
	keys = "etovxqpdygfblzhckisuran",
	create_hl_autocmd = false,
})
vim.api.nvim_set_hl(0, "HopNextKey", { link = "label" })
vim.api.nvim_set_hl(0, "HopNextKey1", { link = "label" })
vim.api.nvim_set_hl(0, "HopNextKey2", { link = "label" })
vim.keymap.set({ "n", "x", "o" }, "<cr>", "<cmd>HopLineStart<cr>")
vim.keymap.set("v", "<cr>", function()
	vim.cmd("HopLine")
	vim.cmd("norm V")
end)
vim.keymap.set("n", "d<cr>", function()
	local start_line = vim.fn.line(".")
	local hop = require("hop")
	local opts = setmetatable({}, { __index = hop.opts })
	hop.hint_with_regex(require("hop.jump_regex").by_line_start(), opts, function(jump_target)
		local target_line = jump_target.cursor.row
		local from_line = math.min(start_line, target_line)
		local to_line = math.max(start_line, target_line)
		vim.cmd(string.format("%d,%dd", from_line, to_line))
	end)
end)
