# agent-sandbox

Run Claude Code in an isolated Docker container with full permissions but no access to your host filesystem beyond what's explicitly mounted.

Sessions and workspaces are stored in `~/.agent-sandbox/` and persist after the container exits so you can resume or retrieve artifacts.

## Installation

Copy the scripts to `~/bin` and the Docker files to `~/agent-sandbox`:

```bash
cp bin/agent bin/agent-build ~/bin/
chmod +x ~/bin/agent ~/bin/agent-build
cp -r docker/ ~/.agent-sandbox/docker/
```

Make sure `~/bin` is in your PATH, then build the image:

```bash
agent-build
```

**Dependencies:** Docker, `jq` (`brew install jq`), and a working [Claude Code](https://claude.ai/code) login on your host.

## Usage

```bash
agent                        # fresh workspace, interactive Claude session
agent "fix the tests"        # pass a prompt directly
agent --name myproject       # label the session
agent --repo owner/repo      # clone a GitHub repo into the workspace
agent --repo ~/code/foo      # mount an existing local repo
agent --shell                # drop into a zsh shell instead of Claude
agent --resume <session-id>  # resume a previous session
```

### Session management

```bash
agent ls                     # list all sessions, newest first
agent rm <session-id>        # remove a session and its workspace
agent clean                  # remove unnamed sessions older than 7 days
agent clean --days 0         # remove all unnamed sessions
```

### Ollama backend

```bash
agent --ollama http://192.168.1.50:11434
# or set OLLAMA_BASE_URL and just pass --ollama
```

### Rebuild the image

```bash
agent-build            # normal build
agent-build --no-cache # force full layer rebuild
```

## Session storage

Each session lives at `~/.agent-sandbox/<session-id>/`:

```
~/.agent-sandbox/
  docker/           ← Dockerfile + entrypoint (installed by init-shell / copied manually)
  sessions/
    20240315-143022-workspace-unnamed/
      session.json  ← session metadata
      workspace/    ← files created during the session
    20240315-160000-myrepo-feature/
      session.json
      workspace/    ← cloned repo lives here
```

For mounted local repos (`--repo ~/path/to/repo`), the workspace is the original directory and is never deleted by `agent rm` or `agent clean`.

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `AGENT_SANDBOX_DIR` | `~/.agent-sandbox/docker` | Where `agent-build` looks for the Dockerfile |
| `OLLAMA_BASE_URL` | — | Default Ollama URL for `--ollama` |
| `DOCKER_CONTEXT` | system default | Docker context (e.g. `desktop-linux` for Docker Desktop on Mac) |
