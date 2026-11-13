import { fail, redirect } from '@sveltejs/kit';
import { getSafeRedirectPath } from '$lib/utils/redirect';
import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals, url }) => {
	const next = getSafeRedirectPath(url.searchParams.get('next'), '/profile');
	if (locals.user) {
		throw redirect(303, next);
	}
	return { next };
};

export const actions: Actions = {
	default: async ({ request, locals, url }) => {
		const formData = await request.formData();
		const email = formData.get('email')?.toString().trim();
		const password = formData.get('password')?.toString();
		const username = formData.get('username')?.toString().trim();
		const displayName = formData.get('display_name')?.toString().trim() || username;
		const favoriteClub = formData.get('favorite_club_id')?.toString().trim() || 'arsenal';
		const safeNext = getSafeRedirectPath(
			formData.get('next')?.toString() ?? url.searchParams.get('next'),
			'/profile'
		);

		if (!email || !password || !username) {
			return fail(400, {
				error: 'Email, password, and username are required.',
				email,
				username,
				displayName,
				favoriteClub,
				next: safeNext
			});
		}

		const normalizedUsername = username.replace(/[^a-zA-Z0-9_]/g, '').toLowerCase();
		if (normalizedUsername.length < 3) {
			return fail(400, {
				error: 'Username must contain at least 3 letters, numbers, or underscores.',
				email,
				username,
				displayName,
				favoriteClub,
				next: safeNext
			});
		}

		if (password.length < 6) {
			return fail(400, {
				error: 'Password must be at least 6 characters long.',
				email,
				username,
				displayName,
				favoriteClub,
				next: safeNext
			});
		}

		const callbackUrl = new URL('/auth/callback', url.origin);
		if (safeNext !== '/profile') {
			callbackUrl.searchParams.set('next', safeNext);
		}

		const { data, error } = await locals.supabase.auth.signUp({
			email,
			password,
			options: {
				emailRedirectTo: callbackUrl.toString(),
				data: {
					username: normalizedUsername,
					display_name: displayName,
					favorite_club_id: favoriteClub
				}
			}
		});

		if (error) {
			return fail(400, {
				error: error.message,
				email,
				username,
				displayName,
				favoriteClub,
				next: safeNext
			});
		}

		if (data.user && !data.session) {
			return {
				needsEmailVerification: true,
				email,
				next: safeNext
			};
		}

		throw redirect(303, safeNext);
	}
};
