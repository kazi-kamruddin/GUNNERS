import { ApiError, fetchMatchDetailStrict } from '$lib/api/football';
import { error } from '@sveltejs/kit';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params, fetch }) => {
	let match = null;
	try {
		match = await fetchMatchDetailStrict(params.id, fetch);
	} catch (err) {
		if (err instanceof ApiError) {
			const status = err.status === 0 || err.status >= 500 ? 503 : err.status;
			throw error(status, err.detail);
		}
		throw error(503, 'Arsenal match service is temporarily unavailable.');
	}

	if (!match) {
		throw error(404, 'Match dossier not found');
	}

	return { match };
};
