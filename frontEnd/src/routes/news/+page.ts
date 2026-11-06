import { fetchArsenalNews } from '$lib/api/football';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ url }) => {
	const category = url.searchParams.get('category') || 'all';
	const feed = await fetchArsenalNews(category);
	return {
		category,
		feed
	};
};
