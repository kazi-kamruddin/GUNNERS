import { fail, redirect } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals }) => {
	// If already signed in, redirect to profile or home
	if (locals.user) {
		throw redirect(303, '/profile');
	}
	return {};
};

export const actions: Actions = {
	default: async ({ request, locals }) => {
		const formData = await request.formData();
		const email = formData.get('email')?.toString().trim();
		const password = formData.get('password')?.toString();
		const username = formData.get('username')?.toString().trim();
		const displayName = formData.get('display_name')?.toString().trim() || username;
		const favoriteClub = formData.get('favorite_club_id')?.toString().trim() || 'arsenal';

		if (!email || !password || !username) {
			return fail(400, {
				error: 'Email, password, and username are required.',
				email,
				username,
				displayName,
				favoriteClub
			});
		}

		if (password.length < 6) {
			return fail(400, {
				error: 'Password must be at least 6 characters long.',
				email,
				username,
				displayName,
				favoriteClub
			});
		}

		const { error } = await locals.supabase.auth.signUp({
			email,
			password,
			options: {
				data: {
					username,
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
				favoriteClub
			});
		}

		throw redirect(303, '/profile');
	}
};
