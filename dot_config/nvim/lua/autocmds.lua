local group = vim.api.nvim_create_augroup("lomzem", { clear = true })

vim.api.nvim_create_autocmd("BufWritePost", {
	group = group,
	pattern = "*/chezmoi/**",
	callback = function()
		vim.system({ "chezmoi", "apply" }, { text = true, detach = true })
	end,
})
