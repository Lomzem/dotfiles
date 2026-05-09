require("opts")
require("binds")

require("colorschemes")

vim.pack.add({ "https://github.com/nvim-mini/mini.base16" })
-- vim.pack.add({ "http://github.com/RRethy/base16-nvim" })
-- require("matugen").setup()

require("lsp")

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

vim.pack.add({ "https://github.com/nvim-treesitter/nvim-treesitter" })
-- Auto install based on filetype
vim.api.nvim_create_autocmd({ "Filetype" }, {
	callback = function(event)
		local ok, nvim_treesitter = pcall(require, "nvim-treesitter")
		if not ok then
			return
		end

		local parsers = require("nvim-treesitter.parsers")
		if not parsers[event.match] then
			return
		end

		local lang = vim.treesitter.language.get_lang(vim.bo[event.buf].ft)
		nvim_treesitter.install({ lang }):await(function(err)
			if not err then
				pcall(vim.treesitter.start, event.buf)
			end
		end)
	end,
})

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

vim.pack.add({ "https://github.com/supermaven-inc/supermaven-nvim" })
require("supermaven-nvim").setup({
	keymaps = {
		accept_suggestion = "<right>",
	},
})

vim.pack.add({ "https://github.com/cbochs/grapple.nvim" })
do
	local grapple = require("grapple")
	---@module "grapple"
	---@type grapple.settings
	grapple.setup({
		scope = "cwd",
		icons = false,
		status = true,
	})
	-- if vim.v.argv[3] == "." and grapple.exists({ index = 1 }) then
	-- 	vim.schedule(function()
	-- 		grapple.select({ index = 1 })
	-- 	end)
	-- end
	vim.keymap.set("n", "<leader>a", "<cmd>Grapple tag<cr>")
	vim.keymap.set("n", "<c-e>", "<cmd>Grapple toggle_tags<cr>")
	vim.keymap.set("n", "<leader>A", function()
		grapple.reset({ notify = false })
		grapple.tag()
	end)
	vim.keymap.set("n", "<a-1>", "<cmd>Grapple select index=1<cr>")
	vim.keymap.set("n", "<a-2>", "<cmd>Grapple select index=2<cr>")
	vim.keymap.set("n", "<a-3>", "<cmd>Grapple select index=3<cr>")
	vim.keymap.set("n", "<a-4>", "<cmd>Grapple select index=4<cr>")
	vim.keymap.set("n", "<a-5>", "<cmd>Grapple select index=5<cr>")
	vim.keymap.set("n", "<a-6>", "<cmd>Grapple select index=6<cr>")
	vim.keymap.set("n", "<a-7>", "<cmd>Grapple select index=7<cr>")
	vim.keymap.set("n", "<a-8>", "<cmd>Grapple select index=8<cr>")
	vim.keymap.set("n", "<a-9>", "<cmd>Grapple select index=9<cr>")
end

vim.pack.add({
	"https://github.com/nvim-lualine/lualine.nvim",
	"https://github.com/nvim-tree/nvim-web-devicons",
})
require("lualine").setup({
	options = {
		icons_enabled = true,
		theme = "auto",
		component_separators = { left = "", right = "" },
		section_separators = { left = "", right = "" },
		disabled_filetypes = {
			statusline = {},
			winbar = {},
		},
		ignore_focus = {},
		always_divide_middle = true,
		always_show_tabline = true,
		globalstatus = false,
		refresh = {
			statusline = 1000,
			tabline = 1000,
			winbar = 1000,
			refresh_time = 16, -- ~60fps
			events = {
				"WinEnter",
				"BufEnter",
				"BufWritePost",
				"SessionLoadPost",
				"FileChangedShellPost",
				"VimResized",
				"Filetype",
				"CursorMoved",
				"CursorMovedI",
				"ModeChanged",
			},
		},
	},
	sections = {
		lualine_a = { "mode" },
		lualine_b = { "diagnostics" },
		lualine_c = { "filename" },
		lualine_x = {},
		lualine_y = {},
		lualine_z = {},
	},
	inactive_sections = {
		lualine_a = {},
		lualine_b = {},
		lualine_c = { "filename" },
		lualine_x = { "location" },
		lualine_y = {},
		lualine_z = {},
	},
	tabline = {},
	winbar = {},
	inactive_winbar = {},
	extensions = {},
})
