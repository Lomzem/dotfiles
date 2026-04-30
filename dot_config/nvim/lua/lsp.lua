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

vim.pack.add({
    "https://github.com/stevearc/conform.nvim" -- formatter
})
require("conform").setup({
    format_on_save = {
            timeout_ms = 500,
    lsp_format = "fallback",
    async = true,
    },
    formatters_by_ft = {
        lua = {"stylua"},
    },
})
