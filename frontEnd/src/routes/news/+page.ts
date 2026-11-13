import { fetchArsenalNewsResult } from '$lib/api/football';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ url, fetch }) => {
	const category = url.searchParams.get('category') || 'all';
	const tag = url.searchParams.get('tag') || 'all';
	const search = url.searchParams.get('search') || '';
	const res = await fetchArsenalNewsResult(
		{
			limit: 12,
			offset: 0,
			category,
			tag,
			search
		},
		false,
		fetch
	);

	return {
		category,
		tag,
		search,
		feed: res.data,
		apiError: res.error
	};
};
