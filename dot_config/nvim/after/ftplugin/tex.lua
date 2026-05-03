vim.api.nvim_create_autocmd("BufWritePost", {
	pattern = "*.tex",
	callback = function()
		local file = vim.fn.expand("%:p")
		local file_basename = vim.fn.fnamemodify(file, ":t:r")
		local cmd = string.format("pdflatex %s; latexmk -c", file)
		vim.fn.jobstart(cmd, {
			on_exit = function()
				vim.fs.rm(file_basename .. ".aux", { force = true })
				vim.fs.rm(file_basename .. ".log", { force = true })
				vim.fs.rm(file_basename .. ".out", { force = true })
			end,
		})
	end,
})
