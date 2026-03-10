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
    projects: content.getProjects(),
    posts:    content.getPosts(),
  }));
});

app.get('/projects/', (req, res) => {
  res.send(tmpl.projectsIndex({ ...ctx(), projects: content.getProjects() }));
});

app.get('/projects/:slug/', (req, res) => {
  const item = content.getProject(safeSlug(req.params.slug));
  if (!item) return res.status(404).send('Not found');
  res.send(tmpl.post({ ...ctx(), ...item.data, contentHtml: item.html }));
});

app.get('/writing/', (req, res) => {
  res.send(tmpl.writingIndex({ ...ctx(), posts: content.getPosts() }));
});

app.get('/writing/:slug/', (req, res) => {
  const item = content.getPost(safeSlug(req.params.slug));
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

app.listen(PORT, () => console.log(`http://localhost:${PORT}`));
