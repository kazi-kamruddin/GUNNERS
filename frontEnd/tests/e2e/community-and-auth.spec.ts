import { expect, test } from '@playwright/test';
import { installApiMocks, navigateSpa } from './helpers/api-mocks';

test.describe('Community Gates, Auth Controls & Session Safety', () => {
	test('Terrace guest browsing never opens auth dialog on Tab focus and restores focus on Escape', async ({
		page
	}) => {
		await installApiMocks(page);
		await page.goto('/');
		await page.waitForLoadState('load');
		await navigateSpa(page, '/terrace');

		const signInPublishBtn = page.getByRole('button', { name: 'Sign in to publish' });
		await expect(signInPublishBtn).toBeVisible();
		await expect(page.locator('a[href="/signup?next=%2Fterrace"]').first()).toBeVisible();

		// Tabbing across interactive controls must NEVER open an auth modal trap
		for (let i = 0; i < 8; i++) {
			await page.keyboard.press('Tab');
			await expect(page.locator('div[role="dialog"]')).toHaveCount(0);
		}

		await signInPublishBtn.focus();
		await expect(page.locator('div[role="dialog"]')).toHaveCount(0);

		await signInPublishBtn.click();
		const authDialog = page.locator('div[role="dialog"][aria-labelledby="terrace-auth-modal-title"]');
		await expect(authDialog).toBeVisible();
		await expect(authDialog.locator('a[href="/login?next=%2Fterrace"]')).toBeVisible();

		await page.keyboard.press('Escape');
		await expect(authDialog).toBeHidden();
		await expect(signInPublishBtn).toBeFocused();
	});

	test('Messages and Notifications show clean guest sign-in gates with ?next preservation', async ({
		page
	}) => {
		await installApiMocks(page);
		await page.goto('/messages');
		await page.waitForLoadState('load');

		await expect(page.locator('a[href="/login?next=%2Fmessages"]').first()).toBeVisible();
		await expect(page.locator('a[href="/signup?next=%2Fmessages"]').first()).toBeVisible();

		await page.goto('/notifications');
		await page.waitForLoadState('load');
		await expect(page.getByText('Sign in to view notifications')).toBeVisible();
		await expect(page.locator('a[href="/login?next=%2Fnotifications"]').first()).toBeVisible();
	});

	test('Login & Signup preserve ?next path, toggle password visibility accessibly, and reject GET /auth/signout', async ({
		page
	}) => {
		await page.goto('/login?next=%2Flab%3Ftab%3Dtrends');
		await page.waitForLoadState('load');

		const passwordInput = page.locator('#password');
		const toggleBtn = page.locator('button[aria-controls="password"]');
		await expect(passwordInput).toHaveAttribute('type', 'password');
		await expect(toggleBtn).toHaveAttribute('aria-pressed', 'false');

		await toggleBtn.click();
		await expect(passwordInput).toHaveAttribute('type', 'text');
		await expect(toggleBtn).toHaveAttribute('aria-pressed', 'true');

		await expect(page.locator('input[name="next"]')).toHaveValue('/lab?tab=trends');
		await expect(page.locator('a[href="/signup?next=%2Flab%3Ftab%3Dtrends"]').first()).toBeVisible();

		await page.goto('/signup?next=%2Fpredictions');
		await page.waitForLoadState('load');
		const signupToggle = page.locator('button[aria-controls="password"]');
		await expect(page.locator('#password')).toHaveAttribute('type', 'password');
		await signupToggle.click();
		await expect(page.locator('#password')).toHaveAttribute('type', 'text');
		await expect(page.locator('input[name="next"]')).toHaveValue('/predictions');

		// GET /auth/signout must NEVER sign out (405 Method Not Allowed)
		const signoutGet = await page.request.get('/auth/signout');
		expect(signoutGet.status()).toBe(405);
	});
});
