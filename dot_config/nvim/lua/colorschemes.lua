vim.pack.add({ "https://github.com/catppuccin/nvim" })
vim.pack.add({ "https://github.com/ellisonleao/gruvbox.nvim" })
vim.pack.add({ "https://github.com/nyoom-engineering/oxocarbon.nvim" })
vim.pack.add({ "https://github.com/projekt0n/github-nvim-theme" })
vim.pack.add({ "https://github.com/rebelot/kanagawa.nvim" })
vim.pack.add({ "https://github.com/rose-pine/neovim" })
vim.pack.add({ "https://github.com/vague-theme/vague.nvim" })
vim.pack.add({ "https://github.com/olivercederborg/poimandres.nvim" })
vim.pack.add({ "https://github.com/sainnhe/gruvbox-material" })

require("kanagawa").setup({
	overrides = function()
		return {
			-- Replace "#16161D" with your preferred color or "NONE" for transparency
			Normal = { bg = "#14141a" },
		}
	end,
})

vim.cmd("colorscheme kanagawa")
