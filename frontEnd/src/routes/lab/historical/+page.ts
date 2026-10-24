import { fetchHistoricalMatches, fetchHistoricalMatchDetail } from '$lib/api/football';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ url }) => {
	const matches = await fetchHistoricalMatches();
	const requestedId = url.searchParams.get('match') || (matches.length > 0 ? matches[0].id : 'hist_ars_barca_2011');
	const detail = await fetchHistoricalMatchDetail(requestedId);

	return {
		matches,
		activeMatchId: requestedId,
		detail
	};
};
