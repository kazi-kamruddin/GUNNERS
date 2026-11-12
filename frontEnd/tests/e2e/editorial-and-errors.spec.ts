import { expect, test } from '@playwright/test';
import { installApiMocks, navigateSpa } from './helpers/api-mocks';

test.describe('Editorial Routes, Filters & Error Recovery', () => {
	test('Armory news wire syncs URL params, resets filters, and recovers from mocked 500 via Retry', async ({
		page
	}) => {
		let failNextNews = false;
		await installApiMocks(page, {
			newsOverride: async (url, route) => {
				if (failNextNews) {
					failNextNews = false;
					await route.fulfill({
						status: 500,
						contentType: 'application/json',
						body: JSON.stringify({ detail: 'Simulated upstream news outage' })
					});
					return;
				}
				const category = url.searchParams.get('category');
				const tag = url.searchParams.get('tag');
				const articles = [
					{
						id: 'news_1',
						title: 'Saka leads Arsenal build-up overload against Chelsea',
						summary: 'Right half-space combinations unlocked Chelsea early.',
						source_name: 'Arseblog',
						source_category: 'fan_blog',
						article_url: 'https://arseblog.com/example-saka',
						image_url: 'https://crests.football-data.org/57.png',
						published_at: '2026-11-12T12:00:00Z',
						author: 'Andrew Mangan',
						tags: ['Saka', 'Tactics']
					},
					{
						id: 'news_2',
						title: 'Arteta confirms Calafiori recovery timeline ahead of UCL clash',
						summary: 'Defensive rotation options ahead of midweek action.',
						source_name: 'BBC Sport',
						source_category: 'broadcast',
						article_url: 'https://bbc.co.uk/sport/football/example-arteta',
						image_url: 'https://crests.football-data.org/57.png',
						published_at: '2026-11-11T16:30:00Z',
						author: 'BBC Football',
						tags: ['Arteta', 'UCL']
					}
				].filter((a) => {
					if (category && category !== 'all' && a.source_category !== category) return false;
					if (tag && tag !== 'all' && !a.tags.includes(tag)) return false;
					return true;
				});

				await route.fulfill({
					status: 200,
					contentType: 'application/json',
					body: JSON.stringify({
						total: articles.length,
						has_more: false,
						sources_active: ['Arseblog', 'BBC Sport'],
						cached_at: '2026-11-12T12:00:00Z',
						articles
					})
				});
			}
		});

		await page.goto('/');
		await page.waitForLoadState('load');
		await navigateSpa(page, '/news');

		await expect(page.getByText('Saka leads Arsenal build-up overload against Chelsea')).toBeVisible();
		await expect(page.getByText('Arteta confirms Calafiori recovery timeline')).toBeVisible();

		await page.getByRole('button', { name: 'Fan blogs' }).click();
		await expect(page).toHaveURL(/category=fan_blog/);

		await page.getByRole('button', { name: '#Saka' }).click();
		await expect(page).toHaveURL(/category=fan_blog/);
		await expect(page).toHaveURL(/tag=Saka/);
		await expect(page.getByText('Showing 1 of 1 dispatches')).toBeVisible();

		const resetBtn = page.getByRole('button', { name: 'Reset filters' });
		await expect(resetBtn).toBeVisible();
		await resetBtn.click();
		await expect(page).toHaveURL(/\/news$/);
		await expect(page.getByText('Showing 2 of 2 dispatches')).toBeVisible();

		failNextNews = true;
		await page.getByRole('button', { name: 'Sync feeds' }).click();
		const alertBanner = page.getByRole('alert').filter({ hasText: 'The Armory wire is temporarily unavailable' });
		await expect(alertBanner).toBeVisible();
		await expect(alertBanner).toContainText('Simulated upstream news outage');

		await alertBanner.getByRole('button', { name: 'Retry' }).click();
		await expect(alertBanner).toBeHidden();
		await expect(page.getByText('Saka leads Arsenal build-up overload against Chelsea')).toBeVisible();
	});

	test('Matches ledger filters sync URL and Match Center handles 404 vs 503 failure states', async ({
		page
	}) => {
		let simulate500 = false;
		await installApiMocks(page, {
			matchDetailOverride: async (matchId, route) => {
				if (simulate500) {
					await route.fulfill({
						status: 500,
						contentType: 'application/json',
						body: JSON.stringify({ detail: 'Match ledger database unreachable' })
					});
					return;
				}
				if (matchId === 'match_1') {
					await route.fulfill({
						status: 200,
						contentType: 'application/json',
						body: JSON.stringify({
							id: 'match_1',
							competition_id: 'PL',
							competition_name: 'Premier League',
							season_id: '2025-2026-PL',
							home_team_id: 'arsenal',
							home_team_name: 'Arsenal FC',
							away_team_id: 'chelsea',
							away_team_name: 'Chelsea FC',
							matchday: 29,
							utc_date: '2026-04-12T15:30:00Z',
							status: 'FINISHED',
							home_score: 3,
							away_score: 1,
							venue: 'Emirates Stadium',
							referee: 'Michael Oliver',
							source: 'football-data.org',
							goalscorers: [{ player: 'Bukayo Saka', minute: 22, team: 'Arsenal FC' }],
							lineups: {
								home: { formation: '4-3-3', xi: [{ name: 'David Raya', number: 1, position: 'GK' }] },
								away: { formation: '4-2-3-1', xi: [{ name: 'Robert Sánchez', number: 1, position: 'GK' }] }
							},
							highlights: []
						})
					});
					return;
				}
				await route.fulfill({
					status: 404,
					contentType: 'application/json',
					body: JSON.stringify({ detail: 'Match dossier not found' })
				});
			}
		});

		await page.goto('/');
		await page.waitForLoadState('load');
		await navigateSpa(page, '/matches');

		await expect(page.getByText('2 matches shown')).toBeVisible();
		await page.getByRole('button', { name: 'Completed results' }).click();
		await expect(page).toHaveURL(/status=FINISHED/);
		await expect(page.getByText('1 matches shown')).toBeVisible();

		await page.locator('#comp-select').selectOption('PL');
		await expect(page).toHaveURL(/comp=PL/);

		await page.locator('#season-select').selectOption('2025-2026-PL');
		await expect(page).toHaveURL(/season=2025-2026-PL/);

		await page.locator('a[href="/matches/match_1"]').first().click();
		await expect(page).toHaveURL(/\/matches\/match_1$/);
		await expect(page.getByRole('heading', { level: 1 })).toContainText('Arsenal FC');
		await expect(page.getByText('Bukayo Saka')).toBeVisible();

		// Missing match ID -> HTTP 404 semantic error boundary
		await navigateSpa(page, '/matches/does-not-exist');
		await expect(page.getByText('Error 404')).toBeVisible();
		await expect(page.getByRole('heading', { level: 1 })).toHaveText('Page not found');

		// Upstream 500 -> mapped cleanly to HTTP 503 Service temporarily unavailable + Retry recovery
		simulate500 = true;
		await navigateSpa(page, '/matches/match_1');
		await expect(page.getByText('Error 503')).toBeVisible();
		await expect(page.getByRole('heading', { level: 1 })).toHaveText('Service temporarily unavailable');

		simulate500 = false;
		await page.getByRole('button', { name: 'Retry' }).click();
		await expect(page.getByRole('heading', { level: 1 })).toContainText('Arsenal FC');
	});

	test('Squad directory comparison and player dossier photo switcher update aria-pressed cleanly', async ({
		page
	}) => {
		await installApiMocks(page);
		await page.goto('/');
		await page.waitForLoadState('load');
		await navigateSpa(page, '/squad');

		await expect(page.getByText('3 squad players')).toBeVisible();
		const midTab = page.getByRole('button', { name: 'Midfielders' });
		await midTab.click();
		await expect(midTab).toHaveAttribute('aria-pressed', 'true');
		await expect(page).toHaveURL(/position=Midfielder/);
		await expect(page.getByText('1 squad players')).toBeVisible();

		await page.getByRole('button', { name: 'All Gunners' }).click();
		await expect(page.getByText('3 squad players')).toBeVisible();

		const compareButtons = page.getByRole('button', { name: 'Compare' });
		await compareButtons.nth(0).click();
		await compareButtons.nth(0).click(); // Second remaining "Compare" button

		const compPanel = page.locator('section[aria-label="Head-to-head player comparison"]');
		await expect(compPanel).toBeVisible();
		await expect(compPanel.locator('table')).toBeVisible();
		await expect(page).toHaveURL(/compare1=ply_saka/);
		await expect(page).toHaveURL(/compare2=ply_rice/);

		await page.locator('a[href="/squad/ply_saka"]').first().click();
		await expect(page).toHaveURL(/\/squad\/ply_saka$/);

		const portraitBtn = page.getByRole('button', { name: 'Portrait' });
		const actionBtn = page.getByRole('button', { name: 'Match action' });
		await expect(portraitBtn).toHaveAttribute('aria-pressed', 'true');
		await expect(actionBtn).toHaveAttribute('aria-pressed', 'false');

		await actionBtn.click();
		await expect(actionBtn).toHaveAttribute('aria-pressed', 'true');
		await expect(portraitBtn).toHaveAttribute('aria-pressed', 'false');
	});
});
