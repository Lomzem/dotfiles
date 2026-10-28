# Secret handling

## Active safeguards

This dotfiles repository uses `.githooks/pre-commit` to reject credential filenames
and scan the staged diff with Gitleaks. `.githooks/pre-push` scans all local Git
history, including commits that bypassed the commit hook. Scanner output is fully
redacted. Both checks fail if Gitleaks is missing; the commit hook also needs Python.
Gitleaks is already part of the decman development module.

Enable the hooks after cloning this repository:

```sh
git config --local core.hooksPath .githooks
```

These hooks are specific to this repository. Other repositories need their own
commit checks and CI secret scanning. A local `--no-verify` can bypass hooks, so
enable the hosting provider's push protection too when available. Don't disable
checks to clear a finding; resolve the credential or review a narrowly scoped
false positive instead. Run a manual audit with:

```sh
gitleaks dir --redact=100 --no-banner .
gitleaks git --log-opts=--all --redact=100 --no-banner .
```

The managed `~/.config/git/ignore` excludes local dotenv files and common private
key formats across repositories. This repo also excludes chezmoi source names
such as `private_dot_env`. Sanitized `.env.example`, `.env.sample`, and
`.env.template` files remain allowed and are still scanned. Ignore rules do not
remove already tracked files or history, and `git add -f` bypasses ignores.

Git now caches HTTPS credentials in memory for one hour instead of saving new
credentials in plaintext. You may need to authenticate again after cache expiry
or reboot. Existing `~/.git-credentials` is retained with permissions restricted
to its owner; after confirming replacement authentication works, remove that
legacy file. For persistent storage use an OS keyring-backed credential helper.

## Everyday practice

- Keep real values in a password manager or an untracked local file with mode
  `600`. Supply them only to the process that needs them; avoid exporting all
  credentials from `.zshenv` or `.zshrc`, where every child process inherits them.
- For secrets managed by chezmoi, use password-manager template references or
  `chezmoi add --encrypt`. A `private_` source prefix sets permissions; it does
  **not** encrypt content or prevent Git from tracking it. Set up encryption
  before adding sensitive files.
- Prefer a tool's secure prompt, stdin, or secret-input interface. Avoid literal
  secrets in command arguments, which can appear in process listings and logs.
- New Zsh sessions ignore commands starting with a space in native history;
  Atuin also supports this. This is a fallback, not protection from command
  output, terminal recording, process inspection, or inherited environment values.
- Inspect variable names or whether credentials exist instead of dumping `env`,
  `printenv`, auth files, or HTTP headers. Disable shell tracing around secrets.
  Redact values before sharing logs, diffs, screenshots, or agent context.
- If a value leaks, revoke or rotate it first, then remove copies and coordinate
  any history rewrite. Deleting a working-tree value does not invalidate a key.

## Verification and scope

Initial audit on 2026-10-27: Gitleaks reported no findings in the working tree or
all local Git refs. Disposable-repository checks confirmed clean commits succeed,
forced-added `.env` files are blocked, staged tokens are blocked even when the
working copy is clean, and a token committed without hooks is blocked by the
push check. Test tokens stayed in temporary repositories; output was redacted.
Existing unrelated live Zsh customizations were preserved during activation.

Detection is pattern-based and cannot guarantee that every secret is caught.
No credentials were revoked and no history was rewritten. The retained legacy
credential file still needs removal after replacement authentication is verified.

References: [Gitleaks](https://github.com/gitleaks/gitleaks),
[Git credential helpers](https://git-scm.com/docs/gitcredentials),
[chezmoi encryption](https://www.chezmoi.io/user-guide/encryption/),
[Atuin history exclusions](https://docs.atuin.sh/main/guide/excluding-commands/).
