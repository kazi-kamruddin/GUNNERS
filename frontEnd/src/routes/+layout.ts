import { createBrowserClient, createServerClient, isBrowser } from '@supabase/ssr';
import { SUPABASE_URL, SUPABASE_ANON_KEY } from '$lib/supabase';
import type { LayoutLoad } from './$types';

export const load: LayoutLoad = async ({ data, depends, fetch }) => {
	depends('supabase:auth');

	if (!isBrowser()) {
		const supabase = createServerClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
			global: { fetch },
			cookies: {
				getAll() {
					return data.cookies;
				}
			}
		});

		return {
			supabase,
			session: data.session,
			user: data.user,
			profile: data.profile
		};
	}

	const supabase = createBrowserClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
		global: { fetch }
	});

	const {
		data: { user },
		error: userError
	} = await supabase.auth.getUser();

	if (userError || !user) {
		return {
			supabase,
			session: null,
			user: null,
			profile: null
		};
	}

	const {
		data: { session }
	} = await supabase.auth.getSession();

	return {
		supabase,
		session: session ?? data.session,
		user,
		profile: data.profile
	};
};
