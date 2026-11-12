import { fetchPlayer } from '$lib/api/football';
import { error } from '@sveltejs/kit';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params }) => {
	const player = await fetchPlayer(params.id);
	if (!player) {
		throw error(404, 'Squad player dossier not found');
	}
	return { player };
};
