# pstack catch-up skills — 2026-11-03

Installed `bro`, `ketchup`, and `ketchup-video` from `cursor/plugins` revision
`6ea74587e384e1a8035c09ae33a46fe3f881eb9b`. Source files live under
`dot_agents/skills/{bro,ketchup,ketchup-video}`; each directory includes its
MIT license, pinned provenance, and Codex manual-invocation metadata.

Decisions: preserve the upstream workflows with small portability edits.
Claude Code retains `disable-model-invocation: true`; Codex uses
`policy.allow_implicit_invocation: false`. Use `/bro`, `/ketchup`, and
`/ketchup-video` in Claude Code, or the corresponding `$name` in Codex.
The existing global Claude/Codex skill symlinks share `~/.agents/skills`.
Replaced `/visualize` with available plotting tools, clarified the video
skill's direct reference to Ketchup, and added terminal artifact links and
rendering preflight. No Cursor plugin or model configuration was installed.

Verification: parsed all three YAML frontmatters and Codex policies; checked
local Markdown links and license bytes; read the recursive built-in chezmoi
diff before applying only the three new directories. All 12 installed files
match source byte-for-byte through `.agents`, `.claude`, and `.codex`.
The recursive post-apply diff is empty. FFmpeg and ffprobe are installed.
The configured external diff tool rejected a directory target, so review used
`chezmoi --use-builtin-diff --no-pager diff -r`.

The Laziness Protocol kept this to three skills and existing discovery links;
Prove It Works required comparing the actual installed files. No model session
was launched and no catch-up video was rendered; workflow behavior remains to
be exercised on the next invocation. Fully redacted Gitleaks scans of the working
tree and all local Git history passed. Shipping is authorized directly to the
chezmoi repository; the Git history records the resulting commit.
