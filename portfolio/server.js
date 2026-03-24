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
// User images (avatar, project photos) — volume-mounted in Docker
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
    pages: content.getPages(),
  }));
});

app.get('/pages/', (req, res) => {
  res.send(tmpl.pagesIndex({ ...ctx(), pages: content.getPages() }));
});

app.get('/pages/:slug/', (req, res) => {
  const item = content.getPage(safeSlug(req.params.slug));
  if (!item) return res.status(404).send('Not found');
  res.send(tmpl.post({ ...ctx(), ...item.data, contentHtml: item.html }));
});


app.get('/uses/', (req, res) => {
  const item = content.getUsesPage();
  res.send(tmpl.page({ ...ctx(), title: item.data.title || 'Uses', contentHtml: item.html }));
});

app.get('/links/', (req, res) => {
  res.send(tmpl.linksPage(ctx()));
});

app.use((req, res) => res.status(404).send('Not found'));

app.listen(PORT, () => console.log(`Service started successfully on port ${PORT}`));
