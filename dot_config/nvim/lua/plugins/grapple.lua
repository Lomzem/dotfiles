vim.pack.add({ "https://github.com/cbochs/grapple.nvim" })
do
	local grapple = require("grapple")
	---@module "grapple"
	---@type grapple.settings
	grapple.setup({
		scope = "cwd",
		icons = false,
		status = true,
	})
	-- if vim.v.argv[3] == "." and grapple.exists({ index = 1 }) then
	-- 	vim.schedule(function()
	-- 		grapple.select({ index = 1 })
	-- 	end)
	-- end
	vim.keymap.set("n", "<leader>a", "<cmd>Grapple tag<cr>")
	vim.keymap.set("n", "<c-e>", "<cmd>Grapple toggle_tags<cr>")
	vim.keymap.set("n", "<leader>A", function()
		grapple.reset({ notify = false })
		grapple.tag()
	end)
	vim.keymap.set("n", "<a-1>", "<cmd>Grapple select index=1<cr>")
	vim.keymap.set("n", "<a-2>", "<cmd>Grapple select index=2<cr>")
	vim.keymap.set("n", "<a-3>", "<cmd>Grapple select index=3<cr>")
	vim.keymap.set("n", "<a-4>", "<cmd>Grapple select index=4<cr>")
	vim.keymap.set("n", "<a-5>", "<cmd>Grapple select index=5<cr>")
	vim.keymap.set("n", "<a-6>", "<cmd>Grapple select index=6<cr>")
	vim.keymap.set("n", "<a-7>", "<cmd>Grapple select index=7<cr>")
	vim.keymap.set("n", "<a-8>", "<cmd>Grapple select index=8<cr>")
	vim.keymap.set("n", "<a-9>", "<cmd>Grapple select index=9<cr>")
end
