# Portfolio

Static portfolio website served by a lightweight Express.js server. Deployable via Docker to a home server or any VPS. Content lives in plain Markdown files.

## Local development

**Without Docker:**
```bash
cd portfolio
npm install
npm run dev     # node --watch, auto-restarts on file changes → http://localhost:3000
```

**With Docker (mirrors production):**
```bash
docker compose up --build
```
The dev override (`docker-compose.override.yml`) is automatically merged, which mounts source directories for live reloading.

## How it works

The server is ~50 lines of Express. There is no build step — Markdown files are read and rendered per request.

```
server.js              # Express app and routes
src/
├── content.js         # Reads Markdown + front matter, renders HTML
└── templates.js       # Page templates as JS template literal functions
content/               # Your Markdown content (volume-mounted in Docker)
│   ├── projects/
│   ├── writing/
│   └── uses.md
data/                  # Site config (volume-mounted in Docker)
│   ├── site.json      # title, tagline, description, URL
│   └── links.json     # GitHub, LinkedIn, etc.
public/
└── css/custom.css     # Style overrides (Pico CSS served from node_modules)
```

### Request flow

1. Express route handler fires (e.g. `GET /projects/my-project/`)
2. `content.js` reads the matching `.md` file, parses front matter with `gray-matter`, renders body with `marked`
3. `templates.js` receives the data and returns a full HTML string via JS template literals
4. Response sent — no files written, no cache

`data/site.json` and `data/links.json` are also re-read per request, so edits to those files take effect immediately without a restart.

### Layouts

Two layouts, composed around a shared `base()` shell:

```
base()        HTML shell: <head>, nav, footer
├── page()    simple titled content page
└── post()    article with date and tag metadata
```

The homepage and listing pages (`/projects/`, `/writing/`) have their own template functions.

## Adding content

### New project

Create `content/projects/my-project.md`:

```markdown
---
title: "Project Name"
date: 2025-06-01
summary: "One-line description shown on the dashboard and listing."
tags:
  - docker
  - tooling
---

Full writeup in Markdown. Available at /projects/my-project/
```

### New blog post

Create `content/writing/my-post.md` — same front matter shape.

### Update links

Edit `data/links.json`. Optional `note` field appears as a subtitle on the links page:

```json
[
  { "label": "GitHub",   "url": "https://github.com/yourusername" },
  { "label": "LinkedIn", "url": "https://linkedin.com/in/yourhandle" },
  { "label": "Email",    "url": "mailto:you@example.com", "note": "preferred" }
]
```

### Update site identity

Edit `data/site.json`:

```json
{
  "title": "Your Name",
  "tagline": "Software engineer. Builder of things.",
  "description": "Meta description used in <head>.",
  "url": "https://yoursite.example.com"
}
```

## Deployment

### Home server

Pushing to `main` automatically builds a multi-platform image (`amd64` + `arm64`) and pushes it to GHCR via `.github/workflows/publish.yml`.

**One-time setup:**

1. **Make the package public** (optional, avoids needing to `docker login` on the server): GitHub → your profile → Packages → `portfolio` → Package settings → Change visibility → Public.

3. **Start the stack:**
   ```bash
   docker compose pull
   docker compose up -d
   ```

**Deploying updates:**

```bash
docker compose pull && docker compose up -d
```

Content changes (`content/`, `data/`) are volume-mounted and live immediately — no pull or restart needed.

### Local Docker

```bash
docker compose up --build
```

### Reverse proxy (optional)

To serve on port 80/443, put Caddy or Nginx in front. Example `Caddyfile`:

```
yoursite.example.com {
    reverse_proxy portfolio:3000
}
```

### Environment variables

| Variable | Default | Description |
|---|---|---|
| `PORT` | `3000` | Port the server listens on |
