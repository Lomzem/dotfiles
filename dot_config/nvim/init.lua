require("opts")
require("binds")

vim.pack.add({ "https://github.com/catppuccin/nvim" })

vim.cmd("colorscheme catppuccin-mocha")

require("lsp")

vim.pack.add({ "https://github.com/nvim-lua/plenary.nvim" })

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

vim.pack.add({
	"https://github.com/nvim-mini/mini.ai",
	"https://github.com/nvim-mini/mini.move",
	"https://github.com/nvim-mini/mini.surround",
})
require("mini.ai").setup()
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
require("mini.surround").setup({
	mappings = {
		add = "S", -- Add surrounding in Normal and Visual modes
		delete = "ds", -- Delete surrounding
		find = "", -- Find surrounding (to the right) default: sf
		find_left = "", -- Find surrounding (to the left) default: sF
		highlight = "", -- Highlight surrounding default: ysh
		replace = "cs", -- Replace surrounding
		update_n_lines = "", -- Update `n_lines`lj default: snj
		suffix_last = "l", -- Suffix to search with "prev" method
		suffix_next = "n", -- Suffix to search with "next" method
	},
})

vim.pack.add({ "https://github.com/windwp/nvim-autopairs" })
do
	local npairs = require("nvim-autopairs")
	local Rule = require("nvim-autopairs.rule")
	local cond = require("nvim-autopairs.conds")
	npairs.setup({
		check_ts = true,
	})
	npairs.add_rules({
		Rule("<", ">"):with_pair(cond.none()):with_move(cond.done()):use_key(">"),
	})
end

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
vim.keymap.set("n", "<cr>", function()
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

vim.pack.add({ "https://github.com/mikavilpas/yazi.nvim" })
vim.keymap.set("n", "<leader>pv", require("yazi").yazi)
