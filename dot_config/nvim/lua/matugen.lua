local M = {}

function M.setup()
	require("base16-colorscheme").setup({
		-- Background tones
		base00 = "#141316", -- Default Background
		base01 = "#211f22", -- Lighter Background (status bars)
		base02 = "#2b292d", -- Selection Background
		base03 = "#948f99", -- Comments, Invisibles
		-- Foreground tones
		base04 = "#cbc4cf", -- Dark Foreground (status bars)
		base05 = "#e6e1e6", -- Default Foreground
		base06 = "#e6e1e6", -- Light Foreground
		base07 = "#e6e1e6", -- Lightest Foreground
		-- Accent colors
		base08 = "#ffb4ab", -- Variables, XML Tags, Errors
		base09 = "#f0b8c6", -- Integers, Constants
		base0A = "#ccc2db", -- Classes, Search Background
		base0B = "#d1bcff", -- Strings, Diff Inserted
		base0C = "#f0b8c6", -- Regex, Escape Chars
		base0D = "#d1bcff", -- Functions, Methods
		base0E = "#ccc2db", -- Keywords, Storage
		base0F = "#93000a", -- Deprecated, Embedded Tags
	})
end

-- Register a signal handler for SIGUSR1 (matugen updates)
local signal = vim.uv.new_signal()
signal:start(
	"sigusr1",
	vim.schedule_wrap(function()
		package.loaded["matugen"] = nil
		require("matugen").setup()
	end)
)

return M
