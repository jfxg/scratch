FROM node:22-slim

# ── System packages ───────────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    ca-certificates \
    python3 \
    python3-pip \
    ripgrep \
    fd-find \
    jq \
    build-essential \
    zsh \
    && rm -rf /var/lib/apt/lists/*

# ── GitHub CLI ────────────────────────────────────────────────────────────────
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
        | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
    && chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
        > /etc/apt/sources.list.d/github-cli.list \
    && apt-get update && apt-get install -y gh \
    && rm -rf /var/lib/apt/lists/*

# ── Claude Code ───────────────────────────────────────────────────────────────
RUN npm install -g @anthropic-ai/claude-code

# ── fd alias (Debian names the binary fdfind) ─────────────────────────────────
RUN ln -s $(which fdfind) /usr/local/bin/fd

# ── Entrypoint script (runs as root before user switch so it's in a stable path)
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# ── Dedicated agent user (UID auto-assigned to avoid conflicts with base image) ─
RUN useradd -m -s /bin/zsh agent \
    && mkdir -p /workspace && chown agent:agent /workspace

USER agent

# ── oh-my-zsh ─────────────────────────────────────────────────────────────────
# Install unattended — the host's .zshrc will be mounted over the generated one
RUN sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended

WORKDIR /workspace
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["zsh"]
