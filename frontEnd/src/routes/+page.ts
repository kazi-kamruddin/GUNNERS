import {
	fetchMatchSummary,
	fetchInsights,
	fetchPosts,
	fetchSyncStatus,
	queryAnalytics
} from '$lib/api/football';
import type { AnalyticsResponse } from '$lib/types/football';
import type { PageLoad } from './$types';

function formatBenchmark(res: AnalyticsResponse | null): string {
	const item = res?.series?.[0];
	if (!item || item.matches_played === 0) return '—';
	const val = Number.isFinite(item.metric_value) ? item.metric_value : 0;
	if (item.unit === '%') return `${val.toFixed(1)}%`;
	return val.toFixed(2);
}

export const load: PageLoad = async () => {
	const [summary, insights, posts, syncStatus, homeWinRes, cleanSheetRes, goalsPerMatchRes] =
		await Promise.all([
			fetchMatchSummary('arsenal'),
			fetchInsights('arsenal'),
			fetchPosts('arsenal'),
			fetchSyncStatus(),
			queryAnalytics({ metric: 'win_rate', team_ids: ['arsenal'], venue: 'home' }),
			queryAnalytics({ metric: 'clean_sheet_rate', team_ids: ['arsenal'], venue: 'all' }),
			queryAnalytics({ metric: 'goals_per_match', team_ids: ['arsenal'], venue: 'all' })
		]);

	return {
		summary,
		insights: insights.slice(0, 3),
		posts: posts.slice(0, 4),
		syncStatus,
		benchmarks: {
			homeWinRate: formatBenchmark(homeWinRes),
			cleanSheetRate: formatBenchmark(cleanSheetRes),
			goalsPerMatch: formatBenchmark(goalsPerMatchRes)
		}
	};
};
