import {
	fetchFormationPresets,
	fetchSquadResult,
	fetchTacticalBoardsResult
} from '$lib/api/football';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ url, parent, fetch }) => {
	const parentData = await parent();
	const viewingClub = url.searchParams.get('club') || parentData.profile?.favorite_club_id || 'arsenal';
	const accessToken = parentData.session?.access_token ?? null;

	const [presets, squadResult, boardsResult] = await Promise.all([
		fetchFormationPresets(),
		fetchSquadResult(viewingClub, undefined, fetch),
		fetchTacticalBoardsResult(viewingClub, accessToken, fetch)
	]);

	return {
		presets,
		squad: squadResult.data,
		squadError: squadResult.error,
		communityBoards: boardsResult.data,
		boardsError: boardsResult.error,
		viewingClub
	};
};
