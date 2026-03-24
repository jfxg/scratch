import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';
import * as content from './src/content.js';
import * as tmpl from './src/templates.js';

const app  = express();
const PORT = process.env.PORT || 3000;
const ROOT = path.dirname(fileURLToPath(import.meta.url));

// ── Static assets ─────────────────────────────────────────────
// Pico CSS from node_modules, custom styles from public/
app.use('/css', express.static(path.join(ROOT, 'node_modules/@picocss/pico/css')));
app.use(express.static(path.join(ROOT, 'public')));
// User images (avatar, post thumbnails) — volume-mounted in Docker
app.use('/images', express.static(path.join(ROOT, 'content/images')));

// ── Shared context (re-read per request so edits take effect without restart) ─
const ctx = () => ({
  site:  content.getSiteData(),
  links: content.getLinks(),
});

// Sanitise URL slugs to prevent path traversal
const safeSlug = (s) => s.replace(/[^a-z0-9-_]/gi, '');

// ── Routes ────────────────────────────────────────────────────

app.get('/', (req, res) => {
  res.send(tmpl.home({
    ...ctx(),
    posts: content.getPosts(),
  }));
});

app.get('/posts/', (req, res) => {
  res.send(tmpl.postsIndex({ ...ctx(), posts: content.getPosts() }));
});

app.get('/posts/:slug/', (req, res) => {
  const item = content.getPost(safeSlug(req.params.slug));
  if (!item) return res.status(404).send('Not found');
  res.send(tmpl.post({ ...ctx(), ...item.data, contentHtml: item.html }));
});

app.get('/experience/', (req, res) => {
  const item = content.getStaticPage('experience');
  res.send(tmpl.page({ ...ctx(), title: 'Experience', contentHtml: item.html }));
});


app.get('/links/', (req, res) => {
  res.send(tmpl.linksPage(ctx()));
});

app.use((req, res) => res.status(404).send('Not found'));

app.listen(PORT, () => console.log(`Service started successfully on port ${PORT}`));
