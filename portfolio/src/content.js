import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import matter from 'gray-matter';
import { marked } from 'marked';

const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const CONTENT_DIR = path.join(ROOT, 'content');
const DATA_DIR    = path.join(ROOT, 'data');

// ── Data files ────────────────────────────────────────────────

export function getSiteData() {
  return JSON.parse(fs.readFileSync(path.join(DATA_DIR, 'site.json'), 'utf8'));
}

export function getLinks() {
  return JSON.parse(fs.readFileSync(path.join(DATA_DIR, 'links.json'), 'utf8'));
}

// ── Collection readers ────────────────────────────────────────

function readCollection(subdir) {
  const dir = path.join(CONTENT_DIR, subdir);
  return fs.readdirSync(dir)
    .filter(f => f.endsWith('.md'))
    .map(f => {
      const raw = fs.readFileSync(path.join(dir, f), 'utf8');
      const { data, content } = matter(raw);
      return {
        slug: f.replace(/\.md$/, ''),
        url:  `/${subdir}/${f.replace(/\.md$/, '')}/`,
        data,
        content,
      };
    })
    .sort((a, b) => new Date(b.data.date) - new Date(a.data.date));
}

export const getProjects = () => readCollection('projects');
export const getPosts    = () => readCollection('writing');

// ── Single item readers ───────────────────────────────────────

function readItem(subdir, slug) {
  const file = path.join(CONTENT_DIR, subdir, `${slug}.md`);
  if (!fs.existsSync(file)) return null;
  const { data, content } = matter(fs.readFileSync(file, 'utf8'));
  return { data, html: marked.parse(content) };
}

export const getProject  = (slug) => readItem('projects', slug);
export const getPost     = (slug) => readItem('writing', slug);

export function getUsesPage() {
  const { data, content } = matter(
    fs.readFileSync(path.join(CONTENT_DIR, 'uses.md'), 'utf8')
  );
  return { data, html: marked.parse(content) };
}

// ── Helpers ───────────────────────────────────────────────────

export function readableDate(dateVal) {
  if (!dateVal) return '';
  return new Date(dateVal).toLocaleDateString('en-US', {
    year: 'numeric', month: 'long', day: 'numeric',
  });
}
