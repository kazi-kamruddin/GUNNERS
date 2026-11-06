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

export const ARSENAL_THEME: ClubTheme = {
	id: 'arsenal',
	slug: 'arsenal',
	name: 'Arsenal FC',
	short_name: 'Arsenal',
	primary_color: '#EF0107',
	secondary_color: '#FFFFFF',
	accent_color: '#9C824A',
	league: 'Premier League',
	country: 'England'
};

export const CLUBS: Record<string, ClubTheme> = {
	arsenal: ARSENAL_THEME,
	chelsea: { id: 'chelsea', slug: 'chelsea', name: 'Chelsea FC', short_name: 'Chelsea', primary_color: '#034694', secondary_color: '#FFFFFF', accent_color: '#6A7AB5', league: 'Premier League', country: 'England' },
	tottenham: { id: 'tottenham', slug: 'tottenham', name: 'Tottenham Hotspur', short_name: 'Tottenham', primary_color: '#132257', secondary_color: '#FFFFFF', accent_color: '#A0A0A0', league: 'Premier League', country: 'England' },
	'manchester-city': { id: 'manchester-city', slug: 'manchester-city', name: 'Manchester City', short_name: 'Man City', primary_color: '#6CABDD', secondary_color: '#1C2C5B', accent_color: '#D4AF37', league: 'Premier League', country: 'England' },
	liverpool: { id: 'liverpool', slug: 'liverpool', name: 'Liverpool FC', short_name: 'Liverpool', primary_color: '#C8102E', secondary_color: '#00B2A9', accent_color: '#F6EB61', league: 'Premier League', country: 'England' },
	'real-madrid': { id: 'real-madrid', slug: 'real-madrid', name: 'Real Madrid CF', short_name: 'Real Madrid', primary_color: '#00529F', secondary_color: '#FFFFFF', accent_color: '#EEB028', league: 'La Liga', country: 'Spain' },
	barcelona: { id: 'barcelona', slug: 'barcelona', name: 'FC Barcelona', short_name: 'Barcelona', primary_color: '#A50044', secondary_color: '#004D98', accent_color: '#EDBB00', league: 'La Liga', country: 'Spain' },
	milan: { id: 'milan', slug: 'milan', name: 'AC Milan', short_name: 'AC Milan', primary_color: '#FB090B', secondary_color: '#000000', accent_color: '#C0C0C0', league: 'Serie A', country: 'Italy' }
};

class ThemeState {
	viewingClubId = 'arsenal';
	favoriteClubId = 'arsenal';
	currentTheme = ARSENAL_THEME;

	setViewingClub(_clubId?: string) {
		this.applyCssTokens();
	}

	setFavoriteClub(_clubId?: string) {
		this.applyCssTokens();
	}

	applyCssTokens() {
		if (!isBrowser()) return;
		const root = document.documentElement;
		root.style.setProperty('--club-primary', ARSENAL_THEME.primary_color);
		root.style.setProperty('--club-secondary', ARSENAL_THEME.secondary_color);
		root.style.setProperty('--club-accent', ARSENAL_THEME.accent_color);
	}
}

export const themeState = new ThemeState();
