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

// ── Posts collection ──────────────────────────────────────────
// Defined in content/posts.json — array of { title, description, content, thumbnail }.
// content is a path to a .md file relative to content/; slug is derived from its filename.

function readPostsJson() {
  return JSON.parse(fs.readFileSync(path.join(CONTENT_DIR, 'posts.json'), 'utf8'));
}

export function getPosts() {
  return readPostsJson().map(data => {
    const slug = path.basename(data.content, '.md');
    return { slug, url: `/posts/${slug}/`, data };
  });
}

export function getPost(slug) {
  const data = readPostsJson().find(p => path.basename(p.content, '.md') === slug);
  if (!data) return null;
  const mdFile = path.join(CONTENT_DIR, data.content);
  const html = fs.existsSync(mdFile)
    ? marked.parse(fs.readFileSync(mdFile, 'utf8'))
    : '';
  return { data, html };
}

export function getStaticPage(name) {
  const { data, content } = matter(
    fs.readFileSync(path.join(CONTENT_DIR, `${name}.md`), 'utf8')
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
