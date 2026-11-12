# Forensic UX/UI Audit — Shell & Editorial Routes (`audit-editorial`)

> **Date:** 2026-11-13  
> **Scope:** Global application shell, design tokens, API client resilience, and editorial routes (`/`, `/news`, `/matches`, `/matches/[id]`, `/squad`, `/squad/[id]`, `+error.svelte`)  
> **Design Authorities:** `design.md`, `frontEnd/src/tokens.css`, `frontEnd/src/base.css`, `frontEnd/src/app.css`, `frontEnd/src/app.html`  
> **Skill Standards:** `improve-ui`, `hallmark` (v2.0.0 Floor & `--kept`), `a11y-audit` (WCAG 2.2 AA & ARIA APG)  
> **Baseline Mechanical Gate:** `node ".agents/skills/hallmark/scripts/sloplint.mjs" "frontEnd/src" --genre editorial --kept` → `0 FAIL, 0 REFLEX, 0 WARN across 26 file(s); kept: links 28/28, fields 6/6, handlers 74/78`

---

## 1. Design Language & Audited Surface Contract

- **Audited Surface:**
  - Shell & Theme: `frontEnd/src/routes/+layout.svelte`, `+layout.ts`, `+layout.server.ts`, `+error.svelte`, `frontEnd/src/app.html`, `frontEnd/src/lib/stores/theme.svelte.ts`
  - Editorial Routes: `frontEnd/src/routes/+page.svelte` (`+page.ts`), `news/+page.svelte` (`news/+page.ts`), `matches/+page.svelte` (`matches/+page.ts`), `matches/[id]/+page.svelte` (`matches/[id]/+page.ts`), `squad/+page.svelte` (`squad/+page.ts`), `squad/[id]/+page.svelte` (`squad/[id]/+page.ts`)
  - Shared Client & Types: `frontEnd/src/lib/api/football.ts`, `frontEnd/src/lib/types/football.ts`
- **Design Sources:** `design.md`, `frontEnd/src/tokens.css`, `frontEnd/src/base.css`, `frontEnd/src/app.css`, `.hallmark/before.json`
- **Documented Decisions:**
  - Genre `editorial`, Shape `Ledger`, Vibe `"Arsenal matchday programme meets precision tactical ledger"`, Axes `dark/slab-serif/chromatic-red`, Posture `restrained`.
  - Tokens: `--color-paper` (`oklch(14% 0.012 24)`), `--color-paper-2` (`oklch(18% 0.014 24)`), `--color-paper-3` (`oklch(22% 0.016 24)`), `--color-ink` (`oklch(95% 0.008 75)`), `--color-ink-2` (`oklch(84% 0.010 60)`), `--color-muted` (`oklch(68% 0.014 40)`), `--color-accent` (`oklch(56% 0.22 27)`), `--color-accent-ink` (`oklch(98% 0.005 75)`), `--color-accent-2` (`oklch(76% 0.11 78)`), `--color-focus` (`oklch(60% 0.21 27)`), `--color-error` (`oklch(62% 0.19 25)`), `--color-success` (`oklch(68% 0.15 152)`).
  - Controls: Primary `--color-accent` fill + `--color-accent-ink` text, `4px` radius (`--radius-card`); Secondary `1px solid var(--color-rule)` on `--color-paper-2`; zero box-shadows (`--shadow-card: none`).
  - Kept Contracts (`sloplint --kept`): Must preserve all 28 kept links (`+layout.svelte`: `/`, `/auth/signout`, `/board`, `/lab`, `/login`, `/matches`, `/messages`, `/news`, `/notifications`, `/profile`, `/signup`, `/squad`, `/terrace`; `+page.svelte`: `/board`, `/lab`, `/lab?metric=...`, `/matches`, `/messages?recipient=...`, `/news`, `/squad`, `/terrace`; `matches/+page.svelte`: `/board`, `/predictions`, `/terrace`; `squad/+page.svelte`: `/board`), kept field names, kept DOM IDs (`comp-select`, `season-select`, etc.), and kept handlers (`selectCategory`, `toggleTag`, `handleRefresh`, `applyFilters`, `handlePositionChange`, `toggleCompare`, etc.).
- **Explicit Exceptions:** None documented.

---

## 2. Summary Severity Matrix

| ID | Sev | Title | Primary Files | Skill |
| :--- | :---: | :--- | :--- | :--- |
| **P0-1** | `P0` | Missing mobile navigation (`<768px`) & missing `/predictions` masthead link | `+layout.svelte` | `hallmark`, `a11y-audit` |
| **P0-2** | `P0` | WCAG AA contrast failure on `text-accent` small/body links & `text-error` badges on `paper-3` | `tokens.css`, `+page.svelte`, `news`, `matches`, `matches/[id]`, `squad`, `+error.svelte` | `a11y-audit`, `hallmark` |
| **P0-3** | `P0` | Render ~50s cold-start freeze, silent API error masking, synthetic fake fixtures, & false 404s | `+layout.svelte`, `+page.ts`, `football.ts`, `matches/[id]/+page.ts`, `squad/[id]/+page.ts`, `squad/+page.svelte` | `systematic-debugging`, `improve-ui` |
| **P1-1** | `P1` | Mobile header overflow (`320px–390px`) & silent tablet nav clipping (`768px–1140px`) | `+layout.svelte` | `improve-ui`, `hallmark` |
| **P1-2** | `P1` | Missing `aria-current="page"`, skip-to-content link, & dynamic notification count `aria-label` | `+layout.svelte` | `a11y-audit` |
| **P1-3** | `P1` | `/matches` mobile row crushing (`320px–390px`) & season `<select>` width blowout | `matches/+page.svelte` | `improve-ui`, `hallmark` |
| **P1-4** | `P1` | `/news` pill clipping (`320px`), 208px empty broken-image boxes, silent re-filter & missing reset CTA | `news/+page.svelte` | `improve-ui`, `hallmark` |
| **P1-5** | `P1` | Stale URL filter UI on `/matches` & `/squad`, silent compare errors, & off-screen comparison jump | `matches/+page.ts`, `matches/+page.svelte`, `squad/+page.ts`, `squad/+page.svelte` | `improve-ui`, `systematic-debugging` |
| **P1-6** | `P1` | Duplicate `<h1>` landmarks on `/matches/[id]` & oversized `84px` `<h1>` in narrow column on `/squad/[id]` | `matches/[id]/+page.svelte`, `squad/[id]/+page.svelte`, `tokens.css` | `a11y-audit`, `hallmark` |
| **P1-7** | `P1` | Sub-44px touch targets (`28px–36px`) & missing `aria-pressed` / `aria-live` across controls | `+layout.svelte`, `news`, `matches`, `matches/[id]`, `squad`, `squad/[id]` | `a11y-audit` |
| **P2-1** | `P2` | Redundant duplicate card `<a>` links on `/squad` (50+ Tab stops) & missing teammate compare CTA on `/squad/[id]` | `squad/+page.svelte`, `squad/[id]/+page.svelte` | `a11y-audit`, `improve-ui` |
| **P2-2** | `P2` | Non-semantic `<div>` grid for Squad comparison table & missing crest `onerror` fallbacks | `squad/+page.svelte`, `matches/+page.svelte`, `matches/[id]/+page.svelte` | `a11y-audit`, `improve-ui` |
| **P2-3** | `P2` | `base.css` `30ch/40ch` capping on card headlines, panel `<h2>` scale drift, & stale `"2024/25"` `<title>` | `base.css`, `+page.svelte`, `news/+page.svelte`, `squad/+page.svelte`, `matches/[id]/+page.svelte` | `improve-ui`, `a11y-audit` |
| **P2-4** | `P2` | `themeState.applyCssTokens()` overrides OKLCH tokens with raw hex & sticky header `z-50` < `--z-sticky-nav` | `theme.svelte.ts`, `+layout.svelte`, `tokens.css` | `hallmark` |
| **P3-1** | `P3` | Colophon footer quick links, local timezone label on `/matches`, & retry action on `+error.svelte` | `+layout.svelte`, `matches/+page.svelte`, `+error.svelte` | `improve-ui`, `hallmark` |

---

## 3. Detailed Forensic Findings

### P0 — Blocking

#### P0-1: Missing Mobile Navigation (`<768px`) & `/predictions` Unreachable from Masthead
- **Evidence:**
  - `frontEnd/src/routes/+layout.svelte:114-123`: `<nav aria-label="Primary navigation" class="hidden md:flex items-center gap-6 text-sm text-muted overflow-x-auto">` applies `hidden md:flex` with **zero** mobile toggle button, drawer, or secondary mobile nav bar.
  - `frontEnd/src/routes/+layout.svelte:115-122`: The 8 desktop links (`Home`, `The Armory`, `The Dugout`, `Squad`, `The Terrace`, `Data Lab`, `Matches`, `Debates`) omit `/predictions`.
- **User Impact:** On `320px` and `390px` viewports (every phone), users cannot navigate from the header to any desk (`The Armory`, `The Dugout`, `Squad`, `The Terrace`, `Data Lab`, `Matches`, `Debates`, or `Predictor`). On desktop, `/predictions` is invisible in primary navigation.
- **Proposed Solution:**
  - Add a `44x44px` (`min-w-[44px] min-h-[44px]`) menu `<button>` (`lg:hidden`, `type="button"`, `aria-expanded={mobileMenuOpen}`, `aria-controls="mobile-primary-nav"`, `aria-label="Toggle navigation menu"`) in the header.
  - Render a collapsible `#mobile-primary-nav` drawer directly below `<header>` (using `bg-paper border-b border-rule`, zero drop-shadow, `min-h-[44px]` link rows) containing all primary routes including `/predictions`, closing on link click, `Escape`, and `afterNavigate`.
  - Add `<a href="/predictions">` (`Predictor`) to the desktop `<nav>` while keeping all 13 existing kept links in `+layout.svelte`.
- **Skill Responsible:** `hallmark`, `a11y-audit`
- **Scope:** `frontEnd/src/routes/+layout.svelte`
- **Risk:** Low. Preserve all existing `href` targets (`sloplint --kept`).
- **Acceptance Criteria:**
  1. At `320px`, `390px`, and `768px` viewports, a visible keyboard-operable menu button opens all 9 primary desk routes (`/`, `/news`, `/board`, `/squad`, `/terrace`, `/lab`, `/matches`, `/predictions`, `/messages`) with `>=44px` hit targets.
  2. Pressing `Escape` or navigating closes the mobile drawer and returns focus to the toggle button on `Escape`.
  3. `/predictions` is reachable from the primary `<nav>` on desktop and mobile; `sloplint --kept` reports `links 28/28`.

#### P0-2: WCAG 2.2 AA Contrast Failures on `text-accent` Small/Body Text & `text-error` Form Badges
- **Evidence:** Exact linear-sRGB relative luminance ratios computed from `frontEnd/src/tokens.css:80-92`:
  - `--color-accent` (`oklch(56% 0.22 27)`) on `--color-paper` (`oklch(14% 0.012 24)`): **3.83:1** (FAILS AA `4.5:1` for `< 18pt` / `< 14pt bold`).
  - `--color-accent` on `--color-paper-2` (`oklch(18% 0.014 24)`): **3.62:1** (FAILS AA `4.5:1`).
  - `--color-accent` on `--color-paper-3` (`oklch(22% 0.016 24)`): **3.34:1** (FAILS AA `4.5:1`).
  - `--color-error` (`oklch(62% 0.19 25)`) on `--color-paper-3`: **4.36:1** (FAILS AA `4.5:1` for `text-xs` badges).
  - Note: `--color-accent` background with `--color-accent-ink` (`oklch(98% 0.005 75)`) passes AA at **4.91:1**.
  - Affected small-text instances (`13px–16px`):
    - `frontEnd/src/routes/+page.svelte:68, 89, 123, 148, 177, 189, 201, 213, 285, 319`
    - `frontEnd/src/routes/news/+page.svelte:345`
    - `frontEnd/src/routes/matches/+page.svelte:97`
    - `frontEnd/src/routes/matches/[id]/+page.svelte:195, 318`
    - `frontEnd/src/routes/squad/+page.svelte:296`
    - `frontEnd/src/routes/+error.svelte:20`
- **User Impact:** Small crimson links (`Full schedule`, `Match center`, `Read dispatch`, `Join debate`, `Watch`), goal minutes (`18'`), squad jersey labels (`#7`), and `L` form badges fail WCAG 2.2 AA `4.5:1` legibility on dark charcoal surfaces.
- **Proposed Solution:**
  - Keep `--color-accent: oklch(56% 0.22 27)` for primary filled buttons (`4.91:1` with `--color-accent-ink`) and large `>= 24px` display numerals (`#p1.jersey_number`).
  - Add `--color-accent-text: oklch(70% 0.18 27)` (`>= 5.3:1` on `paper`, `paper-2`, and `paper-3`) in `frontEnd/src/tokens.css` (`@theme static` + `:root`), and switch small/normal `text-accent` links/labels to `text-accent-text` (or `text-accent-2` where warm gold is intended).
  - Adjust `--color-error` in `frontEnd/src/tokens.css:14, 92` to `oklch(67% 0.19 25)` (`>= 5.1:1` on `paper-3`) so small `L` form badges pass AA.
- **Skill Responsible:** `a11y-audit`, `hallmark`
- **Scope:** `frontEnd/src/tokens.css`, `design.md` (document new token), and small-text `text-accent` classes in `+page.svelte`, `news/+page.svelte`, `matches/[id]/+page.svelte`, `squad/+page.svelte`, `+error.svelte`.
- **Risk:** Low (no raw hex values; preserves primary button branding).
- **Acceptance Criteria:**
  1. Every small/normal text token on `paper`, `paper-2`, and `paper-3` computes `>= 4.5:1` WCAG AA contrast.
  2. Primary `.bg-accent.text-accent-ink` buttons remain `4.91:1`.
  3. `sloplint --genre editorial --kept` passes with `0 FAIL`.

#### P0-3: Render ~50s Cold-Start Freeze, Silent API Error Masking & Misleading Fallback / False 404 States
- **Evidence:**
  1. **Blocking Cold-Start Navigation:** Universal `load` functions (`+page.ts:23-49`, `news/+page.ts:4-21`, `matches/+page.ts:4-29`, `squad/+page.ts:4-22`) block route transitions until all `fetch` calls resolve. `+page.ts:24-33` awaits **7 parallel requests**, two of which (`fetchInsights` on `line 27` and `fetchSyncStatus` on `line 29`) are **never rendered** in `+page.svelte`; `squad/+page.ts:11` similarly fetches unused `fetchClubs()`. Meanwhile `+layout.svelte` renders no `navigating` loading bar or cold-start notice.
  2. **Silent Synthetic Fallbacks Masking Failures:**
     - `football.ts:252-285` (`fetchMatchSummary`) catches HTTP 500/timeouts and computes a fake summary from `getLocalFallbackMatches()` (`lines 761-846`), injecting 2024 Wolves/Chelsea scores and a **fabricated future fixture** (`fb-ars-4`, Nottingham Forest at `Date.now() + 3 days`) onto `/` (`+page.svelte:73-157`) with zero error or offline indicator (violating Hallmark Floor #8 against invented figures/states).
     - `football.ts:234-237` (`fetchMatches`) and `football.ts:968-1014` (`fetchArsenalNews`) silently return static arrays on error while ignoring active filter/search arguments.
     - `football.ts:565-577` (`fetchSquad`) returns `[]` on error, causing `squad/+page.svelte:232` to falsely state `"No players found for the selected position."` instead of an API failure.
  3. **False 404 on Server/Network Errors:**
     - `football.ts:240-250` (`fetchMatchDetail`) and `football.ts:579-587` (`fetchPlayer`) return `null` on both `404` and `500`/network timeouts, causing `matches/[id]/+page.ts:7-9` and `squad/[id]/+page.ts:7-9` to throw **`404` ("Match dossier not found" / "Squad player dossier not found")** during Render cold-start or DB outages.
- **User Impact:** Users clicking links while Render wakes (~50s) see an unresponsive screen; users encountering an API timeout see fabricated future fixtures on `/`, broken filter responses on `/news` and `/matches`, `"No players found"` on `/squad`, or bogus 404 pages on valid player/match dossiers.
- **Proposed Solution:**
  - Add a slim top progress bar in `+layout.svelte` reactive to `navigating.to` (`$app/state`), plus a delayed (`> 2500ms`) polite status banner (`"Waking Arsenal data service — initial cold start can take up to 50s…"`).
  - Remove unused `fetchInsights` and `fetchSyncStatus` calls from `+page.ts` and unused `fetchClubs` from `squad/+page.ts`.
  - Add bounded request timeouts (or retry-once on cold start) and non-throwing status wrappers (or `ApiError` propagation on detail routes `res.status !== 404`) in `football.ts`:
    - `matches/[id]/+page.ts` and `squad/[id]/+page.ts` throw SvelteKit `404` **only** on HTTP `404`, and throw `503` (`"Arsenal data service is temporarily unavailable"`) on 5xx/network failure so `+error.svelte` renders an honest retryable state.
    - `/`, `/news`, `/matches`, and `/squad` receive explicit `apiError: boolean` / `isFallback: boolean` metadata from their loaders and render a clear editorial notice (`role="status"`, with a `"Retry"` button calling `invalidateAll()`) whenever live API data could not be reached, instead of silently presenting stale/empty states as truth.
- **Skill Responsible:** `systematic-debugging`, `improve-ui`
- **Scope:** `frontEnd/src/routes/+layout.svelte`, `+page.ts`, `+page.svelte`, `news/+page.ts`, `news/+page.svelte`, `matches/+page.ts`, `matches/+page.svelte`, `matches/[id]/+page.ts`, `squad/+page.ts`, `squad/+page.svelte`, `squad/[id]/+page.ts`, `frontEnd/src/lib/api/football.ts`
- **Risk:** Medium (preserve existing `football.ts` return types or export companion `*Result` wrappers so unowned `/lab`, `/board`, `/predictions`, `/terrace`, `/messages` remain untouched).
- **Acceptance Criteria:**
  1. Clicking any route during slow navigation immediately displays the shell loading bar and, after 2.5s, a cold-start message.
  2. Returning HTTP 500 or network failure from `/api/v1/squad` displays an API-unavailable notice with Retry rather than `"No players found"`.
  3. Returning HTTP 500 from `/api/v1/matches/{id}` or `/api/v1/squad/{id}` renders `Error 503` (not `Error 404`).
  4. Fallback fixtures/news are either clearly badged `"Cached offline preview — live sync unavailable"` or omitted in favor of honest empty/error messaging.

---

### P1 — High Impact

#### P1-1: Mobile Header Overflow (`320px–390px`) & Silent Tablet Nav Clipping (`768px–1140px`)
- **Evidence:**
  - `frontEnd/src/routes/+layout.svelte:108-126, 144-149`: Header container uses `gap-6` (`24px`), `shrink-0` on the brand (`line 110`), `shrink-0` on the right auth cluster (`line 126`), and `whitespace-nowrap` on the profile display name (`line 146-148`) without `max-w-*` or `truncate`. Because `base.css:2` sets `overflow-x: clip`, a signed-in user with a `15+` char display name on a `320px` phone (`288px` inner width) overflows and clips `Sign out` past the right edge.
  - `frontEnd/src/routes/+layout.svelte:114`: Desktop `<nav class="hidden md:flex items-center gap-6 ... overflow-x-auto">` activates at `768px` (`md:`). At `768px–1024px`, 8–9 links + `gap-6` + brand + signed-in controls require `>1100px`, silently clipping `Data Lab`, `Matches`, and `Debates` inside an unindicated scrollable `<nav>`.
- **User Impact:** Signed-in mobile users lose the `Sign out` control on narrow screens; tablet users (`768px–1024px`) miss rightmost desks unless they know to horizontally swipe the header nav.
- **Proposed Solution:** Hide `"North London"` subtitle below `sm:` (`hidden sm:inline`), add `min-w-0` + `max-w-[110px] sm:max-w-[160px] truncate` on the profile pill (`line 146`), tighten mobile header spacing (`gap-2 sm:gap-4`), and move the multi-link desktop `<nav>` breakpoint from `md:flex` to `xl:flex` (or `lg:flex` with `gap-4 xl:gap-6` once tested against 9 links) so `768px` tablets cleanly use the mobile drawer toggle from P0-1.
- **Skill Responsible:** `improve-ui`, `hallmark`
- **Scope:** `frontEnd/src/routes/+layout.svelte`
- **Risk:** Low.
- **Acceptance Criteria:** Zero horizontal clipping or off-screen controls at `320px`, `390px`, `768px`, `1024px`, and `1280px+` even with a 30-character display name.

#### P1-2: Missing `aria-current="page"`, Skip-to-Content Link & Accessible Notification Badge Count
- **Evidence:**
  - `frontEnd/src/routes/+layout.svelte:115-122`: No nav link reads `page.url.pathname` or sets `aria-current="page"`.
  - `frontEnd/src/routes/+layout.svelte:106-175`: No skip link targets `<main>` (`line 173` has no `id`).
  - `frontEnd/src/routes/+layout.svelte:129-143`: Bell link sets static `aria-label="Activity notifications"`, masking the visual `{unreadCount}` badge (`line 139`) from screen readers focusing the link.
- **User Impact:** Keyboard-only visitors must tab through 10–13 header items on every navigation; screen-reader users get no active-page landmark or unread notification count when focusing the bell control.
- **Proposed Solution:** Import `page` from `$app/state`, apply `aria-current={isActive ? 'page' : undefined}` and distinct active styling (`text-ink font-semibold` + bottom accent rule) to matching desktop and mobile nav links, prepend a skip link (`<a href="#main-content" class="visually-hidden focus:not-sr-only ...">Skip to main content</a>`) targeting `<main id="main-content" class="flex-1">`, and dynamically compute `aria-label={unreadCount > 0 ? \`Activity notifications (${unreadCount} unread)\` : 'Activity notifications'}`.
- **Skill Responsible:** `a11y-audit`
- **Scope:** `frontEnd/src/routes/+layout.svelte`
- **Risk:** Low.
- **Acceptance Criteria:** Active route carries `aria-current="page"`; first Tab stop is `"Skip to main content"` and jumps focus/scroll into `<main>`; bell link announces exact unread count.

#### P1-3: `/matches` Mobile Row Crushing (`320px–390px`) & Season `<select>` Width Blowout
- **Evidence:**
  - `frontEnd/src/routes/matches/+page.svelte:251-288`: Each match row places `[Home Team] [min-w-[96px] Score] [Away Team]` inside a single `flex items-center justify-center gap-6` row (`144px` non-team width). At `320px` (`~264px` row inner width), each team column shrinks to `~60px` (`~26px` for text after the `24px` crest), breaking team names into stacked 1-word fragments.
  - `frontEnd/src/routes/matches/+page.svelte:117-131`: Next-fixture quick link uses `flex items-center gap-4` with no `flex-wrap`, squeezing both clubs at `320px–390px`.
  - `frontEnd/src/routes/matches/+page.svelte:187-202`: `<select id="season-select">` contains long option labels (`"2026/27 (Current Campaign): Active Running Season & Live Matchdays"`) inside a flex item lacking `min-w-0 w-full sm:w-auto max-w-full`, pushing past mobile container bounds.
- **User Impact:** Match rows and next-fixture header become cramped and difficult to scan on phones (`320px`–`390px`).
- **Proposed Solution:** On `<640px`, stack or tighten the match row (`grid grid-cols-[1fr_auto_1fr] gap-2 sm:gap-6` with `min-w-0` + `truncate` or a compact vertical scoreline layout on `<420px`), add `flex-wrap` to the Next Fixture link (`line 117`), and apply `w-full sm:w-auto min-w-0 max-w-full` to `#comp-select` and `#season-select` wrappers.
- **Skill Responsible:** `improve-ui`, `hallmark`
- **Scope:** `frontEnd/src/routes/matches/+page.svelte`
- **Risk:** Low (preserves `#comp-select`, `#season-select`, and `applyFilters`).
- **Acceptance Criteria:** At `320px` and `390px`, team names, crests, score boxes, and season `<select>` fit cleanly within `--container` gutters with zero clipping or vertical 4-line wrapping per club name.

#### P1-4: `/news` Category Pill Overflow (`320px`), `208px` Empty Image Boxes & Silent Re-Filtering
- **Evidence:**
  - `frontEnd/src/routes/news/+page.svelte:42, 223`: `'Fan blogs (Pain in the Arsenal, Arseblog)'` with `whitespace-nowrap` (`~315px`) overflows `288px` inner width on `320px` phones.
  - `frontEnd/src/routes/news/+page.svelte:307-320`: `onerror={(e) => ((e.currentTarget as HTMLElement).style.display = 'none')}` hides the `<img>` only, leaving an empty `h-52` (`208px` tall) `bg-paper-2 border border-rule` container (Hallmark "empty wash" failure).
  - `frontEnd/src/routes/news/+page.svelte:27-38, 281-289`:
    1. `lines 281-284` only show loading feedback when `isFiltering && articles.length === 0`; switching categories or searching while articles are already on screen gives zero visual busy feedback.
    2. `lines 285-289` tell the user `"Clear your search filter"` without providing a Clear Filters button.
    3. `line 28` (`if (!initialized && data.feed)`) ignores subsequent `load` runs when navigating via URL query changes (`?tag=...`), and client filter clicks never sync `?category`/`?tag`/`?search` to the URL.
- **User Impact:** Horizontal overflow on `320px`, giant blank boxes on hotlink-blocked RSS images, unresponsive-feeling filters, and lost filter state on refresh.
- **Proposed Solution:** Shorten `cat.id === 'fan_blog'` label to `'Fan blogs'` (keeping `'Pain in the Arsenal, Arseblog'` in the page subtitle or tooltip), track `failedImages = $state<Record<string, boolean>>({})` so failed thumbnails unmount the entire `h-52` wrapper cleanly, set `aria-busy={isFiltering}` + subtle opacity/status notice during re-filtering, add a `"Reset filters"` button to the empty state, sync URL query params via `replaceState`, and remove the one-shot `initialized` lock so `data` updates cleanly.
- **Skill Responsible:** `improve-ui`, `hallmark`
- **Scope:** `frontEnd/src/routes/news/+page.svelte`
- **Risk:** Low (preserves `selectCategory`, `toggleTag`, `handleRefresh`, and `{art.article_url}`).
- **Acceptance Criteria:** All category tabs wrap cleanly at `320px`; broken RSS images leave zero blank `h-52` boxes; re-filtering displays busy feedback; empty state provides a 1-click filter reset.

#### P1-5: Stale Filter UI on `/matches` & `/squad`, Silent Compare Errors & Off-Screen Comparison Jump
- **Evidence:**
  - `frontEnd/src/routes/matches/+page.ts:4-28` & `matches/+page.svelte:8-25`: Loader filters by `?comp=` and `?status=` but does not return them; `selectedComp` and `activeTab` default to `'ALL'`, misrepresenting filtered data. Client filter changes do not sync URL params.
  - `frontEnd/src/routes/squad/+page.ts:18` & `squad/+page.svelte:8, 30-40`: Loader passes `activePosition`, yet `squad/+page.svelte` never reads `data.activePosition`, leaving `"All Gunners"` highlighted on `/squad?position=Midfielder`.
  - `frontEnd/src/routes/squad/+page.svelte:15, 58-84, 128-141`:
    1. `isComparing` (`line 15`) is never rendered anywhere in the markup.
    2. If `comparePlayers(p1Id, p2Id)` returns `null` (network/404), zero error feedback is shown.
    3. Selecting a 2nd player while scrolled down renders the comparison panel off-screen at the top (`line 128`) without scrolling or focusing it, and clicking `"Close comparison"` (`line 136`) leaves `comparePlayer1Id`/`comparePlayer2Id` selected so the next click unexpectedly replaces Player 2.
    4. At `320px–390px`, `line 132` (`flex items-center justify-between`) puts `<h2>` (`--text-section`) next to `"Close comparison"` without `flex-wrap`.
- **User Impact:** Deep-linked or back-navigated users see contradictory filter pills; squad comparisons fail silently or open invisibly above the fold.
- **Proposed Solution:** Return `activeComp` and `activeStatus` from `matches/+page.ts` and sync `selectedComp`/`activeTab`/`selectedSeason` and `squad` `selectedPosition`/`compare1`/`compare2` to URL query params via `replaceState`; on `/squad`, render an explicit loading & error alert for `isComparing`/`compareError`, add `flex-wrap gap-3` + `text-xl` to the comparison header, clear `comparePlayer1Id`/`comparePlayer2Id` (or provide distinct `"Hide"` vs `"Clear"`) on close, and scroll/focus the comparison panel (`comparisonSectionEl.scrollIntoView(...)` + `tabindex="-1"` `.focus()`) when populated.
- **Skill Responsible:** `improve-ui`, `systematic-debugging`
- **Scope:** `frontEnd/src/routes/matches/+page.ts`, `matches/+page.svelte`, `squad/+page.ts`, `squad/+page.svelte`
- **Risk:** Low.
- **Acceptance Criteria:** Visiting `/matches?comp=CL&status=FINISHED` or `/squad?position=Midfielder` highlights the matching controls; selecting 2 players shows loading feedback, handles errors visibly, and brings the comparison panel into view and focus.

#### P1-6: Duplicate `<h1>` Landmarks on `/matches/[id]` & Oversized `84px` `<h1>` in Narrow Column on `/squad/[id]`
- **Evidence:**
  - `frontEnd/src/routes/matches/[id]/+page.svelte:124, 154`: Renders **two** `<h1>` tags on the same page (`{homeName}` and `{awayName}`).
  - `frontEnd/src/routes/squad/[id]/+page.svelte:117`: Renders unclassed `<h1>{player.name}</h1>` inside `lg:col-span-7` (`~570px`), inheriting `--text-display` (`clamp(2.75rem, 5vw + 1rem, 5.25rem)` = up to `84px`!) from `base.css:9`, while `matches/[id]` overrides `h1` down to `text-2xl sm:text-3xl`, and `tokens.css:55` declares `--text-display-s` (`clamp(2.25rem, 4vw + 0.5rem, 3.75rem)`) which is unused across all routes.
- **User Impact:** Screen-reader heading navigation encounters two competing `<h1>` titles on match dossiers; player names wrap into oversized multi-line `84px` blocks inside the right column of `/squad/[id]`.
- **Proposed Solution:** On `matches/[id]/+page.svelte`, render a single semantic `<h1>` (e.g., `<h1 class="visually-hidden">{homeName} vs {awayName} match dossier</h1>` above the scoreboard and `<h2>` for the team names, or a unified single `<h1>` scoreboard header). Standardize interior editorial route `<h1>` elements (`/news`, `/matches`, `/squad`, `/squad/[id]`, `+error.svelte`) on `--text-display-s` (`text-[length:var(--text-display-s)]`) while keeping `--text-display` exclusively for the `/` Stage hero.
- **Skill Responsible:** `a11y-audit`, `hallmark`
- **Scope:** `frontEnd/src/routes/matches/[id]/+page.svelte`, `squad/[id]/+page.svelte`, `news/+page.svelte`, `matches/+page.svelte`, `squad/+page.svelte`
- **Risk:** Low.
- **Acceptance Criteria:** Every route has exactly one `<h1>`; `/squad/[id]` `<h1>` scales gracefully inside `lg:col-span-7` without multi-line distortion.

#### P1-7: Sub-44px Touch Targets & Missing `aria-pressed` / `aria-live` Across Interactive Controls
- **Evidence:**
  - `frontEnd/src/routes/news/+page.svelte:260`: Topic tag buttons are `h-7` (`28px` height).
  - `frontEnd/src/routes/matches/+page.svelte:299, 306, 313` & `squad/+page.svelte:334`: Action buttons (`Match center`, `Debate`, `Predict`, `Compare`) are `h-8` (`32px` height).
  - `frontEnd/src/routes/+layout.svelte:132, 146, 153, 161, 164`, `news/+page.svelte:223`, `matches/+page.svelte:151, 158, 165, 179, 193`, `matches/[id]/+page.svelte:65, 73, 79, 85`, `squad/+page.svelte:218`, `squad/[id]/+page.svelte:52, 60, 66`: Controls are `h-9` (`36px`).
  - Toggle/filter buttons on `/news` (`lines 220, 257`), `/matches` (`lines 148, 155, 162`), and `/squad` (`lines 215, 331`) omit `aria-pressed`; live counters/loading containers omit `aria-live="polite"`.
- **User Impact:** High mobile mis-tap rate on `28px–36px` interactive targets; screen readers are not notified of active filter toggle state or dynamic list updates.
- **Proposed Solution:** Enforce `min-h-[44px]` (`h-11` or `min-h-11`, and `min-w-[44px]` for icon buttons like the header bell) on interactive controls below `md:` (or globally `min-h-10` desktop / `min-h-11` mobile, using `h-10` only where `design.md` specifies `40px` desktop buttons and enlarging `h-7`/`h-8` chips/buttons to `min-h-[44px]` on touch viewports), add `aria-pressed` to all filter & compare buttons, and add `aria-live="polite"` to result count and loading/error status containers.
- **Skill Responsible:** `a11y-audit`
- **Scope:** `+layout.svelte`, `news/+page.svelte`, `matches/+page.svelte`, `matches/[id]/+page.svelte`, `squad/+page.svelte`, `squad/[id]/+page.svelte`
- **Risk:** Low.
- **Acceptance Criteria:** Every interactive button, link chip, and select on `<768px` meets `>=44px` tap height; active filter/compare states expose `aria-pressed="true"`; dynamic list counts announce updates politely.

---

### P2 — Meaningful Polish

#### P2-1: Duplicate Card Links on `/squad` & Missing Teammate Compare CTA on `/squad/[id]`
- **Evidence:**
  - `frontEnd/src/routes/squad/+page.svelte:245, 325`: Each of the 25 player cards renders two separate `<a href="/squad/{encodeURIComponent(player.id)}">` elements (the full portrait/name wrapper and the `"Player dossier"` footer link), doubling keyboard Tab stops (50+ link stops before reaching filters/footer).
  - `frontEnd/src/routes/squad/[id]/+page.svelte:57-70`: Provides links to `/board` and `/lab`, but no direct link back to `/squad?compare1={player.id}` to initiate a comparison from a player's scouting dossier.
- **User Impact:** Tedious keyboard tabbing through the squad grid and extra friction to compare a viewed player with a teammate.
- **Proposed Solution:** Replace the redundant bottom `<a href="/squad/...">Player dossier</a>` (`squad/+page.svelte:325-330`) with a non-focusable `<span>` cue inside the single card `<a>` (or wrap only the card header/footer cleanly so each card has one dossier link + one `Compare` button), and add `<a href="/squad?compare1={encodeURIComponent(player.id)}">Compare teammate</a>` to `squad/[id]/+page.svelte:57-70`.
- **Skill Responsible:** `a11y-audit`, `improve-ui`
- **Scope:** `frontEnd/src/routes/squad/+page.svelte`, `frontEnd/src/routes/squad/[id]/+page.svelte`
- **Risk:** Low (`sloplint --kept` only requires `/board` in `squad/+page.svelte`).
- **Acceptance Criteria:** 1 dossier link + 1 compare button per card on `/squad`; `/squad/[id]` links directly into `/squad?compare1={id}` pre-selecting that player.

#### P2-2: Non-Semantic Comparison Grid on `/squad` & Missing Club Crest `onerror` Fallbacks
- **Evidence:**
  - `frontEnd/src/routes/squad/+page.svelte:166-202`: Head-to-head comparison metrics use `<div class="grid grid-cols-3">` instead of a semantic `<table>` with `<th>` column and row headers.
  - `frontEnd/src/routes/matches/+page.svelte:119-128, 260-283` and `frontEnd/src/routes/matches/[id]/+page.svelte:114-122, 144-152`: External club crest `<img>` tags (`crests.football-data.org`) lack `onerror` handlers.
- **User Impact:** Screen-reader table navigation cannot read column/row relationships in the squad comparison; failed external crest URLs show broken-image icons.
- **Proposed Solution:** Refactor `squad/+page.svelte:166-202` into a `<table>` (`<caption class="visually-hidden">`, `<th scope="col">`, `<th scope="row">`), and track failed crest URLs in `$state` on `/matches` and `/matches/[id]` to hide broken `<img>` tags or render a crisp club-initials badge.
- **Skill Responsible:** `a11y-audit`, `improve-ui`
- **Scope:** `frontEnd/src/routes/squad/+page.svelte`, `matches/+page.svelte`, `matches/[id]/+page.svelte`
- **Risk:** Low.
- **Acceptance Criteria:** Screen readers navigate the comparison as a `<table>` with 3 columns and 5 metric rows; broken crest URLs degrade cleanly with zero broken image icons.

#### P2-3: `base.css` `30ch/40ch` Capping on Card Headlines, Panel `<h2>` Scale Drift & Stale `"2024/25"` `<title>`
- **Evidence:**
  - `frontEnd/src/base.css:9`: `h2 { max-width: 30ch; ... }` and `h3 { max-width: 40ch; ... }` cap heading line lengths globally, so `news/+page.svelte:323` (`<h3 class="text-base ...">`) wraps at `40ch` (~half card width) instead of spanning the card cleanly.
  - `frontEnd/src/routes/squad/+page.svelte:133` (`<h2>Head-to-head player comparison</h2>`) inherits `--text-section` (`up to 56px`) inside a `bg-paper-2` panel, contradicting `text-lg` (`+page.svelte:67`) and `text-base` (`matches/+page.svelte:92, 114`). Similarly, `+page.svelte:280` (`The Terrace pulse` header) lacks `flex-col sm:flex-row` / `flex-wrap`, risking squeeze at `320px`.
  - `frontEnd/src/routes/squad/+page.svelte:88`: `<title>` says `"Arsenal 2024/25 Squad & Player Comparisons | GUNNERS"`, contradicting the current 2026/27 (`arsenalmenssquad2627`) 25-player roster.
  - `frontEnd/src/routes/news/+page.svelte:293-297` & `matches/[id]/+page.svelte:306-310`: Outbound `target="_blank"` links lack screen-reader `(opens in a new tab)` text.
- **User Impact:** Artificially narrow news titles, jarring `56px` panel headers on `/squad`, mobile section-header squeeze on `/`, outdated season metadata in browser tabs, and unannounced new-tab transitions.
- **Proposed Solution:** Add `max-w-none` on card/panel subheadings (`news/+page.svelte:323`, etc.) or move `30ch/40ch` caps to section headings only; align panel-well `<h2>` titles to `text-xl font-display font-bold` and add `flex-wrap gap-3` to `+page.svelte:280`; update `/squad` `<title>` to `"Arsenal First-Team Squad & Player Comparisons | GUNNERS"`; add `<span class="visually-hidden">(opens in a new tab)</span>` inside external `target="_blank"` anchors.
- **Skill Responsible:** `improve-ui`, `a11y-audit`
- **Scope:** `frontEnd/src/base.css`, `+page.svelte`, `news/+page.svelte`, `squad/+page.svelte`, `matches/[id]/+page.svelte`
- **Risk:** Low.
- **Acceptance Criteria:** News card titles fill card width cleanly; panel `<h2>` headings share a consistent `text-xl` scale; `/squad` title reflects current squad; external links announce new-tab behavior.

#### P2-4: `themeState.applyCssTokens()` Overrides OKLCH Tokens with Raw Hex & Header `z-50` < `--z-sticky-nav`
- **Evidence:**
  - `frontEnd/src/lib/stores/theme.svelte.ts:20-22, 55-61` called by `+layout.svelte:86`: Writes inline hex values (`#EF0107`, `#FFFFFF`, `#9C824A`) to `--club-primary`, `--club-secondary`, `--club-accent`, overriding the OKLCH declarations in `tokens.css:96-98`.
  - `frontEnd/src/routes/+layout.svelte:107` uses `z-50` (`50`) rather than `tokens.css:76` `--z-sticky-nav: 300`.
- **User Impact:** Token drift between `tokens.css` OKLCH values and runtime inline styles; potential z-index stacking overlap if any page element uses `--z-sticky` (`200`) or `--z-dropdown` (`100`).
- **Proposed Solution:** Remove inline CSS-var mutation from `themeState.applyCssTokens()` (or align its token strings to `tokens.css` OKLCH definitions while keeping `CLUBS` and `ARSENAL_THEME` exports intact for `/board`, `/lab`, `/messages`, `/supporters`), and set `z-[var(--z-sticky-nav)]` on `<header>`.
- **Skill Responsible:** `hallmark`
- **Scope:** `frontEnd/src/lib/stores/theme.svelte.ts`, `frontEnd/src/routes/+layout.svelte`
- **Risk:** Low.
- **Acceptance Criteria:** Computed `--club-primary` matches `tokens.css` OKLCH; `<header>` stacks at `z-index: 300`.

---

### P3 — Optional Refinement

#### P3-1: Colophon Footer Desk Links, Local Timezone Hint on `/matches`, & Retry Action on `+error.svelte`
- **Evidence:**
  - `frontEnd/src/routes/+layout.svelte:177-185`: Colophon footer contains no navigation links to secondary desks (`/predictions`, `/lab/historical`, `/news`, `/matches`, `/squad`).
  - `frontEnd/src/routes/matches/+page.svelte:41-54`: Formats kickoff in local browser time without `timeZoneName: 'short'`, whereas `/matches/[id]` explicitly formats `UTC`.
  - `frontEnd/src/routes/+error.svelte:29-48`: Offers links to `/`, `/matches`, `/news`, but no `"Try again"` reload action for transient Render cold-start 5xx errors.
- **User Impact:** Harder discovery of `/predictions` and `/lab/historical` from page bottoms; mild timezone ambiguity comparing `/matches` vs `/matches/[id]`; extra friction retrying after a transient error.
- **Proposed Solution:** Add a restrained horizontal row of desk links (including `/predictions` and `/lab/historical`) in the footer colophon, add `timeZoneName: 'short'` to `matches/+page.svelte:44-50`, and add a secondary `"Try again"` `<button>` (`onclick={() => location.reload()}`) in `+error.svelte`.
- **Skill Responsible:** `improve-ui`, `hallmark`
- **Scope:** `frontEnd/src/routes/+layout.svelte`, `matches/+page.svelte`, `+error.svelte`
- **Risk:** Low.
- **Acceptance Criteria:** Footer links wrap cleanly on `320px–1280px+`; match list dates show local TZ abbreviation (`EST`/`BST`/`UTC`, etc.); error page supports 1-click retry.

---

## 4. Recommended Implementation Order (for Phase 2 Planners / Authors)

1. **Token & Base Typography Pass (Unblocks P0-2, P1-6, P2-3, P2-4):** Add `--color-accent-text` and adjust `--color-error` in `tokens.css`, update `design.md` if token list is mirrored, fix `base.css` heading `max-width` scoping, clean `theme.svelte.ts`.
2. **Global Shell Overhaul (P0-1, P1-1, P1-2, P1-7, P3-1):** Upgrade `+layout.svelte` with `navigating` cold-start progress bar, skip link, mobile nav drawer + `/predictions` link, `aria-current="page"`, dynamic bell `aria-label`, `320px` display-name truncation, `>=44px` touch targets, and Colophon footer links; add retry button to `+error.svelte`.
3. **API Resilience & Honest States (P0-3):** Prune dead calls in `+page.ts` / `squad/+page.ts`, preserve `404` vs `503` distinction in `football.ts` and detail loaders, and add non-intrusive degraded-state banners + Retry buttons across `/`, `/news`, `/matches`, `/squad`.
4. **Editorial Route Polish (P1-3, P1-4, P1-5, P1-6, P1-7, P2-1, P2-2, P2-3):** Fix `/news` mobile pills, failed thumbnail unmounting, URL sync, and reset CTA; fix `/matches` mobile row wrapping, select widths, and deep-link filter sync; fix `/matches/[id]` single `<h1>`; fix `/squad` URL sync, comparison loading/error/scroll-focus, semantic `<table>`, duplicate card link, and `/squad/[id]` `<h1>` scale + compare CTA.
5. **Verification Gate:** Re-run `npm --prefix frontEnd run check`, `npm --prefix frontEnd run build`, and `node ".agents/skills/hallmark/scripts/sloplint.mjs" "frontEnd/src" --genre editorial --kept` (must stay `0 FAIL, 0 REFLEX, 0 WARN`, `28/28` kept links).
