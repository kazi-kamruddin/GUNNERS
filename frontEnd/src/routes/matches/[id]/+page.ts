import { fetchMatchDetail } from '$lib/api/football';
import { error } from '@sveltejs/kit';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params }) => {
	const match = await fetchMatchDetail(params.id);
	if (!match) {
		throw error(404, 'Match dossier not found');
	}
	return { match };
};
