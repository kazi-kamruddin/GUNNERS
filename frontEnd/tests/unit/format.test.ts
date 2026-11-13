import { describe, expect, it } from 'vitest';
import {
	formatMatchDate,
	formatMatchDateTime,
	formatMatchTime,
	formatMetricLabel
} from '$lib/utils/format';

describe('formatMetricLabel', () => {
	it('maps known analytics metrics to editorial labels', () => {
		expect(formatMetricLabel('win_rate')).toBe('Win Rate');
		expect(formatMetricLabel('goals_per_match')).toBe('Goals per Match');
		expect(formatMetricLabel('clean_sheet_rate')).toBe('Clean Sheet Rate');
		expect(formatMetricLabel('xg_per_match')).toBe('xG per Match');
		expect(formatMetricLabel('xga_per_match')).toBe('xGA per Match');
	});

	it('title-cases unknown snake_case metrics and falls back cleanly on empty input', () => {
		expect(formatMetricLabel('progressive_passes_per_90')).toBe('Progressive Passes Per 90');
		expect(formatMetricLabel('')).toBe('Metric');
		expect(formatMetricLabel(null)).toBe('Metric');
		expect(formatMetricLabel(undefined)).toBe('Metric');
	});
});

describe('match date & time formatters', () => {
	const iso = '2026-04-12T15:30:00Z';

	it('returns TBD for empty or invalid date inputs', () => {
		expect(formatMatchDate(null)).toBe('TBD');
		expect(formatMatchDate('')).toBe('TBD');
		expect(formatMatchDate('not-a-date')).toBe('TBD');
		expect(formatMatchTime(undefined)).toBe('TBD');
		expect(formatMatchTime('invalid')).toBe('TBD');
		expect(formatMatchDateTime(null)).toBe('TBD');
		expect(formatMatchDateTime('invalid-iso')).toBe('TBD');
	});

	it('formats valid ISO timestamps with year/time and respects includeTimezone option', () => {
		const dateText = formatMatchDate(iso);
		expect(dateText).not.toBe('TBD');
		expect(dateText).toContain('2026');

		const timeWithTz = formatMatchTime(iso, true);
		const timeWithoutTz = formatMatchTime(iso, false);
		expect(timeWithTz).not.toBe('TBD');
		expect(timeWithoutTz).not.toBe('TBD');
		expect(timeWithTz.length).toBeGreaterThanOrEqual(timeWithoutTz.length);

		const dtWithTz = formatMatchDateTime(iso);
		const dtWithoutTz = formatMatchDateTime(iso, { includeTimezone: false });
		expect(dtWithTz).toContain('2026');
		expect(dtWithoutTz).toContain('2026');
		expect(dtWithTz.length).toBeGreaterThanOrEqual(dtWithoutTz.length);
	});
});
