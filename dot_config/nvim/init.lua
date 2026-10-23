vim.g.mapleader = " "
vim.g.maplocalleader = "\\"

-- Load trusted project settings (including ESP32 rust-analyzer configuration).
vim.o.exrc = true

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
vim.opt.linebreak = true
vim.opt.linebreak = true
vim.opt.breakindentopt = "shift:2"
vim.opt.conceallevel = 1
vim.opt.guicursor = ""

local transparent = true

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
vim.keymap.set("n", "<c-/>", "gcc", { remap = true })
vim.keymap.set("v", "<c-/>", "gc", { remap = true })

vim.keymap.set("n", "<leader>e", vim.diagnostic.open_float)
vim.keymap.set("n", "U", function() vim.lsp.buf.code_action() end)
-- vim.keymap.set("n", "K", vim.lsp.buf.hover) -- using pretty_hover
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
            {
                "catppuccin/nvim",
                name = "catppuccin",
                cond = false,
                config = function()
                    require("catppuccin").setup({
                        transparent_background = transparent,
                    })
                    vim.cmd.colorscheme("catppuccin-mocha")
                end,
            },
            {
                "rose-pine/neovim",
                name = "rose-pine",
                config = function()
                    require("rose-pine").setup({
                        styles = {
                            transparency = transparent,
                            italic = false,
                        },
                    })
                    vim.cmd("colorscheme rose-pine")
                end,
            },
            {
                "rebelot/kanagawa.nvim",
                cond = false,
                config = function() vim.cmd.colorscheme("kanagawa") end,
            },
            {
                "decaycs/decay.nvim",
                name = "decay",
                cond = false,
                config = function() vim.cmd.colorscheme("decayce") end,
            },
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
            "nvim-lualine/lualine.nvim",
            dependencies = { "nvim-tree/nvim-web-devicons" },
            opts = {
                sections = {
                    lualine_b = {},
                    lualine_c = { { "filename", path = 1 } },
                    lualine_x = { "diagnostics" },
                    lualine_y = {},
                },
            },
        },
        {
            "Fildo7525/pretty_hover",
            event = "LspAttach",
            opts = {},
            keys = { {
                "K",
                function() require("pretty_hover").hover() end,
            } },
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
                    "basedpyright", -- python
                    "clang-format", -- c
                    "clangd", -- c
                    "json-lsp", -- json
                    "kdlfmt", -- niri
                    "lua-language-server", -- lua
                    "prettier", -- javascript
                    "ruff", -- python
                    "shfmt", -- shell
                    "stylua", -- lua
                    "tombi", -- toml
                },
            },
        },
        {
            "dmtrKovalenko/fff",
            lazy = false,
            build = function() require("fff.download").download_or_build_binary() end,
            opts = {},
            keys = {
                {
                    "<c-p>",
                    function() require("fff").find_files() end,
                },
                {
                    "<leader>ps",
                    function() require("fff").live_grep() end,
                },
                {
                    "<leader>pc",
                    function() require("fff").live_grep_under_cursor() end,
                    mode = { "n", "x" },
                },
            },
        },
        {
            "stevearc/conform.nvim",
            event = { "BufWrite" },
            cmd = "Format",
            keys = {
                {
                    "<leader>f",
                    function() vim.cmd("Format") end,
                    mode = { "n", "v", "x" },
                },
            },
            config = function()
                require("conform").setup({
                    format_on_save = function(bufnr)
                        local disabled_filetypes = {}

                        local filetype = vim.bo[bufnr].filetype

                        for _, disabled in ipairs(disabled_filetypes) do
                            if filetype == disabled then return nil end
                        end

                        return {
                            timeout_ms = 500,
                            lsp_format = "fallback",
                        }
                    end,
                    formatters_by_ft = {
                        c = { "clang-format" },
                        cpp = { "clang-format" },
                        javascript = { "prettier" },
                        kdl = { "kdlfmt" },
                        lua = { "stylua" },
                        python = { "ruff" },
                        toml = { "tombi" },
                        zsh = { "shfmt" },
                    },
                })
                vim.api.nvim_create_user_command("Format", function(args)
                    local range = nil
                    if args.count ~= -1 then
                        local end_line = vim.api.nvim_buf_get_lines(0, args.line2 - 1, args.line2, true)[1]
                        range = {
                            start = { args.line1, 0 },
                            ["end"] = { args.line2, end_line:len() },
                        }
                    end
                    require("conform").format({ async = true, lsp_format = "fallback", range = range })
                end, { range = true })
            end,
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
            {
                "nvim-mini/mini.splitjoin",
                opts = {
                    mappings = {
                        toggle = "<leader>j",
                    },
                },
            },
            {
                "nvim-mini/mini.surround",
                opts = {
                    mappings = {
                        add = "S",
                        delete = "ds",
                        replace = "cs",
                    },
                },
            },
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
        -- Lazy
        {
            "dlyongemallo/diffview-plus.nvim",
            version = "*",
            cmd = {
                "DiffviewOpen",
                "DiffviewToggle",
                "DiffviewFileHistory",
                "DiffviewDiffFiles",
                "DiffviewLog",
            },
        },
        {
            "folke/snacks.nvim",
            opts = {
                input = { enabled = true },
                notifier = { enabled = true },
                picker = { enabled = true },
            },
            keys = {
                {
                    "<leader>lg",
                    function() Snacks.lazygit() end,
                },
                {
                    "gd",
                    function() Snacks.picker.lsp_definitions() end,
                },
                {
                    "gr",
                    function() Snacks.picker.lsp_references() end,
                },
                {
                    "gm",
                    function() Snacks.picker.lsp_symbols() end,
                },
                {
                    "gM",
                    function() Snacks.picker.lsp_workspace_symbols() end,
                },
            },
        },
        {
            "supermaven-inc/supermaven-nvim",
            config = function()
                require("supermaven-nvim").setup({
                    keymaps = {
                        accept_suggestion = "<right>",
                    },
                })
            end,
        },
        {
            "mikavilpas/yazi.nvim",
            version = "*", -- use the latest stable version
            event = "VeryLazy",
            dependencies = {
                { "nvim-lua/plenary.nvim", lazy = true },
            },
            keys = {
                {
                    "<leader>pv",
                    mode = { "n", "v" },
                    "<cmd>Yazi<cr>",
                },
            },
            ---@type YaziConfig | {}
            opts = {
                -- if you want to open yazi instead of netrw, see below for more info
                open_for_directories = true,
                keymaps = {
                    show_help = "<f1>",
                },
            },
            -- 👇 if you use `open_for_directories=true`, this is recommended
            init = function()
                -- mark netrw as loaded so it's not loaded at all.
                --
                -- More details: https://github.com/mikavilpas/yazi.nvim/issues/802
                vim.g.loaded_netrwPlugin = 1
            end,
        },
    },
})
vim.keymap.set("n", "<leader>lz", "<cmd>Lazy<cr>")

vim.lsp.enable("rust_analyzer")

vim.api.nvim_create_autocmd("VimEnter", {
    callback = function()
        local buf = vim.api.nvim_get_current_buf()
        local blank = vim.api.nvim_buf_line_count(buf) == 1 and vim.api.nvim_buf_get_lines(buf, 0, 1, false)[1] == ""
        if vim.fn.argc() ~= 0 or not blank then return end
        vim.schedule(function()
            if require("grapple").exists({ index = 1 }) then pcall(require("grapple").select, { index = 1 }) end
        end)
    end,
})
