# scratch

A personal collection of scripts and dotfile backups.

## Structure

```
bin/          Shell scripts and utilities
shell/        Zsh config and Oh My Zsh customisations
git/          Git global config and ignore rules
```

## bin

| Script | Description |
|--------|-------------|
| `backup-shell` | Copies dotfiles and shell configs from `$HOME` into this repo |

## Dotfiles

| File | Source |
|------|--------|
| `shell/.zshrc` | `~/.zshrc` |
| `shell/.zprofile` | `~/.zprofile` |
| `shell/oh-my-zsh/custom/themes/` | `~/.oh-my-zsh/custom/themes/` |
| `git/.gitconfig` | `~/.gitconfig` |
| `git/ignore` | `~/.config/git/ignore` |

## Usage

Run `bin/backup-shell` to pull the latest configs from your home directory into this repo, then commit the changes.
