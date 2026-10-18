import { fetchMatchSummary, fetchInsights, fetchPosts, fetchSyncStatus } from '$lib/api/football';
import type { PageLoad } from './$types';

export const load: PageLoad = async () => {
	const [summary, insights, posts, syncStatus] = await Promise.all([
		fetchMatchSummary('arsenal'),
		fetchInsights(),
		fetchPosts('global'),
		fetchSyncStatus()
	]);

	return {
		summary,
		insights: insights.slice(0, 3),
		posts: posts.slice(0, 4),
		syncStatus
	};
};
