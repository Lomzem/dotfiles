local M = {}

function M.setup()
	require("base16-colorscheme").setup({
		-- Background tones
		base00 = "#181212", -- Default Background
		base01 = "#241e1e", -- Lighter Background (status bars)
		base02 = "#2f2828", -- Selection Background
		base03 = "#a08c8c", -- Comments, Invisibles
		-- Foreground tones
		base04 = "#d7c1c1", -- Dark Foreground (status bars)
		base05 = "#ece0df", -- Default Foreground
		base06 = "#ece0df", -- Light Foreground
		base07 = "#ece0df", -- Lightest Foreground
		-- Accent colors
		base08 = "#ffb4ab", -- Variables, XML Tags, Errors
		base09 = "#e5c18d", -- Integers, Constants
		base0A = "#e6bdbc", -- Classes, Search Background
		base0B = "#ffb3b4", -- Strings, Diff Inserted
		base0C = "#e5c18d", -- Regex, Escape Chars
		base0D = "#ffb3b4", -- Functions, Methods
		base0E = "#e6bdbc", -- Keywords, Storage
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
