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
