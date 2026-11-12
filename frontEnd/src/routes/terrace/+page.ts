import { fetchPosts, fetchInsights, fetchTrendingTags, fetchTacticalBoards } from '$lib/api/football';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ url, parent }) => {
	const parentData = await parent();
	const clubParam = url.searchParams.get('club') || 'arsenal';
	const searchParam = url.searchParams.get('search') || undefined;
	const tagParam = url.searchParams.get('tag') || undefined;
	const accessToken = parentData.session?.access_token ?? null;

	const [posts, insights, trendingTags, tacticalBoards] = await Promise.all([
		fetchPosts(clubParam, parentData.user?.id, searchParam, tagParam, accessToken),
		fetchInsights(),
		fetchTrendingTags(),
		fetchTacticalBoards()
	]);

	return {
		user: parentData.user,
		profile: parentData.profile,
		initialPosts: posts,
		availableInsights: insights,
		availableTacticalBoards: tacticalBoards,
		initialClub: clubParam,
		initialSearch: searchParam || '',
		initialTag: tagParam || '',
		trendingTags
	};
};
