vim.g.mapleader = " "
vim.g.localleader = "\\"

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

-- Comment and preserve cursor position
vim.keymap.set("n", "<c-_>", ":let p=getpos('.')<CR>gcc:call setpos('.', p)<CR>", { remap = true })
vim.keymap.set("v", "<c-_>", "gc", { remap = true })
vim.keymap.set("n", "<c-/>", ":let p=getpos('.')<CR>gcc:call setpos('.', p)<CR>", { remap = true })
vim.keymap.set("v", "<c-/>", "gc", { remap = true })

vim.keymap.set("n", "<leader>q", "<c-z>") -- suspend
vim.keymap.set("n", "<a-q>", "<cmd>q<cr>") -- quit
vim.keymap.set("n", "Y", "yy")
vim.keymap.set("n", "D", "dd")
vim.keymap.set("n", "d%", "v%D")
vim.keymap.set("n", "J", "<cmd>let p=getpos('.')<bar>join<bar>call setpos('.', p)<cr>") -- Keeps cursor in place
vim.keymap.set("n", "<", "<<")
vim.keymap.set("n", ">", ">>")
vim.keymap.set("v", "<", "<gv") -- preserve selection
vim.keymap.set("v", ">", ">gv") -- preserve selection
vim.keymap.set("n", "z=", "1z=") --spellcheck
