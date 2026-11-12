# Design: GUNNERS

The locked system. Every Hallmark run reads this first and pages share it. Change it on purpose; the file is the rule.

## System
- Genre: editorial
- Shape of the first page: Ledger
- Theme: brand (vibe: "Arsenal matchday programme meets precision tactical ledger")
- Axes: dark/slab-serif/chromatic-red · posture: restrained

## Tokens
`tokens.css` is the source of truth. The roles:
```css
:root {
  --color-paper: oklch(14% 0.012 24);  --color-paper-2: oklch(18% 0.014 24);  --color-paper-3: oklch(22% 0.016 24);
  --color-ink: oklch(95% 0.008 75);  --color-ink-2: oklch(84% 0.010 60);  --color-muted: oklch(68% 0.014 40);  --color-rule: oklch(26% 0.015 24);
  --color-accent: oklch(56% 0.22 27);  --color-accent-ink: oklch(98% 0.005 75);  --color-focus: oklch(60% 0.21 27);
  --font-display: "Besley", Georgia, ui-serif, serif;  --font-body: "Hanken Grotesk", ui-sans-serif, system-ui, sans-serif;  --font-outlier: "JetBrains Mono", ui-monospace, monospace;
  --radius-card: 4px;  --radius-pill: 999px;  --rule-hair: 1px;  --shadow-card: none;
}
```
The spacing scale, the type scale, the easings and the durations are the scaffold's and live in `tokens.css`.

## Controls
- Primary: `--color-accent` fill with `--color-accent-ink` text · `4px` (`--radius-card`) · `40px`
- Secondary: `1px solid var(--color-rule)` outline on `--color-paper-2` or transparent · same radius and height

## Motion
- Character: brisk; one reveal at most; under reduced motion everything ends at once.

## Exports
`tokens.css` in this project (`frontEnd/src/tokens.css`), wired with `@theme static` for Tailwind v4.
