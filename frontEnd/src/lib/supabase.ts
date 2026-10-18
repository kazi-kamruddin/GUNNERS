import { createBrowserClient, createServerClient, isBrowser } from '@supabase/ssr';
import type { SupabaseClient } from '@supabase/supabase-js';

export const SUPABASE_URL = (import.meta.env.PUBLIC_SUPABASE_URL as string) || 'https://mock.supabase.co';
export const SUPABASE_ANON_KEY = (import.meta.env.PUBLIC_SUPABASE_ANON_KEY as string) || 'mock-anon-key';

let browserClient: SupabaseClient | null = null;

export function getSupabaseBrowserClient(): SupabaseClient {
	if (!isBrowser()) {
		return createBrowserClient(SUPABASE_URL, SUPABASE_ANON_KEY);
	}

	if (!browserClient) {
		browserClient = createBrowserClient(SUPABASE_URL, SUPABASE_ANON_KEY);
	}

	return browserClient;
}
