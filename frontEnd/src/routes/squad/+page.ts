import { fetchSquadResult } from '$lib/api/football';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ url, fetch }) => {
	const posParam = url.searchParams.get('position') || 'all';
	const compare1 = url.searchParams.get('compare1');
	const compare2 = url.searchParams.get('compare2');

	const squadRes = await fetchSquadResult('arsenal', posParam !== 'all' ? posParam : undefined, fetch);

	return {
		players: squadRes.data,
		squadError: squadRes.error,
		activeClubId: 'arsenal',
		activePosition: posParam,
		initialCompare1: compare1,
		initialCompare2: compare2
	};
};
