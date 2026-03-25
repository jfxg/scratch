# Portfolio

Static portfolio website served by a lightweight Express.js server. Deployable via Docker to a home server or any VPS. Content lives in Markdown files and JSON config.

## Local development

**Without Docker:**
```bash
npm install
npm run dev     # node --watch, auto-restarts on file changes → http://localhost:3000
```

**With Docker (mirrors production):**
```bash
docker compose up --build
```
The dev override (`docker-compose.override.yml`) is automatically merged, which mounts source directories for live reloading.

## How it works

The server is ~50 lines of Express. There is no build step — content files are read and rendered per request.

```
server.js              # Express app and routes
src/
├── content.js         # Reads content files, renders Markdown to HTML
└── templates.js       # Page templates as JS template literal functions
content/               # Your content (volume-mounted in Docker)
├── posts.json         # List of post tiles (title, description, content path, thumbnail)
├── posts/             # Markdown files for individual posts
├── experience.md      # Experience / CV page content
└── images/            # Images for avatar and post thumbnails (served at /images/)
data/                  # Site config (volume-mounted in Docker)
├── site.json          # Title, short title, description, URL, nav pages
└── links.json         # GitHub, LinkedIn, Email, etc.
public/
└── css/custom.css     # Style overrides (Pico CSS served from node_modules)
```

### Request flow

1. Express route handler fires
2. `content.js` reads the matching file(s), renders Markdown with `marked`
3. `templates.js` receives the data and returns a full HTML string
4. Response sent — no files written, no cache

All files under `content/` and `data/` are re-read per request, so edits take effect immediately without a restart.

### Layouts

```
base()          HTML shell: <head>, nav, footer
├── page()      plain content page (used for nav pages like Experience)
└── post()      article with optional date and tag metadata
```

The homepage and posts index have their own template functions.

## Adding content

### New post tile

Post tiles appear on the homepage and at `/posts/`. Each tile is defined by an entry in `content/posts.json` pointing to a Markdown file.

**1. Add an entry to `content/posts.json`:**

```json
[
  {
    "title": "My Project",
    "description": "Short description shown on the tile.",
    "content": "posts/my-project.md",
    "thumbnail": "/images/my-project.jpg"
  }
]
```

- `thumbnail` is optional — tiles render fine without one.
- The slug and URL (`/posts/my-project/`) are derived from the `content` filename.

**2. Create the Markdown file at `content/posts/my-project.md`:**

```markdown
## Overview

Full writeup in Markdown here.
```

No front matter needed — all metadata lives in `posts.json`.

### New nav page

Nav pages are top-level pages linked in the navbar (e.g. Experience, Links).

**1. Add the page to the `pages` array in `data/site.json`:**

```json
{
  "title": "About",
  "path": "/about/",
  "tagline": "A short tagline shown in the navbar."
}
```

**2. Create the content file at `content/about.md`.**

**3. Add a route in `server.js`:**

```js
app.get('/about/', (req, res) => {
  const item = content.getStaticPage('about');
  res.send(tmpl.page({ ...ctx(), title: 'About', contentHtml: item.html }));
});
```

### Update links

Edit `data/links.json`. The optional `icon` field takes a Font Awesome class and renders as an icon on the homepage and links page. The optional `note` field appears as a subtitle on the links page.

```json
[
  { "label": "GitHub",   "url": "https://github.com/yourusername",       "icon": "fa-brands fa-github" },
  { "label": "LinkedIn", "url": "https://linkedin.com/in/yourhandle",    "icon": "fa-brands fa-linkedin" },
  { "label": "Email",    "url": "mailto:you@example.com",                "icon": "fa-solid fa-envelope" }
]
```

### Update site identity

Edit `data/site.json`:

```json
{
  "title": "Your Name",
  "shortTitle": "YN",
  "description": "Meta description used in <head> and on the homepage.",
  "url": "https://yoursite.example.com",
  "avatar": "/images/profile.jpg",
  "pages": [
    { "title": "Home",       "path": "/",            "tagline": "..." },
    { "title": "Posts",      "path": "/posts/",      "tagline": "..." },
    { "title": "Experience", "path": "/experience/", "tagline": "..." },
    { "title": "Links",      "path": "/links/",      "tagline": "..." }
  ]
}
```

- `shortTitle` is currently unused but reserved for abbreviation use.
- `avatar` is optional — remove the field to hide the profile picture.
- `pages` drives both the navbar links and the per-page tagline shown under the title.

### Add images

Drop image files into `content/images/` and reference them as `/images/filename.jpg`. This directory is volume-mounted in Docker so images can be added without rebuilding.

## Deployment

### Home server

Pushing to `main` automatically builds a multi-platform image (`amd64` + `arm64`) and pushes it to GHCR via `.github/workflows/publish.yml`.

**One-time setup:**

1. **Make the package public** (optional, avoids needing to `docker login` on the server): GitHub → your profile → Packages → `portfolio` → Package settings → Change visibility → Public.

2. **Start the stack:**
   ```bash
   docker compose pull
   docker compose up -d
   ```

**Deploying updates:**

```bash
docker compose pull && docker compose up -d
```

Content changes (`content/`, `data/`) are volume-mounted and live immediately — no pull or restart needed.

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
