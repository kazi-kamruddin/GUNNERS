import {
	fetchMatchSummaryResult,
	fetchPostsResult,
	queryAnalytics
} from '$lib/api/football';
import type { AnalyticsResponse } from '$lib/types/football';
import type { PageLoad } from './$types';

function formatBenchmark(res: AnalyticsResponse | null): string {
	const item = res?.series?.[0];
	if (!item || item.matches_played === 0) return 'N/A';
	const val = Number.isFinite(item.metric_value) ? item.metric_value : 0;
	if (item.unit === '%') return `${val.toFixed(1)}%`;
	return val.toFixed(2);
}

function formatSamples(res: AnalyticsResponse | null): number {
	return res?.series?.[0]?.matches_played ?? 0;
}

export const load: PageLoad = async ({ fetch }) => {
	const [summaryRes, postsRes, homeWinRes, cleanSheetRes, goalsPerMatchRes] = await Promise.all([
		fetchMatchSummaryResult('arsenal', fetch),
		fetchPostsResult('arsenal', undefined, undefined, undefined, undefined, fetch),
		queryAnalytics({ metric: 'win_rate', team_ids: ['arsenal'], venue: 'home' }),
		queryAnalytics({ metric: 'clean_sheet_rate', team_ids: ['arsenal'], venue: 'all' }),
		queryAnalytics({ metric: 'goals_per_match', team_ids: ['arsenal'], venue: 'all' })
	]);

	const benchmarksUnavailable = !homeWinRes && !cleanSheetRes && !goalsPerMatchRes;

	return {
		summary: summaryRes.data,
		summaryError: summaryRes.error,
		posts: (postsRes.data ?? []).slice(0, 4),
		postsError: postsRes.error,
		benchmarksUnavailable,
		benchmarks: {
			homeWinRate: formatBenchmark(homeWinRes),
			homeWinSamples: formatSamples(homeWinRes),
			cleanSheetRate: formatBenchmark(cleanSheetRes),
			cleanSheetSamples: formatSamples(cleanSheetRes),
			goalsPerMatch: formatBenchmark(goalsPerMatchRes),
			goalsPerMatchSamples: formatSamples(goalsPerMatchRes)
		}
	};
};
