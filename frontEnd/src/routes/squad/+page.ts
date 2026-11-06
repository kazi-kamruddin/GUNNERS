import { fetchSquad, fetchClubs } from '$lib/api/football';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ url }) => {
	const posParam = url.searchParams.get('position') || undefined;
	const compare1 = url.searchParams.get('compare1');
	const compare2 = url.searchParams.get('compare2');

	const [players, clubs] = await Promise.all([
		fetchSquad('arsenal', posParam),
		fetchClubs()
	]);

	return {
		players,
		clubs,
		activeClubId: 'arsenal',
		activePosition: posParam,
		initialCompare1: compare1,
		initialCompare2: compare2
	};
};
