import { fetchPosts, fetchInsights } from '$lib/api/football';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ url, parent }) => {
	const parentData = await parent();
	const clubParam = url.searchParams.get('club') || 'global';

	const [posts, insights] = await Promise.all([
		fetchPosts(clubParam, parentData.user?.id),
		fetchInsights()
	]);

	return {
		initialPosts: posts,
		availableInsights: insights,
		initialClub: clubParam
	};
};
