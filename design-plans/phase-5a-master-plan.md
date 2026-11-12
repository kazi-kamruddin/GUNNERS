# Phase 5A Master UX Architecture & Remediation Blueprint

> **Date:** 2026-11-13  
> **Phase:** Phase 2 — UX Architecture & Design Strategy (Executed through Phase 8 Release Gate)  
> **Author:** `audit-editorial`  
> **Execution Status:** **COMPLETED & VERIFIED** (`verification-matrix.md` §11 — `svelte-check` `0/0`, `vite build` `194 modules`, `test:unit` `16/16`, `test:e2e` `19/19` in Edge, `sloplint --kept` `0 FAIL / 0 REFLEX / 0 WARN` across `27` files, `impeccable detect` `[]`, `pytest` `60/60`)  
> **Inputs:** [`design-plans/frontend-audit.md`](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/design-plans/frontend-audit.md), [`design-plans/verification-matrix.md`](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/design-plans/verification-matrix.md), [`design.md`](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/design.md), [`tokens.css`](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/tokens.css), [`base.css`](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/base.css), [`app.css`](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/app.css), [`.hallmark/before.json`](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/.hallmark/before.json)  
> **Hard Gate:** Preserve Hallmark v2.0.0 editorial broadsheet (`Ledger`) system — OKLCH tokens only, zero drop-shadows (`--shadow-card: none`), zero uppercase tracked eyebrows, zero `transition: all`, and `sloplint.mjs --genre editorial --kept` passing at `0 FAIL, 0 REFLEX, 0 WARN`.

---

## 1. UX Pro Max Guidance (Filtered Through Hallmark v2.0.0)

Two initial `--stack svelte` queries (`"editorial navigation mobile drawer"`, `"sports tactical board accessibility"`) returned **`0 results`** from `stacks/svelte.csv`. Retrying per `ui-ux-pro-max/SKILL.md` with explicit `--domain ux` (`"navigation drawer keyboard focus"`, `"modal dialog accessible contrast"`) returned **6 verified guidelines**, strictly reconciled against Hallmark `design.md`:

| Guideline (UX Pro Max `ux-guidelines.csv`) | Hallmark v2.0.0 Translation for Gunners |
| :--- | :--- |
| **Keyboard Navigation & Aligned Tab Order** | Keep desktop & mobile drawer DOM order sequential; remove `focus:outline-none` on pitch SVG tokens; replace `<div role="button">` lightboxes and clickable `<tr>`s with native `<button>` / `<a href>`. |
| **Visible Focus States Inside Modals** | Never strip outlines without replacement. Use `base.css` `2px solid var(--color-focus)` (`oklch(60% 0.21 27)`) on every control, drawer link, pitch token, and `:focus-within` upload wrapper. |
| **Focus Not Obscured (WCAG 2.2)** | Close the mobile drawer on `afterNavigate` and route sticky `<header>` to `z-[var(--z-sticky-nav)]` (`300`), modals to `z-[var(--z-modal)]` (`400`), and toasts to `z-[var(--z-toast)]` (`500`) so focused items are never hidden behind sticky bars. (Treated as AA focus-visibility safeguard without over-claiming AAA.) |
| **Color & Typography Contrast (`>= 4.5:1`)** | Keep `--color-accent` (`oklch(56% 0.22 27)`) on filled `.bg-accent.text-accent-ink` buttons (**4.91:1**). Introduce `--color-accent-text: oklch(70% 0.18 27)` (**>=5.3:1** on `paper`, `paper-2`, `paper-3`) for small crimson links/labels and adjust `--color-error` to `oklch(67% 0.19 25)` (**>=5.1:1** on `paper-3`). Note: UX Pro Max's Tailwind `focus:ring-blue-500` / `#333` examples are rejected in favor of Hallmark OKLCH tokens. |

---

## 2. Navigation, Shell & Cold-Start Architecture (`+layout.svelte` & `+layout.ts`)

1. **Responsive Masthead Breakpoint & Mobile Drawer (`ED-P0-01`, `ED-P1-01`):**
   - Raise desktop `<nav>` from `hidden md:flex` (`768px`) to `hidden lg:flex` (`1024px`) and remove `overflow-x-auto` silent clipping.
   - Add **Predictor** (`<a href="/predictions">Predictor</a>`) to primary desktop & mobile navigation (all 9 desks: `/`, `/news`, `/board`, `/squad`, `/terrace`, `/lab`, `/matches`, `/predictions`, `/messages`).
   - Below `1024px` (`lg:hidden`), render a `min-w-[44px] min-h-[44px]` hamburger/menu toggle (`type="button"`, `aria-expanded={mobileMenuOpen}`, `aria-controls="mobile-primary-nav"`, `aria-label="Toggle navigation menu"`).
   - Render `#mobile-primary-nav` directly inside/beneath `<header>` (`bg-paper border-b border-rule`, zero shadow, `min-h-[44px]` link rows) wired with `use:focusTrap` when open, closing on link click, `Escape` (returning focus to menu toggle), and SvelteKit `afterNavigate`.
2. **Header Landmarks, Skip Link & `320px` Truncation (`ED-P1-02`, `ED-P1-07`, `ED-P2-04`):**
   - Prepend `<a href="#main-content" class="visually-hidden focus:not-sr-only ...">Skip to main content</a>` and ensure `<main id="main-content" tabindex="-1">` sits immediately after `<header>`.
   - Set `aria-current={isActive(href) ? 'page' : undefined}` on desktop and mobile nav links, plus dynamic notification label `aria-label={unreadCount > 0 ? \`Notifications (${unreadCount} unread)\` : 'Notifications'}`.
   - Truncate signed-in supporter display names (`max-w-[7rem] sm:max-w-[10rem] truncate`) and ensure every header icon button/link satisfies `>= 44x44px` hit target.
   - Elevate `<header>` from `z-50` to `z-[var(--z-sticky-nav)]` (`300`) and expand `Colophon` footer with quick links to `/news`, `/matches`, `/squad`, `/lab`, `/predictions`, `/terrace`.
3. **Render ~50s Cold-Start Progress Bar & Delayed Notice (`ED-P0-03`):**
   - Import `navigating` from `$app/state` (already verified supported on `@sveltejs/kit@3.1.0` in `verification-matrix.md:116`).
   - Display a `2px` `--color-accent` top progress indicator immediately when `navigating.to !== null`.
   - Start a `2500ms` timer inside a clean `$effect` whenever `navigating.to !== null`; if still navigating past `2500ms`, reveal a polite broadsheet status strip (`role="status"`): `"Waking Arsenal data service — initial cold start can take up to 50s…"`.
4. **Auth Session Consistency (`COM-P0-3`):**
   - `frontEnd/src/routes/auth/signout/+server.ts`: Remove `export const GET` completely; keep `POST` only (every caller in `+layout.svelte:150` and `profile/+page.svelte:366` already submits `<form method="POST" action="/auth/signout">`).
   - `frontEnd/src/routes/+layout.ts`: On SSR (`!isBrowser()`), return `data.session` and `data.user` already verified by `hooks.server.ts` (`safeGetSession()`); in browser (`isBrowser()`), call `getUser()` first and only read `getSession()` when `user` is non-null, returning `{ session: null, user: null }` otherwise.

---

## 3. Token, Typography & Asset Calibration

| File | Calibration | Contrast / Mechanical Guarantee |
| :--- | :--- | :--- |
| `frontEnd/src/tokens.css` | Add `--color-accent-text: oklch(70% 0.18 27)` in both `@theme static` and `:root`. Raise `--color-error` to `oklch(67% 0.19 25)`. | `--color-accent-text` on `paper` / `paper-2` / `paper-3` >= `5.3:1` AA; `--color-error` on `paper-3` >= `5.1:1` AA; `--color-accent` + `--color-accent-ink` remains `4.91:1`. |
| `frontEnd/src/base.css` | Relax global `h1, h2, h3 { max-width: 30ch }` when inside `.card-headline` / broadsheet grid cards (`max-width: none` inside grid cards or narrow `max-width: 48ch` where needed) so desktop cards don't wrap artificially early (`ED-P2-03`). | Preserves `52–68ch` prose measure on `<p>`, `<li>`, `blockquote`. |
| `frontEnd/src/lib/stores/theme.svelte.ts` | Remove raw hex overrides (`#EF0107`, `#DA291C`, etc.) of `--color-accent` in `applyCssTokens()` (`ED-P2-04`). Expose a secondary non-text crest/club badge variable `--color-club-highlight` if needed, keeping Hallmark OKLCH tokens authoritative. | Prevents breaking WCAG AA contrast when supporters select custom clubs. |
| `frontEnd/src/app.html` | Update Google Fonts query to `Besley:wght@700&family=Hanken+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@500;700` (`BASE-03`). | Eliminates faux bolding (`font-synthesis: none` safety). |
| `frontEnd/src/lib/assets/favicon.svg` | Replace stock orange Svelte logo (`#ff3e00`) with a minimalist Hallmark Arsenal broadsheet monogram (`#141212` paper disc, `#DC2626` cannon/monogram mark, `#F5F2EB` rule) (`BASE-04`). | Clean SVG `< 1 KB`, valid title `"The Gunners"`. |
| `frontEnd/package.json` & `vite.config.ts` | Remove unused `echarts@^6.1.0` (`BASE-01`); switch `vite.config.ts` adapter import from `@sveltejs/adapter-auto` to `@sveltejs/adapter-vercel` (`BASE-02`). | Zero unused chart bundle/lock weight; eliminates Vercel adapter build warning. |

---

## 4. Shared Foundation Modules (Phase 3 — Slice A)

Create clean, framework-native primitives in `frontEnd/src/lib/` so Slices B, C, and D stay DRY and conflict-free:

1. **`frontEnd/src/lib/actions/focusTrap.ts`** (`use:focusTrap={{ active, onEscape, initialFocusSelector }}`):
   - Captures `document.activeElement` on activation; moves initial focus inside the container; traps `Tab` / `Shift+Tab` across focusable descendants; invokes `onEscape` on `Escape` (bound cleanly at document/window level while active); restores focus to trigger element on deactivation/unmount.
   - Consumed by: Mobile nav drawer (`+layout.svelte`), Edit Player modal (`TacticalBoard.svelte`), Save Insight modal (`lab/+page.svelte`), Auth Gate & Image Lightbox (`terrace/+page.svelte`), Start Debate modal (`messages/+page.svelte`).
2. **`frontEnd/src/lib/components/StateBanner.svelte`**:
   - Props: `variant: 'error' | 'warning' | 'info' | 'empty'`, `title: string`, `message: string`, `retryLabel?: string`, `onretry?: () => void`, `actionHref?: string`, `actionLabel?: string`.
   - Uses `role={variant === 'error' ? 'alert' : 'status'}`, Hallmark broadsheet styling (`bg-paper-2`, `border border-rule`, `border-l-2 border-l-error` / `border-l-accent-2`, zero shadows, `min-h-[44px]` button).
3. **`frontEnd/src/lib/utils/redirect.ts`**:
   - `getSafeRedirectPath(raw: string | null | undefined, fallback = '/')`: Rejects protocol-relative `//`, external schemes (`http:`, `javascript:`), and auth loops (`/login`, `/signup`), returning safe internal paths (preserving query strings like `?tab=shot_map`).
4. **`frontEnd/src/lib/utils/format.ts`**:
   - `formatMetricLabel(metric: string)` (replaces broken `.replace('_', ' ')` in `supporters/[username]`), `formatMatchDateTime(iso: string)` with local timezone abbreviation (`new Intl.DateTimeFormat(..., { timeZoneName: 'short' })`).
5. **Typed Error Propagation in `frontEnd/src/lib/api/football.ts` & `community.ts`:**
   - Define `export class ApiError extends Error { status: number; isNetworkError: boolean; constructor(...) }` and `fetchWithTimeout(fetchFn, url, init, timeoutMs = 15000)`.
   - Add explicit result wrappers / strict methods (`fetchMatchesResult`, `fetchMatchDetailStrict`, `fetchPlayerStrict`, `fetchSquadResult`, `fetchArsenalNewsResult`, `fetchMatchSummaryResult`, `fetchInsightSummaryStrict`, `fetchTacticalBoards(..., token?)`, `deleteTacticalBoard(id, token)`, `deleteInsight(id, token)`):
     - Detail loaders (`matches/[id]`, `squad/[id]`) only return `null` on HTTP `404` and throw `ApiError(503)` on `5xx`/network timeout so SvelteKit `+error.svelte` renders **503 Service Unavailable** instead of a fake **404**.
     - List/dashboard loaders return `{ data, error: string | null, isFallback: boolean }` so UI renders `StateBanner` with Retry rather than pretending an outage is `"No players found"` or injecting unmarked fake future matches.
     - Replace departed `Zinchenko #35` at `football.ts:862` with `Calafiori #33`.
     - Preserve all existing exported function signatures cleanly while upgrading consumers across Slices B, C, and D.

---

## 5. `sloplint --kept` Contract Preservation Strategy

Per `sloplint.mjs:4253-4261` and `.hallmark/before.json`, **28 links, 6 form field names, 74 handlers, and 30 IDs** are mechanically enforced. Workers MUST obey these exact rules:

1. **Preserve All 6 Field `name`s (`bio`, `display_name`, `email`, `favorite_club_id`, `password`, `username`) & All 30 DOM IDs (`#comp-select`, `#season-select`, `#metric-select`, `#image-url-input`, `#target-supporter-id`, `#initial-opening-message`, `#ins-title`, `#ins-desc`, etc.).**
2. **Preserve Existing Link & Handler Expressions Unless Intentionally Replaced:**
   - Adding new links (`/predictions` in `+layout.svelte`, `/matches/{pred.match_id}` in `predictions`) keeps all 28 baseline links satisfied.
   - On `lab/+page.svelte`, keep `onchange={runQuery}` present alongside any new reactive bindings.
   - Keep `onclick={onshare}`, `onclick={handlePublishPost}`, `onclick={handleSavePlayerModal}`, `onclick={submitInsight}`, `onclick={handleStartNewDebate}`, etc. intact.
3. **Required Hallmark Stamp Comments in `frontEnd/src/app.css` (Slice A + Phase 8 verification):**
   Any baseline kept handler/link intentionally removed or upgraded for P0/P1 safety MUST be recorded in `frontEnd/src/app.css` with a reason >= 12 chars so `--kept` exits `0` with `0 FAIL, 0 WARN`:
   ```css
   /* Hallmark · dropped requireAuth('comment'), requireAuth('post') · WCAG 3.2.1/2.1.2 fix removing guest onfocus keyboard trap in terrace */
   /* Hallmark · dropped lightboxImageUrl = null · replaced nested role=button backdrop keydown with focusTrap Escape handler */
   /* Hallmark · reworded "/supporters/{entry.user_name}" to "/supporters/{encodeURIComponent(entry.user_name)}" · encode supporter path segment */
   ```
   *(Note: verify `sloplint.mjs --kept` matches `dropped` tokens case-insensitively with `>=4`-char substring matching and zero commas inside each token; Phase 8 verifier runs `--kept` as a mandatory release gate and adjusts `app.css` stamp if any additional kept string was legitimately refactored.)*

---

## 6. Disjoint Execution Slices & Dependency Graph (Phases 3–8)

```text
Phase 3: Slice A (exec-foundation) — Tokens, Shell, FocusTrap, StateBanner, API Clients, Signout/Layout Auth
   ├──> Phase 4: Slice B (exec-editorial)    — /, /news, /matches, /matches/[id], /squad, /squad/[id]
   ├──> Phase 5: Slice C (exec-interactive)  — /board, TacticalBoard, /lab, /lab/historical, /predictions
   └──> Phase 6: Slice D (exec-community)    — /terrace, /messages, /notifications, /supporters/[u], Auth pages
            └──> Phase 7 & 8: Verifier + Playwright-Edge E2E + sloplint --kept + Context Sync
```

**Slices B, C, and D share ZERO files** and can run concurrently immediately after Phase 3 (Slice A) passes `npm run check`.

| Phase & Slice | Strictly Owned Writable Files (Disjoint) | Findings Resolved | Gate Before Moving Next |
| :--- | :--- | :--- | :--- |
| **Phase 3 — Slice A**<br>(`exec-foundation`) | `design.md`, `frontEnd/package.json`, `frontEnd/vite.config.ts`, `frontEnd/src/app.html`, `frontEnd/src/app.css`, `frontEnd/src/tokens.css`, `frontEnd/src/base.css`, `frontEnd/src/lib/assets/favicon.svg`, `frontEnd/src/lib/stores/theme.svelte.ts`, `frontEnd/src/lib/actions/focusTrap.ts` *(new)*, `frontEnd/src/lib/components/StateBanner.svelte` *(new)*, `frontEnd/src/lib/utils/redirect.ts` *(new)*, `frontEnd/src/lib/utils/format.ts` *(new)*, `frontEnd/src/lib/api/football.ts`, `frontEnd/src/lib/api/community.ts`, `frontEnd/src/routes/+layout.svelte`, `frontEnd/src/routes/+layout.ts`, `frontEnd/src/routes/+error.svelte`, `frontEnd/src/routes/auth/signout/+server.ts` | `BASE-01..04`, `ED-P0-01`, `ED-P0-02` (tokens), `ED-P0-03` (shell/API), `ED-P1-01`, `ED-P1-02`, `ED-P1-07` (shell), `ED-P2-03` (`base.css`), `ED-P2-04`, `ED-P3-01` (footer/error), `COM-P0-3` (signout/`+layout.ts`), `INT-P1-01` (`football.ts:862`), `INT-P1-03`/`INT-P1-11` (API delete helpers), `INT-P1-06`/`COM-P1-3` (API error propagation) | `npm --prefix frontEnd run check` = 0 errors; `npm --prefix frontEnd run build` = 0 errors (no adapter warning); `sloplint --kept` = 0 FAIL |
| **Phase 4 — Slice B**<br>(`exec-editorial`) | `frontEnd/src/routes/+page.{ts,svelte}`, `frontEnd/src/routes/news/+page.{ts,svelte}`, `frontEnd/src/routes/matches/+page.{ts,svelte}`, `frontEnd/src/routes/matches/[id]/+page.{ts,svelte}`, `frontEnd/src/routes/squad/+page.{ts,svelte}`, `frontEnd/src/routes/squad/[id]/+page.{ts,svelte}` | `ED-P0-02` (route links), `ED-P0-03` (route loaders/UI), `ED-P1-03..07`, `ED-P2-01..03`, `ED-P3-01` (tz) | `npm --prefix frontEnd run check` + `sloplint --kept` clean |
| **Phase 5 — Slice C**<br>(`exec-interactive`) | `frontEnd/src/lib/components/TacticalBoard.svelte`, `frontEnd/src/lib/components/HistoricalPitchExplorer.svelte`, `frontEnd/src/routes/board/+page.{ts,svelte}`, `frontEnd/src/routes/lab/+page.{ts,svelte}`, `frontEnd/src/routes/lab/historical/+page.{ts,svelte}`, `frontEnd/src/routes/predictions/+page.{ts,svelte}` | `INT-P0-01..07`, `INT-P1-01..14`, `INT-P2-01..07`, `INT-P3-01..02` | `npm --prefix frontEnd run check` + `sloplint --kept` clean |
| **Phase 6 — Slice D**<br>(`exec-community`) | `frontEnd/src/routes/terrace/+page.{ts,svelte}`, `frontEnd/src/routes/messages/+page.{ts,svelte}`, `frontEnd/src/routes/notifications/+page.{ts,svelte}`, `frontEnd/src/routes/supporters/[username]/+page.{ts,svelte}`, `frontEnd/src/routes/login/+page.{server.ts,svelte}`, `frontEnd/src/routes/signup/+page.{server.ts,svelte}`, `frontEnd/src/routes/profile/+page.{server.ts,svelte}`, `frontEnd/src/routes/auth/callback/+server.ts`, `frontEnd/src/routes/auth/reset-password/+page.svelte` | `COM-P0-1..3` (routes), `COM-P1-1..9`, `COM-P2-1..5`, `COM-P3-1..2` | `npm --prefix frontEnd run check` + `sloplint --kept` clean |
| **Phase 7 — E2E & Verification** | `frontEnd/package.json` (`@playwright/test` devDep if authorized), `frontEnd/tests/e2e/*` *(new)*, `design-plans/verification-matrix.md` | Runtime DOM/a11y verification across `320px`, `390px`, `768px`, `1280px` using headless Edge (`channel: 'msedge'`) | Zero console/page errors, zero horizontal overflow, axe/focus-walk/target-size pass, error-state & cold-start probes pass |
| **Phase 8 — Final Gate & Context Sync** | `frontEnd/src/app.css` *(stamp check only if needed)*, `.project-context/05_UI_ARCHITECTURE_AND_DESIGN_SYSTEM.md`, `.project-context/07_CURRENT_STATE_AND_ROADMAP.md`, `.project-context/PORTABLE_CONTEXT.md`, `reference/context Gunners 20oct.md`, `design-plans/skill-activation-ledger.md` | Full verification & proportional context maintenance (`AGENTS.md` §7.2) | `npm run check`, `npm run build`, `sloplint --genre editorial --kept`, `impeccable detect`, `sync_context.py --check`, `pytest` all PASS |

---

## 7. Non-Negotiable Acceptance & Rollback Policy

- **Backend Contract Preservation:** Zero unrequested changes to FastAPI routes (`/api/v1/*`) or Supabase migrations. All UI fixes adapt cleanly to existing backend endpoints (including existing `DELETE /api/v1/tactics/{id}`, `DELETE /api/v1/insights/{id}`, and `GET /api/v1/supporters/{username}`).
- **Verification Discipline:** No worker may report completion without re-running `npm --prefix frontEnd run check` and `node ".agents/skills/hallmark/scripts/sloplint.mjs" "frontEnd/src" --genre editorial --kept` and reporting exact exit codes and counts.
- **Git Restraint:** No autonomous `git add`, `git commit`, or `git push`.

---

## 8. Execution Outcome & Deferred Live-Cloud QA (`2026-11-13`)

- **All Phases 3–8 Completed & Verified (`verification-matrix.md` §11):**
  - Slice A foundation (`focusTrap.ts` with `HTMLElement | SVGElement` capture/restoration, `StateBanner.svelte`, `format.ts`, `redirect.ts`, strict `ApiError` wrappers, conditional `adapterVercel` on Vercel/Linux vs `adapterAuto` on local Windows, AA `--color-accent-text` & `--color-error` tokens, `<1024px` masthead drawer, `POST`-only `/auth/signout`).
  - Slice B editorial routes (`/`, `/news`, `/matches`, `/matches/[id]`, `/squad`, `/squad/[id]`) + Slice C interactive studio (`/board`, `TacticalBoard.svelte`, `/lab`, `/lab/historical`, `HistoricalPitchExplorer.svelte`, `/predictions`) + Slice D community/auth (`/terrace`, `/messages`, `/notifications`, `/supporters/[username]`, `/login`, `/signup`, `/profile`, `/auth/*`).
  - Automated Vitest unit suite (`3` files, `16/16` passed) + Playwright Edge E2E suite (`4` specs, `19/19` passed across `320px`, `390px`, `768px`, `1024px`, `1280px` using mocked `/api/v1/*` JSON responses) + `.github/workflows/ci.yml` integration (`test:unit` + Playwright Chromium `test:e2e`).
- **Deferred Live-Cloud / External Flows (`verification-matrix.md` §10.5):**
  - Authenticated live-session flows without mock cookies: `/board` owner 2-step `Delete` confirmation, `/lab` authenticated `#ins-modal-title` Insight save/delete, `/messages` authenticated mobile `'list'`/`'thread'` switcher & Realtime DM delivery, `/terrace` authenticated optimistic cheer rollback & Storage uploads.
  - Hallmark `sloplint --render` tier skipped locally due to absent `puppeteer-core` / `HALLMARK_PUPPETEER` (static `--genre editorial --kept` passed `0 FAIL, 0 REFLEX, 0 WARN` across `27` files).
