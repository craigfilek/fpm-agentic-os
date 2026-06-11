# DESIGN.md

The one file you read before building any web page in this rig. Read this, then build. No Figma, no guessing.

**Scope (council decision, 2026-06-05):** this kit is the **calm / product** voice only. The **loud** voice (memes / social posts) lives in a separate file, `brand.css` — do NOT mix the two on one page. If a page ever truly needs both (e.g. a loud hero on an otherwise calm page), revisit this boundary then.

## 1 · The one rule (most important)

**Every page links `build-a.css` and uses only its tokens and classes. Never hardcode a color or a font. Never fork or copy the CSS into a page.**

```html
<link rel="stylesheet" href="build-a.css">
```

`build-a.css` is the single source of truth. If a page needs a color, a radius, a shadow, or a font, it already exists as a token. Use the token. If you think you need a new component, that is a deliberate add to `build-a.css` — not a one-off `<style>` in the page.

## 2 · Tokens (use these, not raw values)

All live in `:root` in `build-a.css`. Reach them with `var(--name)`.

- **Text:** `--color-text`, `--color-text-secondary`, `--color-text-heading`, `--color-text-disabled`
- **Accent:** `--color-accent`, `--color-accent-hover`
- **Surfaces:** `--color-bg-page`, `--color-bg-input`, `--color-bg-hover`, `--color-bg-menu`, `--color-bg-menu-active`
- **Lines + placeholder:** `--color-border`, `--color-placeholder`
- **Radii:** `--radius-sm` (4px), `--radius-md` (8px), `--radius-pill` (100px)
- **Shadow:** `--shadow-subtle`
- **Fonts:** `--font` (Open Sans, the workhorse), `--mono` (IBM Plex Mono, for labels/code)

Rule: never write `#69749c` or `'Open Sans'` in a page. Write `var(--color-accent)` and `var(--font)`. That is how themes stay alive.

## 3 · Themes

Three themes. They all swap the SAME tokens, so anything built on tokens just works.

- **Light** — the default. No attribute needed.
- **Sand** — `<html data-theme="sand">` (the real Build A look).
- **Dark** — `<html data-theme="dark">`.

Add the toggle by copying the `.tt` block and this script (from `styleguide.html`):

```html
<div class="tt" id="tt">
  <button data-set="light">Light</button>
  <button data-set="sand">Sand</button>
  <button data-set="dark">Dark</button>
</div>
<script>
function setTheme(t){if(t==="light")document.documentElement.removeAttribute("data-theme");
  else document.documentElement.setAttribute("data-theme",t);localStorage.setItem("sift-theme",t);
  [...document.querySelectorAll("#tt button")].forEach(b=>b.classList.toggle("on",b.dataset.set===t));}
[...document.querySelectorAll("#tt button")].forEach(b=>b.onclick=()=>setTheme(b.dataset.set));
setTheme(localStorage.getItem("sift-theme")||"light");
</script>
```

## 4 · Components (real classes — use these, don't invent)

- `.pill` — a mono chip / tag. `.pill.solid` = accent fill (active/primary tag). `.pill.soft` = quiet grey tag.
- `.card` — white surface, soft border, 8px radius, subtle shadow. Use for any section or box.
- `.btn` / `button` — secondary button. Add `.primary` (`.btn.primary`) for the main action.
- `.label` — tiny mono uppercase label, for field/detail captions.
- `table` / `th` / `td` / `thead th` — styled out of the box; just write a plain `<table>`.
- `a` — links are styled (accent, bold, underline on hover); just use `<a>`.
- **App-shell pieces:** `.appbar` (sticky top header), `.brand` + `.brand .slash` + `.brand .sub` (logo + " / " + view name), `.tt` + `.tt button.on` (theme toggle).
- **Sidebar nav:** `.menu` (left column), `.menu.right` (right column), `.menu section`, `.menu .mh` (section header), `.menu .mi` (a nav item) + `.mi.on` (active), `.menu .note` (a side note).
- **Body:** `.bodywrap` (the center content area inside the shell).
- **Doc widths:** `.wrap` (760px centered), `.wide` (1180px centered).

## 5 · Two layouts (pick one)

**(a) App-shell** — for consoles and dashboards. Sticky header + 3-column grid.

```html
<div class="appbar"><div class="brand">◆ SIFT <span class="slash">/</span> <span class="sub">view</span></div> ...tt... </div>
<div class="app">
  <nav class="menu"> ...sections + .mi items... </nav>
  <main class="bodywrap"> ...content... </main>
  <aside class="menu right"> ...notes... </aside>
</div>
```

`.app` is `grid-template-columns:256px 1fr 284px`. It collapses to one column under 1000px. Use when the page has navigation and tools around the content.

**(b) Simple centered doc** — for posts, reference, and reading pages. A single column.

```html
<div class="appbar"> ...brand + tt... </div>
<div class="doc">  <!-- or class="wrap" -->
  <header><h1>Title</h1><div class="meta">subtitle</div></header>
  ...content in <h2>, <p>, .card...
</div>
```

Use this when the page is just text to read (like `styleguide.html`). Reach for it first — most pages are docs, not consoles.

## 6 · Voice

Write like the styleguide page: plain, 11th-grade, short sentences, low jargon. Say the thing. One idea per line. No filler, no buzzwords.

## 7 · How to make a new page (4 steps)

1. **Copy the template** — start from `styleguide.html` (doc) or `sift.html` (app-shell).
2. **Link the CSS** — keep `<link rel="stylesheet" href="build-a.css">`. Nothing else.
3. **Pick a layout** — doc for reading, app-shell for a console (section 5).
4. **Drop content** — use the classes in section 4 and tokens in section 2. No raw colors or fonts.

That is the whole job. ~2 minutes. No Figma.

## 8 · Product pages (the real Purpose.ai app layout)

Marketing/doc pages (sections 1–7) use `build-a.css`. **Product pages are different** — they match the real Purpose.ai app and use a different stylesheet: `tokens.css`.

### Source of truth: `tokens.css`

`tokens.css` is a **verbatim copy** of `purpose.ai/src/app/tokens.css` — the real token file, generated from Nataliia's Figma. Every colour, size, radius, and the type scale live there.

- **Never hand-edit `tokens.css`.** It's generated. To update after Nataliia changes Figma, run `web/sync-tokens.sh` (re-copies from purpose.ai).
- This keeps ONE source of truth. The kit never owns its own copy of the product's design numbers.

### Layout decision (2026-06-05)

Match **Nataliia's Figma drawing**, not the shipped app. They differ:

| | Left · Center · Right | Top bar |
|---|---|---|
| **Her Figma drawing (we follow this)** | 330 · 780 · 330 | 94px header |
| The shipped app (drifted, ignore) | 280 · fluid · 280 | none |

So a product page is: a full-width **94px header**, then a centered **1440** grid of **330 menu · 780 body · 330 menu**. All from tokens: `--layout-left/center/right`, `--header-h`, `--menu-w`.

### How to make a product page

1. **Copy** `_template-product.html`.
2. Keep `<link rel="stylesheet" href="shell.css">`. Just that one file — it pulls in `tokens.css` itself.
3. Change the markup inside `<main class="body">`. Use `var(--token)` for any new style — never a raw `#hex`.

`shell.css` is the **mobile-first, extensible** shell + components. Phone = stacked single column with a hamburger drawer; at **≥1100px** it expands to Nataliia's 330·780·330 grid with the 94px header. Add a new component once in `shell.css`; every page gets it.

Key tokens: `--color-accent` (#69749c), `--color-bg-menu` (#f3f3f3), `--input-h` (42), `--btn-primary-h` (46), `--menu-section-h` (46), `--header-h` (94).

Real logos live in `web/logos/` (Black/Blue/Brown/White × basic/compass/full/horizontal/vertical, SVG). Header uses `logos/Blue_compass.svg`.

### BLANKS — still needed from Nataliia (red-dashed in the template)

| Blank | Why |
|---|---|
| **Real icons** | Nav uses emoji placeholders (🏠 ✓ 📌…). Emoji is off-brand and OS-dependent. Need her real SVG glyphs. |
| ~~Logo file~~ ✅ **SOLVED** | Real logos pulled from the 2023 brandbook into `web/logos/`. |
| **Dark-mode colours** | `tokens.css` defines default (grey/light) + **sand** only. No dark theme block — the product template can't do dark yet. |

Until these land, the template shows them red-dashed so nobody mistakes a placeholder for the real thing.
