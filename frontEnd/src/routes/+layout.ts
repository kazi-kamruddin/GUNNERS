import { createBrowserClient, createServerClient, isBrowser } from '@supabase/ssr';
import { SUPABASE_URL, SUPABASE_ANON_KEY } from '$lib/supabase';
import type { LayoutLoad } from './$types';

export const load: LayoutLoad = async ({ data, depends, fetch }) => {
	depends('supabase:auth');

	const supabase = isBrowser()
		? createBrowserClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
				global: { fetch }
			})
		: createServerClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
				global: { fetch },
				cookies: {
					getAll() {
						return data.cookies;
					}
				}
			});

	const {
		data: { session }
	} = await supabase.auth.getSession();

	const {
		data: { user }
	} = await supabase.auth.getUser();

	return {
		supabase,
		session: session ?? data.session,
		user: user ?? data.user,
		profile: data.profile
	};
};
