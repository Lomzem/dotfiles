local M = {}

function M.setup()
	require("mini.base16").setup({
		palette = {
			-- Background tones
			base00 = "#111415", -- Default Background
			base01 = "#1d2021", -- Lighter Background (status bars)
			base02 = "#272a2c", -- Selection Background
			base03 = "#899296", -- Comments, Invisibles
			-- Foreground tones
			base04 = "#bfc8cb", -- Dark Foreground (status bars)
			base05 = "#e1e3e4", -- Default Foreground
			base06 = "#e1e3e4", -- Light Foreground
			base07 = "#e1e3e4", -- Lightest Foreground
			-- Accent colors
			base08 = "#ffb4ab", -- Variables, XML Tags, Errors
			base09 = "#c0c4eb", -- Integers, Constants
			base0A = "#b2cad3", -- Classes, Search Background
			base0B = "#58d6f7", -- Strings, Diff Inserted
			base0C = "#c0c4eb", -- Regex, Escape Chars
			base0D = "#58d6f7", -- Functions, Methods
			base0E = "#b2cad3", -- Keywords, Storage
			base0F = "#93000a", -- Deprecated, Embedded Tags
		},
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
