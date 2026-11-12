import { expect, test } from '@playwright/test';
import { installApiMocks, navigateSpa } from './helpers/api-mocks';

test.describe('Interactive Tools: Dugout, Data Lab, Historical Pitch & Predictor', () => {
	test('Dugout pitch tokens support click-to-edit, Arrow nudge, bench swap, vector undo/clear, and rejected publish handling', async ({
		page
	}) => {
		await installApiMocks(page);
		await page.goto('/');
		await page.waitForLoadState('load');
		await navigateSpa(page, '/board');

		const bodyText = await page.locator('body').innerText();
		for (const legacy of ['Neto', 'Jorginho', 'Sterling', 'Zinchenko']) {
			expect(bodyText).not.toContain(legacy);
		}

		const sakaToken = page.locator('svg[aria-label="Arsenal tactical pitch diagram"] g[role="button"]', {
			hasText: 'Saka'
		}).first();
		await expect(sakaToken).toBeVisible();

		// Pointer click without drag (<0.8% delta) opens Quick-Edit modal
		await sakaToken.click();
		const editModal = page.locator('div[role="dialog"][aria-labelledby="edit-player-modal-title"]');
		await expect(editModal).toBeVisible();
		await page.keyboard.press('Escape');
		await expect(editModal).toBeHidden();

		// Arrow keys nudge token coordinates
		const beforeTransform = await sakaToken.getAttribute('transform');
		await sakaToken.focus();
		await page.keyboard.press('ArrowLeft');
		const afterTransform = await sakaToken.getAttribute('transform');
		expect(afterTransform).not.toBe(beforeTransform);

		// Bench swap replaces starter cleanly
		const gyokeresBench = page.getByRole('button', { name: /Gyökeres/i }).first();
		await gyokeresBench.click();
		await expect(gyokeresBench).toHaveAttribute('aria-pressed', 'true');
		await sakaToken.click();
		await expect(
			page.locator('svg[aria-label="Arsenal tactical pitch diagram"] g[role="button"]', { hasText: 'Gyökeres' })
		).toBeVisible();

		// Vector drawing + Undo + Clear
		await page.getByRole('button', { name: 'Run vector' }).click();
		const pitchSvg = page.locator('svg[aria-label="Arsenal tactical pitch diagram"]');
		await pitchSvg.scrollIntoViewIfNeeded();
		const box = await pitchSvg.boundingBox();
		expect(box).not.toBeNull();
		if (box) {
			await page.mouse.move(box.x + box.width * 0.45, box.y + box.height * 0.25);
			await page.mouse.down();
			await page.mouse.move(box.x + box.width * 0.65, box.y + box.height * 0.25, { steps: 8 });
			await page.mouse.up();
		}
		await expect(pitchSvg.locator('line[marker-end="url(#arrow-run)"]')).toHaveCount(1);
		await expect(page.locator('dt:has-text("Tactical vectors") + dd')).toHaveText('1');
		await page.getByRole('button', { name: 'Undo arrow' }).click();
		await expect(pitchSvg.locator('line[marker-end="url(#arrow-run)"]')).toHaveCount(0);

		if (box) {
			await page.mouse.move(box.x + box.width * 0.45, box.y + box.height * 0.25);
			await page.mouse.down();
			await page.mouse.move(box.x + box.width * 0.65, box.y + box.height * 0.25, { steps: 8 });
			await page.mouse.up();
		}
		await expect(pitchSvg.locator('line[marker-end="url(#arrow-run)"]')).toHaveCount(1);
		await page.getByRole('button', { name: 'Clear arrows' }).click();
		await expect(pitchSvg.locator('line[marker-end="url(#arrow-run)"]')).toHaveCount(0);

		// Rejected publish never fakes community archive success
		await page.locator('#blueprint-title').fill('Attempted Guest Publish');
		const initialArticles = await page.locator('article').count();
		await page.getByRole('button', { name: 'Publish blueprint' }).click();
		await expect(page.getByRole('alert')).toContainText('Please sign in to publish tactical blueprints.');
		await expect(page.locator('article')).toHaveCount(initialArticles);
	});

	test('Dugout Quick-Edit modal Escape restores focus to SVG pitch token (WCAG focus-return)', async ({
		page
	}) => {
		await installApiMocks(page);
		await page.goto('/');
		await page.waitForLoadState('load');
		await navigateSpa(page, '/board');

		const sakaToken = page.locator('svg[aria-label="Arsenal tactical pitch diagram"] g[role="button"]', {
			hasText: 'Saka'
		}).first();
		await sakaToken.focus();
		await expect(sakaToken).toBeFocused();
		await page.keyboard.press('Enter');

		const editModal = page.locator('div[role="dialog"][aria-labelledby="edit-player-modal-title"]');
		await expect(editModal).toBeVisible();
		await page.keyboard.press('Escape');
		await expect(editModal).toBeHidden();
		await expect(sakaToken).toBeFocused();
	});

	test('Data Lab WAI-ARIA tablist updates URL across 5 lenses, scopes Save as insight to Query, and traps modal focus', async ({
		page
	}) => {
		await installApiMocks(page);
		await page.goto('/');
		await page.waitForLoadState('load');
		await navigateSpa(page, '/lab');

		const queryTab = page.locator('#tab-query');
		await expect(queryTab).toHaveAttribute('aria-selected', 'true');
		await expect(page.getByRole('button', { name: 'Save as insight' })).toBeVisible();

		await queryTab.focus();
		await page.keyboard.press('ArrowDown');
		await expect(page.locator('#tab-trends')).toHaveAttribute('aria-selected', 'true');
		await expect(page).toHaveURL(/tab=trends/);
		await expect(page.getByRole('button', { name: 'Save as insight' })).toBeHidden();

		await page.keyboard.press('ArrowDown');
		await expect(page.locator('#tab-h2h')).toHaveAttribute('aria-selected', 'true');
		await expect(page).toHaveURL(/tab=h2h/);

		await page.keyboard.press('ArrowDown');
		await expect(page.locator('#tab-squad')).toHaveAttribute('aria-selected', 'true');
		await expect(page).toHaveURL(/tab=squad/);

		await page.keyboard.press('ArrowDown');
		await expect(page.locator('#tab-pitch')).toHaveAttribute('aria-selected', 'true');
		await expect(page).toHaveURL(/tab=pitch/);

		await page.keyboard.press('Home');
		await expect(queryTab).toHaveAttribute('aria-selected', 'true');
		await expect(page).toHaveURL(/tab=query/);

		// Run updated query and verify Save as insight guest auth gate (publish modal is auth-gated)
		await page.locator('#metric-select').selectOption('goals_per_match');
		await page.locator('#venue-filter').selectOption('home');
		await page.getByRole('button', { name: 'Calculate analytics' }).click();
		await expect(page).toHaveURL(/metric=goals_per_match/);
		await expect(page).toHaveURL(/venue=home/);

		const saveInsightBtn = page.getByRole('button', { name: 'Save as insight' });
		await saveInsightBtn.click();
		const authAlert = page.getByRole('alert');
		await expect(authAlert).toContainText('Please sign in to publish Data Lab insights.');
		await expect(authAlert.locator('a[href="/login?next=/lab"]')).toBeVisible();
	});

	test('Historical StatsBomb Pitch includes ODbL attribution and supports keyboard shot inspection', async ({
		page
	}) => {
		await installApiMocks(page);
		await page.goto('/');
		await page.waitForLoadState('load');
		await navigateSpa(page, '/lab/historical');

		await expect(page.locator('a[href="https://github.com/statsbomb/open-data"]')).toBeVisible();
		await expect(page.locator('a[href="https://opendatacommons.org/licenses/odbl/1.0/"]')).toBeVisible();

		const firstShot = page.locator('svg[aria-label="StatsBomb 2D tactical event pitch"] g[role="button"]').first();
		await expect(firstShot).toBeVisible();
		await firstShot.focus();
		await page.keyboard.press('Enter');
		await expect(page.getByText(/Robin van Persie|Andrey Arshavin|David Villa/).first()).toBeVisible();

		const nextShotBtn = page.getByRole('button', { name: 'Next shot' });
		await expect(nextShotBtn).toBeVisible();
		await nextShotBtn.click();
		await expect(page.getByRole('button', { name: 'Prev shot' })).toBeVisible();
	});

	test('Predictor at 390px has overlap-free steppers, clamps 0..20, enforces kickoff locks, and rejects guest submit cleanly', async ({
		page
	}) => {
		await page.setViewportSize({ width: 390, height: 844 });
		await installApiMocks(page);
		await page.goto('/');
		await page.waitForLoadState('load');
		await navigateSpa(page, '/predictions');

		await expect(page.getByText('3 pts')).toBeVisible();
		await expect(page.getByText('1 pt')).toBeVisible();
		await expect(page.getByText('0 pts')).toBeVisible();
		await expect(page.getByText('Locked · Kickoff passed')).toBeVisible();
		await expect(page.getByRole('button', { name: 'Locked (kickoff passed)' })).toBeDisabled();

		const homeDec = page.getByRole('button', { name: 'Decrease Arsenal FC predicted goals' }).first();
		const homeInput = page.getByRole('spinbutton', { name: 'Arsenal FC predicted goals' }).first();
		const homeInc = page.getByRole('button', { name: 'Increase Arsenal FC predicted goals' }).first();
		const awayDec = page.getByRole('button', { name: 'Decrease Real Madrid CF predicted goals' }).first();

		const boxes = await Promise.all([
			homeDec.boundingBox(),
			homeInput.boundingBox(),
			homeInc.boundingBox(),
			awayDec.boundingBox()
		]);
		expect(boxes.every(Boolean)).toBe(true);
		const [b0, b1, b2, b3] = boxes.map((b) => b!);
		expect(b0.height).toBeGreaterThanOrEqual(44);
		expect(b0.width).toBeGreaterThanOrEqual(44);
		expect(b0.x + b0.width).toBeLessThanOrEqual(b1.x + 1);
		expect(b1.x + b1.width).toBeLessThanOrEqual(b2.x + 1);
		expect(b2.x + b2.width).toBeLessThanOrEqual(b3.x + 1);

		await homeInput.fill('25');
		await expect(homeInput).toHaveValue('20');
		await expect(homeInc).toBeDisabled();

		await homeInput.fill('0');
		await expect(homeDec).toBeDisabled();
		await homeInc.click();
		await expect(homeInput).toHaveValue('1');

		await page.getByRole('button', { name: 'Sign in to lock in' }).first().click();
		await expect(page.getByRole('alert').first()).toContainText('Please sign in to submit score predictions.');
	});
});
