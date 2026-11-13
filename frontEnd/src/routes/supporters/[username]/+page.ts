import { ApiError, fetchSupporterProfileStrict } from '$lib/api/football';
import { error } from '@sveltejs/kit';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params, fetch }) => {
	try {
		const supporterProfile = await fetchSupporterProfileStrict(params.username, fetch);
		if (!supporterProfile) {
			throw error(404, `Supporter @${params.username} not found`);
		}
		return { supporterProfile };
	} catch (err) {
		if (err instanceof ApiError) {
			const status = err.isNetworkError || err.status >= 500 || err.status === 0 ? 503 : err.status;
			throw error(status, err.detail);
		}
		throw err;
	}
};
