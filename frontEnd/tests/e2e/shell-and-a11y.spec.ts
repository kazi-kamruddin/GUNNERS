import { expect, test } from '@playwright/test';
import { installApiMocks, navigateSpa } from './helpers/api-mocks';

const ALL_ROUTES = [
	'/',
	'/news',
	'/matches',
	'/squad',
	'/board',
	'/lab',
	'/lab/historical',
	'/terrace',
	'/predictions',
	'/messages',
	'/notifications',
	'/login',
	'/signup'
];

const VIEWPORTS = [
	{ name: '320px', width: 320, height: 740 },
	{ name: '390px', width: 390, height: 844 },
	{ name: '768px', width: 768, height: 1024 },
	{ name: '1024px', width: 1024, height: 800 },
	{ name: '1280px', width: 1280, height: 800 }
];

test.describe('Shell, Responsive Geometry & Accessibility Probes', () => {
	for (const vp of VIEWPORTS) {
		test(`zero horizontal overflow across all 13 routes at ${vp.name}`, async ({ page }) => {
			await page.setViewportSize({ width: vp.width, height: vp.height });
			await installApiMocks(page);

			const consoleErrors: string[] = [];
			const pageErrors: string[] = [];
			page.on('console', (msg) => {
				if (msg.type() === 'error') consoleErrors.push(`${page.url()}: ${msg.text()}`);
			});
			page.on('pageerror', (err) => {
				pageErrors.push(`${page.url()}: ${err.message}`);
			});

			await page.goto('/');
			await page.waitForLoadState('load');

			for (const route of ALL_ROUTES) {
				if (route !== '/') {
					await navigateSpa(page, route);
				}
				if (route === '/') {
					await expect(page.locator('h1').first()).toBeVisible();
				} else {
					await expect(page.locator('#main-content')).toBeVisible();
				}

				const metrics = await page.evaluate(() => ({
					scrollWidth: document.documentElement.scrollWidth,
					innerWidth: window.innerWidth
				}));
				expect(
					metrics.scrollWidth,
					`Horizontal overflow on ${route} at ${vp.name}: scrollWidth=${metrics.scrollWidth} > innerWidth=${metrics.innerWidth}`
				).toBeLessThanOrEqual(metrics.innerWidth);
			}

			expect(pageErrors, `Uncaught pageerrors at ${vp.name}: ${pageErrors.join(' | ')}`).toEqual([]);
			expect(consoleErrors, `Console errors at ${vp.name}: ${consoleErrors.join(' | ')}`).toEqual([]);
		});
	}

	test('skip link moves focus to #main-content and desktop nav highlights active route including Predictor', async ({
		page
	}) => {
		await page.setViewportSize({ width: 1280, height: 800 });
		await installApiMocks(page);
		await page.goto('/');
		await page.waitForLoadState('load');

		await page.keyboard.press('Tab');
		const skipLink = page.locator('a.skip-link');
		await expect(skipLink).toBeFocused();
		await expect(skipLink).toHaveAttribute('href', '#main-content');
		await page.keyboard.press('Enter');
		await expect(page).toHaveURL(/#main-content$/);

		const desktopNav = page.locator('nav[aria-label="Primary navigation"]');
		await expect(desktopNav).toBeVisible();
		const predictorLink = desktopNav.locator('a[href="/predictions"]');
		await expect(predictorLink).toHaveText('Predictor');
		await expect(desktopNav.locator('a[href="/"]')).toHaveAttribute('aria-current', 'page');

		await predictorLink.click();
		await expect(page).toHaveURL(/\/predictions$/);
		await expect(predictorLink).toHaveAttribute('aria-current', 'page');
	});

	test('mobile <1024px drawer traps Tab focus, restores focus on Escape, and closes on route navigation', async ({
		page
	}) => {
		await page.setViewportSize({ width: 390, height: 844 });
		await installApiMocks(page);
		await page.goto('/');
		await page.waitForLoadState('load');

		const menuBtn = page.locator('button[aria-controls="mobile-primary-nav"]');
		await expect(menuBtn).toBeVisible();
		await expect(menuBtn).toHaveAttribute('aria-expanded', 'false');

		await menuBtn.click();
		const drawer = page.locator('#mobile-primary-nav');
		await expect(drawer).toBeVisible();
		await expect(menuBtn).toHaveAttribute('aria-expanded', 'true');

		for (let i = 0; i < 14; i++) {
			await page.keyboard.press('Tab');
			const insideDrawer = await page.evaluate(() => {
				const el = document.activeElement;
				const container = document.getElementById('mobile-primary-nav');
				return Boolean(el && container && container.contains(el));
			});
			expect(insideDrawer, `Tab escaped #mobile-primary-nav on step ${i + 1}`).toBe(true);
		}

		await page.keyboard.press('Escape');
		await expect(drawer).toBeHidden();
		await expect(menuBtn).toHaveAttribute('aria-expanded', 'false');
		await expect(menuBtn).toBeFocused();

		await menuBtn.click();
		await expect(drawer).toBeVisible();
		await drawer.locator('a[href="/predictions"]').click();
		await expect(page).toHaveURL(/\/predictions$/);
		await expect(drawer).toBeHidden();
	});

	test('header controls meet >=44px hit-target size and h1 meets dark-theme contrast tokens', async ({
		page
	}) => {
		await page.setViewportSize({ width: 1280, height: 800 });
		await installApiMocks(page);
		await page.goto('/');
		await page.waitForLoadState('load');

		const headerTargets = await page.evaluate(() => {
			const header = document.querySelector('header');
			if (!header) return [];
			return Array.from(header.querySelectorAll('a, button'))
				.map((el) => {
					const r = el.getBoundingClientRect();
					return {
						text: (el.textContent || el.getAttribute('aria-label') || '').trim(),
						width: Math.round(r.width),
						height: Math.round(r.height),
						visible: r.width > 0 && r.height > 0
					};
				})
				.filter((item) => item.visible);
		});

		expect(headerTargets.length).toBeGreaterThan(0);
		for (const target of headerTargets) {
			expect(
				target.height,
				`Header control "${target.text}" height ${target.height}px < 44px`
			).toBeGreaterThanOrEqual(44);
		}

		const themeCheck = await page.evaluate(() => {
			const toSrgb = (cssColor: string): [number, number, number] | null => {
				if (!cssColor || cssColor === 'transparent' || cssColor === 'rgba(0, 0, 0, 0)') return null;
				const canvas = document.createElement('canvas');
				canvas.width = 1;
				canvas.height = 1;
				const ctx = canvas.getContext('2d');
				if (!ctx) return null;
				ctx.fillStyle = '#000000';
				ctx.fillStyle = cssColor;
				ctx.fillRect(0, 0, 1, 1);
				const data = ctx.getImageData(0, 0, 1, 1).data;
				return [data[0], data[1], data[2]];
			};
			const relLum = ([r, g, b]: [number, number, number]) => {
				const lin = [r, g, b].map((c) => {
					const s = c / 255;
					return s <= 0.03928 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4);
				});
				return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2];
			};

			const h1 = document.querySelector('h1');
			const h1Color = h1 ? getComputedStyle(h1).color : '';
			const surfaceEl = document.querySelector('.bg-paper') || document.body;
			const surfaceBg = getComputedStyle(surfaceEl).backgroundColor;
			const rootStyles = getComputedStyle(document.documentElement);

			const fg = toSrgb(h1Color);
			const bg = toSrgb(surfaceBg);

			let contrastRatio = 0;
			let bgLum = 1;
			if (fg && bg) {
				const l1 = relLum(fg);
				const l2 = relLum(bg);
				bgLum = l2;
				contrastRatio = (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
			}
			return {
				paperToken: rootStyles.getPropertyValue('--color-paper').trim(),
				inkToken: rootStyles.getPropertyValue('--color-ink').trim(),
				accentToken: rootStyles.getPropertyValue('--color-accent').trim(),
				surfaceBg,
				h1Color,
				bgLum,
				contrastRatio
			};
		});

		expect(themeCheck.paperToken).not.toBe('');
		expect(themeCheck.inkToken).not.toBe('');
		expect(themeCheck.accentToken).not.toBe('');
		expect(themeCheck.bgLum, 'Background should be dark-surface luminance < 0.1').toBeLessThan(0.1);
		expect(
			themeCheck.contrastRatio,
			`h1 contrast ratio ${themeCheck.contrastRatio.toFixed(2)} < 4.5`
		).toBeGreaterThanOrEqual(4.5);
	});
});
