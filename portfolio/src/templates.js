import { readableDate } from './content.js';

// ── Base HTML shell ───────────────────────────────────────────

function base({ site, links, title, description, body }) {
  const pageTitle = title && title !== 'Home'
    ? `${title} — ${site.title}`
    : site.title;

  const footerLinks = links
    .map((l, i) =>
      `<a href="${l.url}" target="_blank" rel="noopener noreferrer">${l.label}</a>` +
      (i < links.length - 1 ? ' &middot; ' : '')
    )
    .join('');

  return `<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${pageTitle}</title>
  <meta name="description" content="${description || site.description}">
  <link rel="stylesheet" href="/css/pico.min.css">
  <link rel="stylesheet" href="/css/custom.css">
</head>
<body>
  <header class="container-fluid site-header">
    <nav>
      <ul><li><a href="/" class="site-title">${site.title}</a></li></ul>
      <ul>
        <li><a href="/projects/">Projects</a></li>
        <li><a href="/writing/">Writing</a></li>
        <li><a href="/uses/">Uses</a></li>
        <li><a href="/links/">Links</a></li>
      </ul>
    </nav>
  </header>
  ${body}
  <footer class="container-fluid site-footer">
    <small>${footerLinks}</small>
  </footer>
</body>
</html>`;
}

// ── Page layout ───────────────────────────────────────────────

export function page(ctx) {
  return base({
    ...ctx,
    body: `<main class="container">
  <article>
    <header><h1>${ctx.title}</h1></header>
    ${ctx.contentHtml}
  </article>
</main>`,
  });
}

// ── Post layout (article with date + tags) ────────────────────

export function post(ctx) {
  const displayTags = (ctx.tags || [])
    .filter(t => t !== 'project' && t !== 'writing')
    .map(t => `<span class="tag">${t}</span>`)
    .join(' ');

  const meta = ctx.date
    ? `<p class="post-meta"><small>${readableDate(ctx.date)}</small>` +
      (displayTags ? ` &nbsp;&middot;&nbsp; ${displayTags}` : '') +
      `</p>`
    : '';

  return base({
    ...ctx,
    body: `<main class="container">
  <article class="post">
    <header>
      <h1>${ctx.title}</h1>
      ${meta}
    </header>
    ${ctx.contentHtml}
  </article>
</main>`,
  });
}

// ── Homepage dashboard ────────────────────────────────────────

export function home({ site, links, projects, posts }) {
  const linkButtons = links
    .map(l => `<a href="${l.url}" target="_blank" rel="noopener noreferrer" role="button" class="outline secondary">${l.label}</a>`)
    .join('\n      ');

  function cards(items, urlFn) {
    if (!items.length) return '<p><em>Coming soon.</em></p>';
    return `<div class="card-grid">` +
      items.slice(0, 3).map(p => `
      <a href="${p.url}" class="card">
        <article>
          <h3>${p.data.title}</h3>
          ${p.data.date ? `<p><small>${readableDate(p.data.date)}</small></p>` : ''}
          <p>${p.data.summary || ''}</p>
        </article>
      </a>`).join('') +
      `</div>`;
  }

  return base({
    site, links, title: 'Home',
    body: `<main class="container">
  <section class="intro">
    <h1>${site.title}</h1>
    <p class="tagline">${site.tagline}</p>
    <div class="intro-links">
      ${linkButtons}
    </div>
  </section>

  <section class="dashboard-section">
    <div class="section-header">
      <h2>Projects</h2><a href="/projects/">All projects &rarr;</a>
    </div>
    ${cards(projects)}
  </section>

  <section class="dashboard-section">
    <div class="section-header">
      <h2>Writing</h2><a href="/writing/">All posts &rarr;</a>
    </div>
    ${cards(posts)}
  </section>
</main>`,
  });
}

// ── Projects index ────────────────────────────────────────────

export function projectsIndex({ site, links, projects }) {
  const cards = projects.length
    ? `<div class="card-grid">` +
      projects.map(p => `
    <a href="${p.url}" class="card">
      <article>
        <h3>${p.data.title}</h3>
        <p>${p.data.summary || ''}</p>
      </article>
    </a>`).join('') +
      `</div>`
    : '<p><em>Projects coming soon.</em></p>';

  return base({
    site, links, title: 'Projects',
    body: `<main class="container"><h1>Projects</h1>${cards}</main>`,
  });
}

// ── Writing index ─────────────────────────────────────────────

export function writingIndex({ site, links, posts }) {
  const items = posts.length
    ? `<ul>` +
      posts.map(p => `
    <li>
      <a href="${p.url}">${p.data.title}</a>
      ${p.data.date ? `<small> &mdash; ${readableDate(p.data.date)}</small>` : ''}
      ${p.data.summary ? `<br><small>${p.data.summary}</small>` : ''}
    </li>`).join('') +
      `</ul>`
    : '<p><em>Writing coming soon.</em></p>';

  return base({
    site, links, title: 'Writing',
    body: `<main class="container"><h1>Writing</h1>${items}</main>`,
  });
}

// ── Links page ────────────────────────────────────────────────

export function linksPage({ site, links }) {
  const items = links.map(l => `
    <li>
      <a href="${l.url}" target="_blank" rel="noopener noreferrer">${l.label}</a>
      ${l.note ? `<br><small>${l.note}</small>` : ''}
    </li>`).join('');

  return base({
    site, links, title: 'Links',
    body: `<main class="container">
  <article>
    <header><h1>Links</h1></header>
    <ul class="links-list">${items}</ul>
  </article>
</main>`,
  });
}
