import type { Session, SupabaseClient, User } from '@supabase/supabase-js';

export interface UserProfile {
	id: string;
	username: string;
	display_name: string;
	favorite_club_id: string;
	bio?: string;
	avatar_url?: string;
	created_at: string;
	updated_at: string;
}

declare global {
	namespace App {
		// interface Error {}
		interface Locals {
			supabase: SupabaseClient;
			safeGetSession: () => Promise<{ session: Session | null; user: User | null }>;
			session: Session | null;
			user: User | null;
			profile: UserProfile | null;
		}
		interface PageData {
			session: Session | null;
			user: User | null;
			profile: UserProfile | null;
		}
		// interface PageState {}
		// interface Platform {}
	}
}

export {};
