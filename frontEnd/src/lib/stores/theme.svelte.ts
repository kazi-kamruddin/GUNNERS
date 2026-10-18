import { isBrowser } from '@supabase/ssr';

export interface ClubTheme {
	id: string;
	slug: string;
	name: string;
	short_name: string;
	primary_color: string;
	secondary_color: string;
	accent_color: string;
	league: string;
	country: string;
}

export const CLUBS: Record<string, ClubTheme> = {
	arsenal: {
		id: 'arsenal',
		slug: 'arsenal',
		name: 'Arsenal FC',
		short_name: 'Arsenal',
		primary_color: '#EF0107',
		secondary_color: '#FFFFFF',
		accent_color: '#9C824A',
		league: 'Premier League',
		country: 'England'
	},
	'real-madrid': {
		id: 'real-madrid',
		slug: 'real-madrid',
		name: 'Real Madrid CF',
		short_name: 'Real Madrid',
		primary_color: '#00529F',
		secondary_color: '#FFFFFF',
		accent_color: '#EEB028',
		league: 'La Liga',
		country: 'Spain'
	},
	barcelona: {
		id: 'barcelona',
		slug: 'barcelona',
		name: 'FC Barcelona',
		short_name: 'Barcelona',
		primary_color: '#A50044',
		secondary_color: '#004D98',
		accent_color: '#EDBB00',
		league: 'La Liga',
		country: 'Spain'
	},
	milan: {
		id: 'milan',
		slug: 'milan',
		name: 'AC Milan',
		short_name: 'AC Milan',
		primary_color: '#FB090B',
		secondary_color: '#000000',
		accent_color: '#C0C0C0',
		league: 'Serie A',
		country: 'Italy'
	}
};

class ThemeState {
	viewingClubId = $state<string>('arsenal');
	favoriteClubId = $state<string>('arsenal');

	currentTheme = $derived(CLUBS[this.viewingClubId] || CLUBS.arsenal);

	setViewingClub(clubId: string) {
		if (CLUBS[clubId]) {
			this.viewingClubId = clubId;
			this.applyCssTokens();
		}
	}

	setFavoriteClub(clubId: string) {
		if (CLUBS[clubId]) {
			this.favoriteClubId = clubId;
			// By default, set viewing club to favorite club when initialized
			this.setViewingClub(clubId);
		}
	}

	applyCssTokens() {
		if (!isBrowser()) return;
		const root = document.documentElement;
		const theme = this.currentTheme;
		root.style.setProperty('--club-primary', theme.primary_color);
		root.style.setProperty('--club-secondary', theme.secondary_color);
		root.style.setProperty('--club-accent', theme.accent_color);
	}
}

export const themeState = new ThemeState();
