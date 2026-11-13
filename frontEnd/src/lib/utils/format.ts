const METRIC_LABELS: Record<string, string> = {
	win_rate: 'Win Rate',
	goals_per_match: 'Goals per Match',
	clean_sheet_rate: 'Clean Sheet Rate',
	goal_difference: 'Goal Difference',
	points_per_match: 'Points per Match',
	shot_conversion: 'Shot Conversion',
	xg_per_match: 'xG per Match',
	xga_per_match: 'xGA per Match'
};

export function formatMetricLabel(metric: string | null | undefined): string {
	if (!metric) return 'Metric';
	const key = metric.trim().toLowerCase();
	if (METRIC_LABELS[key]) return METRIC_LABELS[key];
	return metric
		.trim()
		.replaceAll('_', ' ')
		.replace(/\b\w/g, (ch) => ch.toUpperCase());
}

export function formatMatchDate(iso: string | null | undefined): string {
	if (!iso) return 'TBD';
	const date = new Date(iso);
	if (Number.isNaN(date.getTime())) return 'TBD';
	return new Intl.DateTimeFormat(undefined, {
		weekday: 'short',
		day: 'numeric',
		month: 'short',
		year: 'numeric'
	}).format(date);
}

export function formatMatchTime(iso: string | null | undefined, includeTimezone = true): string {
	if (!iso) return 'TBD';
	const date = new Date(iso);
	if (Number.isNaN(date.getTime())) return 'TBD';
	return new Intl.DateTimeFormat(undefined, {
		hour: '2-digit',
		minute: '2-digit',
		...(includeTimezone ? { timeZoneName: 'short' } : {})
	}).format(date);
}

export function formatMatchDateTime(
	iso: string | null | undefined,
	opts: { includeTimezone?: boolean } = {}
): string {
	if (!iso) return 'TBD';
	const date = new Date(iso);
	if (Number.isNaN(date.getTime())) return 'TBD';
	return new Intl.DateTimeFormat(undefined, {
		day: 'numeric',
		month: 'short',
		year: 'numeric',
		hour: '2-digit',
		minute: '2-digit',
		...(opts.includeTimezone !== false ? { timeZoneName: 'short' } : {})
	}).format(date);
}
