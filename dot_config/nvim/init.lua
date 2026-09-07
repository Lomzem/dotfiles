vim.g.mapleader = " "
vim.g.maplocalleader = "\\"

vim.o.number = true
vim.o.relativenumber = true
vim.opt.fillchars = { eob = " " }
vim.o.tabstop = 4
vim.o.softtabstop = 4
vim.o.shiftwidth = 4
vim.o.expandtab = true
vim.o.autoindent = true
vim.o.smartindent = true
vim.o.hlsearch = false
vim.o.incsearch = true
vim.o.ignorecase = true
vim.o.smartcase = true
vim.o.wrap = false
vim.o.termguicolors = true
vim.o.updatetime = 60
vim.o.laststatus = 0
vim.o.cmdheight = 0
vim.o.winborder = "rounded"
vim.o.splitright = true
vim.o.splitbelow = true
vim.o.swapfile = false
vim.o.undofile = true

vim.keymap.set("n", "y=", function()
    local lines = vim.api.nvim_buf_get_lines(0, 0, -1, false)
    local joined_lines = vim.fn.join(lines, "\n")
    joined_lines = vim.fn.trim(joined_lines)
    vim.fn.setreg("+", joined_lines)
    vim.notify("Copied to clipboard", vim.log.levels.INFO)
end) -- Copy all
vim.keymap.set({ "n", "v", "x" }, "<leader>y", function()
    vim.cmd("normal! y")
    local reg = vim.fn.getreg('"')
    local trimmed = vim.fn.trim(reg)
    vim.fn.setreg("+", trimmed)
end, { silent = true })

vim.keymap.set("n", "<c-u>", "<c-u>zz")
vim.keymap.set("n", "<c-d>", "<c-d>zz")
vim.keymap.set("n", "H", "_")
vim.keymap.set("n", "L", "$")
vim.keymap.set("n", "<a-q>", "<cmd>q<cr>")
vim.keymap.set("n", "<c-s>", "<cmd>w<cr>")
vim.keymap.set("i", "<c-s>", "<esc><cmd>w<cr>")
vim.keymap.set("i", "<c-c>", "<esc>")
vim.keymap.set("n", "Y", "yy")
vim.keymap.set("n", "D", "dd")
vim.keymap.set("n", "J", "<cmd>let p=getpos('.')<bar>join<bar>call setpos('.', p)<cr>")
vim.keymap.set("n", "<", "<<")
vim.keymap.set("n", ">", ">>")
vim.keymap.set("v", "<", "<gv")
vim.keymap.set("v", ">", ">gv")
vim.keymap.set("n", "z=", "1z=")

vim.keymap.set("n", "<leader>e", vim.diagnostic.open_float)
vim.keymap.set("n", "K", vim.lsp.buf.hover)
vim.keymap.set("n", "<a-p>", function() vim.diagnostic.jump({ count = -1 }) end)
vim.keymap.set("n", "<a-n>", function() vim.diagnostic.jump({ count = 1 }) end)

-- Bootstrap lazy.nvim
local lazypath = vim.fn.stdpath("data") .. "/lazy/lazy.nvim"
if not (vim.uv or vim.loop).fs_stat(lazypath) then
    local lazyrepo = "https://github.com/folke/lazy.nvim.git"
    local out = vim.fn.system({ "git", "clone", "--filter=blob:none", "--branch=stable", lazyrepo, lazypath })
    if vim.v.shell_error ~= 0 then
        vim.api.nvim_echo({
            { "Failed to clone lazy.nvim:\n", "ErrorMsg" },
            { out, "WarningMsg" },
            { "\nPress any key to exit..." },
        }, true, {})
        vim.fn.getchar()
        os.exit(1)
    end
end
vim.opt.rtp:prepend(lazypath)
require("lazy").setup({
    spec = {
        {
            "rose-pine/neovim",
            name = "rose-pine",
            config = function() vim.cmd("colorscheme rose-pine-moon") end,
        },
        {
            "folke/lazydev.nvim",
            ft = "lua",
            opts = {
                library = {
                    { path = "${3rd}/luv/library", words = { "vim%.uv" } },
                },
            },
        },
        {
            "mason-org/mason-lspconfig.nvim",
            opts = {},
            dependencies = {
                { "mason-org/mason.nvim", opts = {} },
                "neovim/nvim-lspconfig",
            },
        },
        {
            "WhoIsSethDaniel/mason-tool-installer.nvim",
            opts = {
                ensure_installed = {
                    "clang-format",
                    "clangd",
                    "kdlfmt", -- niri
                    "lua-language-server",
                    "stylua",
                },
            },
        },
        {
            "dmtrKovalenko/fff",
            lazy = false,
            build = function() require("fff.download").download_or_build_binary() end,
            opts = {},
            keys = {
                { "<c-p>", function() require("fff").find_files() end },
                { "<leader>ps", function() require("fff").live_grep() end },
                { "<leader>pc", function() require("fff").live_grep_under_cursor() end, mode = { "n", "x" } },
            },
        },
        {
            "stevearc/conform.nvim",
            opts = {
                format_on_save = { timeout_ms = 500, lsp_format = "fallback" },
                formatters_by_ft = {
                    lua = { "stylua" },
                    kdl = { "kdlfmt" },
                },
            },
        },
        {
            "saghen/blink.cmp",
            dependencies = {
                "saghen/blink.lib",
            },
            build = function() require("blink.cmp").build():pwait() end,

            ---@module 'blink.cmp'
            ---@type blink.cmp.Config
            opts = {
                keymap = { preset = "default" },
                completion = { documentation = { auto_show = false } },
                sources = { default = { "lsp", "path", "snippets", "buffer" } },
                fuzzy = { implementation = "rust" },
                cmdline = {
                    keymap = { preset = "inherit" },
                    completion = { menu = { auto_show = true } },
                },
            },
        },
        {
            { "nvim-mini/mini.ai", opts = {} },
            { "nvim-mini/mini.pairs", opts = {} },
            { "nvim-mini/mini.surround", opts = {} },
        },
        {
            "cbochs/grapple.nvim",
            dependencies = { "nvim-tree/nvim-web-devicons", lazy = true },
            opts = { scope = "cwd" },
            cmd = "Grapple",
            keys = {
                { "<leader>a", "<cmd>Grapple toggle<cr>" },
                { "<c-e>", "<cmd>Grapple toggle_tags<cr>" },
                { "<a-1>", "<cmd>Grapple select index=1<cr>" },
                { "<a-2>", "<cmd>Grapple select index=2<cr>" },
                { "<a-3>", "<cmd>Grapple select index=3<cr>" },
                { "<a-4>", "<cmd>Grapple select index=4<cr>" },
            },
        },
        {
            "folke/snacks.nvim",
            opts = {
                notifier = { enabled = true },
                input = { enabled = true },
                picker = { enabled = true },
            },
        },
        {
            "folke/noice.nvim",
            event = "VeryLazy",
            opts = {
                lsp = {
                    override = {
                        ["vim.lsp.util.convert_input_to_markdown_lines"] = true,
                        ["vim.lsp.util.stylize_markdown"] = true,
                    },
                },
            },
            dependencies = {
                "MunifTanjim/nui.nvim",
                "rcarriga/nvim-notify",
            },
            checker = { enabled = true },
        },
    },
})
vim.keymap.set("n", "<leader>lz", "<cmd>Lazy<cr>")

vim.api.nvim_create_autocmd("VimEnter", {
    callback = function()
        if vim.fn.argc() ~= 0 then return end
        vim.schedule(function() pcall(require("grapple").select, { index = 1 }) end)
    end,
})
