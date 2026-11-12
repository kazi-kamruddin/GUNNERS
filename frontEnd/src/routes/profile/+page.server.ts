import { fail, redirect } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals }) => {
	if (!locals.user) {
		throw redirect(303, '/login');
	}

	// Fetch fresh profile data
	const { data: profile } = await locals.supabase
		.from('profiles')
		.select('*')
		.eq('id', locals.user.id)
		.single();

	return {
		user: locals.user,
		profile: profile ?? locals.profile
	};
};

export const actions: Actions = {
	updateProfile: async ({ request, locals }) => {
		if (!locals.user) {
			throw redirect(303, '/login');
		}

		const formData = await request.formData();
		const displayName = formData.get('display_name')?.toString().trim();
		const bio = formData.get('bio')?.toString().trim() ?? '';
		const favoriteClub = formData.get('favorite_club_id')?.toString().trim() ?? 'arsenal';
		const avatarUrlRaw = formData.get('avatar_url')?.toString().trim();

		if (!displayName) {
			return fail(400, { error: 'Display name cannot be empty.' });
		}

		const updatePayload: Record<string, string> = {
			display_name: displayName,
			bio,
			favorite_club_id: favoriteClub,
			updated_at: new Date().toISOString()
		};
		if (avatarUrlRaw !== undefined && avatarUrlRaw !== '') {
			updatePayload.avatar_url = avatarUrlRaw;
		}

		const { error } = await locals.supabase
			.from('profiles')
			.update(updatePayload)
			.eq('id', locals.user.id);

		if (error) {
			return fail(400, { error: error.message });
		}

		return { success: true };
	}
};
