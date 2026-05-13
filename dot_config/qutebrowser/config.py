# qute://help/configuring.html#configpy

from dataclasses import dataclass


# Misc
c.zoom.default = "110%"
c.colors.webpage.darkmode.enabled = True
c.url.searchengines["DEFAULT"] = "https://unduck.link?q={}"
c.url.default_page = "file:///home/lomzem/coding/startpage/dist/index.html"
c.url.start_pages = ["file:///home/lomzem/coding/startpage/dist/index.html"]
c.content.user_stylesheets = ["~/.config/qutebrowser/styles/global.css"]

# Files Command
c.fileselect.handler = "external"
FILE_SELECT_COMMAND = ["kitty", "/home/lomzem/.local/bin/yazi-picker", "{}"]
c.fileselect.multiple_files.command = FILE_SELECT_COMMAND
c.fileselect.single_file.command = FILE_SELECT_COMMAND

# Tabs
c.tabs.position = "right"
c.tabs.width = "7%"

# Fonts
c.fonts.default_family = "monospace"
c.fonts.default_size = "13pt"
c.fonts.web.size.minimum = 18

# Binds: misc
config.bind("<ctrl-,>", "config-source")
config.bind("<alt-shift-d>", "config-cycle colors.webpage.darkmode.enabled true false")
config.bind("<space>nd", "clear-messages")
config.bind("gh", "cmd-set-text --space :help")

# Binds: tabs
config.bind("<alt-k>", "tab-prev")
config.bind("<alt-j>", "tab-next")
config.bind("<ctrl-tab>", "tab-next")
config.bind("<ctrl-shift-tab>", "tab-prev")
config.bind("x", "tab-close")
config.bind("<ctrl-t>", "cmd-set-text --space :open -t")

# Binds: history
config.bind("<alt-h>", "back")
config.bind("<alt-l>", "forward")

# Binds: navigation
config.bind("k", "scroll-px 0 -100")
config.bind("j", "scroll-px 0 100")

# half page
config.bind("u", "scroll-px 0 -1000")
config.bind("d", "scroll-px 0 1000")

# Colors


@dataclass
class Theme:
    bg: str
    fg: str
    card: str


# https://github.com/vague-theme/vague
THEME = Theme(
    bg="#141415",
    fg="#cdcdcd",
    card="#333738",
)

c.colors.tabs.bar.bg = THEME.bg
c.colors.tabs.even.bg = THEME.bg
c.colors.tabs.odd.bg = THEME.bg
c.colors.tabs.selected.even.bg = THEME.card
c.colors.tabs.selected.odd.bg = THEME.card

c.colors.statusbar.url.fg = THEME.fg
c.colors.statusbar.url.success.http.fg = THEME.fg
c.colors.statusbar.url.success.https.fg = THEME.fg
