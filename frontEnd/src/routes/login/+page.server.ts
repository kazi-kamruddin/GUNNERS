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
		const safeNext = getSafeRedirectPath(
			formData.get('next')?.toString() ?? url.searchParams.get('next'),
			'/profile'
		);

		if (!email || !password) {
			return fail(400, {
				error: 'Email and password are required.',
				email,
				next: safeNext
			});
		}

		const { error } = await locals.supabase.auth.signInWithPassword({
			email,
			password
		});

		if (error) {
			return fail(400, {
				error: error.message,
				email,
				next: safeNext
			});
		}

		throw redirect(303, safeNext);
	}
};
