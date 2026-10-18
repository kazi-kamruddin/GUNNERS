import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ locals: { session, user, profile }, cookies }) => {
	return {
		session,
		user,
		profile,
		cookies: cookies.getAll()
	};
};
