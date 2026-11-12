import { ApiError, fetchPlayerStrict } from '$lib/api/football';
import { error } from '@sveltejs/kit';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params, fetch }) => {
	let player = null;
	try {
		player = await fetchPlayerStrict(params.id, fetch);
	} catch (err) {
		if (err instanceof ApiError) {
			const status = err.status === 0 || err.status >= 500 ? 503 : err.status;
			throw error(status, err.detail);
		}
		throw error(503, 'Arsenal squad service is temporarily unavailable.');
	}

	if (!player) {
		throw error(404, 'Squad player dossier not found');
	}

	return { player };
};
