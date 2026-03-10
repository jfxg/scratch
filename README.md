# scratch

Personal scripts, dotfiles, and tooling — including an isolated Docker sandbox for running Claude Code agents.

## Structure

```
bin/                        Scripts, synced to ~/bin via init-shell
shell/                      Zsh config and Oh My Zsh customisations
git/                        Git global config and ignore rules
ssh/                        SSH client config
vim/                        Vim config
portfolio/                  Static portfolio website (11ty + Pico CSS)
```

## Scripts

| Script | Description |
|--------|-------------|
| `backup-shell` | Copies dotfiles from `$HOME` into this repo |
| `init-shell` | Applies repo dotfiles to `$HOME` (dry-run by default, `--apply` to write) |
| `sync-shell-remote` | Compares and syncs shell config to a remote host over SSH (reads from `$HOME`, safe to run from anywhere) |
| `agent` | Spins up an isolated Docker sandbox and runs Claude Code with full permissions (from [jfxg/agent-sandbox](https://github.com/jfxg/agent-sandbox)) |
| `agent-build` | Builds (or rebuilds) the `agent-sandbox` Docker image (from [jfxg/agent-sandbox](https://github.com/jfxg/agent-sandbox)) |

## Dotfiles

| File | Maps to |
|------|---------|
| `shell/.zshrc` | `~/.zshrc` |
| `shell/.zprofile` | `~/.zprofile` |
| `shell/.zshrc.local.example` | Reference template — copy to `~/.zshrc.local` per machine |
| `shell/oh-my-zsh/custom/themes/` | `~/.oh-my-zsh/custom/themes/` |
| `git/.gitconfig` | `~/.gitconfig` |
| `git/ignore` | `~/.config/git/ignore` |
| `ssh/config` | `~/.ssh/config` |
| `vim/.vimrc` | `~/.vimrc` |

Machine-specific shell config (Homebrew paths, work tools, etc.) lives in `~/.zshrc.local` on each machine and is intentionally not tracked here.

## Setup on a new machine

```bash
git clone <this repo> ~/projects/scratch
~/projects/scratch/bin/init-shell          # dry-run: shows what would change
~/projects/scratch/bin/init-shell --apply  # apply dotfiles and sync ~/bin
cp ~/projects/scratch/shell/.zshrc.local.example ~/.zshrc.local
# edit ~/.zshrc.local with machine-specific config
```

After `init-shell --apply`, all scripts are available directly from `~/bin` — no need to reference the repo path. To sync shell config to a remote machine:

```bash
sync-shell-remote user@host          # dry-run: shows what would change
sync-shell-remote --apply user@host  # sync to remote
```

## Portfolio

Static portfolio website with a dashboard homepage, project deep-dives, and a writing/blog section. Served by a lightweight Express.js server, deployed via Docker. See [`portfolio/README.md`](portfolio/README.md) for full usage.

```bash
cd portfolio
npm install && npm run dev   # dev server → http://localhost:3000
docker compose up --build   # or run in Docker (mirrors production)
```

Content lives in `portfolio/content/` as Markdown files. Volume-mounted in Docker so edits are live without a rebuild.

## Agent sandbox

Runs Claude Code in an isolated Docker container with full permissions but no access to your host filesystem beyond what's explicitly mounted. Maintained in the standalone [jfxg/agent-sandbox](https://github.com/jfxg/agent-sandbox) repo; `init-shell` clones it to `~/projects/agent-sandbox` and installs the scripts.

```bash
agent-build              # build the image (once, or after editing the Dockerfile)
agent                    # start an interactive Claude session in a fresh workspace
agent "fix the tests"    # pass a prompt directly
agent --repo ~/code/foo  # mount an existing repo instead of a fresh workspace
agent --shell            # drop into a zsh shell for debugging
```

Sessions and workspaces are preserved at `~/.agent-sandbox/sessions/<session-id>/` after the container exits. See [jfxg/agent-sandbox](https://github.com/jfxg/agent-sandbox) for full usage.
