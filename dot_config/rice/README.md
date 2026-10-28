# Wallpaper themes and fonts

`rice` generates a wallpaper palette, checks its contrast, saves your approved
adjustments, and applies it across the desktop. Approved palettes are associated
with the image contents, so renaming an image does not regenerate its colors.

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
- Fuzzel, Zathura, Yazi, GTK, and Qt pick up changes when reopened. Zathura
  recolors documents by default; **Ctrl+R** restores original document colors.
- Helium's local launcher and desktop entry load the generated theme and font
  bridge on the next normal browser launch. The bridge refreshes default and
  fixed-width fonts every 30 seconds. After later palette changes, reload the
  Rice theme at `helium://extensions` or reopen Helium. Browser chrome uses the
  system font. rice never edits the live browser Preferences file.
- T3 publishes the generated **Rice** environment theme. Select it once in
  Settings → Appearance; later color changes update that stable theme. All four
  interface/composer/code/terminal font preferences are updated, preserving sizes.
  Already-open clients may need reopening for font changes.
- Vesktop's enabled theme list gains `rice.theme.css`; other enabled themes and
  settings are retained. Its running client may need reopening.
- Qt6ct is declared in decman. `QT_QPA_PLATFORMTHEME=qt6ct` reaches applications
  started from Niri after the next login. Qt5 is not installed on this machine.
- Native transparent backgrounds keep text opaque. Helium, T3, Vesktop, Zathura,
  and matching GTK windows use mild whole-window opacity where necessary; this
  also fades their content. Niri rules can be adjusted for individual apps.
- Noctalia's lock screen blurs its own wallpaper; it never shows the unlocked
  session through the lock surface.

Noctalia's stock wallpaper picker is guarded by a wallpaper-change hook. It may
briefly display an unfamiliar image before the hook restores the current one;
use the rice gallery for review before any wallpaper change.

## Configuration and recovery

| Location | Purpose |
| --- | --- |
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
