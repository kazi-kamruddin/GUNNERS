import { fetchSupporterProfile } from '$lib/api/football';
import { error } from '@sveltejs/kit';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params }) => {
	const profile = await fetchSupporterProfile(params.username);
	if (!profile) {
		throw error(404, `Supporter @${params.username} not found`);
	}
	return { profile };
};
