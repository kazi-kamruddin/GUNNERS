# Phase 1 Forensic UX/UI Audit — Community, Messaging & Authentication

> **Audit Scope:** `/terrace`, `/messages`, `/notifications`, `/supporters/[username]`, `/login`, `/signup`, `/profile`, `/auth/reset-password`, `/auth/callback`, `/auth/signout`, `hooks.server.ts`, `lib/supabase.ts`, `lib/api/community.ts`  
> **Design Authority:** [design.md](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/design.md), [tokens.css](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/tokens.css), [base.css](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/base.css), [app.css](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/app.css)  
> **Skills Applied:** `improve-ui`, `hallmark` (v2.0.0 editorial/Ledger), `a11y-audit` (WCAG 2.1/2.2 AA & ARIA APG), `supabase` (SSR/Auth/Storage/Realtime)  
> **Mode:** Strictly read-only static forensic audit (`design-plans/audit-community.md` only)  
> **Date:** 2026-11-13

---

## 1. Design Language & System Baseline

- **Audited Surface:** Community, Direct Messaging, Notifications, Public Supporter Portfolios, and Supabase SSR Authentication/Profile flows (`frontEnd/src/routes/{terrace,messages,notifications,supporters/[username],login,signup,profile,auth/*}`, `frontEnd/src/hooks.server.ts`, `frontEnd/src/lib/supabase.ts`, `frontEnd/src/lib/api/community.ts`).
- **Design Sources:**
  - [design.md](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/design.md): Genre `editorial`, shape `Ledger`, dark/slab-serif/chromatic-red (`--color-paper: oklch(14% 0.012 24)`, `--color-paper-2: oklch(18% 0.014 24)`, `--color-paper-3: oklch(22% 0.016 24)`, `--color-ink`, `--color-ink-2`, `--color-muted`, `--color-rule`, `--color-rule-2`, `--color-accent: oklch(56% 0.22 27)`, `--color-accent-2: oklch(76% 0.11 78)`, `--color-error`, `--color-success`), flat broadsheet surfaces (`--shadow-card: none`), `--radius-card: 4px`, `--radius-pill: 999px`.
  - [tokens.css](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/tokens.css): Defines `--z-sticky-nav: 300`, `--z-modal: 400`, `--z-toast: 500`, spacing/type scales, and `@theme static` Tailwind v4 bindings.
  - [base.css](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/base.css): Global `:focus-visible` ring (`2px solid var(--color-focus)`), `.visually-hidden`, `overflow-x: clip`, `prefers-reduced-motion: reduce`.
- **Governing Owners & Consumers:**
  - Root SSR/CSR auth & notification badge sync: [hooks.server.ts](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/hooks.server.ts), [+layout.server.ts](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/+layout.server.ts), [+layout.ts](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/+layout.ts), [+layout.svelte](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/+layout.svelte).
  - Community REST client & shared API client: [community.ts](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/lib/api/community.ts), [football.ts](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/lib/api/football.ts).
- **Explicit Exceptions:** None documented.

---

## 2. Severity Index & Executive Summary

| Severity | Count | Summary |
| :--- | :---: | :--- |
| **P0** | 3 | Mobile `/messages` stacked `640px` layout trap + missing thread switcher; `/terrace` guest `onfocus` keyboard trap + non-trapped modals + invalid nested `role="button"` lightbox; `GET /auth/signout` logout-CSRF/prefetch hazard + `+layout.ts` unverified `getSession()` fallback |
| **P1** | 9 | `/terrace` enabled Publish silently no-ops without text; `/terrace` & `/supporters/[username]` broken `author_name`-vs-`username` links & self-DM `"Direct debate"` 400 error; `/terrace` off-screen cheer rollback error + missing `aria-pressed`/`aria-expanded` + comment loading flash; `/messages` Realtime optimistic-send race duplicate + fake static `"Realtime active"` status + missing auto-scroll; `/messages` partial-row clickability + inaccessible Start Debate modal + silent invalid `?c=` fallback; lost `?next=` redirect context across `/login`, `/signup`, `/profile`, `/terrace`, `/messages`, `/notifications`; `/notifications` missing `aria-live`, double-submit, & navigation error-loss race; `/signup` missing `emailRedirectTo` & resend + `/auth/reset-password` recovery hash/error race; `/profile` invisible focus ring on `visually-hidden` avatar input, impossible avatar removal, orphaned uploads, `invalidateAll()` form wipe, & `320px` UUID overflow |
| **P2** | 5 | Missing password visibility toggles, `autocomplete`, `use:enhance` pending states, & `role="alert"` across auth/profile forms; `/terrace` dead `clearImageAttachment()`, inline Edit missing upload/preview, missing `maxlength`/counters & image `onerror` fallbacks; `/terrace` undersized `h-6`/`h-7` touch targets & mobile search squeeze; `/messages` missing multi-day date dividers, bubble `break-words`, & noisy `(Arsenal)` suffix; `/supporters/[username]` `metric.replace('_', ' ')` bug, missing post permalinks, unranked guidance, & `+page.ts` `profile` key shadowing |
| **P3** | 2 | Modal `z-50` colliding with sticky header `z-50` instead of `tokens.css` `--z-modal`/`--z-sticky-nav`; generic image `alt` text, unused `lib/supabase.ts` import + silent mock URL, raw OAuth errors, & `/notifications` `limit=20` clarity |

---

## 3. Detailed Findings

### P0 — Critical Blockers

#### `COM-P0-1` · `/messages` mobile inbox ↔ active thread collapse & desktop container overflow
- **Severity:** `P0`
- **File Citations:**
  - [messages/+page.svelte:498](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/messages/+page.svelte#L498)
  - [messages/+page.svelte:500](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/messages/+page.svelte#L500)
  - [messages/+page.svelte:578](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/messages/+page.svelte#L578)
  - [messages/+page.svelte:137-139](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/messages/+page.svelte#L137-L139)
  - [messages/+page.svelte:646-673](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/messages/+page.svelte#L646-L673)
- **Evidence:**
  1. Line 498 renders `<div class="grid grid-cols-1 md:grid-cols-12 h-[640px] border border-rule bg-paper-2">` with both the Conversations sidebar (`line 500`) and Active Chat Window (`line 578`) visible simultaneously in a single column on `< 768px` viewports.
  2. Neither column has `min-h-0` or `overflow-hidden`, so on desktop long message lists expand past `640px` and on mobile both panels fight inside a fixed `640px` height with no scroll separation.
  3. On initial load (`lines 137-138`), if `loadedConvs.length > 0`, `activeConvId` is automatically set to `loadedConvs[0].id`. There is no mobile "Back to conversations" button in the chat header (`lines 646-673`) and no control to return to the supporter directory view (`!activeConvId` at `line 579`).
- **User Impact:** Mobile users cannot cleanly switch between their conversation list and active thread; the composer and thread header get squeezed or clipped off-screen, and users with ≥1 conversation can never access the inline supporter directory picker without opening the modal.
- **Proposed Solution:**
  - Add a responsive mobile view state (`mobileView: 'list' | 'thread'`) toggled on conversation selection and via an explicit `← Conversations` button (`min-h-9`) in the chat header (`md:hidden`).
  - Use `hidden md:flex` on the inactive pane below `md`, keep `min-h-0 overflow-hidden` on both `md:col-span-4` and `md:col-span-8` inside `h-[min(72dvh,640px)]`, and add a `"Find supporter"` / `"All debates"` reset button to return to `!activeConvId` on desktop if desired.
  - Preserve Hallmark tokens (`bg-paper`, `bg-paper-2`, `border-rule`, `rounded-card`).
- **Skill Responsible:** `improve-ui` + `hallmark`
- **Scope:** `frontEnd/src/routes/messages/+page.svelte`
- **Risk:** Low. Switching visibility with responsive Tailwind classes (`hidden md:flex`) keeps desktop split-pane intact while fixing mobile navigation.
- **Acceptance Criteria:**
  - At `375x812`, `/messages` shows either the full-height Conversations list OR the active thread with a visible `Back to conversations` button; neither panel overflows the `border-rule` shell.
  - At `1280x800`, 50+ messages scroll strictly inside `.overflow-y-auto` without stretching the `640px` container.

---

#### `COM-P0-2` · `/terrace` guest `onfocus` keyboard trap, non-trapped modals & invalid nested lightbox semantics
- **Severity:** `P0`
- **File Citations:**
  - [terrace/+page.svelte:722-731](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/terrace/+page.svelte#L722-L731)
  - [terrace/+page.svelte:1264-1266](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/terrace/+page.svelte#L1264-L1266)
  - [terrace/+page.svelte:1287-1340](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/terrace/+page.svelte#L1287-L1340)
  - [terrace/+page.svelte:1343-1366](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/terrace/+page.svelte#L1343-L1366)
  - [terrace/+page.svelte:1048-1059](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/terrace/+page.svelte#L1048-L1059)
- **Evidence:**
  1. Composer `<textarea>` (`lines 725-727`) and reply `<input>` (`lines 1264-1266`) invoke `requireAuth(...)` inside `onfocus`. A keyboard-only guest tabbing through the page unexpectedly opens `showAuthModal` on focus (WCAG 3.2.1 On Focus). If focus is restored to the trigger on close, `onfocus` immediately re-opens the modal in an infinite loop (WCAG 2.1.2 No Keyboard Trap).
  2. `showAuthModal` (`lines 1288-1340`) lacks `role="dialog"`, `aria-modal="true"`, `aria-labelledby`, `Escape` close handling, focus trapping, initial focus placement, and focus restoration.
  3. Image lightbox (`lines 1343-1366`) renders `<div role="button" tabindex="0" onclick={...} onkeydown={(e) => e.key === 'Escape' && ...}>` wrapping a nested `<button type="button">Close</button>` (`lines 1352-1358`). Nesting an interactive `<button>` inside `role="button"` violates ARIA/HTML content models (WCAG 4.1.2), and `Escape` only fires if focus lands on the backdrop itself.
- **User Impact:** Keyboard and screen-reader users browsing as guests are trapped or disoriented when tabbing past the composer/reply inputs, cannot reliably dismiss modals with `Escape`, and lose focus context when opening/closing the image lightbox.
- **Proposed Solution:**
  - For guests (`!data.user`), render the composer with a clear non-trapping read-only/sign-in bar (e.g., `"Sign in to publish to The Terrace"` button calling `requireAuth('post')` on `onclick`, or disable/gate on `onclick`/submit rather than `onfocus`). Same for the reply bar (`lines 1257-1277`): replace `onfocus` auto-modal with an explicit `"Sign in to reply"` button for guests.
  - Convert both `showAuthModal` and `lightboxImageUrl` overlays to proper modal dialogs (`role="dialog"`, `aria-modal="true"`, `aria-labelledby`, window/dialog `Escape` handler, initial focus into the dialog, `Tab`/`Shift+Tab` focus trap, and focus restoration to `previouslyFocusedElement` on close).
  - Replace `<div role="button">` in the lightbox with a non-interactive backdrop `<div>` (`onclick` outside content closes, `Close` `<button>` inside handles keyboard close).
- **Skill Responsible:** `a11y-audit`
- **Scope:** `frontEnd/src/routes/terrace/+page.svelte` (or a small shared accessible modal helper if reused by `/messages`).
- **Risk:** Low-Medium. Removing `onfocus` auto-opening eliminates the focus-restore loop completely.
- **Acceptance Criteria:**
  - Keyboard-only guest can `Tab` cleanly from page header through filters, composer, feed posts, and footer without any modal opening involuntarily.
  - Pressing `Escape` from anywhere inside `showAuthModal` or `lightboxImageUrl` closes the dialog and returns focus to the element that triggered it; `Tab` stays trapped inside the open dialog.
  - Zero nested interactive elements (`button` inside `role="button"`).

---

#### `COM-P0-3` · `GET /auth/signout` session-destruction CSRF/prefetch hazard & `+layout.ts` unverified `getSession()` fallback
- **Severity:** `P0`
- **File Citations:**
  - [auth/signout/+server.ts:4-12](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/auth/signout/+server.ts#L4-L12)
  - [+layout.ts:21-34](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/+layout.ts#L21-L34)
  - [hooks.server.ts:22-45](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/hooks.server.ts#L22-L45)
- **Evidence:**
  1. `auth/signout/+server.ts:9-12` defines `export const GET` calling `await locals.supabase.auth.signOut()`, allowing any cross-origin `<img>`/`<iframe>` or SvelteKit link preload to destroy the user's authenticated session via a safe HTTP `GET` request. Both `+layout.svelte:150` and `profile/+page.svelte:366` already submit via `<form method="POST" action="/auth/signout">`.
  2. `+layout.ts:21-34` runs `supabase.auth.getSession()` (`line 23`) and `supabase.auth.getUser()` (`line 27`) independently on SSR and CSR, then returns `session: session ?? data.session, user: user ?? data.user` (`lines 31-32`). If `getUser()` returns `null` (revoked/expired JWT) while a stale cookie still holds a `session` object, `data.session` remains non-null while `data.user` is `null` (contradicting `hooks.server.ts:29-31` which zeroes both). Also during SSR, `+layout.ts` performs redundant auth network verification after `hooks.server.ts` already ran `safeGetSession()`.
- **User Impact:** Users can be unexpectedly signed out via `GET /auth/signout` prefetch/CSRF; stale client/SSR sessions can desync `data.user` (`null`) from `data.session` (truthy), causing routes like `messages/+page.ts:7-9` (which checks `session?.user?.id`, not `user?.id`) to issue failing `401` API calls before client state catches up.
- **Proposed Solution:**
  - Remove `GET` handler from `auth/signout/+server.ts` (keep `POST` only; if a fallback `GET` is desired for direct URL visits, redirect to `/profile` or `/` without calling `signOut()`).
  - In `+layout.ts`: on SSR (`!isBrowser()`), trust `data.session` and `data.user` validated by `hooks.server.ts` (`safeGetSession()`); in browser (`isBrowser()`), validate with `getUser()` first and only read `getSession()` when `user` is non-null (matching `hooks.server.ts:22-41` and Supabase SSR guidance), returning `{ session: null, user: null }` if `getUser()` fails.
  - Ensure `messages/+page.ts:6-9` and `notifications/+page.ts:5-8` check `const { user, session, profile } = await parent()` (`Boolean(user && session?.access_token)`).
- **Skill Responsible:** `supabase` + `sveltekit-data-flow`
- **Scope:** `frontEnd/src/routes/auth/signout/+server.ts`, `frontEnd/src/routes/+layout.ts`, `frontEnd/src/routes/messages/+page.ts`, `frontEnd/src/routes/notifications/+page.ts`
- **Risk:** Medium (touches SSR/CSR auth plumbing; test login, OAuth callback, signout, and expired-cookie handling carefully).
- **Acceptance Criteria:**
  - `GET /auth/signout` does NOT invalidate the user's Supabase session (returns `405` or redirects without signing out); `POST /auth/signout` signs out and redirects `303 /`.
  - When `getUser()` returns an invalid/expired user, both `data.user` and `data.session` resolve to `null` across SSR and CSR loads.

---

### P1 — High-Impact Functional, UX & Accessibility Defects

#### `COM-P1-1` · `/terrace` enabled Publish button silently no-ops when photo is attached without text
- **Severity:** `P1`
- **File Citations:**
  - [terrace/+page.svelte:154-156](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/terrace/+page.svelte#L154-L156)
  - [terrace/+page.svelte:890-897](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/terrace/+page.svelte#L890-L897)
  - [terrace.py:226-269](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/backEnd/app/api/v1/endpoints/terrace.py#L226-L269)
- **Evidence:** The `Publish to Terrace` button at `line 893` uses `disabled={isSubmitting || isUploadingImage || (!newPostContent.trim() && !newPostImageUrl.trim())}`, enabling the button as soon as an image is uploaded or URL-pasted even if `newPostContent` is empty. However, `handlePublishPost()` at `line 156` executes `if (!newPostContent.trim()) return;` silently, and `PostCreateRequest.content` requires `min_length=1`.
- **User Impact:** Supporters who upload a match photo and click the active `Publish to Terrace` button experience a dead button with zero error or validation hint.
- **Proposed Solution:** Either disable Publish whenever `!newPostContent.trim()` (removing `&& !newPostImageUrl.trim()`) AND display a clear helper message below the composer when an image is attached without caption text (e.g., `"Add a short observation or caption to publish your photo."`), or validate on click and show an inline error beside the textarea (`aria-describedby`). Keep `PostCreateRequest` contract intact.
- **Skill Responsible:** `improve-ui`
- **Scope:** `frontEnd/src/routes/terrace/+page.svelte`
- **Risk:** Low.
- **Acceptance Criteria:**
  - Clicking `Publish to Terrace` never results in a silent no-op; attempting to publish a photo-only post either keeps the button clearly disabled with helper text or displays an inline error prompting for caption text.

---

#### `COM-P1-2` · `/terrace` & `/supporters/[username]` broken `author_name` → `/supporters/` links & self-DM `"Direct debate"` 400 error
- **Severity:** `P1`
- **File Citations:**
  - [terrace/+page.svelte:922-935](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/terrace/+page.svelte#L922-L935)
  - [terrace/+page.svelte:1165-1170](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/terrace/+page.svelte#L1165-L1170)
  - [supporters/[username]/+page.svelte:84-91](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/supporters/[username]/+page.svelte#L84-L91)
  - [supporters.py:106-122](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/backEnd/app/api/v1/endpoints/supporters.py#L106-L122)
  - [messaging.py:168-169](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/backEnd/app/api/v1/endpoints/messaging.py#L168-L169)
- **Evidence:**
  1. `terrace/+page.svelte:923` and `1166` link author names to `/supporters/{encodeURIComponent(post.author_name)}` (`comment.author_name`), while `terrace.py:249-253` stores `display_name` (which can differ from `Profile.username`). `supporters.py:114` looks up `Profile` by `func.lower(Profile.username) == uname_lower`, so any user whose `display_name !== username` lands on a degraded fallback view (`profile = None`, missing `avatar_url`, `bio`, and `Profile.id`-matched insights/predictions) or a `404` if they haven't authored items under that exact string.
  2. `terrace/+page.svelte:929-935` renders `"Direct debate"` (`?recipient=...`) on **all** posts including the current user's own posts (`isPostOwner === true`), and `supporters/[username]/+page.svelte:84-91` renders `"Challenge to debate"` even when viewing one's own public dossier (linked directly from `/profile:175-180`). Submitting triggers `400 Cannot start conversation with yourself` (`messaging.py:168-169`).
- **User Impact:** Clicking an author's name on `/terrace` can fail to resolve their real supporter profile (`avatar_url`, `bio`, stats); clicking `"Direct debate"` / `"Challenge to debate"` on one's own post or dossier opens a broken DM modal that errors on submit.
- **Proposed Solution:**
  - Hide `"Direct debate"` on `/terrace` when `isPostOwner` is true (or `post.author_id === data.user?.id`), and hide `"Challenge to debate"` on `/supporters/[username]` when `data.user?.id === profile.user_id` (showing `"Edit profile"` link to `/profile` instead!).
  - Also pass `author_username` from `PostResponse`/`CommentResponse` (or resolve `Profile.id` fallback in `supporters.py` if backend extends `PostResponse`, or keep `username` distinct from `display_name` when posting from `/terrace`). Note: in `terrace/+page.svelte:161,479`, `authorName` passes `data.profile?.display_name || ...`; if `author_username` isn't yet on `PostResponse`, flag a small additive field or lookup in `supporters.py` / `terrace.py` as part of the handoff plan while keeping UI changes clean.
- **Skill Responsible:** `improve-ui` + `sveltekit-data-flow`
- **Scope:** `frontEnd/src/routes/terrace/+page.svelte`, `frontEnd/src/routes/supporters/[username]/+page.svelte` (optional additive `author_username` in `backEnd/app/schemas/terrace.py` & `terrace.py` if scoped)
- **Risk:** Low.
- **Acceptance Criteria:**
  - Signed-in users never see `"Direct debate"` on their own Terrace posts or `"Challenge to debate"` on their own `/supporters/[username]` dossier (they see `"Edit profile"` instead).
  - Author profile links on `/terrace` resolve to the author's real `Profile` record even when `display_name` contains spaces or differs from `username`.

---

#### `COM-P1-3` · `/terrace` off-screen cheer rollback error, missing `aria-pressed`/`aria-expanded` & comment loading flash
- **Severity:** `P1`
- **File Citations:**
  - [terrace/+page.svelte:434-469](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/terrace/+page.svelte#L434-L469)
  - [terrace/+page.svelte:602-618](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/terrace/+page.svelte#L602-L618)
  - [terrace/+page.svelte:1139-1153](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/terrace/+page.svelte#L1139-L1153)
  - [terrace/+page.svelte:1253-1255](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/terrace/+page.svelte#L1253-L1255)
  - [football.ts:451-459](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/lib/api/football.ts#L451-L459)
- **Evidence:**
  1. `Cheer ({post.reactions_count})` (`lines 1139-1145`) lacks `aria-pressed={post.user_reacted}`, and `Debates ({post.comments_count})` (`lines 1147-1153`) lacks `aria-expanded={!!expandedComments[post.id]}`.
  2. When `toggleReaction` or `createComment` or `deleteTerracePost` fails (`lines 447-458`), `errorBanner` renders only at `line 602` at the top of the page. On a scrolled feed, the optimistic cheer reverts silently in-place while the error message is completely off-screen.
  3. `toggleCommentSection(postId)` (`lines 462-469`) sets `expandedComments[postId] = true` before `await fetchComments(postId)` resolves, without a per-post `loadingComments[postId]` flag. While loading (and on network error, since `football.ts:457` catches and returns `[]`), the UI immediately renders `"No comments yet. Join the conversation below."` (`line 1254`) even when `post.comments_count > 0`!
- **User Impact:** Screen readers don't know if a post is cheered or if its debate thread is expanded; scrolled users miss failed cheer/reply errors; expanding any debate flashes a false `"No comments yet"` empty state.
- **Proposed Solution:**
  - Add `aria-pressed={post.user_reacted}` to the Cheer button and `aria-expanded={!!expandedComments[post.id]}` + `aria-controls="comments-{post.id}"` to the Debates button.
  - Add per-post `postActionErrors[postId]` rendered inline beneath the action bar (`role="alert"`), in addition to or instead of top-only `errorBanner` for post-scoped actions.
  - Add `loadingComments[postId]` and `commentLoadErrors[postId]` states (`Loading replies…` / retry prompt) so `"No comments yet"` only shows when loaded cleanly with 0 items.
- **Skill Responsible:** `a11y-audit` + `improve-ui`
- **Scope:** `frontEnd/src/routes/terrace/+page.svelte` (and optionally non-swallowing comment fetch helper or error flag).
- **Risk:** Low.
- **Acceptance Criteria:**
  - Cheer and Debates buttons expose accurate `aria-pressed` and `aria-expanded` states.
  - Failed cheer rollback displays an inline `role="alert"` message directly inside the affected post card.
  - Expanding a post with `comments_count > 0` shows `"Loading replies…"` until comments resolve, never flashing `"No comments yet."`.

---

#### `COM-P1-4` · `/messages` Realtime optimistic-send race duplicate, hardcoded `"Realtime active"` status & no auto-scroll
- **Severity:** `P1`
- **File Citations:**
  - [messages/+page.svelte:278-304](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/messages/+page.svelte#L278-L304)
  - [messages/+page.svelte:329-371](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/messages/+page.svelte#L329-L371)
  - [messages/+page.svelte:672](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/messages/+page.svelte#L672)
  - [messages/+page.svelte:676](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/messages/+page.svelte#L676)
- **Evidence:**
  1. `line 672` renders hardcoded static `<span class="text-success font-semibold shrink-0">Realtime active</span>`. `.subscribe()` at `line 304` ignores subscription status callbacks (`SUBSCRIBED`, `TIMED_OUT`, `CHANNEL_ERROR`, `CLOSED`), so the UI falsely claims Realtime is active even when disconnected or using mock credentials.
  2. In `handleSendMessage()` (`lines 329-371`), an optimistic message (`id: msg_opt_...`) is appended to `messages`. If Supabase Realtime `INSERT` (`lines 288-293`) arrives *before* `await sendMessage(...)` resolves, `!messages.some((m) => m.id === incoming.id)` evaluates `true` and appends `incoming`. When `sendMessage(...)` subsequently resolves, `line 367` maps `msg_opt_...` → `sent` (same `id`), leaving **two identical bubbles** in `messages`.
  3. The message stream (`line 676`) never scrolls to the bottom on thread load, send, or incoming Realtime message.
- **User Impact:** Fast Realtime round-trips duplicate the sender's own messages in the thread; users receive deceptive `"Realtime active"` assurance when WebSocket is down; long threads open scrolled to the oldest message at the top.
- **Proposed Solution:**
  - Track `realtimeStatus = $state<'connecting' | 'live' | 'reconnecting' | 'offline'>('connecting')` from `.subscribe((status) => ...)` and display truthful status text (with `aria-live="polite"`), using `--color-success` for live, `--color-accent-2` for connecting/reconnecting, and `--color-error` for offline/error.
  - Deduplicate optimistic + Realtime inserts cleanly: if `incoming.sender_id === data.currentUserId`, check for an optimistic `msg_opt_*` entry with matching `content` (or check `messages.some((m) => m.id === sent.id)` inside `handleSendMessage` at `line 367`, removing `optimisticMsg.id` instead of duplicating `sent`!). Specifically, at `line 367`: if `sent.id` already exists in `messages`, filter out `optimisticMsg.id`; otherwise replace `optimisticMsg.id` with `sent`. And in Realtime handler, if a `msg_opt_` bubble from `currentUserId` matches `incoming.content`, replace that `msg_opt_` item in-place! Also key the `{#each messages as msg (msg.id)}` loop cleanly.
  - Bind a `messagesContainer` ref and smoothly scroll to bottom (`scrollTop = scrollHeight`) when `activeConvId` loads or `messages.length` increases while near the bottom.
- **Skill Responsible:** `supabase` + `improve-ui`
- **Scope:** `frontEnd/src/routes/messages/+page.svelte`
- **Risk:** Low.
- **Acceptance Criteria:**
  - Sending a message when Realtime fires before the HTTP response resolves renders exactly 1 bubble (zero duplicates).
  - Channel status reflects actual `SUBSCRIBED` / `CHANNEL_ERROR` / `CLOSED` callbacks.
  - Opening or sending in a 30+ message thread scrolls automatically to the newest message.

---

#### `COM-P1-5` · `/messages` partial-row clickability, inaccessible Start Debate modal & silent invalid `?c=` fallback
- **Severity:** `P1`
- **File Citations:**
  - [messages/+page.svelte:133-139](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/messages/+page.svelte#L133-L139)
  - [messages/+page.svelte:521-571](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/messages/+page.svelte#L521-L571)
  - [messages/+page.svelte:592-641](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/messages/+page.svelte#L592-L641)
  - [messages/+page.svelte:735-877](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/messages/+page.svelte#L735-L877)
- **Evidence:**
  1. Each conversation item (`lines 521-571`) is a `<div>` where only the participant name `<button>` (`lines 539-545`) is clickable; clicking the avatar, `@username`, last message preview, or timestamp does nothing, and `isSelected` has no `aria-current="true"` or `aria-pressed`.
  2. The `Start new debate` modal (`lines 735-877`) lacks `role="dialog"`, `aria-modal="true"`, `aria-labelledby`, `Escape` close, focus trap, focus restoration, and keyboard selection (`aria-pressed` / arrow navigation) for supporter search results (`lines 771-811`). Both the empty-state directory (`line 595`) and modal search (`line 760`) share the same `supporterQuery` state.
  3. When arriving at `/messages?c=<invalid_or_inaccessible_id>`, `lines 133-139` silently fall back to `loadedConvs[0]` without telling the user the requested thread wasn't found.
- **User Impact:** Users clicking anywhere on a conversation card outside the title text think the inbox is frozen; keyboard/screen-reader users cannot trap or Escape-close the debate modal; broken deep links silently open the wrong conversation.
- **Proposed Solution:**
  - Make the entire conversation item a `<button type="button" aria-current={isSelected ? 'true' : undefined} class="w-full text-left ...">` (keeping internal layout intact).
  - Add accessible dialog semantics (`role="dialog"`, `aria-modal="true"`, `aria-labelledby="start-debate-title"`, `Escape` handler, initial focus on `#modal-supporter-search`, Tab trap, focus restore) and `aria-pressed={isChosen}` + `Enter`/`ArrowDown`/`ArrowUp` support in the modal supporter list; also pre-fill `targetUsername` when `initialRecipient` matches a supporter or check if an existing conversation with `initialRecipient.id` already exists (selecting it directly or offering to jump to it!).
  - If `data.initialConversationId` is provided and not found in `loadedConvs`, display a dismissible inline notice (`"Requested conversation could not be loaded or you are not a member."`).
- **Skill Responsible:** `a11y-audit` + `improve-ui`
- **Scope:** `frontEnd/src/routes/messages/+page.svelte`
- **Risk:** Low.
- **Acceptance Criteria:**
  - Clicking anywhere on a conversation row selects that thread and updates `aria-current="true"`.
  - Modal supports `Escape` close, focus trapping, and keyboard supporter selection.
  - Invalid `?c=` displays an honest notice rather than silently switching threads without explanation.

---

#### `COM-P1-6` · Lost `?next=` redirect destination across `/login`, `/signup`, `/profile` & auth gates
- **Severity:** `P1`
- **File Citations:**
  - [auth/callback/+server.ts:4-10,26](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/auth/callback/+server.ts#L4-L10)
  - [login/+page.server.ts:4-9,36](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/login/+page.server.ts#L4-L9)
  - [login/+page.svelte:34](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/login/+page.svelte#L34)
  - [signup/+page.svelte:17](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/signup/+page.svelte#L17)
  - [profile/+page.server.ts:5-7](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/profile/+page.server.ts#L5-L7)
  - [messages/+page.svelte:483](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/messages/+page.svelte#L483)
  - [terrace/+page.svelte:1319](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/terrace/+page.svelte#L1319)
  - [notifications/+page.svelte:189](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/notifications/+page.svelte#L189)
- **Evidence:** `/auth/callback/+server.ts:5-9` already implements safe open-redirect protection (`rawNext.startsWith('/') && !rawNext.startsWith('//') && !rawNext.includes('\\')`). However, `login/+page.server.ts:36` hardcodes `throw redirect(303, '/profile')`, `login/+page.svelte:34` and `signup/+page.svelte:17` omit `?next=` on `redirectTo`, `profile/+page.server.ts:6` redirects to `/login` without `?next=/profile`, and the sign-in CTAs on `/terrace`, `/messages`, `/notifications`, and `/supporters/[username]` link to `/login` without preserving the current path + query string (e.g., `/messages?recipient=...`).
- **User Impact:** A guest clicking `"Challenge to debate"` on `/supporters/GoonerAlex` or opening `/messages?c=...` or `/terrace` to reply is forced through `/login`, then dumped onto `/profile` instead of returning to their intended debate or post.
- **Proposed Solution:**
  - Extract a small `getSafeRedirectPath(raw: string | null, fallback = '/profile')` helper (reusing the exact `startsWith('/') && !startsWith('//') && !includes('\\')` check from `auth/callback/+server.ts`, plus rejecting control characters/newlines).
  - Preserve `?next={encodeURIComponent(page.url.pathname + page.url.search)}` on Sign In / Create Account links inside `/terrace`, `/messages`, `/notifications`, and `profile/+page.server.ts`.
  - Read `next` in `login/+page.server.ts` (from URL or hidden form input), `login/+page.svelte` / `signup/+page.svelte` (appending `?next=...` to `/auth/callback` and `Sign up` / `Sign in` cross-links), and `signup/+page.server.ts:70` when auto-logged-in.
- **Skill Responsible:** `sveltekit-data-flow` + `supabase`
- **Scope:** `frontEnd/src/routes/login/*`, `signup/*`, `profile/+page.server.ts`, `auth/callback/+server.ts`, `terrace/+page.svelte`, `messages/+page.svelte`, `notifications/+page.svelte`
- **Risk:** Low-Medium (must preserve strict open-redirect guard on all `next` consumers so external URLs like `https://evil.com`, `//evil.com`, or `/\evil.com` always fall back to `/profile`).
- **Acceptance Criteria:**
  - Signing in via email/password or Google OAuth from `/messages?recipient=usr_seed_alex` returns the user directly to `/messages?recipient=usr_seed_alex`.
  - Malicious `?next=https://evil.com` or `?next=//evil.com` redirects safely to `/profile`.

---

#### `COM-P1-7` · `/notifications` missing `aria-live` announcements, mark-read pending state, mobile header wrap & link navigation race
- **Severity:** `P1`
- **File Citations:**
  - [notifications/+page.svelte:37-58](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/notifications/+page.svelte#L37-L58)
  - [notifications/+page.svelte:66-118](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/notifications/+page.svelte#L66-L118)
  - [notifications/+page.svelte:157](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/notifications/+page.svelte#L157)
  - [notifications/+page.svelte:163-171](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/notifications/+page.svelte#L163-L171)
  - [notifications/+page.svelte:206-238](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/notifications/+page.svelte#L206-L238)
- **Evidence:**
  1. There is no `aria-live="polite"` status region anywhere in `notifications/+page.svelte`. Realtime inserts (`lines 37-58`) and read-status updates (`lines 66-118`) happen silently for assistive technology.
  2. Neither `Mark all read ({unreadCount})` (`lines 163-171`) nor per-row `Mark read` (`lines 228-237`) tracks in-flight pending state (`disabled`), permitting duplicate requests and giving no confirmation text when `Mark all read` succeeds.
  3. Clicking `<a href={notif.link} onclick={() => handleMarkRead(notif)}>` (`lines 206-209`) navigates immediately while `handleMarkRead` runs asynchronously; if the `POST /notifications/{id}/read` request fails, the user has already left `/notifications` and never sees the error or rollback (and on future return, the notification is unexpectedly still unread).
  4. Page header (`line 157`) uses `flex items-end justify-between gap-4` without `flex-wrap`, risking horizontal crowding on `320px` screens when `Mark all read` is visible.
- **User Impact:** Screen-reader users receive no live notification or mark-read feedback; slow connections can leave clicked notifications unread without warning; narrow mobile headers crowd.
- **Proposed Solution:**
  - Add a polite status region (`<p aria-live="polite" class="visually-hidden">{statusAnnouncement}</p>` or visible subtle status line) announcing new Realtime alerts (`"New notification: …"`) and `"Marked as read"` / `"All notifications marked as read"`.
  - Add `isMarkingAll` and `markingIds` pending flags to disable repeat clicks during requests.
  - On notification link click (`!notif.is_read`), either use `navigator.sendBeacon` / `keepalive: true` on the mark-read request or await `handleMarkRead(notif)` before `goto(notif.link)` (with `e.preventDefault()` only when `!notif.is_read`, navigating even if mark-read fails or surfacing inline retry).
  - Add `flex-wrap` to `line 157` (`flex flex-wrap items-end justify-between gap-4`).
- **Skill Responsible:** `a11y-audit` + `improve-ui`
- **Scope:** `frontEnd/src/routes/notifications/+page.svelte` (and optional `keepalive` option in `markNotificationRead` in `football.ts`)
- **Risk:** Low.
- **Acceptance Criteria:**
  - Marking a single item or all items announces the update in an `aria-live="polite"` region and disables the button while in flight.
  - Clicking an unread notification reliably persists `is_read=true` before/during route transition.

---

#### `COM-P1-8` · `/signup` missing `emailRedirectTo` & verification resend + `/auth/reset-password` recovery hash/error race
- **Severity:** `P1`
- **File Citations:**
  - [signup/+page.server.ts:41-51](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/signup/+page.server.ts#L41-L51)
  - [signup/+page.svelte:48-60](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/signup/+page.svelte#L48-L60)
  - [auth/reset-password/+page.svelte:16-54](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/auth/reset-password/+page.svelte#L16-L54)
  - [auth/reset-password/+page.svelte:122-135](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/auth/reset-password/+page.svelte#L122-L135)
- **Evidence:**
  1. `signup/+page.server.ts:41-51` omits `emailRedirectTo: '${url.origin}/auth/callback'` in `signUp({ options })`, so email confirmation links may redirect to `/` instead of exchanging the PKCE code at `/auth/callback`.
  2. When `form?.needsEmailVerification` renders (`signup/+page.svelte:48-60`), there is no `"Resend confirmation email"` button if the user misses or expires the email.
  3. On `/auth/reset-password` (`auth/reset-password/+page.svelte:19-48`), `initRecovery()` immediately checks `getSession()` before Supabase finishes processing implicit `#access_token=...&type=recovery` hash tokens or emitting `PASSWORD_RECOVERY`, and ignores `?error_description=`/`?error=` query params returned by Supabase on expired links, showing a generic expired message even when the provider gave a specific reason.
- **User Impact:** New signups verifying via email may land unauthenticated or get stuck without a resend option; password recovery users arriving with hash tokens or expired links see premature or unhelpful expired-link states.
- **Proposed Solution:**
  - Pass `url` into `signup/+page.server.ts` action and set `emailRedirectTo: `${url.origin}/auth/callback`` (forwarding safe `?next=` if present). Add a `"Resend verification email"` button in `signup/+page.svelte` calling `data.supabase.auth.resend({ type: 'signup', email: form.email, options: { emailRedirectTo: ... } })` with cooldown/status feedback.
  - In `auth/reset-password/+page.svelte`, read `params.get('error_description') || params.get('error')` first (and hash params if present), call `getUser()` alongside `onAuthStateChange` (`PASSWORD_RECOVERY`), and only finish `checkingSession = false` after any hash-exchange microtask settles so valid recovery links never flash the expired state.
- **Skill Responsible:** `supabase` + `improve-ui`
- **Scope:** `frontEnd/src/routes/signup/+page.server.ts`, `frontEnd/src/routes/signup/+page.svelte`, `frontEnd/src/routes/auth/reset-password/+page.svelte`
- **Risk:** Low-Medium (verify against live Supabase email confirmation & recovery redirect URLs).
- **Acceptance Criteria:**
  - `signUp()` sets `emailRedirectTo` to `<origin>/auth/callback`.
  - Verification screen offers a working `Resend confirmation email` action with status/error feedback.
  - Recovery links with `?error_description=...` display the provider reason cleanly; valid recovery sessions never flash the expired screen.

---

#### `COM-P1-9` · `/profile` invisible focus ring on avatar input, impossible avatar removal, orphaned uploads, `invalidateAll()` form wipe & `320px` UUID overflow
- **Severity:** `P1`
- **File Citations:**
  - [profile/+page.svelte:66-108](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/profile/+page.svelte#L66-L108)
  - [profile/+page.svelte:197-210](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/profile/+page.svelte#L197-L210)
  - [profile/+page.svelte:226-242](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/profile/+page.svelte#L226-L242)
  - [profile/+page.svelte:248-276](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/profile/+page.svelte#L248-L276)
  - [profile/+page.server.ts:44-46](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/profile/+page.server.ts#L44-L46)
- **Evidence:**
  1. `<input id="avatar-upload" class="visually-hidden">` (`lines 233-240`) holds keyboard focus off-screen while the visible `<label for="avatar-upload">` (`lines 227-232`) has no focus styling (`focus-within` / `:has(:focus-visible)`), violating WCAG 2.4.7 Focus Visible.
  2. `profile/+page.server.ts:44-46` only writes `avatar_url` when `avatarUrlRaw !== ''`, and there is no `"Remove avatar"` button in `profile/+page.svelte` to clear a broken or unwanted avatar back to initials.
  3. `handleAvatarSelect` (`line 67`) uses a timestamped filename (`${data.user.id}/${Date.now()}-...`) with `upsert: true`, accumulating orphaned files in `avatars` Storage on every upload, and calls `await invalidateAll()` (`line 101`) which can reset unsaved edits in the un-bound `display_name` / `bio` inputs (`lines 260, 275`). Also `avatarLoadFailed` (`line 158`) fails silently to initials with no notice to the user.
  4. Account `<dl>` rows (`lines 197-210`) use `flex justify-between` without `gap-4`, `flex-wrap`, or `break-all`, so a 36-char UUID (`line 208`) or long email collides/overflows on `320px–375px` viewports.
- **User Impact:** Keyboard users cannot see when the avatar picker is focused; users can never delete an uploaded avatar; uploading an avatar after typing a new bio can discard their typed bio; mobile profile metadata overflows.
- **Proposed Solution:**
  - Style the avatar trigger with `focus-within:outline-2 focus-within:outline-focus focus-within:outline-offset-2` (or place `<input class="visually-hidden">` inside `<label>` with Tailwind `has-[:focus-visible]:outline-2 has-[:focus-visible]:outline-[var(--color-focus)]`).
  - Add a `"Remove portrait"` button when `avatarUrl` is set, and allow `profile/+page.server.ts` (or a dedicated `?/removeAvatar` action / explicit `remove_avatar` flag) to set `avatar_url = null` while preserving Storage RLS (`${uid}/...`).
  - Bind `displayNameInput` / `bioInput` to `$state` (synced initially) so `invalidateAll()` does not overwrite unsaved typing, or remove previous `avatars` object on replacement (`storage.from('avatars').remove([oldPath])`) when stored in user's folder.
  - Add `gap-4 flex-wrap` and `break-all text-right` on `<dd>` in `lines 197-210` (or replace raw `User ID` UUID with `Joined` date / concise account handle).
- **Skill Responsible:** `a11y-audit` + `supabase` + `improve-ui`
- **Scope:** `frontEnd/src/routes/profile/+page.svelte`, `frontEnd/src/routes/profile/+page.server.ts`
- **Risk:** Low.
- **Acceptance Criteria:**
  - Tabbing onto the avatar upload control displays a visible `--color-focus` ring around the button.
  - Users can upload, preview, and remove their avatar cleanly without wiping unsaved `display_name`/`bio` edits.
  - Profile metadata rows fit cleanly inside `320px` width without horizontal overflow.

---

### P2 — Medium-Impact Ergonomics, Validation, Responsive & Copy Polish

#### `COM-P2-1` · Auth & Profile forms lack password visibility toggles, `autocomplete`, `use:enhance` pending states, live hints & `role="alert"`
- **Severity:** `P2`
- **File Citations:**
  - [login/+page.svelte:95-99,134-212](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/login/+page.svelte#L95-L99)
  - [signup/+page.svelte:42-46,95-176](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/signup/+page.svelte#L42-L46)
  - [profile/+page.svelte:185-195,219-224,248-359](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/profile/+page.svelte#L185-L195)
  - [auth/reset-password/+page.svelte:101-121,137-176](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/auth/reset-password/+page.svelte#L101-L121)
  - [008_overhaul_schema_and_rls.sql:200-208](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/db/migrations/008_overhaul_schema_and_rls.sql#L200-L208)
- **Evidence:**
  1. None of the 4 password-entry routes (`/login`, `/signup`, `/profile`, `/auth/reset-password`) provide a show/hide password toggle.
  2. Inputs across all 4 routes omit `autocomplete` (`email`, `current-password`, `new-password`, `username`, `name`), impairing password managers and WCAG 1.3.5.
  3. `<form method="POST">` on `/login`, `/signup`, and `/profile` (`updateProfile`) omit `use:enhance` submit-pending states (`isSubmitting`), allowing accidental double-clicks without loading feedback.
  4. All error/success banners on `/login`, `/signup`, `/profile`, and `/auth/reset-password` omit `role="alert"` / `aria-live="polite"`.
  5. `/signup` password requirement (`minlength="6"`) only lives in a disappearing placeholder, and `username` gives no format guidance even though `handle_new_user()` (`008_overhaul_schema_and_rls.sql:203-204`) strips non-`[a-zA-Z0-9_]` characters and lowercases it.
- **User Impact:** Higher typo rates and lockouts on mobile password entry; screen readers fail to announce form errors or saves; double-submissions on signup/login; unexpected username normalization.
- **Proposed Solution:**
  - Add accessible `Show` / `Hide` toggle buttons (`aria-pressed`, `aria-controls`) inside relative wrappers on password inputs.
  - Add semantic `autocomplete` attributes to every auth/profile input.
  - Wire SvelteKit `use:enhance` on `/login`, `/signup`, and `/profile` (`?/updateProfile`) to show `"Signing in…"`, `"Creating account…"`, `"Saving…"` with `disabled`.
  - Add `role="alert"` to error banners and `aria-live="polite"` to success banners.
  - Add persistent helper text under `#username` (`"Letters, numbers, and underscores only; stored lowercase"`) and `#password` (`"At least 6 characters"`), plus live password-match indicator on `/profile` and `/auth/reset-password`.
- **Skill Responsible:** `a11y-audit` + `improve-ui`
- **Scope:** `frontEnd/src/routes/login/+page.svelte`, `signup/+page.svelte`, `profile/+page.svelte`, `auth/reset-password/+page.svelte`
- **Risk:** Low.
- **Acceptance Criteria:**
  - Every password field toggles between `password` and `text` with `aria-pressed`; every auth/profile field carries appropriate `autocomplete`.
  - Submitting `/login`, `/signup`, or `/profile` disables the submit button with a pending label until completion and announces errors via `role="alert"`.

---

#### `COM-P2-2` · `/terrace` dead `clearImageAttachment()`, inline Edit lacks upload/preview & missing character limits / image `onerror`
- **Severity:** `P2`
- **File Citations:**
  - [terrace/+page.svelte:271-276](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/terrace/+page.svelte#L271-L276)
  - [terrace/+page.svelte:722-731,739-745,786-799](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/terrace/+page.svelte#L722-L731)
  - [terrace/+page.svelte:986-1034,1053-1058,1066,1104](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/terrace/+page.svelte#L986-L1034)
  - [terrace/+page.svelte:1257-1277](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/terrace/+page.svelte#L1257-L1277)
- **Evidence:**
  1. `clearImageAttachment()` (`lines 271-276`) is never called (`Cancel` at `line 741` and `Remove` at `line 791` mutate `newPostImageUrl = ''` directly, leaving stale `imageUploadError` visible).
  2. Inline post Edit (`lines 986-1034`) only exposes a raw URL `<input>` (`line 1004`), with no image preview, no `Clear image` button, and no `terrace-media` file upload option.
  3. Composer (`line 728`, backend limit `2000`) and reply input (`line 1258`, backend limit `1000`) lack `maxlength` / counter feedback, so long posts only fail after submit with HTTP 422.
  4. Preview `<img>` (`line 788`) and feed `<img>` (`line 1054`) lack `onerror` broken-URL fallback; preview wrapper (`line 787`) omits `rounded-card`; `lines 1066, 1104` have redundant `pl-4 py-2` overridden by `p-4`.
- **User Impact:** Stale upload errors linger after removing/cancelling photos; post owners editing an image post cannot preview or upload a replacement photo; users typing long tactical debriefs hit surprise 422 errors.
- **Proposed Solution:**
  - Call `clearImageAttachment()` from both `Cancel` (`line 741`) and `Remove` (`line 791`), and add `rounded-card` to `line 787`.
  - Add an inline image preview + `Remove image` button (and optional file upload reusing the `terrace-media` handler) to the inline Edit panel (`lines 1000-1012`).
  - Add `maxlength="2000"` + subtle remaining-char counter when `> 1600` chars on composer/edit, and `maxlength="1000"` on reply inputs.
  - Add `onerror` state on attachment images to show a clean fallback notice (`"Image could not be loaded"`) instead of a broken image icon.
- **Skill Responsible:** `improve-ui`
- **Scope:** `frontEnd/src/routes/terrace/+page.svelte`
- **Risk:** Low.
- **Acceptance Criteria:**
  - Cancelling or removing a photo clears both preview and any prior `imageUploadError`.
  - Editing a post shows a thumbnail preview of the current image and allows clearing or replacing it.
  - Broken image URLs render a clean textual fallback rather than a broken browser image glyph.

---

#### `COM-P2-3` · `/terrace` undersized `h-6`/`h-7` touch targets & mobile search bar squeeze
- **Severity:** `P2`
- **File Citations:**
  - [terrace/+page.svelte:622-652](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/terrace/+page.svelte#L622-L652)
  - [terrace/+page.svelte:693-705](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/terrace/+page.svelte#L693-L705)
  - [terrace/+page.svelte:964-979,1177-1245](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/terrace/+page.svelte#L964-L979)
- **Evidence:**
  1. Comment Confirm/Cancel/Save/Cancel buttons (`lines 1181, 1189, 1233, 1241`) use `h-6` (`24px` tall), and post/comment `Edit` / `Delete` text buttons (`lines 964-979, 1195-1210`) have zero vertical/horizontal padding, falling below comfortable mobile touch targets (recommended `>= 32-36px`, WCAG 2.5.8 spacing/size). Trending topic pills (`line 701`) use `h-7` (`28px`).
  2. Search bar row (`line 622`) uses `flex items-center gap-3` without `flex-wrap`, squeezing `#search` input on `320px–375px` screens whenever `Reset` is rendered alongside `Search`.
- **User Impact:** Mobile users miss or mis-tap `Edit`/`Delete`/`Confirm` controls on posts and comments, and the search input becomes cramped when filters are active on small phones.
- **Proposed Solution:**
  - Bump `h-6` / unpadded action buttons to `min-h-8 px-2.5` (and trending pills to `min-h-8`), and add `flex-wrap` on `line 622` (`flex flex-wrap sm:flex-nowrap items-center gap-2.5`) with `min-w-[200px]` on the input container.
- **Skill Responsible:** `a11y-audit` + `improve-ui`
- **Scope:** `frontEnd/src/routes/terrace/+page.svelte`
- **Risk:** Low.
- **Acceptance Criteria:**
  - All post/comment action buttons have `>= 32px` height and clean spacing; search bar never squishes below usable width at `320px`.

---

#### `COM-P2-4` · `/messages` missing multi-day date dividers, bubble `break-words` & noisy `(Arsenal)` suffix
- **Severity:** `P2`
- **File Citations:**
  - [messages/+page.svelte:431-438](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/messages/+page.svelte#L431-L438)
  - [messages/+page.svelte:500](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/messages/+page.svelte#L500)
  - [messages/+page.svelte:686-701](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/messages/+page.svelte#L686-L701)
- **Evidence:**
  1. `formatTime()` (`lines 431-438`) formats only `HH:MM` (`toLocaleTimeString`), omitting dates across multi-day conversations.
  2. Message bubbles (`line 696`) lack `break-words` / `[overflow-wrap:anywhere]`, so long unbroken links or hashes overflow horizontally.
  3. Sidebar (`line 500`) applies `border-r border-rule` unconditionally instead of `border-b md:border-b-0 md:border-r`.
  4. Line 692 prints `({msgClub.short_name})` (`(Arsenal)`) on every single bubble in an Arsenal-only supporter portal.
- **User Impact:** Multi-day debates look like they all happened today; pasted links can break mobile chat bubble width.
- **Proposed Solution:**
  - Insert lightweight date-separator headings (`Today`, `Yesterday`, or `Nov 11`) whenever `new Date(msg.created_at).toDateString()` changes between consecutive messages, or include short date in `formatTime` when not today.
  - Add `break-words [overflow-wrap:anywhere]` to `line 696`, fix `md:border-r border-b md:border-b-0` on `line 500`, and omit redundant `({msgClub.short_name})` when `msg.sender_club_id === 'arsenal'`.
- **Skill Responsible:** `improve-ui`
- **Scope:** `frontEnd/src/routes/messages/+page.svelte`
- **Risk:** Low.
- **Acceptance Criteria:**
  - Multi-day conversations show clear day transitions; long unbroken URLs wrap cleanly inside `max-w-[75%]` bubbles at `375px`.

---

#### `COM-P2-5` · `/supporters/[username]` `metric.replace('_', ' ')` underscore leak, missing Terrace post links, unclear `Unranked` & `profile` key shadowing
- **Severity:** `P2`
- **File Citations:**
  - [supporters/[username]/+page.svelte:100-105](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/supporters/[username]/+page.svelte#L100-L105)
  - [supporters/[username]/+page.svelte:146](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/supporters/[username]/+page.svelte#L146)
  - [supporters/[username]/+page.svelte:188-200](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/supporters/[username]/+page.svelte#L188-L200)
  - [supporters/[username]/+page.ts:10](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/supporters/[username]/+page.ts#L10)
  - [+layout.ts:33](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/+layout.ts#L33)
- **Evidence:**
  1. `line 146` calls `ins.metric.replace('_', ' ')` (single replacement), rendering `"goals per_match"` or `"clean sheet_rate"` on insight cards.
  2. `recent_posts` items (`lines 189-199`) display text and counts with no link to `/terrace#post-{post.id}`, whereas `featured_insights` (`lines 160-165`) links to `/lab`.
  3. `prediction_rank === 0 ? 'Unranked' : ...` (`line 103`) gives no hint on how ranking works or where to predict.
  4. `supporters/[username]/+page.ts:10` returns `{ profile }`, shadowing `+layout.ts:33`'s logged-in `profile` key on `page.data`.
- **User Impact:** Typographical underscore artifact in insight labels; visitors cannot jump from a supporter's post snippet to the full Terrace thread; new supporters don't know why they're `Unranked`.
- **Proposed Solution:**
  - Replace `ins.metric.replace('_', ' ')` with `ins.metric.replaceAll('_', ' ')` (or a clean metric label map).
  - Add a `"View on Terrace"` link (`href="/terrace#post-{post.id}"`) on each `recent_posts` entry.
  - Below `Unranked`, show muted caption `"0 scored predictions"` (and if viewing own profile, link to `/predictions`).
  - Rename the return property in `supporters/[username]/+page.ts` to `supporterProfile` so `+layout.ts`'s `data.profile` (authenticated user) is never shadowed.
- **Skill Responsible:** `improve-ui` + `sveltekit-data-flow`
- **Scope:** `frontEnd/src/routes/supporters/[username]/+page.svelte`, `frontEnd/src/routes/supporters/[username]/+page.ts`
- **Risk:** Low.
- **Acceptance Criteria:**
  - Insight cards display `"goals per match"` / `"clean sheet rate"` with zero underscores; Terrace post rows link to `/terrace#post-{id}`; `data.profile` remains the signed-in user's profile.

---

### P3 — Minor Token Alignment, Copy & Cleanup

#### `COM-P3-1` · Modals hardcode `z-50` matching sticky header instead of `tokens.css` z-index scale (`--z-modal` / `--z-sticky-nav`)
- **Severity:** `P3`
- **File Citations:**
  - [tokens.css:76-78](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/tokens.css#L76-L78)
  - [+layout.svelte:107](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/+layout.svelte#L107)
  - [terrace/+page.svelte:1288,1345](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/terrace/+page.svelte#L1288)
  - [messages/+page.svelte:736](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/messages/+page.svelte#L736)
- **Evidence:** `tokens.css` defines `--z-sticky-nav: 300` and `--z-modal: 400`, yet `+layout.svelte:107`, `terrace/+page.svelte:1288,1345`, and `messages/+page.svelte:736` all use `z-50`.
- **User Impact:** Fragile stacking order if sticky nav and modal overlays interact across nested stacking contexts.
- **Proposed Solution:** Use `z-[var(--z-sticky-nav)]` on the header and `z-[var(--z-modal)]` on all modal/lightbox backdrops.
- **Skill Responsible:** `hallmark`
- **Scope:** `+layout.svelte`, `terrace/+page.svelte`, `messages/+page.svelte`
- **Risk:** Low.
- **Acceptance Criteria:** Modals reliably stack above the sticky header via `tokens.css` tokens (`400 > 300`).

---

#### `COM-P3-2` · Generic image `alt` text, unused `lib/supabase.ts` import, raw OAuth errors & `/notifications` cap clarity
- **Severity:** `P3`
- **File Citations:**
  - [terrace/+page.svelte:1055,1361](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/terrace/+page.svelte#L1055)
  - [notifications/+page.svelte:160,195-199](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/notifications/+page.svelte#L160)
  - [login/+page.svelte:95-99](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/login/+page.svelte#L95-L99)
  - [lib/supabase.ts:1,4-5](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/lib/supabase.ts#L1)
- **Evidence:**
  1. `terrace/+page.svelte:1055` (`alt="Post attachment"`) and `line 1361` (`alt="Full size preview"`) provide generic screen-reader labels with no author context.
  2. `lib/supabase.ts:1` imports unused `createServerClient` and silently defaults to `'https://mock.supabase.co'` / `'mock-anon-key'` without warning in dev/prod if env vars are unset.
  3. `login/+page.svelte:97` echoes raw `?error=` codes (e.g. `access_denied`) directly from `auth/callback`.
  4. `notifications/+page.svelte` fetches default `limit=20` (`notifications.py:24`) with no subtitle or `"Showing latest 20 alerts"` note.
- **User Impact:** Minor screen-reader clarity and troubleshooting polish.
- **Proposed Solution:**
  - Enrich image `alt` (`"Photo shared by {post.author_name}"`) and lightbox button `aria-label` (`"Enlarge photo shared by {post.author_name}"`).
  - Remove unused `createServerClient` import in `lib/supabase.ts` and log a `console.warn` when `PUBLIC_SUPABASE_URL` is missing.
  - Map common `?error=` values (`access_denied` → `"Google sign-in was cancelled. Try again or sign in with email."`) on `/login`.
  - Add a muted footer/caption (`"Showing your 20 most recent notifications"`) on `/notifications` when `notifications.length === 20`.
- **Skill Responsible:** `improve-ui` + `supabase`
- **Scope:** `terrace/+page.svelte`, `notifications/+page.svelte`, `login/+page.svelte`, `lib/supabase.ts`
- **Risk:** Low.
- **Acceptance Criteria:** Screen readers hear descriptive attachment labels; cancelled Google OAuth shows human-readable copy; `lib/supabase.ts` has zero unused imports.

---

## 4. Recommended Fix Execution Order (Phase 2 Handoff)

1. **Auth & SSR Foundation (`COM-P0-3`, `COM-P1-6`, `COM-P1-8`, `COM-P2-1`):** Harden `auth/signout/+server.ts` (`POST`-only) & `+layout.ts` (`getUser()`-gated session), preserve safe `?next=` across all auth gates, add `emailRedirectTo` + resend + recovery hash/error handling, and upgrade form `autocomplete`/password toggles/`use:enhance`/`role="alert"`.
2. **Direct Messaging (`COM-P0-1`, `COM-P1-4`, `COM-P1-5`, `COM-P2-4`):** Fix mobile inbox ↔ thread switching & `min-h-0` scroll containment, fix Realtime optimistic-send deduplication + truthful status + auto-scroll, make full conversation rows clickable, and add accessible dialog/keyboard support to the Start Debate modal.
3. **The Terrace (`COM-P0-2`, `COM-P1-1`, `COM-P1-2`, `COM-P1-3`, `COM-P2-2`, `COM-P2-3`):** Remove guest `onfocus` traps, add focus-trapped accessible modals/lightbox, fix photo-only Publish guard, fix author portfolio links & hide self-DM CTA, add inline post error notices + `aria-pressed`/`aria-expanded` + comment loading state, and polish Edit image UX & touch targets.
4. **Profile, Notifications & Supporters (`COM-P1-7`, `COM-P1-9`, `COM-P2-5`, `COM-P3-1`, `COM-P3-2`):** Add `aria-live` & mark-read pending/navigation safety on `/notifications`, fix `/profile` avatar focus ring + remove action + `320px` overflow, fix `/supporters/[username]` underscore bug + Terrace permalinks + `supporterProfile` key rename, and align modal z-index to `tokens.css`.
