import { readableDate } from './content.js';

// ── Base HTML shell ───────────────────────────────────────────

function base({ site, links, title, description, body }) {
  const pageTitle = title && title !== 'Home'
    ? `${title} — ${site.title}`
    : site.title;

  const navTitle = (!title || title === 'Home') ? site.title : title;
  const navLink = (label, href) => label === title
    ? `<span class="nav-current">${label}</span>`
    : `<a href="${href}">${label}</a>`;

  const footerLinks = links
    .map((l, i) =>
      `<a href="${l.url}" target="_blank" rel="noopener noreferrer">${l.label}</a>` +
      (i < links.length - 1 ? ' &middot; ' : '')
    )
    .join('');

  return `<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${pageTitle}</title>
  <meta name="description" content="${description || site.description}">
  <link rel="stylesheet" href="/css/pico.min.css">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
  <link rel="stylesheet" href="/css/custom.css">
</head>
<body>
  <header class="container site-header">
    <nav>
      <ul>
        <li>
          <a href="/" class="nav-brand">
            <strong class="nav-page-title">${navTitle}</strong>
            <small class="nav-tagline">${site.tagline}</small>
          </a>
        </li>
      </ul>
      <ul class="nav-links">
        <li>${navLink('Home', '/')}</li>
        <li>${navLink('Pages', '/pages/')}</li>
        <li>${navLink('Links', '/links/')}</li>
      </ul>
    </nav>
  </header>
  ${body}
  <footer class="container site-footer">
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
    ${meta ? `<header>${meta}</header>` : ''}
    ${ctx.contentHtml}
  </article>
</main>`,
  });
}

// ── Homepage dashboard ────────────────────────────────────────

export function home({ site, links, pages }) {
  const linkButtons = links
    .map(l => l.icon
      ? `<a href="${l.url}" target="_blank" rel="noopener noreferrer" class="icon-btn" aria-label="${l.label}" title="${l.label}"><i class="${l.icon}" aria-hidden="true"></i></a>`
      : `<a href="${l.url}" target="_blank" rel="noopener noreferrer" role="button" class="outline secondary">${l.label}</a>`)
    .join('\n      ');

  function cards(items) {
    if (!items.length) return '<p><em>Coming soon.</em></p>';
    return `<div class="card-grid">` +
      items.slice(0, 3).map(p => `
      <a href="${p.url}" class="card">
        <article>
          <h3>${p.data.title}</h3>
          ${p.data.thumbnail ? `<img src="${p.data.thumbnail}" alt="${p.data.title}" class="card-thumbnail">` : ''}
          <p>${p.data.description || ''}</p>
        </article>
      </a>`).join('') +
      `</div>`;
  }

  return base({
    site, links, title: 'Home',
    body: `<main class="container">
  <section class="intro">
    <div class="intro-text">
      <p class="tagline">${site.description}</p>
      <div class="intro-links">
        ${linkButtons}
      </div>
    </div>
    ${site.avatar ? `<img src="${site.avatar}" alt="Profile picture" class="profile-pic">` : ''}
  </section>

  <section class="dashboard-section">
    <div class="section-header">
      <h2>Pages</h2><a href="/pages/">All pages &rarr;</a>
    </div>
    ${cards(pages)}
  </section>

</main>`,
  });
}

// ── Pages index ───────────────────────────────────────────────

export function pagesIndex({ site, links, pages }) {
  const cards = pages.length
    ? `<div class="card-grid">` +
      pages.map(p => `
    <a href="${p.url}" class="card">
      <article>
        ${p.data.thumbnail ? `<img src="${p.data.thumbnail}" alt="${p.data.title}" class="card-thumbnail">` : ''}
        <h3>${p.data.title}</h3>
        <p>${p.data.description || ''}</p>
      </article>
    </a>`).join('') +
      `</div>`
    : '<p><em>Coming soon.</em></p>';

  return base({
    site, links, title: 'Pages',
    body: `<main class="container">${cards}</main>`,
  });
}

// ── Links page ────────────────────────────────────────────────

export function linksPage({ site, links }) {
  const items = links.map(l => `
    <li>
      <a href="${l.url}" target="_blank" rel="noopener noreferrer" class="links-list-item">
        ${l.icon ? `<i class="${l.icon}" aria-hidden="true"></i>` : ''}
        <span>${l.label}</span>
      </a>
      ${l.note ? `<small>${l.note}</small>` : ''}
    </li>`).join('');

  return base({
    site, links, title: 'Links',
    body: `<main class="container">
  <ul class="links-list">${items}</ul>
</main>`,
  });
}
