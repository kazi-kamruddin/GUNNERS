import {
	ApiError,
	fetchHistoricalMatchesResult,
	fetchHistoricalMatchDetailStrict
} from '$lib/api/football';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ url, fetch }) => {
	const matchesResult = await fetchHistoricalMatchesResult(fetch);
	const matches = matchesResult.data;
	const requestedId =
		url.searchParams.get('match') ||
		(matches.length > 0 ? matches[0].id : 'hist_ars_barca_2011');

	let detail = null;
	let detailError: string | null = null;
	try {
		detail = await fetchHistoricalMatchDetailStrict(requestedId, fetch);
		if (!detail && !matchesResult.error) {
			detailError = 'Requested historical fixture telemetry was not found.';
		}
	} catch (err) {
		detailError =
			err instanceof ApiError
				? err.detail
				: 'Unable to reach historical match telemetry service.';
	}

	return {
		matches,
		matchesError: matchesResult.error,
		activeMatchId: requestedId,
		detail,
		detailError
	};
};
