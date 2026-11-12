import { fail, redirect } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';

function extractOwnedAvatarPath(url: string | null | undefined, userId: string): string | null {
	if (!url) return null;
	const marker = '/storage/v1/object/public/avatars/';
	const idx = url.indexOf(marker);
	if (idx === -1) return null;
	const path = decodeURIComponent(url.slice(idx + marker.length).split('?')[0]);
	return path.startsWith(`${userId}/`) ? path : null;
}

export const load: PageServerLoad = async ({ locals, url }) => {
	if (!locals.user) {
		throw redirect(303, `/login?next=${encodeURIComponent(url.pathname + url.search)}`);
	}

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
			throw redirect(303, '/login?next=%2Fprofile');
		}

		const formData = await request.formData();
		const displayName = formData.get('display_name')?.toString().trim();
		const bio = formData.get('bio')?.toString().trim() ?? '';
		const favoriteClub = formData.get('favorite_club_id')?.toString().trim() ?? 'arsenal';
		const avatarUrlRaw = formData.get('avatar_url')?.toString().trim();
		const removeAvatar = formData.get('remove_avatar')?.toString() === 'true';

		if (!displayName) {
			return fail(400, { error: 'Display name cannot be empty.' });
		}

		const updatePayload: Record<string, string | null> = {
			display_name: displayName,
			bio,
			favorite_club_id: favoriteClub,
			updated_at: new Date().toISOString()
		};
		if (removeAvatar) {
			updatePayload.avatar_url = null;
		} else if (avatarUrlRaw !== undefined && avatarUrlRaw !== '') {
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
	},
	removeAvatar: async ({ locals }) => {
		if (!locals.user) {
			throw redirect(303, '/login?next=%2Fprofile');
		}

		const { data: currentProfile } = await locals.supabase
			.from('profiles')
			.select('avatar_url')
			.eq('id', locals.user.id)
			.single();

		const existingPath = extractOwnedAvatarPath(currentProfile?.avatar_url, locals.user.id);

		const { error } = await locals.supabase
			.from('profiles')
			.update({
				avatar_url: null,
				updated_at: new Date().toISOString()
			})
			.eq('id', locals.user.id);

		if (error) {
			return fail(400, { error: error.message });
		}

		if (existingPath) {
			await locals.supabase.storage.from('avatars').remove([existingPath]).catch(() => {});
		}

		return { avatarRemoved: true };
	}
};
