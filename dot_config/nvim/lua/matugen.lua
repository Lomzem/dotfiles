local M = {}

function M.setup()
	require("mini.base16").setup({
		palette = {
			-- Background tones
			base00 = "#161616", -- Default Background
			base01 = "#262626", -- Lighter Background (status bars)
			base02 = "#303030", -- Selection Background
			base03 = "#636363", -- Comments, Invisibles
			-- Foreground tones
			base04 = "#dde1e6", -- Dark Foreground (status bars)
			base05 = "#f2f4f8", -- Default Foreground
			base06 = "#f2f4f8", -- Light Foreground
			base07 = "#f2f4f8", -- Lightest Foreground
			-- Accent colors
			base08 = "#ee5396", -- Variables, XML Tags, Errors
			base09 = "#be95ff", -- Integers, Constants
			base0A = "#42be65", -- Classes, Search Background
			base0B = "#33b1ff", -- Strings, Diff Inserted
			base0C = "#b180ff", -- Regex, Escape Chars
			base0D = "#80ceff", -- Functions, Methods
			base0E = "#96e9ad", -- Keywords, Storage
			base0F = "#8c023e", -- Deprecated, Embedded Tags
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
