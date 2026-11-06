import { fetchInsights, queryAnalytics, fetchSeasons } from '$lib/api/football';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ url }) => {
	const metric = url.searchParams.get('metric') || 'win_rate';
	const teamsParam = url.searchParams.get('teams');
	const team_ids = teamsParam ? teamsParam.split(',').filter(Boolean) : ['arsenal'];
	const venue = url.searchParams.get('venue') || 'all';
	const seasonId = url.searchParams.get('season') || undefined;

	const [insights, initialResult, seasons] = await Promise.all([
		fetchInsights(),
		queryAnalytics({
			metric,
			team_ids,
			venue,
			season_id: seasonId
		}),
		fetchSeasons()
	]);

	return {
		initialMetric: metric,
		initialTeamIds: team_ids,
		initialVenue: venue,
		initialResult,
		insights,
		seasons,
		activeSeasonId: seasonId || 'all'
	};
};
