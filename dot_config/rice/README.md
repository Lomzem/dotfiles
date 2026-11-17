# Wallpaper themes and fonts

`rice` generates a wallpaper palette, checks its contrast, saves your approved
adjustments, and applies it across the desktop. Approved palettes are associated
with the image contents, so renaming an image does not regenerate its colors.

## Use Rice from Zsh

Run `rice` for the current setup and common commands, or `rice --help` for
the full command list. Zsh completes wallpaper names and installed fonts.

```sh
rice list
rice check mitsuha --json
rice use mitsuha
rice edit mitsuha
```

`check`, `use`, and `edit` accept a wallpaper name from `rice list` or an
image path. Use unique image stems in your wallpaper directories. `check`
writes a PNG preview to the Rice cache and reports any failed contrast or hue
checks with suggested fixes. The JSON includes the preview path and the
supported color and opacity roles.

`use` loads `~/.config/rice/palettes/NAME.json` first, then looks for an
approved profile matching the image contents, then generates a palette.
It applies only a passing palette. `edit` opens the named JSON file using
`VISUAL` or `EDITOR`, starting from the approved or generated colors on first
edit. Saving a passing palette and exiting the editor applies it. Failed
checks leave the file available for further edits. Run `rice check` for a
preview before applying a palette edited outside the CLI.

Named files use `colors` and `opacity` with `panels` and `terminal` keys.
Missing opacity values inherit the approved profile's settings or Rice's
82% defaults. You can track a named palette with
`chezmoi add ~/.config/rice/palettes/NAME.json`. `rice reapply` reloads
the active named file and keeps the previous setup available for `rice restore`.
The Noctalia gallery and wallpaper hook use the approved profiles below.

## Choose and review

**Mod+Shift+W** opens the Noctalia wallpaper gallery. Approved images apply their
saved palette. New images get a draft with **Report**, **Preview**, and **Approve**
actions. The **Fonts** button opens a graphical font chooser.

```sh
rice draft ~/mitsuha.jpeg
rice report ~/mitsuha.jpeg
rice set ~/mitsuha.jpeg primary=#a2c9ff alpha.terminal=0.9
rice preview ~/mitsuha.jpeg
rice restore
rice approve ~/mitsuha.jpeg --name Mitsuha --apply
chezmoi add ~/.config/rice/profiles
```

Drafts are never approved automatically. Review the HTML report before approving.
`rice draft IMAGE --regenerate` starts another candidate while keeping the
approved revision intact. The next approval saves a new revision.

The report checks controlled text and UI colors against WCAG AA contrast
thresholds: 4.5:1 for ordinary text and 3:1 for meaningful UI indicators. It uses
full-resolution wallpaper bounds for transparent surfaces and preserves semantic
red, yellow, and green. Approval and application refuse failing controlled pairs.
Noctalia's floating panels use the most transparent native preset that passes
those checks. This measures theme colors; it does not certify arbitrary web
content, PDF illustrations, application icons, or compositor-faded windows.

## Change fonts everywhere

```sh
rice fonts --pick
rice fonts --interface Inter --monospace "JetBrainsMono Nerd Font"
rice fonts
chezmoi add ~/.config/rice/settings.json
```

Both choices are independent of wallpapers and palettes. Only installed font
families are accepted. Existing application font sizes are preserved; Qt preserves existing sizes and other preferences; a new
configuration starts at 11 points. Kitty, terminal Neovim/Yazi, Fuzzel, Noctalia,
GTK, Qt, T3 Code, Vesktop, and Helium's default/fixed-width browser preferences
use the central choices. Websites can specify their own fonts.

## Switch and restore

```sh
rice select IMAGE         # apply its approved palette, or prepare a draft
rice wallpaper IMAGE      # change wallpaper while keeping the current palette
rice palette Mitsuha      # use a named palette on the current wallpaper
rice restore              # restore the setup before the preview/change
rice reapply              # render again after editing templates
rice status
rice list
```

Wallpaper-only and named-palette changes also check contrast against the chosen
wallpaper. Repeated previews retain the setup from before the first preview.
The first application captures existing files and font preferences, including
absent files and symlinks. Required Noctalia IPC failures roll back generated
files and preferences; incomplete recovery is explicitly reported. rice never
restarts working applications.

## Application behavior

- Kitty, Noctalia, and Niri reload live. Neovim sessions started with this config
  watch the generated colorscheme. Existing Neovim sessions from before setup
  need the updated config loaded or a new session.
- Television uses the generated `rice` theme on its next launch. Its selected
  row sits on a checked surface rather than ANSI bright black, which this palette
  keeps for light comment text.
- Fuzzel, Zathura, Yazi, GTK, and Qt pick up changes when reopened. Zathura
  recolors documents by default; **Ctrl+R** restores original document colors.
- Helium's local launcher and desktop entry load the generated theme and font
  bridge on the next normal browser launch. The bridge refreshes default and
  fixed-width fonts every 30 seconds. After later palette changes, reload the
  Rice theme at `helium://extensions` or reopen Helium. Browser chrome uses the
  system font. rice never edits the live browser Preferences file.
- T3 publishes the generated **Rice** environment theme. Select it once in
  Settings → Appearance. Rice maps the interface colors and adds the wallpaper
  behind the conversation, tinted at the panel opacity. T3's Zsh terminals
  load the Rice ANSI colors at startup and refresh them on the next prompt
  after a palette change. Rice keeps all four T3 font sizes while updating the
  families. Already-open clients may need reopening for font changes.
- Vesktop's enabled theme list gains `rice.theme.css`; other enabled themes and
  settings are retained. Vencord reloads generated CSS live, including interface
  and code font families, while preserving Discord's text sizes. Native window
  transparency is enabled for the next full Vesktop relaunch; rice leaves the
  running app open. One background uses the central panel alpha, with transparent
  structural layers and solid controls, menus and dialogs. Niri blurs the
  wallpaper behind it without fading text or icons.
  If an older theme overrides the colors, check Vencord's QuickCSS and other
  enabled themes. On this machine the old generated Catppuccin QuickCSS was
  disabled through **Settings → Vencord → Enable Custom CSS**; its file is retained.
- Qt6ct is declared in decman. `QT_QPA_PLATFORMTHEME=qt6ct` reaches applications
  started from Niri after the next login. Qt5 is not installed on this machine.
- Prefer native background alpha so text/icons stay opaque. Kitty uses its own
  `background_opacity` (currently 82%); Neovim/Yazi inherit that terminal surface.
  Fuzzel and Noctalia use their native surface alpha. Niri has no blanket window
  fade. Only Helium and T3 Code use a 90% whole-window fallback on Linux, where
  their current main windows lack native background-only transparency.
  **Mod+Shift+O** toggles that fallback; fullscreen content remains opaque.
- Noctalia's lock screen blurs its own wallpaper; it never shows the unlocked
  session through the lock surface.

Noctalia's stock wallpaper picker is guarded by a wallpaper-change hook. It may
briefly display an unfamiliar image before the hook restores the current one;
use the rice gallery for review before any wallpaper change.

## Configuration and recovery

| Location | Purpose |
| --- | --- |
| `~/.config/rice/palettes/*.json` | Editable palettes for the named CLI workflow |
| `~/.config/rice/profiles/*.json` | Approved palette revisions; add to chezmoi |
| `~/.config/rice/settings.json` | Central fonts and wallpaper directories |
| `~/.local/lib/rice/` | Controller and application templates |
| `~/.local/share/rice/` | Native picker and browser font bridge |
| `~/.local/state/rice/` | Drafts, reports, original-file snapshots and active state |

Generated app themes are runtime output. Edit a draft with `rice set`, the central
fonts with `rice fonts`, or the templates in chezmoi, then run `rice reapply`.
Noctalia's GUI overrides can otherwise mask the managed theme/font settings;
rice removes only the keys it owns and verifies unrelated settings survive.
Palettes, generator settings and revisions remain available when caches are removed.

If application fails, read the reported error before retrying. `rice restore`
restores the previous setup. Recovery snapshots are private files under
`~/.local/state/rice/backups`; retain them until you are satisfied with the change.

## Glass and website styles

Niri blurs window backgrounds and visible popups against the wallpaper. Noctalia
requests its own native blur regions as panels draw; forcing compositor blur on
its surfaces causes wallpaper flashes during transitions and blurs the desktop
through its invisible fullscreen click shield. Only Fuzzel needs the explicit
launcher layer blur rule. Hollow focus rings keep Chromium/Electron windows from
revealing a solid ring fill instead of the wallpaper. Background-only alpha is preferred: Kitty controls its
own 82% background opacity and keeps text fully opaque. Fuzzel and Noctalia also
control their own surface alpha. The only whole-window opacity rules are explicit
90% fallbacks for Helium and T3 Code; other apps are not faded by the compositor.
Fullscreen windows retain normal opacity. **Mod+Shift+O** toggles
the compositor opacity rule for the focused window, so photographs, video or a
low-contrast application can be made opaque immediately. This does not change
Kitty's native alpha. Existing keybindings are preserved.

`rice reapply` also generates four Stylus UserCSS files under
`~/.local/share/rice/userstyles`: `github.user.css`, `google.user.css`,
`duckduckgo.user.css`, and `youtube.user.css`. They use approved colors for page,
card, text, selection and accent roles. GitHub retains native diff semantics;
YouTube retains video, thumbnails and player colors. Google targets the search
and homepage hosts listed in its stylesheet, leaving accounts and other Google
products alone. Keep Google Search → Settings → Other settings → Dark theme
set to **On** as the native base. The stylesheet also covers nested AI Overview
text roles, collapsed/expanded fade masks, source cards and metadata. Website markup changes may require selector updates.

Install these local files using Stylus with **Allow access to file URLs** enabled.
The installer records the source file as the update URL; `@updateURL file:`
metadata is intentionally omitted because Stylus rejects it. Enable **Check for
updates** in each installer. After a palette change, use Stylus's **Check all
styles for updates**, or wait for its hourly checks (configured in the current browser). Keeping a local installer
tab open with live reload enabled gives immediate updates. Stable style names
and namespaces let reinstallations replace the existing style.

Dark Reader provides fallback on other sites. Its generated
`darkreader.patch.json` is a patch, not a full import. Export existing settings
from Dark Reader → Settings → Advanced, then merge:

```sh
rice darkreader ~/Downloads/Dark-Reader-Settings.json \
  --output ~/Downloads/Dark-Reader-Rice.json
```

Import the resulting file in the same Advanced screen. The merge preserves
existing site exclusions, per-site themes, fonts and unrelated preferences;
adds the styled domains to the exclusions; sets dark background/text, selection
and scrollbar colors; and keeps Dark Reader from replacing the browser theme.
The source export and existing output files are never overwritten. Use a fresh
export and a new output filename for later changes. Dark Reader imports are a
separate step because the installed extension has no supported external settings
API. Browser settings backups remain private under
`~/.local/state/rice/browser-backups`, outside the dotfiles repository.
