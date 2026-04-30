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

vim.keymap.set("n", "Y", "yy")
vim.keymap.set("n", "D", "dd")
vim.keymap.set("n", "d%", "v%D")

vim.keymap.set("n", "<c-p>", Snacks.picker.files)
