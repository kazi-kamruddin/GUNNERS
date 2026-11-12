# Phase 1 Forensic UX/UI Audit — Interactive Studio, Data Lab & Predictor

> **Auditor:** `audit-interactive`  
> **Date:** 2026-11-13  
> **Status:** Complete (Strictly Read-Only Audit)  
> **Audited Surface:**
> - **The Dugout (Tactical Pitch Studio):** [`frontEnd/src/lib/components/TacticalBoard.svelte`](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/lib/components/TacticalBoard.svelte), [`frontEnd/src/routes/board/+page.svelte`](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/board/+page.svelte), [`frontEnd/src/routes/board/+page.ts`](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/board/+page.ts)
> - **The Data Lab & Historical Pitch Explorer:** [`frontEnd/src/routes/lab/+page.svelte`](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/lab/+page.svelte), [`frontEnd/src/routes/lab/+page.ts`](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/lab/+page.ts), [`frontEnd/src/lib/components/HistoricalPitchExplorer.svelte`](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/lib/components/HistoricalPitchExplorer.svelte), [`frontEnd/src/routes/lab/historical/+page.svelte`](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/lab/historical/+page.svelte), [`frontEnd/src/routes/lab/historical/+page.ts`](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/lab/historical/+page.ts)
> - **Matchday Predictor & Leaderboard:** [`frontEnd/src/routes/predictions/+page.svelte`](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/predictions/+page.svelte), [`frontEnd/src/routes/predictions/+page.ts`](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/routes/predictions/+page.ts)
> - **Shared Client API & Contracts:** [`frontEnd/src/lib/api/football.ts`](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/lib/api/football.ts), [`frontEnd/src/lib/api/community.ts`](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/lib/api/community.ts), [`frontEnd/src/lib/stores/theme.svelte.ts`](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/lib/stores/theme.svelte.ts)
>
> **Design Authority & Skill Guides Verified:**
> - [`design.md`](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/design.md), [`frontEnd/src/tokens.css`](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/tokens.css), [`frontEnd/src/base.css`](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/base.css), [`frontEnd/src/app.css`](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/app.css)
> - [`.agents/skills/hallmark/SKILL.md`](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/.agents/skills/hallmark/SKILL.md), [`.agents/skills/a11y-audit/SKILL.md`](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/.agents/skills/a11y-audit/SKILL.md), [`.agents/skills/svelte-runes/SKILL.md`](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/.agents/skills/svelte-runes/SKILL.md), [`.agents/skills/improve-ui/SKILL.md`](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/.agents/skills/improve-ui/SKILL.md)
> - [`.project-context/03_API_CONTRACTS.md`](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/.project-context/03_API_CONTRACTS.md), [`.project-context/05_UI_ARCHITECTURE_AND_DESIGN_SYSTEM.md`](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/.project-context/05_UI_ARCHITECTURE_AND_DESIGN_SYSTEM.md)

---

## 1. Executive Summary & Severity Matrix

Across the three interactive surfaces (`/board`, `/lab` + `/lab/historical`, and `/predictions`), the core Hallmark v2.0.0 broadsheet palette (`--color-paper`, `--color-accent`, `--color-accent-2`, `--color-pitch`), normalized `0..100` SVG coordinate architecture, and primary Happy-Path endpoints are well-grounded. However, a forensic line-by-line inspection reveals **29 verified findings** (encompassing 32 distinct defects) across accessibility, mobile layout physics, state/data integrity, truthful API error feedback, SSR hydration, and CRUD parity:

| Severity | Count | Summary of Critical Themes |
| :--- | :---: | :--- |
| **P0** (Blocker / Data Integrity / Severe Mobile & A11y Break) | **6** | `predictions` mobile scoreline grid overflow (`col-span-1` ~41px holding ~102px inputs); `TacticalBoard` `focus:outline-none` + 0px drag threshold blocking touch tap-to-edit + `touch-none` scroll trap & stuck pointer draw; `lab` stale `metric`/`venue` saved into mismatched insight snapshot; `lab` Save Insight modal missing dialog/focus-trap/Escape; `$effect`-only state hiding SSR content (Hallmark Floor #7) across all 4 routes. |
| **P1** (High / Core UX, Brand Truth, CRUD & Error Parity) | **14** | Legacy departed bench (`Neto #32`, `Jorginho #20`, `Sterling #30`) & readonly Terrace bench leak; `"GUNNERS REBORN"` PNG banner + missing tactical arrows in PNG export; missing `DELETE /api/v1/tactics/{id}` & `DELETE /api/v1/insights/{id}` owner UI + unauthenticated `fetchTacticalBoards`; `football.ts` / `community.ts` swallowing HTTP/network errors as empty states; incomplete `?tab=` / `?match=` / club URL sync & optimistic clipboard toast; SVG chart mobile legibility (`~4.6px` text, `~7px` overlapping penalty shots); StatsBomb ODbL link attribution; 60s countdown drift & leaderboard async race + unencoded `/supporters/` link; missing keyboard token nudging/bench swap & `<select id="player-role">` option mismatch. |
| **P2** (Medium / Ergonomics, Sample Confidence & Polish) | **7** | Missing Undo / per-arrow delete on `/board`; `onshare` discarding unsaved pitch edits; first-time user hints & mobile 8-col bench truncation; `Query` tab non-reactive selects & zero/unequal sample-size confidence warnings; non-keyboard `<tr>` in Trends table & static Pass Network nodes; `z-50` modal/toast colliding with sticky header (`z-50`); Prediction History truncation, missing `/matches/{id}` links & `total_predictions_count` social proof. |
| **P3** (Low / Maintainability & Minor Refinements) | **2** | Unkeyed `{#each}` blocks across dynamic SVG/list loops; unused `_authorClub` constant & minor template cleanup. |

### Top 5 Immediate Action Items
1. **INT-P0-01 (`predictions/+page.svelte:334-366`):** Replace the `grid-cols-7` (`col-span-1` = ~41px) scoreline layout with a responsive flex/stacked matchup row + `44px` `-`/`+` numeric steppers and `inputmode="numeric"`.
2. **INT-P0-02 & INT-P0-03 (`TacticalBoard.svelte:88-152, 401-411, 494`):** Remove `focus:outline-none`, add visible `:focus-visible` SVG ring, enforce a `> 0.8%` drag threshold before `hasDragged = true`, scope `touch-none` to active token drag / drawing modes (plus `setPointerCapture` + `onpointercancel`), so mobile scrolling and tap-to-edit both work reliably.
3. **INT-P0-04 (`lab/+page.svelte:245-286, 628-700`):** Bind `"Save as insight"` to `result`'s actual queried parameters (or auto-run `runQuery()` on `<select>` change) so `InsightCreateRequest` never pairs stale `snapshot` data with newly selected `metric`/`venue`.
4. **INT-P0-05 (`lab/+page.svelte:1571-1642` & `TacticalBoard.svelte:570-657`):** Add full WAI-ARIA dialog semantics (`role="dialog"`, `aria-modal="true"`, `aria-labelledby`), focus trap, `Escape` close, backdrop close, and trigger focus restoration, elevated to `--z-modal` (`z-[400]`).
5. **INT-P0-07 (`board/+page.svelte`, `lab/+page.svelte`, `HistoricalPitchExplorer.svelte`, `predictions/+page.svelte`):** Eliminate `$effect`-only data initialization so initial SSR payloads render visibly without JS and without hydration layout shift (Hallmark Floor #7).

---

## 2. Surface 1: Tactical Pitch Studio (`/board` & `TacticalBoard.svelte`)

### [INT-P0-02] Zero-Threshold Drag Detection Breaks Tap-to-Edit & `touch-none` Traps Mobile Scroll
- **Severity:** `P0`
- **Citations:**
  - `frontEnd/src/lib/components/TacticalBoard.svelte:84-152` (`handlePointerDown`, `handlePointerMove`, `handlePointerUp`)
  - `frontEnd/src/lib/components/TacticalBoard.svelte:401-411` (`<div class="... touch-none">` and `<svg>` event bindings)
  - Contrast with [`05_UI_ARCHITECTURE_AND_DESIGN_SYSTEM.md:76`](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/.project-context/05_UI_ARCHITECTURE_AND_DESIGN_SYSTEM.md#L76)
- **Evidence:**
  1. Line 102 sets `hasDragged = true;` unconditionally on the **first** `pointermove` event, with no distance threshold (despite `05_UI_ARCHITECTURE_AND_DESIGN_SYSTEM.md:76` documenting a `< 0.8%` delta threshold). Any 1px touch jitter or mouse micro-movement suppresses opening `editingPlayer` at lines 126–133.
  2. Line 401 applies `touch-none` permanently to the entire pitch wrapper, even when `activeTool === 'select'` (where touching empty turf does nothing) or when `readonly === true` (including embedded previews on `/terrace`). On mobile (`390px`), vertical page scrolling starting over the pitch is completely blocked.
  3. Lines 88–95 (`activeTool !== 'select'`) do not call `setPointerCapture(e.pointerId)` on `<svg>`, and lines 402–411 lack `onpointercancel`. If a pointer leaves the SVG or is cancelled by the OS during drag/draw, `draggingPlayerId` or `isDrawingVector` remains stuck `true`.
- **User Impact:** Mobile and trackpad users cannot reliably tap a player token to edit/swap from the Arsenal squad, cannot scroll past the pitch on narrow screens, and can get stuck with a dangling dashed vector line following the cursor.
- **Proposed Solution:**
  - Record `dragStartCoords = getPitchCoords(e)` in `handlePointerDown`; set `hasDragged = true` in `handlePointerMove` only when `Math.hypot(pt.x - dragStartCoords.x, pt.y - dragStartCoords.y) >= 0.8` (preserving `0..100` normalized pitch coordinates).
  - Apply `touch-none` **only** when `!readonly && (draggingPlayerId !== null || activeTool !== 'select')` (i.e., `class="... {!readonly && (activeTool !== 'select' || draggingPlayerId) ? 'touch-none' : 'touch-pan-y'}"`).
  - Call `(e.currentTarget as Element).setPointerCapture(e.pointerId)` when starting vector drawing, and bind `onpointercancel={handlePointerCancel}` on `<svg>` to reset `draggingPlayerId`, `isDrawingVector`, `vectorStart`, and `vectorCurrent`.
- **Skill Responsible:** `improve-ui`, `svelte-runes`
- **Scope:** `frontEnd/src/lib/components/TacticalBoard.svelte`
- **Risk:** Low — isolated pointer state cleanup; verify `/terrace` `readonly={true}` embed allows normal vertical scroll.
- **Acceptance Criteria:**
  1. Tapping a token with `< 0.8%` normalized pointer drift opens the Edit Player modal reliably on touch and mouse.
  2. With `activeTool === 'select'` (or `readonly={true}`), swiping vertically over empty pitch turf scrolls the page on `390px` viewports; dragging a token or drawing a vector suppresses scroll during the gesture.
  3. Firing `pointercancel` mid-drag or mid-draw cleanly resets active gesture state.

---

### [INT-P0-03] Player Tokens Suppress `:focus-visible` Outline & SVG Misuses `role="application"`
- **Severity:** `P0`
- **Citations:**
  - `frontEnd/src/lib/components/TacticalBoard.svelte:406` (`role="application"`)
  - `frontEnd/src/lib/components/TacticalBoard.svelte:494` (`class={readonly ? '' : 'cursor-grab active:cursor-grabbing focus:outline-none'}`)
- **Evidence:**
  - Line 494 explicitly applies `focus:outline-none` to interactive `<g role="button" tabindex="0">` player tokens without rendering any alternative `:focus-visible` ring in CSS or SVG. This directly violates **Hallmark Floor #6** (*"Every interactive element has `:focus-visible`, appearing instantly"*) and **`a11y-audit` Phase 2**.
  - Line 406 marks `<svg>` with `role="application"`, instructing assistive technologies to disable browse/virtual cursor navigation inside the pitch even though `<svg>` itself has no `tabindex` or `onkeydown` handler.
- **User Impact:** Keyboard-only users tabbing through the 11 starting tokens have zero visual indication of which player is focused, and screen-reader users encounter an application-mode trap.
- **Proposed Solution:**
  - Remove `focus:outline-none` on line 494 and add a scoped `.pitch-token:focus-visible` CSS rule (`outline: 2px solid var(--color-focus); outline-offset: 4px;`) plus a crisp SVG focus halo (`stroke="var(--color-focus)"`) when focused, keeping `--color-focus` from `tokens.css:91`.
  - Change `<svg role="application" ...>` (`line 406`) to `role={readonly ? 'img' : 'group'}` with `aria-label="Arsenal tactical pitch diagram"` so screen readers navigate the 11 `<g role="button">` tokens naturally in interactive mode and treat `/terrace` embeds as a single graphic in `readonly` mode.
- **Skill Responsible:** `a11y-audit`, `hallmark`
- **Scope:** `frontEnd/src/lib/components/TacticalBoard.svelte`
- **Risk:** Low.
- **Acceptance Criteria:**
  1. Tabbing across starting XI tokens displays an instant `2px` `--color-focus` ring on every focused token.
  2. In `readonly={true}` (`/terrace`), `<svg>` exposes `role="img"` and tokens have `tabindex="-1"`.

---

### [INT-P1-01] Legacy Departed Fallback Bench Players (`Neto #32`, `Jorginho #20`, `Sterling #30`) & Readonly Bench Leak
- **Severity:** `P1`
- **Citations:**
  - `frontEnd/src/lib/components/TacticalBoard.svelte:50-63` (`$effect` populating `Neto #32`, `Jorginho #20`, `Sterling #30`)
  - `frontEnd/src/lib/components/TacticalBoard.svelte:539-567` (Substitutes bench section)
  - `frontEnd/src/routes/terrace/+page.svelte:1127-1132` (`<TacticalBoardComponent ... readonly={true} />` without `bench`)
  - `frontEnd/src/lib/api/football.ts:862` (offline `4-3-3` fallback preset still lists `Zinchenko #35`)
  - Backend truth: [`backEnd/app/api/v1/endpoints/squad.py:16-24`](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/backEnd/app/api/v1/endpoints/squad.py#L16-L24) (`DEPARTED_PLAYER_IDS`)
- **Evidence:**
  - `TacticalBoard.svelte:53, 57, 59` hardcodes `Neto #32`, `Jorginho #20`, and `Sterling #30`, all of whom were explicitly pruned via `DEPARTED_PLAYER_IDS` from the active 25-player Arsenal squad.
  - Because `lines 50-63` run unconditionally when `bench.length === 0`, even `readonly={true}` embeds on `/terrace` (`terrace/+page.svelte:1127-1132`) populate and render the 8-button Substitutes Bench with interactive copy (`"Select a bench player to swap into the starting eleven"`) and clickable `<button>` elements that silently do nothing.
- **User Impact:** Supporters see departed players as current Arsenal substitutes on `/board` and inside every tactical post on `/terrace`, while `/terrace` feed cards are bloated with dead swap buttons.
- **Proposed Solution:**
  - Update default bench initialization to derive up to 8 non-starting players from `squadPlayers` when available (excluding names/numbers already present in `lineup`), falling back to current 2026/27 Arsenal squad members (`Kepa #13`, `Timber #12`, `Calafiori #33`, `Lewis-Skelly #49`, `Merino #23`, `Eze #10`, `Trossard #19`, `Madueke #20`).
  - Also update `football.ts:862` offline preset LB from `Zinchenko #35` to `Calafiori #33` (or `Lewis-Skelly #49`) for consistency.
  - Guard bench initialization and rendering with `{#if !readonly && bench && bench.length > 0}` (or render bench only when explicitly provided in `readonly` mode without swap instructions/button semantics).
- **Skill Responsible:** `improve-ui`, `svelte-runes`
- **Scope:** `frontEnd/src/lib/components/TacticalBoard.svelte`, `frontEnd/src/lib/api/football.ts`
- **Risk:** Low — `/terrace` embeds only pass `lineup` and `annotations`.
- **Acceptance Criteria:**
  1. Zero departed player names (`Neto`, `Jorginho`, `Sterling`, `Zinchenko`) appear in default `/board` bench or offline presets.
  2. `/terrace` tactical post embeds (`readonly={true}`) do not render dead bench swap buttons.

---

### [INT-P1-02] Stale `"GUNNERS REBORN"` PNG Export Banner, Missing Tactical Arrows, Text Overflow & Raw RGB Palette
- **Severity:** `P1`
- **Citations:**
  - `frontEnd/src/lib/components/TacticalBoard.svelte:208-310` (`exportLineupAsImage`)
- **Evidence:**
  - Line 246 draws `'GUNNERS REBORN : ARSENAL MATCHDAY TACTICAL LINEUP'` (legacy pre-overhaul project name).
  - Line 249 draws `FORMATION: ${formationName.toUpperCase()}` left-aligned at `x=960` inside a banner ending at `x=1150`; names like `5-3-2 Low Block Counter` overflow past the red banner edge.
  - Lines 251–277 draw `lineup` tokens and `bench`, **completely omitting `annotations`** (`run`, `pass`, `press` vectors). An exported PNG never includes any tactical arrows drawn by the user.
  - Lines 290–295 space bench labels at fixed `bx += 115`, clipping longer surnames (`#49 Lewis-Skelly`), and lines 216–295 hardcode raw RGB strings instead of resolving Hallmark `tokens.css` variables.
  - Line 307–309 catches export errors silently with `console.error` only.
- **User Impact:** Supporters exporting a tactical blueprint to share on social media or The Terrace receive a graphic stamped `"GUNNERS REBORN"` with clipped text and none of their tactical arrows.
- **Proposed Solution:**
  - Replace banner text with `'GUNNERS : ARSENAL MATCHDAY TACTICAL LINEUP'` and set `ctx.textAlign = 'right'` at `x=1130` for `FORMATION: ${formationName.toUpperCase()}` (resetting `textAlign = 'left'` afterward).
  - Render `annotations` (`run`, `pass`, `press` dashed/solid lines + arrowheads) onto the canvas using the exact `50 + (x / 100) * 1100`, `60 + (y / 100) * 680` mapping before drawing player tokens.
  - Resolve canvas colors from `getComputedStyle(document.documentElement)` tokens (`--color-pitch`, `--color-pitch-2`, `--color-accent`, `--color-accent-2`, `--color-paper`, `--color-ink`, `--color-success`, `--color-error`) with safe fallbacks, format the bench strip as a 2-row 4-column grid (`260px` column width) to prevent overlap, and surface an `exportErrorMessage` banner on failure.
- **Skill Responsible:** `hallmark`, `improve-ui`
- **Scope:** `frontEnd/src/lib/components/TacticalBoard.svelte`
- **Risk:** Low — self-contained Canvas 2D function; test `getComputedStyle` OKLCH color parsing in browsers (modern Chrome/Firefox/Safari support `oklch()` in Canvas 2D; provide hex fallbacks or canvas probe).
- **Acceptance Criteria:**
  1. Exported PNG displays `GUNNERS : ARSENAL MATCHDAY TACTICAL LINEUP`, right-aligned formation label without clipping, all drawn `run`/`pass`/`press` arrows with arrowheads, and non-overlapping 8-slot bench text.

---

### [INT-P1-03] Missing Owner-Delete UI for `DELETE /api/v1/tactics/{id}` & Unauthenticated `fetchTacticalBoards`
- **Severity:** `P1`
- **Citations:**
  - `frontEnd/src/routes/board/+page.svelte:259-291` (Community blueprint cards only have `Load to pitch`)
  - `frontEnd/src/routes/board/+page.ts:11` (`fetchTacticalBoards(viewingClub)` omits `accessToken`)
  - `frontEnd/src/lib/api/football.ts:913-932` (`fetchTacticalBoards` has no `accessToken` param; no `deleteTacticalBoard` function)
  - Backend contract: [`backEnd/app/api/v1/endpoints/tactics.py:251-281, 307-323`](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/backEnd/app/api/v1/endpoints/tactics.py#L251-L323) & [`03_API_CONTRACTS.md:82-84`](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/.project-context/03_API_CONTRACTS.md#L82-L84)
- **Evidence:**
  - Backend exposes `DELETE /api/v1/tactics/{board_id}` verifying `board.user_id == current_user.id`, and `GET /api/v1/tactics` returns the authenticated user's private boards when Bearer auth is sent.
  - Frontend has zero `deleteTacticalBoard()` helper and zero Delete button on owned blueprints in `/board`. `fetchTacticalBoards` also ignores the session JWT, so private boards cannot be loaded.
- **User Impact:** Users who publish a tactical board cannot remove or clean up their own mistakes/duplicates from `/board`.
- **Proposed Solution:**
  - Add `accessToken?: string | null` to `fetchTacticalBoards` & `fetchTacticalBoard`, and add `deleteTacticalBoard(boardId: string, accessToken?: string | null)` in `football.ts` using `buildHeaders` + `throwApiError`.
  - Pass `parentData.session?.access_token` in `board/+page.ts:11`.
  - On `board/+page.svelte`, check `isBoardOwner = Boolean(data.user?.id && b.user_id === data.user.id)` and provide the same accessible 2-step **Delete → Confirm delete / Cancel** pattern used in `/terrace`, removing the deleted board from `communityBoards`, clearing `savedBoardId` if active, and displaying truthful success or `ApiError` toast feedback.
- **Skill Responsible:** `improve-ui`, `a11y-audit`
- **Scope:** `frontEnd/src/lib/api/football.ts`, `frontEnd/src/routes/board/+page.ts`, `frontEnd/src/routes/board/+page.svelte`
- **Risk:** Low — matches `/terrace` 2-step delete pattern; backend already enforces ownership (`403` for non-owners).
- **Acceptance Criteria:**
  1. Authenticated board owners see **Delete** → **Confirm delete / Cancel** on their own blueprints in `/board`.
  2. Confirming calls `DELETE /api/v1/tactics/{id}` with Bearer auth, removes the card on `200`/`204`, and displays truthful error toast on `401`/`403`/`404`/network error.

---

### [INT-P1-04] Missing Keyboard Alternatives for Token Positioning & Bench Swap + `<select id="player-role">` Data Loss
- **Severity:** `P1`
- **Citations:**
  - `frontEnd/src/lib/components/TacticalBoard.svelte:201-206` (`handleRosterSelect` sets `editingPlayer.role = player.position`)
  - `frontEnd/src/lib/components/TacticalBoard.svelte:498-504` (`onkeydown` on starting tokens)
  - `frontEnd/src/lib/components/TacticalBoard.svelte:554-563` (Bench buttons missing `aria-pressed` & `disabled={readonly}`)
  - `frontEnd/src/lib/components/TacticalBoard.svelte:629-645` (`<select id="player-role">` options)
- **Evidence:**
  1. Line 498–504 only handles `Enter`/`Space` to open `editingPlayer`, completely ignoring `selectedBenchPlayerId` (unlike `handlePointerDown` line 79, which completes the bench swap!) and providing **no arrow-key nudging** to reposition a player on the pitch without a mouse/touch drag.
  2. Bench `<button>` at line 554 lacks `aria-pressed={isSelected}` and `aria-label` announcing role/status.
  3. Line 205 sets `editingPlayer.role = player.position` (`"Goalkeeper"`, `"Defender"`, `"Midfielder"`, `"Attacker"`), while `<select id="player-role">` (lines 634–643) only contains `GK, CB, LB, RB, DM, CM, AM, LW, RW, ST` — also missing `LWB`, `RWB`, `LM`, `RM` used by backend presets `3-4-2-1`, `4-4-2`, `3-5-2`, `5-3-2`! Selecting a squad player from the dropdown blanks the role `<select>` UI.
- **User Impact:** Keyboard-only users cannot move players on the pitch or swap substitutes onto the pitch, and picking any player from the Arsenal squad dropdown corrupts the visible role dropdown to blank.
- **Proposed Solution:**
  - In `onkeydown` on starting tokens (`line 498`):
    - If `selectedBenchPlayerId` is set and user presses `Enter`/`Space`, complete `swapBenchWithStarting(selectedBenchPlayerId, player.id)`.
    - Add `ArrowLeft`/`ArrowRight`/`ArrowUp`/`ArrowDown` handling to nudge `player.x` / `player.y` by `2` normalized units (`0.5` with `Shift`), clamped to `[2, 98]`, updating `onchange?.()` and `aria-valuetext`.
  - Add `aria-pressed={isSelected}` and `disabled={readonly}` on bench buttons (`line 554`).
  - Map `player.position` in `handleRosterSelect` to sensible default tactical codes (`Goalkeeper→GK`, `Defender→CB`, `Midfielder→CM`, `Attacker→ST`) OR preserve the slot's existing tactical role (`editingPlayer.role`), and include `LWB`, `RWB`, `LM`, `RM` in `<select id="player-role">` (`lines 634-643`).
- **Skill Responsible:** `a11y-audit`, `svelte-runes`
- **Scope:** `frontEnd/src/lib/components/TacticalBoard.svelte`
- **Risk:** Low — preserves `0..100` coordinates and backend `role` `max_length=20`.
- **Acceptance Criteria:**
  1. Keyboard user can Tab to a bench button (`aria-pressed="true"` on `Enter`), Tab to a starting token, press `Enter` to swap, and use Arrow keys to move any token across the pitch (`2..98`).
  2. Choosing an Arsenal player from `#roster-select` displays a valid selected option in `#player-role`.

---

### [INT-P1-05] Edit Player Modal Missing Dialog Semantics, Focus Trap, Escape & Backdrop Close
- **Severity:** `P1`
- **Citations:**
  - `frontEnd/src/lib/components/TacticalBoard.svelte:570-657`
- **Evidence:**
  - Modal wrapper at line 571 uses `z-50` (same z-index as sticky header in `+layout.svelte:107`) and is a plain `<div>` lacking `role="dialog"`, `aria-modal="true"`, `aria-labelledby`, `Escape` key closing, backdrop click closing, initial focus management, Tab focus trapping, and focus restoration upon close.
  - Also `handleSavePlayerModal` (`line 183-199`) allows saving an empty `editingPlayer.name` or invalid `number < 1 || number > 99` (backend `PlayerToken` requires `1..99`).
- **User Impact:** Screen-reader and keyboard users get lost behind the modal backdrop, cannot dismiss with `Escape`, and on scroll the header (`z-50`) overlaps the modal.
- **Proposed Solution:**
  - Set overlay z-index to `z-[400]` (matching `--z-modal: 400` in `tokens.css:77`), add `role="dialog" aria-modal="true" aria-labelledby="edit-player-title"`, `Escape` & backdrop close, initial focus on `#roster-select` / `#player-name`, Tab loop within modal focusables, and focus return to the triggering token/button. Validate `name.trim()` and `1 <= number <= 99` before saving.
- **Skill Responsible:** `a11y-audit`, `hallmark`
- **Scope:** `frontEnd/src/lib/components/TacticalBoard.svelte`
- **Risk:** Low.
- **Acceptance Criteria:**
  1. Opening the Edit Player modal traps Tab inside the dialog, closes on `Escape` or backdrop click, restores focus to the opener, and sits cleanly above the `z-50` header.

---

### [INT-P2-01] Missing Undo / Per-Vector Delete & Keyboard Vector Creation on `/board`
- **Severity:** `P2`
- **Citations:**
  - `frontEnd/src/lib/components/TacticalBoard.svelte:178-181, 323-397, 456-468`
- **Evidence:**
  - `TacticalBoard` offers only `"Clear arrows"` (`line 388-394`), which deletes every tactical annotation at once without confirmation or undo. Users cannot undo the last drawn arrow, delete a single misdrawn arrow, or undo an accidental token move/preset switch.
  - Vector tools (`Run vector`, `Pass channel`, `High press`) lack `aria-pressed` (`lines 327-363`) and have no click/keyboard way to remove an individual arrow.
- **User Impact:** Drawing 5 tactical vectors and misplacing the 6th forces the user to wipe all 6 vectors and redraw from scratch.
- **Proposed Solution:**
  - Add `aria-pressed={activeTool === ...}` and `aria-pressed={fluidMode}` on toolbar buttons (`lines 327-363`).
  - Add an `"Undo arrow"` (`annotations = annotations.slice(0, -1)`) button alongside `"Clear arrows"` (`#if annotations.length > 0`), and make individual vector lines clickable/focusable (or list removable vector chips below toolbar when `annotations.length > 0`) for keyboard deletion.
- **Skill Responsible:** `improve-ui`, `a11y-audit`
- **Scope:** `frontEnd/src/lib/components/TacticalBoard.svelte`
- **Risk:** Low.
- **Acceptance Criteria:**
  1. Users can undo the most recent tactical arrow or remove an individual arrow without clearing the whole board.
  2. All tool toggle buttons expose `aria-pressed`.

---

### [INT-P2-02] Mobile Pitch Label Legibility, 8-Column Bench Truncation & Toolbar Density on `/board`
- **Severity:** `P2`
- **Citations:**
  - `frontEnd/src/lib/components/TacticalBoard.svelte:323-397, 523-532, 550-564`
  - `frontEnd/src/routes/board/+page.svelte:165-245`
- **Evidence:**
  - Inside `viewBox="0 0 1000 680"`, player name pills use `font-size="10"` (`line 529`) and `width="96"` (`line 528`). On a `390px` mobile screen (`~358px` SVG width -> `0.358x` scale), `font-size="10"` shrinks to **3.6px physical pixels**—effectively unreadable—and longer names (`Lewis-Skelly (LB)`) overflow the `96`-unit pill box.
  - At `768px` (`md`), `grid-cols-2 sm:grid-cols-4 md:grid-cols-8` (`line 550`) squeezes 8 bench buttons into one narrow row where `max-w-[85px]` truncates almost every name (`#12 Jurrië…`).
  - Two separate toolbars (`board/+page.svelte:169-187` and `TacticalBoard.svelte:323-397`) stack ~10 buttons/controls above the pitch on mobile before the pitch is seen.
- **User Impact:** Narrow-screen users struggle to read player names on the pitch and bench, and must scroll past dense stacked toolbars.
- **Proposed Solution:**
  - Increase SVG token pill width dynamically or use `width="112"` + `font-size="12"` (`16` for number) for better scaling, and render `short_name` / last name inside the pill when available.
  - Adjust bench grid to `grid-cols-2 sm:grid-cols-4 lg:grid-cols-8` (`line 550`) and remove `max-w-[85px]` so 4-column tablet buttons show full `#12 Timber` / `#49 Lewis-Skelly` labels.
  - Add a compact, dismissible or concise inline first-time gesture hint (`"Tap token to edit · Drag to reposition · Pick a vector tool to draw"`) in `TacticalBoard` replacing the duplicate hint in `board/+page.svelte:184-186`.
- **Skill Responsible:** `improve-ui`, `hallmark`
- **Scope:** `frontEnd/src/lib/components/TacticalBoard.svelte`, `frontEnd/src/routes/board/+page.svelte`
- **Risk:** Low.
- **Acceptance Criteria:**
  1. At `768px` and `390px`, bench player tags display without premature `85px` clipping.
  2. On `390px`, SVG token numbers and short names remain legible and centered within their pill background.

---

### [INT-P2-03] Truthful Save/Publish Validation, Unsaved `"Share to Terrace"` Loss & Stale `savedBoardId`
- **Severity:** `P2`
- **Citations:**
  - `frontEnd/src/routes/board/+page.svelte:34-53, 55-100, 119-141, 153-160, 197-199, 208-228`
  - Backend schema: [`backEnd/app/schemas/tactics.py:29, 33`](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/backEnd/app/schemas/tactics.py#L29-L33) (`title` `min_length=2, max_length=150`; `tactical_notes` `max_length=3000`)
- **Evidence:**
  1. Line 156 only disables Publish when `!title.trim()`, allowing 1-character titles (`"A"`) or >150-char titles to submit and fail with a raw Pydantic 422 string. No `maxlength` or character count exists on `#blueprint-title` or `#tactical-notes`.
  2. Line 197–199 (`onshare={() => { window.location.href = '/terrace'; }}`) performs a hard page reload to `/terrace`, silently discarding unsaved pitch edits and not pre-attaching any published `savedBoardId`.
  3. Line 34–42 (`handleFormationSelect`) never resets `savedBoardId = null`, so after loading a community board (`savedBoardId = board.id`) and switching to a fresh preset, the success toast link (`line 132`) still references the old `savedBoardId`.
  4. Toast (`lines 119-141`) uses `z-50` without `left-6` / `max-w` mobile constraint and has no dismiss button.
- **User Impact:** Users lose unsaved tactics clicking `"Share to Terrace"`, hit avoidable 422 errors on short/long titles, and get cramped toasts on mobile.
- **Proposed Solution:**
  - Enforce `minlength={2} maxlength={150}` on `#blueprint-title`, `maxlength={3000}` on `#tactical-notes`, disable Publish when `title.trim().length < 2`, and show inline validation helper text.
  - Reset `savedBoardId = null` in `handleFormationSelect` (and when `onchange` fires on `TacticalBoard`).
  - Use SvelteKit `goto('/terrace')` (passing `?tactic=${savedBoardId}` when published, or prompting/auto-saving when unsaved edits exist).
  - Update toast positioning to `fixed bottom-6 right-6 left-6 sm:left-auto max-w-md z-[500]` (`--z-toast`) with a Close button.
- **Skill Responsible:** `improve-ui`, `hallmark`
- **Scope:** `frontEnd/src/routes/board/+page.svelte`
- **Risk:** Low.
- **Acceptance Criteria:**
  1. Publish button enforces `2..150` char title client-side; `"Share to Terrace"` uses SPA navigation without discarding published board context.
  2. Toast renders cleanly on `390px` mobile above sticky header (`z-[500]`) with a Close action.

---

## 3. Surface 2: The Data Lab & Historical Pitch Explorer (`/lab`, `/lab/historical`, `HistoricalPitchExplorer.svelte`)

### [INT-P0-04] Stale `metric`/`venue` Saved Into Mismatched `Insight` Snapshot & Non-Reactive Query Selects
- **Severity:** `P0`
- **Citations:**
  - `frontEnd/src/routes/lab/+page.svelte:245-306` (`openCreateModal`, `submitInsight`)
  - `frontEnd/src/routes/lab/+page.svelte:628-701` (`Query` tab `<select>` controls)
  - `frontEnd/src/routes/lab/+page.svelte:902-910` (`Save as insight` button outside tab guard)
- **Evidence:**
  1. In `Query` (`lines 628-684`), changing `#primary-club`, `#secondary-club`, `#metric-select`, or `#venue-filter` updates reactive `metric`/`venue`/`team1`/`team2` **without** calling `runQuery()` (unlike `#season-filter` at line 693, and unlike all selects in `Trends`, `H2H`, and `Squad` tabs which auto-run on `onchange`).
  2. Meanwhile, `openCreateModal()` (`lines 252-260`) and `submitInsight()` (`lines 273-285`) read the **current** `metric`, `venue`, `team1`, `team2` variables while attaching the **old** `result` object as `snapshot`! Thus changing Metric from `Win rate` to `Goals per match` without clicking `"Calculate analytics"` publishes an insight titled `"Arsenal FC Goals per match: 68.4 %"` whose stored `metric` is `goals_per_match` while `snapshot.metric` is `win_rate`!
  3. Lines 902–910 show `"Save as insight"` whenever `result && result.series.length > 0`, **even when `activeTab` is `trends`, `h2h`, `squad`, or `pitch`**, misleading users into thinking they are saving a Multi-Season Trend or Squad H2H snapshot.
  4. Also when `team1` is changed to match `team2` in comparison mode, `team2` remains equal to `team1` even though `<option disabled={club.id === team1}>` disables it.
- **User Impact:** Users can accidentally publish factually corrupted insights to the community database, or try to save Trends/H2H charts and unknowingly save an old Query result.
- **Proposed Solution:**
  - Auto-run `runQuery()` on `onchange` for `#primary-club`, `#secondary-club`, `#metric-select`, and `#venue-filter` (and auto-swap `team2` to the first different club if `team1 === team2`), OR track `lastQueriedParams` on `result` and show a `"Parameters changed — recalculate"` state while blocking `"Save as insight"` until `result` matches active controls. (Auto-running `runQuery()` on `onchange` also aligns Query with Trends, H2H, and Squad!)
  - Scope `"Save as insight"` strictly to `{#if activeTab === 'query' && result && result.series.length > 0}`.
- **Skill Responsible:** `svelte-runes`, `improve-ui`
- **Scope:** `frontEnd/src/routes/lab/+page.svelte`
- **Risk:** Low — matches existing `onchange` pattern in `Trends`/`H2H`/`Squad`.
- **Acceptance Criteria:**
  1. Published `Insight` records always have `metric`, `venue`, `team_ids`, `title`, and `snapshot` in 100% agreement.
  2. `"Save as insight"` appears only on the `Analytics query` lens when a matching result is loaded.

---

### [INT-P0-05] Save Insight Modal Missing Dialog Semantics, Focus Trap, Escape & Validation Guard
- **Severity:** `P0`
- **Citations:**
  - `frontEnd/src/routes/lab/+page.svelte:1571-1642` (Create Insight Modal)
  - `frontEnd/src/routes/lab/+page.svelte:264` (`if (!result || !insightTitle) return;`)
  - Backend schema: [`backEnd/app/schemas/insight.py:7-8`](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/backEnd/app/schemas/insight.py#L7-L8) (`title` `min_length=3, max_length=200`, `description` `max_length=500`)
- **Evidence:**
  - Lines 1572–1573 render the modal at `z-50` (same layer as `+layout.svelte` sticky `<header class="... z-50">`) without `role="dialog"`, `aria-modal="true"`, `aria-labelledby`, `Escape` handler, backdrop click dismissal, initial focus, Tab focus trap, or focus return.
  - Line 1634 disables submit only on `!insightTitle` (allowing `"  "` or 1–2 chars, which fail backend `422` validation), and inputs lack `minlength={3} maxlength={200}` / `maxlength={500}`.
  - Note also: when `selectedSeason !== 'all'`, `openCreateModal` (`line 259`) omits the selected season from `insightDesc` and `submitInsight` cannot filter `POST /insights` by `season_id` (since `InsightCreateRequest` lacks `season_id`), yet line 1610 claims `"stores the exact query parameters"`.
- **User Impact:** Keyboard and screen-reader users are trapped outside/behind the modal, cannot press `Escape` to close, and hit unvalidated 422 errors on short titles.
- **Proposed Solution:**
  - Elevate modal overlay to `z-[400]` (`--z-modal`), add `role="dialog" aria-modal="true" aria-labelledby="ins-modal-title"`, handle `Escape` + backdrop click, focus `#ins-title` on open, trap `Tab`/`Shift+Tab` inside the modal, and restore focus to the `"Save as insight"` button on close.
  - Validate `insightTitle.trim().length >= 3 && insightTitle.trim().length <= 200` with `maxlength={200}` / `maxlength={500}`, and include `selectedSeason !== 'all'` in the default `insightDesc` + modal summary preview (`Season: ...`).
- **Skill Responsible:** `a11y-audit`, `hallmark`
- **Scope:** `frontEnd/src/routes/lab/+page.svelte`
- **Risk:** Low.
- **Acceptance Criteria:**
  1. Modal opens with focus on `#ins-title`, traps Tab, closes on `Escape`/backdrop click, restores focus on close, and sits at `z-[400]`.
  2. Title validation enforces `3..200` trimmed characters before submit.

---

### [INT-P1-06] Silent Error Swallowing Across Data Lab API Calls Masquerading as Empty Data
- **Severity:** `P1`
- **Citations:**
  - `frontEnd/src/lib/api/football.ts:297-356` (`queryAnalytics`, `fetchMultiSeasonTrends`, `fetchOpponentH2H` return `null` on non-200 or network error)
  - `frontEnd/src/lib/api/football.ts:589-597` (`comparePlayers` returns `null` on error)
  - `frontEnd/src/lib/api/football.ts:730-748` (`fetchHistoricalMatches`, `fetchHistoricalMatchDetail` return `[]`/`null` on error)
  - `frontEnd/src/routes/lab/+page.svelte:1124, 1339, 1454, 1554`
  - `frontEnd/src/lib/components/HistoricalPitchExplorer.svelte:42-53, 392`
- **Evidence:**
  - When Render is cold-starting (`~50s` wakeup) or an API request fails (`500`, `422`, network timeout), every Data Lab helper in `football.ts` catches the error and returns `null` or `[]`.
  - In `lab/+page.svelte`, `result === null` displays `"No completed matches found matching the specified parameters."` (`line 1124`), `trendsData === null` displays `"No multi-season trend records available for this selection."` (`line 1339`), and `playerComparison === null` displays `"Select two distinct Arsenal players from the workbench controls to compare their output."` (`line 1554`) — even though two distinct players ARE selected!
- **User Impact:** Users experiencing a Render cold-start or transient API failure are falsely told no matches or data exist, with no Retry button.
- **Proposed Solution:**
  - Introduce explicit error tracking state per lens (`queryError`, `trendsError`, `h2hError`, `squadError`, `historicalError`) or `ApiError`-throwing variants (or structured `{ data, error }` loaders) so `/lab` and `HistoricalPitchExplorer` render a crisp `role="alert"` error banner with a **"Retry"** button when an API call fails, reserving `"No completed matches found"` strictly for valid `200 OK` responses with `0` rows.
- **Skill Responsible:** `improve-ui`, `svelte-runes`
- **Scope:** `frontEnd/src/lib/api/football.ts`, `frontEnd/src/routes/lab/+page.svelte`, `frontEnd/src/routes/lab/+page.ts`, `frontEnd/src/lib/components/HistoricalPitchExplorer.svelte`
- **Risk:** Medium — preserve existing `null`/`[]` fallback signatures if used by SSR `+page.ts` on other routes (e.g. `/squad` uses `comparePlayers`), or export throwing `*Strict` helpers for interactive client queries.
- **Acceptance Criteria:**
  1. Simulating a 500/network failure in any of the 5 Data Lab lenses renders a clear error notice with a working **Retry** button rather than an empty-data message.

---

### [INT-P1-07] Incomplete `?tab=` / Lens URL Sync, Optimistic Clipboard Toast & Missing `role="tabpanel"` / Arrow Navigation
- **Severity:** `P1`
- **Citations:**
  - `frontEnd/src/routes/lab/+page.svelte:153-243` (`syncUrlParams`, `switchTab`, `runTrendsQuery`, `runH2HQuery`, `copyShareLink`)
  - `frontEnd/src/routes/lab/+page.svelte:582-599, 951` (`role="tablist"`, `role="tab"`, missing `role="tabpanel"`)
  - `frontEnd/src/routes/lab/+page.ts:37-103`
  - `frontEnd/src/lib/components/HistoricalPitchExplorer.svelte:42-53` (`switchMatch` omits URL `?match=` sync)
- **Evidence:**
  1. `runTrendsQuery()` (`line 210`) syncs `{ tab: 'trends', venue: trendsVenue }` but omits `trendsClub` and `trendMetric` (`?tmetric=`). `lab/+page.ts:68` hardcodes `'arsenal'` instead of reading `club` from URL. Same for `runH2HQuery()` (`line 221`) and `lab/+page.ts:69` (`h2hClub`).
  2. `HistoricalPitchExplorer.switchMatch()` (`lines 42-53`) never updates `?match=` in the browser URL (`replaceState`), breaking shareable links on both `/lab?tab=pitch` and `/lab/historical`.
  3. `copyShareLink()` (`lines 238-243`) calls `navigator.clipboard.writeText(...)` without `await` or `.catch()`, showing `"Reproducible analysis link copied to clipboard."` even if clipboard write throws (`NotAllowedError` / insecure context).
  4. `role="tablist"` (`line 582`) lacks `aria-controls` / `id` linkage to a `role="tabpanel"` (`line 951` is `<main>` without `role="tabpanel"` or `aria-labelledby`), and lacks `ArrowUp`/`ArrowDown`/`Home`/`End` keyboard switching per WAI-ARIA APG Tabs.
- **User Impact:** Sharing a Data Lab URL for Trends, H2H, or a Classic Match loses the selected club, metric, or match; clipboard failures lie to the user; screen readers miss tab-to-panel association.
- **Proposed Solution:**
  - Sync `club`, `tmetric` (`Trends`), `opponent` (`H2H`), `p1`/`p2` (`Squad`), and `match` (`HistoricalPitchExplorer.switchMatch`) into URL search params, and read them in `lab/+page.ts`.
  - Make `copyShareLink()` `async`, `await navigator.clipboard.writeText(...)`, and catch failures to show an error toast (`"Clipboard unavailable — copy URL from address bar."`).
  - Wire `id="tab-{tab.id}"`, `aria-controls="lab-tabpanel"`, `tabindex={isActive ? 0 : -1}`, arrow-key navigation on tabs, and `id="lab-tabpanel" role="tabpanel" aria-labelledby="tab-{activeTab}"` on the stage container.
- **Skill Responsible:** `a11y-audit`, `improve-ui`, `svelte-runes`
- **Scope:** `frontEnd/src/routes/lab/+page.svelte`, `frontEnd/src/routes/lab/+page.ts`, `frontEnd/src/lib/components/HistoricalPitchExplorer.svelte`
- **Risk:** Low.
- **Acceptance Criteria:**
  1. Switching tabs, trends club/metric, or historical match updates the URL; reloading restores the exact view.
  2. Denied clipboard write displays an error toast instead of a false success toast.
  3. Tabs implement WAI-ARIA `tablist`/`tab`/`tabpanel` with arrow-key movement.

---

### [INT-P1-08] Mobile SVG Chart Legibility, Tiny/Overlapping Shot Markers & Missing Trends Gap Handling
- **Severity:** `P1`
- **Citations:**
  - `frontEnd/src/routes/lab/+page.svelte:414-423, 1159-1273` (`Trends` SVG `720x300`)
  - `frontEnd/src/lib/components/HistoricalPitchExplorer.svelte:201-208, 212-310` (`700x480` SVG shot map & pass network)
  - Backend telemetry: [`backEnd/app/api/v1/endpoints/historical.py:166-167, 194-195`](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/backEnd/app/api/v1/endpoints/historical.py#L166-L195) (two penalties at exact same `(88.5, 50.0)` with `xg=0.76`)
- **Evidence:**
  1. In `lab/+page.svelte:1160`, `viewBox="0 0 720 300"` scales down to `~318px` wide on `390px` mobile (`0.44x`), shrinking `font-size="11"` axis labels to **4.8px** physical text and `r="14"` hit areas to **12.3px** diameter (failing WCAG 2.2 AA 24×24px target size).
  2. In `lab/+page.svelte:414-418`, `activePts = points.filter(p => p.hasData)` connects non-consecutive seasons with a straight line across missing `matches_played === 0` intermediate seasons.
  3. In `HistoricalPitchExplorer.svelte:213, 234, 291, 302`, `viewBox="0 0 700 480"` scales to `~358px` (`0.51x`) on mobile: pass network names (`font-size="9"`) shrink to **4.6px**, and small shots (`r = Math.max(7, shot.xg * 24)`) render at **7.1px** diameter! Worse, in `hist_ars_spurs_2018`, Aubameyang (10m) and Kane (34m) penalties BOTH have `(x=88.5, y=50.0, xg=0.76)` — Kane's circle draws directly on top of Aubameyang's with identical radius, making Aubameyang's penalty **100% unreachable by pointer/touch**!
  4. `HistoricalPitchExplorer.svelte:202-207` legend relies on color-only labels (`Goal`, `Saved`, `Blocked`, `Miss`) without shape/ring swatches.
- **User Impact:** Mobile users cannot read chart labels or tap small shots, overlapping penalty shots hide earlier goals from pointer interaction, and color-blind users lack shape cues in the shot legend.
- **Proposed Solution:**
  - Wrap wide SVG charts in an `overflow-x-auto` container with a `min-w-[540px]` inner wrapper on narrow mobile (preserving responsive `w-full` on desktop), AND render a touch-friendly **44px-tall horizontal season selector pill strip** below the Trends chart + an accessible shot list/prev-next stepper on mobile in `HistoricalPitchExplorer`.
  - Break the Trends SVG `linePath` whenever an intermediate season has `matches_played === 0` (render dashed gap segment or separate `M` subpaths).
  - In `HistoricalPitchExplorer`, enforce a transparent minimum `r="18"` touch-target hit circle behind each visible shot circle (`r = Math.max(7, shot.xg * 24)`), apply a deterministic micro-jitter (`±1.2` SVG units) when two shots share `(x, y)` within `0.5` units so both are visible/clickable, and add matching colored circle/ring swatches next to `Goal / Saved / Blocked / Miss` in the legend.
- **Skill Responsible:** `a11y-audit`, `improve-ui`, `hallmark`
- **Scope:** `frontEnd/src/routes/lab/+page.svelte`, `frontEnd/src/lib/components/HistoricalPitchExplorer.svelte`
- **Risk:** Low — micro-offset is visual SVG only (`<= 0.2%` of pitch), preserving `0..100` coordinate data and inspector values.
- **Acceptance Criteria:**
  1. On `390px`, chart axis text and pass network player labels remain readable (`>= 10px` effective via horizontal scroll or scaled typography), and every shot/season point has an accessible `>= 24px` (44px mobile pill) target.
  2. In `Arsenal 4-2 Tottenham`, both penalty shots at `(88.5, 50.0)` are independently clickable by mouse/touch.

---

### [INT-P1-09] Sample-Size, Zero-Match & Arsenal-Foundation Scope Messaging Gaps in `/lab`
- **Severity:** `P1`
- **Citations:**
  - `frontEnd/src/routes/lab/+page.svelte:963-989` (Single club hero renders `0 %` when `matches_played === 0`)
  - `frontEnd/src/routes/lab/+page.svelte:1031-1076` (Comparison mode `Result:` banner omits unequal sample warning)
  - `frontEnd/src/routes/lab/+page.svelte:1146-1155` (Trends selected season box omits `n` matches)
  - `frontEnd/src/routes/lab/+page.svelte:127, 633, 724` (`clubList` includes `tottenham`, `manchester-city`, `liverpool`, `real-madrid`, etc.)
- **Evidence:**
  1. When `s.matches_played === 0` (e.g. selecting `Real Madrid` + `2021/22` or `AC Milan` + `away`), `line 966` displays `0 %` or `0 diff` in giant `text-4xl` (`line 966`) as though it were an empirical score rather than `"No sample (0 matches)"`.
  2. In Comparison mode (`lines 1031-1076`), `Arsenal (45 matches)` vs `Real Madrid (2 matches)` renders `"Real Madrid leads by X"` with no low-sample (`n < 5`) or unequal-sample caveat.
  3. Because the DB enforces an **Arsenal-only match foundation** (`05_UI_ARCHITECTURE_AND_DESIGN_SYSTEM.md:39`), selecting `Chelsea`, `Liverpool`, or `Real Madrid` in `Query` or `Trends` computes metrics *only across stored fixtures involving Arsenal*—yet the UI displays `"Chelsea FC win rate: ..."` and labels the Trends table column `"Arteta milestone"` (`line 1305`) even when `trendsClub !== 'arsenal'`!
- **User Impact:** Users can misinterpret opponent metrics as full-league club stats or mistake `0` matches for a `0%` win rate.
- **Proposed Solution:**
  - When `s.matches_played === 0`, display `"Insufficient sample"` (`—`) instead of `0 %` in the hero KPI.
  - Display a clear sample-confidence badge when `matches_played > 0 && matches_played < 5` (`"Small sample (n < 5)"`) or when comparison `Math.abs(t1.matches_played - t2.matches_played) >= 10` (`"Unequal sample sizes"`).
  - Add `n = {activeTrendItem.matches_played} matches` inside the Trends callout box (`line 1147`), label non-Arsenal clubs clearly as `"Stored Arsenal-fixture sample"` in Query/Trends, and conditionally show `"Campaign milestone"` or Arsenal-only note when `trendsClub !== 'arsenal'`.
- **Skill Responsible:** `improve-ui`, `hallmark`
- **Scope:** `frontEnd/src/routes/lab/+page.svelte`
- **Risk:** Low.
- **Acceptance Criteria:**
  1. Zero-match queries display `—` / `"No completed matches in sample"` instead of `0 %`.
  2. Small samples (`< 5` matches) and unequal H2H samples display explicit confidence notes.

---

### [INT-P1-10] StatsBomb ODbL Attribution Missing Required Links & Open-Data Source Citation
- **Severity:** `P1`
- **Citations:**
  - `frontEnd/src/lib/components/HistoricalPitchExplorer.svelte:312-314, 383-388`
  - `backEnd/app/api/v1/endpoints/historical.py:27-28, 152-153`
- **Evidence:**
  - Line 313 renders `activeDetail.license_notice` as unlinked muted text (`"Event data and pitch telemetry provided by StatsBomb open-data initiative under ODbL terms."`), with no link to the **StatsBomb Open Data** repository (`https://github.com/statsbomb/open-data`) or the **Open Database License (ODbL v1.0)** (`https://opendatacommons.org/licenses/odbl/1.0/`), which ODbL attribution terms require when distributing derived visualizations publicly.
  - Also in Passing Network mode (`line 197, 368-370`), the pitch does not explicitly badge the team (`{activeDetail.home_team_name} passing network`) or explain node/line encoding (circle = avg position, stroke width = pass count).
- **User Impact:** Public deployment lacks clickable ODbL 1.0 / StatsBomb source links required by open-data attribution hygiene, and pass network readers lack a visual key.
- **Proposed Solution:**
  - Render `activeDetail.license_notice` with an explicit `"Data source: StatsBomb Open Data"` link (`https://github.com/statsbomb/open-data`, `target="_blank" rel="noopener noreferrer"`) and `"ODbL v1.0"` license link (`https://opendatacommons.org/licenses/odbl/1.0/`).
  - Add a compact key in `pass_network` mode naming `{activeDetail.home_team_name}` and explaining line thickness = pass volume.
- **Skill Responsible:** `improve-ui`, `hallmark`
- **Scope:** `frontEnd/src/lib/components/HistoricalPitchExplorer.svelte`
- **Risk:** Low.
- **Acceptance Criteria:**
  1. Both `/lab?tab=pitch` and `/lab/historical` render clickable StatsBomb Open Data and ODbL v1.0 attribution links.

---

### [INT-P1-11] Missing Owner-Delete UI for `DELETE /api/v1/insights/{id}` & 6-Item Truncation in Saved Insights
- **Severity:** `P1`
- **Citations:**
  - `frontEnd/src/routes/lab/+page.svelte:913-947` (`insights.slice(0, 6)`, Load button only)
  - `frontEnd/src/lib/api/football.ts:358-385` (has `createInsight` & `fetchInsights`, no `deleteInsight`)
  - Backend contract: [`backEnd/app/api/v1/endpoints/insights.py:308-324`](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/backEnd/app/api/v1/endpoints/insights.py#L308-L324) & [`03_API_CONTRACTS.md:53`](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/.project-context/03_API_CONTRACTS.md#L53)
- **Evidence:**
  - Backend implements `DELETE /api/v1/insights/{insight_id}` (`200`, checking `insight.user_id == current_user.id`).
  - Frontend `football.ts` omits `deleteInsight`, and `lab/+page.svelte:926` hard-slices `insights.slice(0, 6)` with no `"Show all"` expansion and no Delete control for owned insights.
- **User Impact:** Supporters cannot delete their own published insights or view insights beyond the 6 most recent ones in `/lab`.
- **Proposed Solution:**
  - Add `deleteInsight(insightId: string, accessToken?: string | null)` to `football.ts`.
  - Add a 2-step **Delete → Confirm / Cancel** control on insights where `data.user?.id && ins.user_id === data.user.id`, and a `"Show all (${insights.length})"` toggle when `insights.length > 6`.
- **Skill Responsible:** `improve-ui`, `a11y-audit`
- **Scope:** `frontEnd/src/lib/api/football.ts`, `frontEnd/src/routes/lab/+page.svelte`
- **Risk:** Low.
- **Acceptance Criteria:**
  1. Authenticated insight authors can delete their own insights with confirmation and error/success toast; `insights > 6` can be expanded.

---

### [INT-P2-04] Shot Inspector Lacks `aria-live="polite"`, Mobile Feedback & Keyboard Pass-Network Inspection
- **Severity:** `P2`
- **Citations:**
  - `frontEnd/src/lib/components/HistoricalPitchExplorer.svelte:281-308, 318-381`
- **Evidence:**
  - Selecting a shot circle updates `selectedShot` in the sidebar (`lines 326-364`), but the inspector container lacks `aria-live="polite"` — screen-reader users hear no announcement of the selected shot's shooter/xG, and mobile users tapping a shot on the SVG see nothing change above the fold because the inspector sits below the SVG (`lg:col-span-4`).
  - In `pass_network` mode (`lines 281-308, 372-379`), nodes and pass-combination rows are non-interactive; hovering/selecting a player or passing channel does not highlight connected links.
- **User Impact:** Screen-reader and mobile users miss shot selection feedback, and pass network exploration is passive.
- **Proposed Solution:**
  - Add `aria-live="polite"` to the Shot Event Inspector container (`line 320`), plus a compact 1-line selected-shot summary banner right below the SVG on `< lg` screens (`lg:hidden`) with a `"View details"` jump or inline values.
  - Allow clicking/focusing a player node or passing combination row to highlight that player's links (`opacity: 1` vs `0.2` for unrelated links).
- **Skill Responsible:** `a11y-audit`, `improve-ui`
- **Scope:** `frontEnd/src/lib/components/HistoricalPitchExplorer.svelte`
- **Risk:** Low.
- **Acceptance Criteria:**
  1. Selecting a shot announces the updated details via `aria-live="polite"` and shows an immediate inline summary below the pitch on mobile.

---

### [INT-P2-05] Non-Semantic Clickable `<tr>` in Multi-Season Trends Table
- **Severity:** `P2`
- **Citations:**
  - `frontEnd/src/routes/lab/+page.svelte:1311-1314`
- **Evidence:**
  - `<tr onclick={() => (selectedTrendSeasonId = item.season_id)} class="cursor-pointer ...">` attaches a click handler to a `<tr>` with no `tabindex`, `role`, or `onkeydown`. Keyboard users cannot select a season from the table (contradicting `a11y-audit` Phase 1.1).
- **User Impact:** Keyboard users browsing the season table cannot inspect rows via keyboard activation.
- **Proposed Solution:**
  - Place a native `<button type="button" onclick={() => (selectedTrendSeasonId = item.season_id)} aria-pressed={isRowActive} class="text-left font-semibold ...">` inside the Season `<td>`, keeping `<tr>` non-interactive.
- **Skill Responsible:** `a11y-audit`
- **Scope:** `frontEnd/src/routes/lab/+page.svelte`
- **Risk:** Low.
- **Acceptance Criteria:**
  1. Every season row in the Trends table is selectable via Tab + Enter/Space using a native `<button>` with `aria-pressed`.

---

### [INT-P2-06] Toast Z-Index (`z-50`) Collides With Sticky Header (`z-50`) & Clips on Mobile
- **Severity:** `P2`
- **Citations:**
  - `frontEnd/src/routes/lab/+page.svelte:543-553` (`z-50`)
  - `frontEnd/src/routes/board/+page.svelte:119-141` (`z-50`)
  - `frontEnd/src/routes/+layout.svelte:107` (`sticky top-0 z-50`)
  - Token spec: [`frontEnd/src/tokens.css:76-78`](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/frontEnd/src/tokens.css#L76-L78) (`--z-sticky-nav: 300; --z-modal: 400; --z-toast: 500;`)
- **Evidence:**
  - Modals and fixed toasts across `/board`, `/lab`, and `TacticalBoard.svelte` use Tailwind `z-50` instead of the `--z-modal: 400` / `--z-toast: 500` tokens defined in `tokens.css`. Because `<header>` also uses `z-50`, modals and toasts share the same z-index plane as the sticky header.
- **User Impact:** Modals/toasts can render underneath or collide with the sticky navigation bar, and toasts lack left margin / close button on `390px` screens.
- **Proposed Solution:**
  - Use `z-[400]` for modal overlays and `z-[500]` for fixed toasts (with `left-6 sm:left-auto max-w-md` and a Close button).
- **Skill Responsible:** `hallmark`
- **Scope:** `frontEnd/src/routes/lab/+page.svelte`, `frontEnd/src/routes/board/+page.svelte`, `frontEnd/src/lib/components/TacticalBoard.svelte`
- **Risk:** Low.
- **Acceptance Criteria:**
  1. Modals (`z-[400]`) and toasts (`z-[500]`) consistently stack above the sticky navigation header.

---

## 4. Surface 3: Matchday Predictor & Leaderboard (`/predictions`)

### [INT-P0-01] Severe Mobile Overflow in `grid-cols-7` Scoreline Input Box & Missing Touch Steppers
- **Severity:** `P0`
- **Citations:**
  - `frontEnd/src/routes/predictions/+page.svelte:334-366`
- **Evidence:**
  - Line 334 uses `grid grid-cols-7 gap-3 items-center`. On a `390px` mobile screen (`358px` inner container width minus `6 × 12px = 72px` gaps = `286px` track budget), `col-span-1` (`line 340`) is **only `40.8px` wide**!
  - Inside that `40.8px` column, lines 340–360 render two `w-10` (`40px`) `<input type="number">` fields + `:` + `gap-2` (`16px`) = **`~102px` minimum width** — overflowing `col-span-1` by **~61px** and colliding directly into `col-span-3` home/away team titles!
  - Additionally:
    - `40x40px` inputs are below `44x44px` mobile touch targets, lack `inputmode="numeric"` and `-`/`+` stepper controls, and clearing an input can leave `NaN`/`null` bound to `predictionInputs[match.id]`.
    - `aria-label="Home team predicted goals"` (`line 346`) and `"Away team predicted goals"` (`line 356`) omit the actual team names, making screen-reader navigation across 10 fixtures ambiguous.
- **User Impact:** On every mobile phone (`<= 480px`), the scoreline inputs overlap team names and are awkward to increment without native spinner arrows.
- **Proposed Solution:**
  - Replace `grid-cols-7` with a responsive layout: on `< sm` (`390px`), stack `[Home Team vs Away Team]` header above a centered `flex items-center justify-center gap-4` scoreline stepper bar (`- [input] + : - [input] +` with `44x44px` `min-h-11 min-w-11` buttons, clamped `0..20`), and on `sm:`+ use `grid-cols-[1fr_auto_1fr] gap-4 items-center` (`auto` ensures the center score box NEVER crushes or overflows!).
  - Add `inputmode="numeric"`, clamp `oninput`/`onchange` values to integers `0..20`, and set `aria-label={`${match.home_team_name} predicted goals`}` / `aria-label={`${match.away_team_name} predicted goals`}`.
- **Skill Responsible:** `improve-ui`, `a11y-audit`, `hallmark`
- **Scope:** `frontEnd/src/routes/predictions/+page.svelte`
- **Risk:** Low — strictly improves mobile ergonomics while preserving `0..20` integer API contract.
- **Acceptance Criteria:**
  1. At `390px` and `1280px`, zero horizontal overlap occurs between team names and score inputs.
  2. Users can adjust scores via `44px` `-`/`+` stepper buttons or direct numeric entry (`0..20` clamped), and screen readers announce team-specific labels.

---

### [INT-P1-12] Silent Leaderboard & History Refresh Failure Wiping Standings + Guest/Auth Error Placement
- **Severity:** `P1`
- **Citations:**
  - `frontEnd/src/routes/predictions/+page.svelte:111-173, 175-182`
  - `frontEnd/src/lib/api/football.ts:641-654` (`fetchLeaderboard` returns `[]` on error)
  - `frontEnd/src/lib/api/community.ts:124-138` (`fetchPredictionHistory` returns `[]` on error)
  - `frontEnd/src/routes/predictions/+page.svelte:64-81` (`$effect` wipes unsaved `predictionInputs` if `data` re-runs)
- **Evidence:**
  1. In `handlePredict` (`lines 153-158`), after saving a prediction, it calls `fetchLeaderboard` and `fetchPredictionHistory`. Both helpers swallow HTTP/network errors and return `[]`, so any transient error **erases the currently visible leaderboard and prediction history** (`"No supporter predictions scored yet."`)!
  2. `refreshLeaderboard` (`lines 175-182`) has the exact same problem: switching to `"Seasonal"` on an API outage shows `"No supporter predictions scored for this campaign yet."` instead of an error notice.
  3. Clicking `"Lock in (3 pts)"` as a guest or encountering a `400`/`401` backend rejection displays `errorBanner` (`lines 282-292`) at the top of the page—completely off-screen when a user is scrolled down to fixture #4 on mobile—and `notificationMessage` (`line 276`) has the same off-screen issue.
  4. `lines 64-81`: `$effect` resets `predictionInputs` whenever `data` changes (e.g. background Supabase token refresh `invalidate('supabase:auth')`), discarding scores the user is currently editing.
- **User Impact:** Users see empty leaderboards on transient errors, miss validation/auth feedback because banners appear off-screen at the top, and can lose typed scores during token refresh.
- **Proposed Solution:**
  - Throw/propagate errors on interactive refreshes (`fetchLeaderboardStrict`, `fetchPredictionHistoryStrict` or `throwApiError`), preserving existing `leaderboard`/`history` on transient failure and showing an inline `role="alert"` + Retry control in the Leaderboard/History sections.
  - Show inline per-fixture error/confirmation status directly inside the fixture card footer (`aria-live="polite"` / `role="alert"`) alongside the page banner, and show `"Sign in to lock in"` CTA clarity on guest cards.
  - Preserve dirty `predictionInputs` across auth revalidation unless `upcoming` match IDs change or a prediction was just saved.
- **Skill Responsible:** `improve-ui`, `svelte-runes`
- **Scope:** `frontEnd/src/lib/api/football.ts`, `frontEnd/src/lib/api/community.ts`, `frontEnd/src/routes/predictions/+page.svelte`
- **Risk:** Low.
- **Acceptance Criteria:**
  1. Failed leaderboard/history requests show an explicit error + Retry without wiping previously loaded data.
  2. Fixture-level rejections (`400` locked, `401` unauth, network) appear inline on the submitted fixture card.

---

### [INT-P1-13] 60s Countdown Drift, Inaccurate Open Fixture Count & Kickoff-Lock Clarity
- **Severity:** `P1`
- **Citations:**
  - `frontEnd/src/routes/predictions/+page.svelte:55-62` (`setInterval(..., 60000)`)
  - `frontEnd/src/routes/predictions/+page.svelte:89-109, 300, 312-329`
- **Evidence:**
  1. `nowMs` updates only every `60000ms` (`line 58`). A match kicking off 20 seconds after page load stays `"Kickoff < 1m"` and keeps inputs/Submit enabled for up to 59 seconds *after* kickoff has passed until clicking Submit triggers a `400` rejection from `predictions.py:142`.
  2. Line 300 displays `{upcoming.length} open for predictions` even if some scheduled matches in `upcoming` are already `isLocked === true`.
  3. Line 326 styles the `Locked` badge identically to muted metadata (`bg-paper-3 text-muted`) with no clear status explanation (`Kickoff passed — locked`) or semantic distinction from active countdowns.
- **User Impact:** Supporters experience confusing countdown freezes near kickoff and misleading `"open for predictions"` counts.
- **Proposed Solution:**
  - Use an adaptive interval (tick every `1000ms` when any unlocked fixture is `< 2 minutes` from kickoff, otherwise every `30000ms` or `60000ms`) so countdowns and lock transitions flip at the exact kickoff second.
  - Compute `openFixturesCount = $derived(upcoming.filter((u) => u.can_predict && !isKickoffPassed(u.match.utc_date, nowMs)).length)` for line 300.
  - Label locked badges `"Locked · Kickoff passed"` with `border-rule-2 text-ink-2` (clear AA contrast) and active `< 1h` countdowns with `text-accent-2 border-accent-2/50`.
- **Skill Responsible:** `improve-ui`, `svelte-runes`
- **Scope:** `frontEnd/src/routes/predictions/+page.svelte`
- **Risk:** Low — ensure `clearTimeout`/`clearInterval` cleanup runs in `$effect` teardown.
- **Acceptance Criteria:**
  1. Header count reflects only unlocked fixtures.
  2. Within 2 minutes of kickoff, the countdown ticks smoothly and automatically locks the card at `0s`.

---

### [INT-P1-14] Leaderboard Mode Race Condition & Unencoded `/supporters/{entry.user_name}` Link
- **Severity:** `P1`
- **Citations:**
  - `frontEnd/src/routes/predictions/+page.svelte:175-196, 530`
  - Backend reference: [`backEnd/app/api/v1/endpoints/supporters.py:105-115`](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/backEnd/app/api/v1/endpoints/supporters.py#L105-L115)
- **Evidence:**
  1. `refreshLeaderboard` (`lines 175-182`) has no request sequence / `AbortController` guard. Rapidly toggling `Seasonal` → `2024-2025` → `All-time` allows an older, slower request to resolve last and overwrite `leaderboard` with the wrong season's standings while the UI reads `"All-time rankings"`.
  2. Line 530 links to `href="/supporters/{entry.user_name}"` without `encodeURIComponent(entry.user_name)`. Names with spaces or `#`/`?` characters break route matching (compare with `/terrace` line 923 which uses `encodeURIComponent`).
- **User Impact:** Rapid leaderboard switching can display mismatched season data under the `"All-time"` header, and supporter links with spaces can 404 or misroute.
- **Proposed Solution:**
  - Track a monotonically increasing `leaderboardRequestId` (or `AbortController`) in `refreshLeaderboard` so stale responses are discarded and `isLoadingLeaderboard` only clears for the latest request.
  - Use `href="/supporters/{encodeURIComponent(entry.user_name)}"` on line 530.
- **Skill Responsible:** `svelte-runes`, `improve-ui`
- **Scope:** `frontEnd/src/routes/predictions/+page.svelte`
- **Risk:** Low.
- **Acceptance Criteria:**
  1. Rapidly switching `All-time` / `Seasonal` / season dropdowns never leaves stale standings visible.
  2. Leaderboard supporter links properly URL-encode `user_name`.

---

### [INT-P2-07] Prediction History Truncation, Missing Match Dossier Links & Missing `total_predictions_count`
- **Severity:** `P2`
- **Citations:**
  - `frontEnd/src/routes/predictions/+page.svelte:369-380, 398-459`
  - `frontEnd/src/lib/types/football.ts:333, 522-537` (`total_predictions_count` on `UpcomingMatchPrediction`, `match_id` on `PredictionHistoryItem`)
- **Evidence:**
  - Line 424 applies `truncate` to `{item.home_team} vs {item.away_team}`, clipping longer fixture titles with no link to `/matches/{item.match_id}` (`match_id` is already returned in `PredictionHistoryItem`!).
  - `Prediction History` lacks any `All` / `Graded` / `Pending` filter when a supporter accumulates dozens of entries, and `Upcoming` fixture cards (`lines 369-380`) never surface `item.total_predictions_count` (`"N supporters predicted"`), wasting real SQL data already fetched by `GET /predictions/upcoming`.
  - Also `upcoming` fixture cards (`lines 336, 363`) truncate `{match.home_team_name}` / `{match.away_team_name}` without `title` or wrapping on narrow screens.
- **User Impact:** Supporters cannot click from their settled prediction directly to the match dossier to see goalscorers, long team names clip silently, and community prediction volume is hidden.
- **Proposed Solution:**
  - Link `{item.home_team} vs {item.away_team}` (`line 424`) to `/matches/{encodeURIComponent(item.match_id)}` with `hover:text-accent` and allow natural wrapping (`line-clamp-2` instead of hard single-line `truncate`, same for fixture card team names on mobile).
  - Add a subtle `"All | Graded | Pending"` filter strip if `history.length > 5`, and show `{item.total_predictions_count} predictions` in the fixture metadata row.
- **Skill Responsible:** `improve-ui`, `hallmark`
- **Scope:** `frontEnd/src/routes/predictions/+page.svelte`
- **Risk:** Low.
- **Acceptance Criteria:**
  1. History rows link to `/matches/{match_id}` and support filtering when >5 items exist; long team names wrap cleanly without clipping.

---

## 5. Cross-Cutting Findings (`SSR`, `Svelte 5 Runes`, `Hallmark`)

### [INT-P0-07] `$effect`-Only State Initialization Breaks SSR Visibility (Hallmark Floor #7) & Causes Hydration Shift
- **Severity:** `P0`
- **Citations:**
  - `frontEnd/src/routes/board/+page.svelte:13-32` (`currentLineup`, `communityBoards` initialized `[]`, populated only in `$effect`)
  - `frontEnd/src/routes/lab/+page.svelte:37-118` (`result`, `insights`, `trendsData`, `h2hData`, `playerComparison` initialized `null`/`[]`, populated only in `$effect`)
  - `frontEnd/src/lib/components/HistoricalPitchExplorer.svelte:21-40` (`selectedMatchId`, `activeDetail` initialized `''`/`null`, populated only in `$effect`)
  - `frontEnd/src/routes/predictions/+page.svelte:13-17, 64-81` (`upcoming`, `leaderboard`, `history`, `predictionInputs` initialized `[]`/`{}`, populated only in `$effect`)
  - Design rule: [`hallmark/SKILL.md:26`](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/.agents/skills/hallmark/SKILL.md#L26) (Floor #7: *"content is visible with scripting off"*) & [`svelte-runes/SKILL.md:290, 304`](file:///e:/coding%20projects/CSE2200%20project/GUNNERS/.agents/skills/svelte-runes/SKILL.md#L290) (*"仅浏览器执行（SSR 自动跳过）"*)
- **Evidence:**
  - In Svelte 5 (`runes: true`), `$effect` never executes during SSR. Because all four routes initialize their primary state variables to `[]` or `null` and populate them inside `$effect`, the server-rendered HTML sent to browsers/crawlers renders:
    - `/board`: an **empty green pitch** (0 players) and `"No community tactics published yet."`
    - `/lab`: `"No completed matches found matching the specified parameters."` and `"0"` saved insights.
    - `/lab/historical`: `"No historical StatsBomb match telemetry available right now."`
    - `/predictions`: `"No upcoming matches scheduled for prediction right now."` and `"No supporter predictions scored yet."`
  - Only after JS downloads and hydrates does `$effect` fire, flashing from empty-state text into full content (severe CLS + Floor #7 failure).
- **User Impact:** Poor Core Web Vitals (CLS flash on every page load), broken no-JS / crawler rendering, and risk of `predictionInputs[match.id]` undefined access if rendered before `$effect` completes.
- **Proposed Solution:**
  - Use Svelte 5's `let x = $derived(data.x)` (writable `$derived` in Svelte 5.25+, which the project runs on `svelte ^5.57.1`!) OR initialize `$state(untrack(() => ...))` synchronously at script top-level (keeping `$effect` strictly for syncing subsequent `data` navigation changes, keyed by a stamp), and provide fallback-safe bindings for `predictionInputs[match.id]`.
- **Skill Responsible:** `svelte-runes`, `hallmark`
- **Scope:** `frontEnd/src/routes/board/+page.svelte`, `frontEnd/src/routes/lab/+page.svelte`, `frontEnd/src/lib/components/HistoricalPitchExplorer.svelte`, `frontEnd/src/routes/predictions/+page.svelte`
- **Risk:** Medium — verify `svelte-check` (`0 errors, 0 warnings`) and test both SSR HTML output and client-side re-navigation (`+page.ts` updates).
- **Acceptance Criteria:**
  1. Inspecting SSR HTML (or disabling JS) renders the initial 4-3-3 pitch & community boards on `/board`, initial Data Lab analysis on `/lab`, StatsBomb pitch on `/lab/historical`, and upcoming fixtures + leaderboard on `/predictions`.
  2. `npm --prefix frontEnd run check` reports `0 errors and 0 warnings`.

---

### [INT-P3-01] Unkeyed `{#each}` Blocks Across Interactive Lists & SVG Layers
- **Severity:** `P3`
- **Citations:**
  - `TacticalBoard.svelte:551, 595` (`bench`, `squadPlayers`)
  - `board/+page.svelte:178, 260` (`data.presets`, `communityBoards`)
  - `HistoricalPitchExplorer.svelte:87, 231, 261, 281, 373` (`matches`, `filteredShots`, `pass_links`, `pass_nodes`)
  - `lab/+page.svelte:585, 633, 649, 665, 697, 724, 739, 782, 798, 843, 861, 926, 1173, 1215, 1309, 1418, 1518`
  - `predictions/+page.svelte:309, 412, 505, 523`
- **Evidence:**
  - While `TacticalBoard.svelte:456` (`annotations`) and `488` (`lineup`) are properly keyed, almost every other `{#each}` in the audited surface is unkeyed. Filtering shots (`HistoricalPitchExplorer.svelte:231`), deleting boards/insights, or refreshing the leaderboard causes Svelte to patch DOM/SVG nodes by index rather than stable entity ID, which can misplace focus or stale input state.
- **User Impact:** Potential focus jumps or wrong input preservation when filtering shots or mutating lists.
- **Proposed Solution:** Add stable keys to all `{#each}` blocks (`(shot.id)`, `(b.id)`, `(ins.id)`, `(item.match.id)`, `(entry.user_id)`, `(pt.row.season_id)`, etc.).
- **Skill Responsible:** `svelte-runes`
- **Scope:** All 5 `.svelte` files in the audited surface.
- **Risk:** Low.
- **Acceptance Criteria:** Every dynamic `{#each}` across the audited `.svelte` files has a unique, stable key expression.

---

### [INT-P3-02] Unused Variable `_authorClub` & Minor Template Cleanup
- **Severity:** `P3`
- **Citations:**
  - `frontEnd/src/routes/board/+page.svelte:261` (`{@const _authorClub = CLUBS[b.author_club_id] || CLUBS['arsenal']}`)
- **Evidence:** `_authorClub` is computed inside the `communityBoards` loop and never referenced in markup.
- **User Impact:** Dead code noise.
- **Proposed Solution:** Remove `_authorClub` (or display club badge only if multi-club affiliation is rendered intentionally).
- **Skill Responsible:** `svelte-runes`
- **Scope:** `frontEnd/src/routes/board/+page.svelte`
- **Risk:** Low.
- **Acceptance Criteria:** Zero unused `@const` declarations in `board/+page.svelte`.

---

## 6. Complete Finding Index (All 29 Consolidated Findings Ranked by Priority)

| ID | Sev | Surface | Summary | File:Line | Primary Skill |
| :--- | :---: | :--- | :--- | :--- | :--- |
| `INT-P0-01` | **P0** | `/predictions` | `grid-cols-7` (`col-span-1` ~41px) overflows `390px` mobile; no steppers/`inputmode`/team labels | `predictions/+page.svelte:334-366` | `improve-ui` |
| `INT-P0-02` | **P0** | `/board` | `hasDragged` 0px threshold breaks tap-to-edit; `touch-none` traps scroll; missing `onpointercancel` | `TacticalBoard.svelte:84-152, 401-411` | `improve-ui` |
| `INT-P0-03` | **P0** | `/board` | `focus:outline-none` on pitch tokens violates Floor #6; `role="application"` traps screen readers | `TacticalBoard.svelte:406, 494` | `a11y-audit` |
| `INT-P0-04` | **P0** | `/lab` | `Save as insight` mixes stale `result` with newly selected `metric`/`venue`; visible on wrong tabs | `lab/+page.svelte:245-286, 628-701, 902` | `svelte-runes` |
| `INT-P0-05` | **P0** | `/lab` | Save Insight modal lacks `role="dialog"`, focus trap, `Escape`, `z-[400]`, & `>=3` char check | `lab/+page.svelte:1571-1642` | `a11y-audit` |
| `INT-P0-07` | **P0** | All 4 | `$effect`-only data hydration hides all content in SSR / no-JS (Hallmark Floor #7 + CLS) | `board/+page.svelte:25`, `lab/+page.svelte:76`, `HistoricalPitchExplorer.svelte:29`, `predictions/+page.svelte:64` | `svelte-runes` |
| `INT-P1-01` | **P1** | `/board` | Departed bench (`Neto #32`, `Jorginho #20`, `Sterling #30`) & readonly bench leak on `/terrace` | `TacticalBoard.svelte:50-63, 539`; `football.ts:862` | `improve-ui` |
| `INT-P1-02` | **P1** | `/board` | `"GUNNERS REBORN"` PNG banner, missing arrows in PNG, clipped formation/bench text, raw RGB | `TacticalBoard.svelte:208-310` | `hallmark` |
| `INT-P1-03` | **P1** | `/board` | Missing owner Delete UI (`DELETE /tactics/{id}`) & unauthenticated `fetchTacticalBoards` | `board/+page.svelte:259-291`, `board/+page.ts:11`, `football.ts:913` | `improve-ui` |
| `INT-P1-04` | **P1** | `/board` | No keyboard token nudging/bench swap; `#roster-select` blanks `#player-role`; missing `aria-pressed` | `TacticalBoard.svelte:205, 498, 554, 629` | `a11y-audit` |
| `INT-P1-05` | **P1** | `/board` | Edit Player modal lacks `role="dialog"`, focus trap, `Escape`, `z-[400]`, & name/number guard | `TacticalBoard.svelte:570-657` | `a11y-audit` |
| `INT-P1-06` | **P1** | `/lab` | `football.ts` swallows HTTP/network errors as `null`/`[]`, faking `"No matches found"` | `football.ts:297-356, 589, 730`; `lab/+page.svelte:1124, 1339, 1554` | `improve-ui` |
| `INT-P1-07` | **P1** | `/lab` | Missing URL sync (`club`, `tmetric`, `?match=`), dishonest clipboard toast, missing `tabpanel` ARIA | `lab/+page.svelte:153-243, 582`, `HistoricalPitchExplorer.svelte:42` | `a11y-audit` |
| `INT-P1-08` | **P1** | `/lab` | Mobile SVG legibility (`~4.6px` text), overlapping penalty shots `(88.5,50)`, color-only legend, trend gaps | `lab/+page.svelte:414, 1159`; `HistoricalPitchExplorer.svelte:202, 212-310` | `a11y-audit` |
| `INT-P1-09` | **P1** | `/lab` | Zero-match `0 %` display, missing low/unequal sample warnings, Arsenal-only club scope confusion | `lab/+page.svelte:963, 1031, 1147, 1305` | `improve-ui` |
| `INT-P1-10` | **P1** | `/lab` | StatsBomb ODbL attribution lacks clickable source & ODbL 1.0 links; pass network missing team key | `HistoricalPitchExplorer.svelte:197, 312-314, 383-388` | `improve-ui` |
| `INT-P1-11` | **P1** | `/lab` | Missing owner Delete UI (`DELETE /insights/{id}`) & 6-item cap in Saved Insights | `lab/+page.svelte:913-947`, `football.ts:358-385` | `improve-ui` |
| `INT-P1-12` | **P1** | `/predictions` | Leaderboard/history refresh errors wipe data to `[]`; off-screen guest/API errors; `$effect` input wipe | `predictions/+page.svelte:64, 111-182`, `football.ts:641`, `community.ts:124` | `improve-ui` |
| `INT-P1-13` | **P1** | `/predictions` | 60s interval drifts past kickoff; `open for predictions` includes locked games; weak lock badge | `predictions/+page.svelte:55-62, 89-109, 300, 325` | `improve-ui` |
| `INT-P1-14` | **P1** | `/predictions` | Leaderboard mode switch async race condition; `/supporters/{user_name}` missing `encodeURIComponent` | `predictions/+page.svelte:175-196, 530` | `svelte-runes` |
| `INT-P2-01` | **P2** | `/board` | Missing Undo arrow / per-arrow delete & `aria-pressed` on tool buttons | `TacticalBoard.svelte:178, 323-397` | `improve-ui` |
| `INT-P2-02` | **P2** | `/board` | Mobile SVG label size (`3.6px`), `md:grid-cols-8` `85px` bench clipping, duplicate hints | `TacticalBoard.svelte:528, 550`; `board/+page.svelte:169` | `improve-ui` |
| `INT-P2-03` | **P2** | `/board` | Client `2..150` title validation, `"Share to Terrace"` reload data loss, stale `savedBoardId` | `board/+page.svelte:34, 119, 156, 197, 208` | `improve-ui` |
| `INT-P2-04` | **P2** | `/lab` | Shot inspector lacks `aria-live="polite"` & mobile summary; static pass network nodes | `HistoricalPitchExplorer.svelte:281-308, 320-381` | `a11y-audit` |
| `INT-P2-05` | **P2** | `/lab` | Trends table `<tr onclick>` is mouse-only (missing native `<button>`) | `lab/+page.svelte:1311-1314` | `a11y-audit` |
| `INT-P2-06` | **P2** | `/board`, `/lab` | Fixed toasts/modals use `z-50` colliding with sticky header (`z-50`) instead of `--z-modal`/`--z-toast` | `board/+page.svelte:122`, `lab/+page.svelte:546, 1572`, `TacticalBoard.svelte:571` | `hallmark` |
| `INT-P2-07` | **P2** | `/predictions` | History lacks `/matches/{id}` links, filters & unclipped names; `total_predictions_count` unused | `predictions/+page.svelte:369, 411-457` | `improve-ui` |
| `INT-P3-01` | **P3** | All 4 | Unkeyed `{#each}` loops across interactive SVG/list collections | `TacticalBoard.svelte`, `board/+page.svelte`, `lab/+page.svelte`, `HistoricalPitchExplorer.svelte`, `predictions/+page.svelte` | `svelte-runes` |
| `INT-P3-02` | **P3** | `/board` | Unused `@const _authorClub` inside `communityBoards` loop | `board/+page.svelte:261` | `svelte-runes` |

*(Note: 29 consolidated items above incorporate all 32 distinct defects identified in Section 2–5, with zero dropped requirements.)*

---

## 7. Phase 2 Remediation Sequence & Verification Gates

Recommended implementation order to minimize merge conflicts and unblock verification:
1. **Batch A — Shared API & SSR Foundations (`football.ts`, `community.ts`, `+page.ts`):**
   - Add `deleteTacticalBoard`, `deleteInsight`, Bearer support on `fetchTacticalBoards`, strict error-throwing query variants (`queryAnalyticsStrict`, `fetchMultiSeasonTrendsStrict`, `fetchOpponentH2HStrict`, `comparePlayersStrict`, `fetchLeaderboardStrict`, `fetchPredictionHistoryStrict`), and update offline `Zinchenko` preset fallback.
2. **Batch B — Tactical Pitch Studio (`TacticalBoard.svelte`, `board/+page.svelte`):**
   - Fix `INT-P0-02`, `INT-P0-03`, `INT-P0-07`, `INT-P1-01..05`, `INT-P2-01..03`, `INT-P2-06`, `INT-P3-01..02` while preserving `0..100` SVG coordinates and `/terrace` `readonly={true}` compatibility.
3. **Batch C — Data Lab & Historical Explorer (`lab/+page.svelte`, `lab/+page.ts`, `HistoricalPitchExplorer.svelte`):**
   - Fix `INT-P0-04`, `INT-P0-05`, `INT-P0-07`, `INT-P1-06..11`, `INT-P2-04..06`, `INT-P3-01`.
4. **Batch D — Matchday Predictor (`predictions/+page.svelte`):**
   - Fix `INT-P0-01`, `INT-P0-07`, `INT-P1-12..14`, `INT-P2-07`, `INT-P3-01`.
5. **Verification Gate:**
   - `npm --prefix frontEnd run check` (`0 errors and 0 warnings`)
   - `npm --prefix frontEnd run build` (clean SSR + client bundle)
   - `node ".agents/skills/hallmark/scripts/sloplint.mjs" "frontEnd/src" --genre editorial --kept` (`0 FAIL, 0 REFLEX, 0 WARN`)
   - Manual / Playwright verification at `390px` mobile and `1280px` desktop: keyboard-only Tab/Enter/Escape/Arrow audit on pitch tokens, modals, shot markers, and `grid-cols-7` replacement on `/predictions`.
