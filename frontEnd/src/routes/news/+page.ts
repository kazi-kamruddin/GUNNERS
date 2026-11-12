import { fetchArsenalNews } from '$lib/api/football';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ url }) => {
	const category = url.searchParams.get('category') || 'all';
	const tag = url.searchParams.get('tag') || 'all';
	const search = url.searchParams.get('search') || '';
	const feed = await fetchArsenalNews({
		limit: 12,
		offset: 0,
		category,
		tag,
		search
	});
	return {
		category,
		tag,
		search,
		feed
	};
};
