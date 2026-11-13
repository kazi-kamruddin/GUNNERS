import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { describe, expect, it, vi } from 'vitest';
import {
	API_BASE,
	ApiError,
	fetchFormationPresets,
	fetchMatchDetailStrict,
	fetchPlayerStrict,
	fetchUpcomingPredictionsStrict,
	getApiErrorMessage
} from '$lib/api/football';

const unitDir = fileURLToPath(new URL('.', import.meta.url));
const tacticalBoardSource = readFileSync(
	resolve(unitDir, '../../src/lib/components/TacticalBoard.svelte'),
	'utf8'
);

const LEGACY_DEPARTED_PLAYERS = ['Zinchenko', 'Neto', 'Jorginho', 'Sterling'];

describe('API error normalization & strict contract wrappers', () => {
	it('defaults API_BASE to localhost:8000/api/v1 when PUBLIC_API_URL is unset', () => {
		expect(API_BASE).toBe('http://localhost:8000/api/v1');
	});

	it('getApiErrorMessage preserves ApiError status and detail or wraps TimeoutError/unknown errors', () => {
		expect(getApiErrorMessage(new ApiError(503, 'Service unavailable'), 'Fallback')).toEqual({
			detail: 'Service unavailable',
			status: 503
		});

		const timeoutErr = new DOMException('Timed out', 'TimeoutError');
		const timeoutResult = getApiErrorMessage(timeoutErr, 'Fallback');
		expect(timeoutResult.status).toBe(0);
		expect(timeoutResult.detail).toContain('timed out');

		expect(getApiErrorMessage('unexpected', 'Fallback msg')).toEqual({
			detail: 'Fallback msg',
			status: 0
		});
	});

	it('fetchMatchDetailStrict returns null on 404, payload on 200, and throws ApiError on 500 or network error', async () => {
		const mockNotFound = vi.fn<typeof fetch>().mockResolvedValue(new Response(null, { status: 404 }));
		await expect(fetchMatchDetailStrict('missing-id', mockNotFound)).resolves.toBeNull();

		const sampleMatch = {
			id: 'm_1',
			competition_id: 'PL',
			competition_name: 'Premier League',
			season_id: '2025-2026-PL',
			home_team_id: 'arsenal',
			home_team_name: 'Arsenal FC',
			away_team_id: 'chelsea',
			away_team_name: 'Chelsea FC',
			utc_date: '2026-04-12T15:30:00Z',
			status: 'FINISHED',
			source: 'football-data.org'
		};
		const mockOk = vi
			.fn<typeof fetch>()
			.mockResolvedValue(new Response(JSON.stringify(sampleMatch), { status: 200 }));
		await expect(fetchMatchDetailStrict('m_1', mockOk)).resolves.toEqual(sampleMatch);

		const mock500 = vi
			.fn<typeof fetch>()
			.mockResolvedValue(new Response(JSON.stringify({ detail: 'Database error' }), { status: 500 }));
		await expect(fetchMatchDetailStrict('m_1', mock500)).rejects.toMatchObject({
			name: 'ApiError',
			status: 500,
			detail: 'Database error',
			isNetworkError: false
		});

		const mockNetwork = vi.fn<typeof fetch>().mockRejectedValue(new TypeError('Failed to fetch'));
		await expect(fetchMatchDetailStrict('m_1', mockNetwork)).rejects.toMatchObject({
			name: 'ApiError',
			status: 0,
			isNetworkError: true
		});
	});

	it('fetchPlayerStrict returns null on 404 and throws ApiError on 503', async () => {
		const mock404 = vi.fn<typeof fetch>().mockResolvedValue(new Response(null, { status: 404 }));
		await expect(fetchPlayerStrict('unknown-gunner', mock404)).resolves.toBeNull();

		const mock503 = vi
			.fn<typeof fetch>()
			.mockResolvedValue(new Response(JSON.stringify({ detail: 'Upstream timeout' }), { status: 503 }));
		await expect(fetchPlayerStrict('ply_saka', mock503)).rejects.toMatchObject({
			name: 'ApiError',
			status: 503,
			detail: 'Upstream timeout'
		});
	});

	it('fetchUpcomingPredictionsStrict sends Authorization header and surfaces 500 errors strictly', async () => {
		const mockFetch = vi.fn<typeof fetch>().mockResolvedValue(
			new Response(JSON.stringify([]), {
				status: 200,
				headers: { 'Content-Type': 'application/json' }
			})
		);
		await expect(fetchUpcomingPredictionsStrict('user-1', 'jwt-token', mockFetch)).resolves.toEqual([]);
		const [calledUrl, calledInit] = mockFetch.mock.calls[0];
		expect(String(calledUrl)).toContain('/predictions/upcoming?user_id=user-1');
		expect((calledInit?.headers as Record<string, string>)['Authorization']).toBe('Bearer jwt-token');

		const mockFail = vi
			.fn<typeof fetch>()
			.mockResolvedValue(new Response(JSON.stringify({ detail: 'Predictor offline' }), { status: 502 }));
		await expect(fetchUpcomingPredictionsStrict(undefined, null, mockFail)).rejects.toMatchObject({
			name: 'ApiError',
			status: 502,
			detail: 'Predictor offline'
		});
	});
});

describe('Arsenal squad roster hygiene in client fallbacks', () => {
	it('local fallback formation presets exclude departed Arsenal players', async () => {
		const warnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});
		const fetchSpy = vi.spyOn(globalThis, 'fetch').mockRejectedValue(new Error('offline'));

		const presets = await fetchFormationPresets();
		expect(presets.length).toBeGreaterThanOrEqual(2);
		const presetNames = presets.flatMap((preset) => preset.players.map((p) => p.name));
		for (const departed of LEGACY_DEPARTED_PLAYERS) {
			expect(presetNames).not.toContain(departed);
		}
		expect(presetNames).toContain('Calafiori');
		expect(presetNames).toContain('Merino');

		fetchSpy.mockRestore();
		warnSpy.mockRestore();
	});

	it('TacticalBoard DEFAULT_BENCH_POOL excludes departed Arsenal players', () => {
		for (const departed of LEGACY_DEPARTED_PLAYERS) {
			expect(tacticalBoardSource).not.toContain(departed);
		}
		expect(tacticalBoardSource).toContain('Gyökeres');
		expect(tacticalBoardSource).toContain('Zubimendi');
	});
});
