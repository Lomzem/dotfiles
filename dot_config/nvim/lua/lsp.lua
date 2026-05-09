vim.pack.add({ "https://github.com/neovim/nvim-lspconfig" })

local installed_lsp = {
	"basedpyright",
	"clangd",
	"cssls",
	"html",
	"jsonls",
	"lua_ls",
	"svelte",
	"tailwindcss",
	"texlab",
	"tinymist",
	"tombi",
	"tsgo",
}
for _, lsp in ipairs(installed_lsp) do
	vim.lsp.enable(lsp)
end

-- formatter
vim.pack.add({
	"https://github.com/stevearc/conform.nvim",
})
require("conform").setup({
	format_after_save = {
		timeout_ms = 500,
		lsp_format = "fallback",
		async = true,
	},
	formatters_by_ft = {
		lua = { "stylua" },
		tex = { "tex-fmt" },
		python = { "ruff_format" },
	},
})

-- completion
vim.pack.add({ "https://github.com/saghen/blink.lib", "https://github.com/saghen/blink.cmp" })
require("blink.cmp").build():wait(60000)
require("blink.cmp").setup({
	keymap = {
		preset = "none",
		["<c-p>"] = { "select_prev", "fallback" },
		["<c-n>"] = { "select_next", "fallback" },
		["<c-l>"] = { "select_and_accept", "fallback" },

		["<C-u>"] = { "scroll_documentation_up", "fallback" },
		["<C-d>"] = { "scroll_documentation_down", "fallback" },

		["<c-e>"] = { "hide", "fallback" },
		["<c-space>"] = { "show", "show_documentation", "hide_documentation" },
		["<A-1>"] = {
			function(cmp)
				cmp.accept({ index = 1 })
			end,
		},
		["<A-2>"] = {
			function(cmp)
				cmp.accept({ index = 2 })
			end,
		},
		["<A-3>"] = {
			function(cmp)
				cmp.accept({ index = 3 })
			end,
		},
		["<A-4>"] = {
			function(cmp)
				cmp.accept({ index = 4 })
			end,
		},
		["<A-5>"] = {
			function(cmp)
				cmp.accept({ index = 5 })
			end,
		},
		["<A-6>"] = {
			function(cmp)
				cmp.accept({ index = 6 })
			end,
		},
		["<A-7>"] = {
			function(cmp)
				cmp.accept({ index = 7 })
			end,
		},
		["<A-8>"] = {
			function(cmp)
				cmp.accept({ index = 8 })
			end,
		},
		["<A-9>"] = {
			function(cmp)
				cmp.accept({ index = 9 })
			end,
		},
		["<A-0>"] = {
			function(cmp)
				cmp.accept({ index = 10 })
			end,
		},
	},
	cmdline = {
		keymap = {
			preset = "inherit",
		},
		completion = {
			menu = { auto_show = true },
		},
	},
	completion = {
		menu = {
			draw = {
				columns = { { "item_idx" }, { "kind_icon" }, { "label", "label_description", gap = 1 } },
				components = {
					item_idx = {
						text = function(ctx)
							return ctx.idx == 10 and "0" or ctx.idx >= 10 and " " or tostring(ctx.idx)
						end,
						highlight = "BlinkCmpItemIdx", -- optional, only if you want to change its color
					},
				},
			},
		},
	},
})
