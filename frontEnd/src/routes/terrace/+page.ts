import { fetchPostsResult, fetchInsights, fetchTrendingTags, fetchTacticalBoards } from '$lib/api/football';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ url, parent, fetch }) => {
	const parentData = await parent();
	const clubParam = url.searchParams.get('club') || 'arsenal';
	const searchParam = url.searchParams.get('search') || undefined;
	const tagParam = url.searchParams.get('tag') || undefined;
	const accessToken = parentData.session?.access_token ?? null;

	const [postsResult, insights, trendingTags, tacticalBoards] = await Promise.all([
		fetchPostsResult(clubParam, parentData.user?.id, searchParam, tagParam, accessToken, fetch),
		fetchInsights(),
		fetchTrendingTags(),
		fetchTacticalBoards(undefined, accessToken)
	]);

	return {
		user: parentData.user,
		profile: parentData.profile,
		initialPosts: postsResult.data,
		postsError: postsResult.error,
		availableInsights: insights,
		availableTacticalBoards: tacticalBoards,
		initialClub: clubParam,
		initialSearch: searchParam || '',
		initialTag: tagParam || '',
		trendingTags
	};
};
