# Chezmoi maintenance

This checkout is the source state; applications read the installed files under
the user's home. Before applying a change, compare its source and live config
with `chezmoi diff` for the affected paths. Preserve live edits in the source,
then apply only the reviewed paths. Keybindings and workspace assignments are
user-owned behavior; preserve them during visual changes.

# Rice changes

Read [the rice guide](dot_config/rice/README.md) before changing palette
generation, app adapters, fonts, transparency, or browser styles. It owns the
current workflow and application limitations. Edit templates and central
settings, then regenerate outputs through `rice`; generated themes are runtime
files. Palette approval belongs to the user, including after regeneration.

For prior decisions or regression evidence, consult the relevant sections of
[RICE.json](RICE.json). It is chronological: later follow-up decisions supersede
earlier requirements and version-specific findings need rechecking against the
installed app. Record new decisions, verification and remaining work there at
handoffs.

For controller changes, run `python3 -m unittest discover -s tests/rice`.
Keep lifecycle and preservation regressions on the public CLI seams documented
in `RICE.json`; disposable HOME/XDG fixtures keep tests off the live desktop.

For transparency changes, verify the composited desktop as well as app output.
An app screenshot can contain correct alpha while an opaque decoration behind
the window hides the wallpaper. Native background alpha is preferred so text
stays opaque; the guide describes the compositor fallbacks.
For native UI automation, verify the target control has keyboard focus before
pressing Return; window focus alone does not establish DevTools focus.

For browser-style changes, verify the actual Helium profile with its installed
Stylus and Dark Reader settings. The controller suite proves rendering and
transactions, while native UI checks establish selector coverage and extension
behavior. Preserve existing styles and exclusions through extension UIs and
export/merge/import flows; browser profile databases remain private runtime data.
