vim.pack.add({
    "https://github.com/catppuccin/nvim",
    "https://github.com/folke/snacks.nvim",
})

vim.cmd("colorscheme catppuccin-mocha")

-- line numbers
vim.o.number = false
vim.o.relativenumber = false
vim.opt.fillchars = { eob = " " }

-- tabs and indenting
vim.o.tabstop = 4
vim.o.softtabstop = 4
vim.o.shiftwidth = 4
vim.o.expandtab = true
vim.o.autoindent = true
vim.o.smartindent = true

-- searching
vim.o.hlsearch = false
vim.o.incsearch = true
vim.o.ignorecase = true
vim.o.smartcase = true

-- appearance
vim.o.wrap = false
vim.o.termguicolors = true
vim.o.updatetime = 60
vim.o.laststatus = 0
vim.o.cmdheight = 0
vim.o.winborder = "single"

-- splits
vim.o.splitright = true
vim.o.splitbelow = true

-- misc
vim.o.swapfile = false
vim.o.undofile = true

require("snacks").setup({
    bigfile = { enabled = true },
    picker = { enabled = true },
})

require("binds")
