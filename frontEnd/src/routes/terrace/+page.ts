import { fetchPosts, fetchInsights, fetchTrendingTags, fetchTacticalBoards } from '$lib/api/football';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ url, parent }) => {
	const parentData = await parent();
	const clubParam = url.searchParams.get('club') || 'global';
	const searchParam = url.searchParams.get('search') || undefined;
	const tagParam = url.searchParams.get('tag') || undefined;

	const [posts, insights, trendingTags, tacticalBoards] = await Promise.all([
		fetchPosts(clubParam, parentData.user?.id, searchParam, tagParam),
		fetchInsights(),
		fetchTrendingTags(),
		fetchTacticalBoards()
	]);

	return {
		initialPosts: posts,
		availableInsights: insights,
		availableTacticalBoards: tacticalBoards,
		initialClub: clubParam,
		initialSearch: searchParam || '',
		initialTag: tagParam || '',
		trendingTags
	};
};
