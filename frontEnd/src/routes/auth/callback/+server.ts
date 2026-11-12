import { redirect } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = async ({ url, locals }) => {
	const rawNext = url.searchParams.get('next') ?? '/profile';
	const safeNext =
		rawNext.startsWith('/') && !rawNext.startsWith('//') && !rawNext.includes('\\')
			? rawNext
			: '/profile';

	const oauthError = url.searchParams.get('error_description') || url.searchParams.get('error');
	if (oauthError) {
		throw redirect(303, `/login?error=${encodeURIComponent(oauthError)}`);
	}

	const code = url.searchParams.get('code');
	if (!code) {
		throw redirect(303, `/login?error=${encodeURIComponent('Missing authentication code.')}`);
	}

	const { error } = await locals.supabase.auth.exchangeCodeForSession(code);
	if (error) {
		throw redirect(303, `/login?error=${encodeURIComponent(error.message)}`);
	}

	throw redirect(303, safeNext);
};
