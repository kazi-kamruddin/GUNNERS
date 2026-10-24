import { fetchFormationPresets, fetchSquad, fetchTacticalBoards } from '$lib/api/football';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ url, parent }) => {
	const parentData = await parent();
	const viewingClub = url.searchParams.get('club') || parentData.profile?.favorite_club_id || 'arsenal';

	const [presets, squad, communityBoards] = await Promise.all([
		fetchFormationPresets(),
		fetchSquad(viewingClub),
		fetchTacticalBoards(viewingClub)
	]);

	return {
		presets,
		squad,
		communityBoards,
		viewingClub
	};
};
