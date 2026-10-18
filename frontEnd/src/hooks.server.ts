import { createServerClient } from '@supabase/ssr';
import type { Handle } from '@sveltejs/kit/hooks';
import { SUPABASE_URL, SUPABASE_ANON_KEY } from '$lib/supabase';
import type { UserProfile } from './app';

export const handle: Handle = async ({ event, resolve }) => {
	event.locals.supabase = createServerClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
		cookies: {
			getAll: () => event.cookies.getAll(),
			setAll: (cookiesToSet) => {
				cookiesToSet.forEach(({ name, value, options }) => {
					event.cookies.set(name, value, { ...options, path: '/' });
				});
			}
		}
	});

	/**
	 * Safe session extraction as recommended by Supabase auth guidelines.
	 * Uses getUser() to validate authentication against Supabase server.
	 */
	event.locals.safeGetSession = async () => {
		try {
			const {
				data: { user },
				error
			} = await event.locals.supabase.auth.getUser();

			if (error || !user) {
				return { session: null, user: null };
			}

			const {
				data: { session }
			} = await event.locals.supabase.auth.getSession();

			return { session, user };
		} catch {
			return { session: null, user: null };
		}
	};

	const { session, user } = await event.locals.safeGetSession();
	event.locals.session = session;
	event.locals.user = user;

	if (user) {
		try {
			const { data: profile } = await event.locals.supabase
				.from('profiles')
				.select('*')
				.eq('id', user.id)
				.single();
			event.locals.profile = profile as UserProfile | null;
		} catch {
			event.locals.profile = null;
		}
	} else {
		event.locals.profile = null;
	}

	return resolve(event, {
		filterSerializedResponseHeaders(name: string) {
			return name === 'content-range' || name === 'x-supabase-api-version';
		}
	});
};
