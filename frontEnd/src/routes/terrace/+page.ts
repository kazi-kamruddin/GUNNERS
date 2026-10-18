import { fetchPosts, fetchInsights, fetchTrendingTags } from '$lib/api/football';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ url, parent }) => {
	const parentData = await parent();
	const clubParam = url.searchParams.get('club') || 'global';
	const searchParam = url.searchParams.get('search') || undefined;
	const tagParam = url.searchParams.get('tag') || undefined;

	const [posts, insights, trendingTags] = await Promise.all([
		fetchPosts(clubParam, parentData.user?.id, searchParam, tagParam),
		fetchInsights(),
		fetchTrendingTags()
	]);

	return {
		initialPosts: posts,
		availableInsights: insights,
		initialClub: clubParam,
		initialSearch: searchParam || '',
		initialTag: tagParam || '',
		trendingTags
	};
};
