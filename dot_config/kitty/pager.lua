-- nvim as kitty's scrollback_pager. Invoked from kitty.conf.
--
-- kitty pipes history plus the current screen with ANSI colors, pads the dump
-- out to the full screen height with blank lines, then appends escapes that
-- restore the cursor position. Feeding that straight into a terminal and
-- jumping to the end parks the view in that padding.

-- Drop the trailing padding and the cursor-restore escapes.
local lines = vim.api.nvim_buf_get_lines(0, 0, -1, false)
while #lines > 0 and lines[#lines]:gsub("\27%[[%d;?]*%a", ""):match("^%s*$") do
	table.remove(lines)
end

-- Neovim's built-in nvim.terminal TermOpen autocmd turns the gutter off for
-- every terminal buffer, so put back whatever init.lua set globally.
local function gutter()
	vim.wo.number = vim.go.number
	vim.wo.relativenumber = vim.go.relativenumber
end

vim.api.nvim_buf_set_lines(0, 0, -1, false, {})
local channel = vim.api.nvim_open_term(0, {})
gutter()

-- Pin the gutter width. It otherwise widens as the line count grows, and the
-- grid is sized once, below.
vim.wo.numberwidth = math.max(4, #tostring(#lines) + 2)

-- nvim_open_term sizes the grid to the whole window and ignores the gutter, so
-- the rightmost columns would land off-screen. A window resize sizes it to the
-- text area instead, so nudge it while the grid is still empty.
pcall(vim.cmd, "vsplit | close")
gutter()

vim.api.nvim_chan_send(channel, table.concat(lines, "\r\n"))

-- chan_send writes on the event loop, so the buffer is still an empty grid at
-- this point. Wait for the line count to settle, which takes 20-30ms.
if #lines > 0 then
	local previous = -1
	vim.wait(5000, function()
		local n = vim.fn.prevnonblank(vim.fn.line("$"))
		if n > 0 and n == previous then
			return true
		end
		previous = n
		return false
	end, 10)
end

vim.bo.modified = false
vim.keymap.set("n", "q", "ZQ", { buffer = 0 })

-- Put the last line of output at the bottom of the window.
vim.api.nvim_win_set_cursor(0, { math.max(vim.fn.prevnonblank(vim.fn.line("$")), 1), 0 })
vim.cmd("normal! zb")
