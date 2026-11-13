import { redirect } from '@sveltejs/kit';
import { getSafeRedirectPath } from '$lib/utils/redirect';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = async ({ url, locals }) => {
	const safeNext = getSafeRedirectPath(url.searchParams.get('next'), '/profile');
	const nextQuery = safeNext !== '/profile' ? `&next=${encodeURIComponent(safeNext)}` : '';

	const oauthError = url.searchParams.get('error_description') || url.searchParams.get('error');
	if (oauthError) {
		throw redirect(303, `/login?error=${encodeURIComponent(oauthError)}${nextQuery}`);
	}

	const code = url.searchParams.get('code');
	if (!code) {
		throw redirect(
			303,
			`/login?error=${encodeURIComponent('Missing authentication code.')}${nextQuery}`
		);
	}

	const { error } = await locals.supabase.auth.exchangeCodeForSession(code);
	if (error) {
		throw redirect(303, `/login?error=${encodeURIComponent(error.message)}${nextQuery}`);
	}

	throw redirect(303, safeNext);
};
