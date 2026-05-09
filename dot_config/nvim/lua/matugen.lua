local M = {}

function M.setup()
	require("mini.base16").setup({
		palette = {
			-- Background tones
			base00 = "#010409", -- Default Background
			base01 = "#161b22", -- Lighter Background (status bars)
			base02 = "#1e252e", -- Selection Background
			base03 = "#515c67", -- Comments, Invisibles
			-- Foreground tones
			base04 = "#8b949e", -- Dark Foreground (status bars)
			base05 = "#c9d1d9", -- Default Foreground
			base06 = "#c9d1d9", -- Light Foreground
			base07 = "#c9d1d9", -- Lightest Foreground
			-- Accent colors
			base08 = "#f85149", -- Variables, XML Tags, Errors
			base09 = "#bc8cff", -- Integers, Constants
			base0A = "#bc8cff", -- Classes, Search Background
			base0B = "#58a6ff", -- Strings, Diff Inserted
			base0C = "#b580ff", -- Regex, Escape Chars
			base0D = "#80bbff", -- Functions, Methods
			base0E = "#b580ff", -- Keywords, Storage
			base0F = "#8e0700", -- Deprecated, Embedded Tags
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
