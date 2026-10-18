import { fetchSquad, fetchClubs } from '$lib/api/football';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ url }) => {
	const clubParam = url.searchParams.get('club') || 'arsenal';
	const posParam = url.searchParams.get('position') || undefined;
	const compare1 = url.searchParams.get('compare1');
	const compare2 = url.searchParams.get('compare2');

	const [players, clubs] = await Promise.all([
		fetchSquad(clubParam, posParam),
		fetchClubs()
	]);

	return {
		players,
		clubs,
		activeClubId: clubParam,
		activePosition: posParam,
		initialCompare1: compare1,
		initialCompare2: compare2
	};
};
