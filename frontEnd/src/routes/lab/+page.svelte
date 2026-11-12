<script lang="ts">
	import { CLUBS } from '$lib/stores/theme.svelte';
	import { ApiError, queryAnalytics, createInsight } from '$lib/api/football';
	import type { AnalyticsResponse, Insight } from '$lib/types/football';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	let mode = $state<'single' | 'comparison'>('single');
	let team1 = $state<string>('arsenal');
	let team2 = $state<string>('real-madrid');
	let metric = $state<string>('win_rate');
	let venue = $state<string>('all');
	let selectedSeason = $state<string>('all');

	let loading = $state(false);
	let result = $state<AnalyticsResponse | null>(null);
	let insights = $state<Insight[]>([]);
	let seasons = $derived(data.seasons || []);

	$effect(() => {
		mode = data.initialTeamIds.length > 1 ? 'comparison' : 'single';
		team1 = data.initialTeamIds[0] || 'arsenal';
		team2 = data.initialTeamIds[1] || 'real-madrid';
		metric = data.initialMetric || 'win_rate';
		venue = data.initialVenue || 'all';
		selectedSeason = data.activeSeasonId || 'all';
		result = data.initialResult;
		insights = data.insights || [];
	});

	let isModalOpen = $state(false);
	let insightTitle = $state('');
	let insightDesc = $state('');
	let isSavingInsight = $state(false);
	let modalError = $state<{ message: string; isAuth?: boolean } | null>(null);
	let toastMessage = $state<string | null>(null);
	let toastKind = $state<'success' | 'error'>('success');
	let toastNeedsLogin = $state(false);
	let toastTimer: ReturnType<typeof setTimeout> | null = null;

	let queryBtnLabel = $derived(loading ? 'Computing…' : 'Calculate analytics');
	let publishBtnLabel = $derived(isSavingInsight ? 'Publishing…' : 'Publish insight');
	let primaryClubLabel = $derived(mode === 'single' ? 'Club' : 'Club A');

	const clubList = Object.values(CLUBS);

	const metricsList = [
		{ id: 'win_rate', label: 'Win rate (%)' },
		{ id: 'goals_per_match', label: 'Goals per match' },
		{ id: 'points_per_game', label: 'Points per game (PPG)' },
		{ id: 'goal_difference', label: 'Goal difference' },
		{ id: 'clean_sheet_rate', label: 'Clean sheet rate (%)' },
		{ id: 'loss_rate', label: 'Loss rate (%)' }
	];

	async function runQuery() {
		loading = true;
		const team_ids = mode === 'single' ? [team1] : [team1, team2];
		try {
			result = await queryAnalytics({
				metric,
				team_ids,
				venue,
				season_id: selectedSeason !== 'all' ? selectedSeason : undefined
			});
			updateUrlState(team_ids);
		} finally {
			loading = false;
		}
	}

	function updateUrlState(team_ids: string[]) {
		if (typeof window !== 'undefined') {
			const url = new URL(window.location.href);
			url.searchParams.set('metric', metric);
			url.searchParams.set('teams', team_ids.join(','));
			url.searchParams.set('venue', venue);
			if (selectedSeason !== 'all') {
				url.searchParams.set('season', selectedSeason);
			} else {
				url.searchParams.delete('season');
			}
			window.history.replaceState({}, '', url.toString());
		}
	}

	function copyShareLink() {
		if (typeof window !== 'undefined') {
			navigator.clipboard.writeText(window.location.href);
			showToast('Reproducible analysis link copied to clipboard.');
		}
	}

	function openCreateModal() {
		if (!result || result.series.length === 0) return;
		if (!data.user || !data.session?.access_token) {
			showToast('Please sign in to publish Data Lab insights.', 'error', true);
			return;
		}
		modalError = null;
		const t1 = result.series[0];
		if (result.series.length === 1) {
			insightTitle = `${t1.team_name} ${getMetricLabel(metric)}: ${t1.metric_value} ${t1.unit} (${venue})`;
		} else {
			const t2 = result.series[1];
			insightTitle = `${t1.team_name} vs ${t2.team_name}: ${getMetricLabel(metric)} comparison`;
		}
		insightDesc = `Computed across eligible completed matches (venue filter: ${venue}).`;
		isModalOpen = true;
	}

	async function submitInsight() {
		if (!result || !insightTitle) return;
		if (!data.user || !data.session?.access_token) {
			modalError = { message: 'Please sign in to publish Data Lab insights.', isAuth: true };
			showToast('Please sign in to publish Data Lab insights.', 'error', true);
			return;
		}
		modalError = null;
		isSavingInsight = true;
		try {
			const team_ids = mode === 'single' ? [team1] : [team1, team2];
			const newInsight = await createInsight(
				{
					title: insightTitle,
					description: insightDesc,
					metric,
					team_ids,
					venue,
					chart_type: mode === 'single' ? 'bar' : 'comparison',
					author_name: data.profile?.display_name || data.user?.email?.split('@')[0] || 'Supporter',
					author_club_id: data.profile?.favorite_club_id || 'arsenal',
					snapshot: result
				},
				data.session?.access_token
			);

			if (newInsight) {
				insights = [newInsight, ...insights];
				isModalOpen = false;
				showToast('Insight published to the community feed.', 'success', false);
			}
		} catch (err) {
			const isAuth = err instanceof ApiError && err.status === 401;
			const msg = isAuth
				? 'Please sign in to publish Data Lab insights.'
				: err instanceof ApiError
					? err.detail
					: 'Could not publish insight. Please try again.';
			modalError = { message: msg, isAuth };
			showToast(msg, 'error', isAuth);
		} finally {
			isSavingInsight = false;
		}
	}

	function loadExistingInsight(ins: Insight) {
		metric = ins.metric;
		venue = ins.venue;
		if (ins.team_ids.length > 1) {
			mode = 'comparison';
			team1 = ins.team_ids[0];
			team2 = ins.team_ids[1];
		} else {
			mode = 'single';
			team1 = ins.team_ids[0];
		}
		result = ins.snapshot;
		updateUrlState(ins.team_ids);
		showToast(`Loaded insight: “${ins.title}”`, 'success', false);
	}

	function getMetricLabel(id: string): string {
		return metricsList.find((m) => m.id === id)?.label || id;
	}

	function showToast(msg: string, kind: 'success' | 'error' = 'success', needsLogin: boolean = false) {
		if (toastTimer) clearTimeout(toastTimer);
		toastMessage = msg;
		toastKind = kind;
		toastNeedsLogin = needsLogin;
		toastTimer = setTimeout(() => {
			toastMessage = null;
			toastNeedsLogin = false;
		}, 5000);
	}

	let maxMetricVal = $derived(
		result && result.series.length > 0
			? Math.max(...result.series.map((s) => Math.abs(s.metric_value)), 1)
			: 1
	);

	let deltaDiff = $derived.by(() => {
		if (!result || result.series.length < 2) return null;
		const s1 = result.series[0];
		const s2 = result.series[1];
		const diff = Math.round((s1.metric_value - s2.metric_value) * 10) / 10;
		if (diff === 0) return { leader: 'Tied', text: 'Equal performance' };
		const leaderName = diff > 0 ? s1.team_name : s2.team_name;
		return {
			leader: leaderName,
			text: `${leaderName} leads by ${Math.abs(diff)} ${s1.unit}`
		};
	});
</script>

<svelte:head>
	<title>The Data Lab | GUNNERS</title>
</svelte:head>

<div class="container py-12 space-y-12">
	<!-- Toast Notification -->
	{#if toastMessage}
		<div
			role={toastKind === 'error' ? 'alert' : 'status'}
			class="fixed bottom-6 right-6 z-50 bg-paper-2 border border-rule-2 px-4 py-3 rounded-card text-xs flex items-center gap-3 {toastKind === 'error' ? 'text-error' : 'text-success'}"
		>
			<span>{toastMessage}</span>
			{#if toastNeedsLogin}
				<a href="/login" class="underline text-ink font-semibold hover:text-accent">Sign in</a>
			{/if}
		</div>
	{/if}

	<!-- Header -->
	<div class="flex flex-col md:flex-row md:items-end justify-between gap-6 border-b-2 border-rule-2 pb-8">
		<div class="space-y-3">
			<h1>The Data Lab</h1>
			<p class="lead text-ink-2">
				Generate reproducible, explainable football statistics across the Mikel Arteta era and publish shareable insight snapshots.
			</p>
		</div>

		<!-- Action Bar -->
		<div class="flex items-center gap-3 flex-wrap">
			<a
				href="/lab/historical"
				class="h-10 px-4 rounded-card border border-rule bg-paper-2 hover:bg-paper-3 text-xs text-accent-2 font-semibold transition-colors inline-flex items-center"
			>
				StatsBomb 2D pitch
			</a>
			<button
				type="button"
				onclick={copyShareLink}
				class="h-10 px-4 rounded-card border border-rule bg-paper-2 hover:bg-paper-3 text-xs text-ink-2 hover:text-ink font-semibold transition-colors"
			>
				Share analysis link
			</button>
			{#if result && result.series.length > 0}
				<button
					type="button"
					onclick={openCreateModal}
					class="h-10 px-4 rounded-card bg-accent hover:opacity-95 text-xs text-accent-ink font-semibold transition-opacity"
				>
					Save as insight
				</button>
			{/if}
		</div>
	</div>

	<!-- Query Builder -->
	<section class="border-t border-rule pt-6 space-y-6">
		<!-- Mode Switcher -->
		<div class="flex items-center justify-between border-b border-rule pb-4 flex-wrap gap-4">
			<div class="flex items-center gap-2 text-xs">
				<button
					type="button"
					onclick={() => { mode = 'single'; runQuery(); }}
					class="h-9 px-3.5 rounded-card transition-colors font-semibold border {mode === 'single' ? 'bg-paper-3 text-ink border-rule-2' : 'bg-paper-2 text-ink-2 border-rule hover:text-ink'}"
				>
					Single club analysis
				</button>
				<button
					type="button"
					onclick={() => { mode = 'comparison'; runQuery(); }}
					class="h-9 px-3.5 rounded-card transition-colors font-semibold border {mode === 'comparison' ? 'bg-paper-3 text-ink border-rule-2' : 'bg-paper-2 text-ink-2 border-rule hover:text-ink'}"
				>
					Head-to-head comparison
				</button>
			</div>

			<span class="text-xs text-accent-2 font-semibold">
				Coverage: Mikel Arteta era (<span class="num font-outlier">2019</span> to present)
			</span>
		</div>

		<!-- Inputs Grid -->
		<div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-4">
			<div>
				<label for="primary-club" class="block text-xs font-semibold text-ink-2 mb-1.5">
					{primaryClubLabel}
				</label>
				<select
					id="primary-club"
					bind:value={team1}
					class="w-full h-10 bg-paper-2 border border-rule rounded-card px-3 text-xs text-ink"
				>
					{#each clubList as club}
						<option value={club.id}>{club.name}</option>
					{/each}
				</select>
			</div>

			{#if mode === 'comparison'}
				<div>
					<label for="secondary-club" class="block text-xs font-semibold text-ink-2 mb-1.5">
						Club B (compare)
					</label>
					<select
						id="secondary-club"
						bind:value={team2}
						class="w-full h-10 bg-paper-2 border border-rule rounded-card px-3 text-xs text-ink"
					>
						{#each clubList as club}
							<option value={club.id} disabled={club.id === team1}>{club.name}</option>
						{/each}
					</select>
				</div>
			{/if}

			<div>
				<label for="metric-select" class="block text-xs font-semibold text-ink-2 mb-1.5">
					Metric
				</label>
				<select
					id="metric-select"
					bind:value={metric}
					class="w-full h-10 bg-paper-2 border border-rule rounded-card px-3 text-xs text-ink"
				>
					{#each metricsList as m}
						<option value={m.id}>{m.label}</option>
					{/each}
				</select>
			</div>

			<div>
				<label for="venue-filter" class="block text-xs font-semibold text-ink-2 mb-1.5">
					Venue filter
				</label>
				<select
					id="venue-filter"
					bind:value={venue}
					class="w-full h-10 bg-paper-2 border border-rule rounded-card px-3 text-xs text-ink"
				>
					<option value="all">All matches</option>
					<option value="home">Home matches only</option>
					<option value="away">Away matches only</option>
				</select>
			</div>

			<div>
				<label for="season-filter" class="block text-xs font-semibold text-accent-2 mb-1.5">
					Arteta season
				</label>
				<select
					id="season-filter"
					bind:value={selectedSeason}
					onchange={runQuery}
					class="w-full h-10 bg-paper-2 border border-rule rounded-card px-3 text-xs text-accent-2 num font-outlier"
				>
					<option value="all">All (2019 to present)</option>
					{#each seasons as s}
						<option value={s.id}>{s.label}</option>
					{/each}
				</select>
			</div>

			<div class="flex items-end">
				<button
					type="button"
					onclick={runQuery}
					disabled={loading}
					class="w-full h-10 px-4 bg-accent hover:opacity-95 text-accent-ink font-semibold text-xs rounded-card transition-opacity"
				>
					{queryBtnLabel}
				</button>
			</div>
		</div>
	</section>

	<!-- Output Display -->
	{#if loading}
		<div class="py-16 text-muted text-sm">
			Computing verified analytics across eligible completed records…
		</div>
	{:else if result && result.series.length > 0}
		{#if mode === 'single'}
			{@const s = result.series[0]}
			<div class="grid grid-cols-1 lg:grid-cols-12 gap-10">
				<!-- Big Metric Hero -->
				<div class="lg:col-span-5 border-t-2 border-rule-2 pt-5 flex flex-col justify-between space-y-6">
					<div class="space-y-2">
						<span class="text-xs font-semibold text-ink-2">{s.team_name}</span>
						<div class="text-4xl font-bold text-ink num font-outlier">
							{s.metric_value} <span class="text-lg text-accent-2 font-normal">{s.unit}</span>
						</div>
						<p class="text-xs text-muted">Formula: {result.formula}</p>
					</div>

					<!-- Visual Record Bar -->
					<div class="pt-4 border-t border-rule space-y-2">
						<div class="flex items-center justify-between text-xs text-ink-2">
							<span>Sample: <strong class="text-ink num font-outlier">{s.matches_played}</strong> matches</span>
							<div class="flex gap-3 num font-outlier font-semibold">
								<span class="text-success">{s.wins}W</span>
								<span class="text-accent-2">{s.draws}D</span>
								<span class="text-error">{s.losses}L</span>
							</div>
						</div>
						{#if s.matches_played > 0}
							<div class="w-full h-2 rounded-card bg-paper-2 overflow-hidden flex">
								<div class="bg-success" style="width: {(s.wins / s.matches_played) * 100}%;" title="Wins"></div>
								<div class="bg-accent-2" style="width: {(s.draws / s.matches_played) * 100}%;" title="Draws"></div>
								<div class="bg-error" style="width: {(s.losses / s.matches_played) * 100}%;" title="Losses"></div>
							</div>
						{/if}
					</div>
				</div>

				<!-- Statistical Breakdown -->
				<div class="lg:col-span-7 border-t-2 border-rule-2 pt-5 flex flex-col justify-between space-y-6">
					<div class="space-y-4">
						<h2 class="text-lg font-bold text-ink">Performance breakdown</h2>
						<div class="grid grid-cols-2 sm:grid-cols-4 gap-6 border-t border-rule pt-4">
							<div>
								<span class="text-xs text-muted">Goals for</span>
								<div class="text-2xl font-bold text-ink mt-1 num font-outlier">{s.goals_for}</div>
							</div>
							<div>
								<span class="text-xs text-muted">Goals against</span>
								<div class="text-2xl font-bold text-ink mt-1 num font-outlier">{s.goals_against}</div>
							</div>
							<div>
								<span class="text-xs text-muted">Goal diff</span>
								<div class="text-2xl font-bold mt-1 num font-outlier {s.goal_difference >= 0 ? 'text-success' : 'text-error'}">
									{s.goal_difference > 0 ? `+${s.goal_difference}` : s.goal_difference}
								</div>
							</div>
							<div>
								<span class="text-xs text-muted">Clean sheets</span>
								<div class="text-2xl font-bold text-ink mt-1 num font-outlier">{s.clean_sheets || 0}</div>
							</div>
						</div>
					</div>

					<div class="pt-4 border-t border-rule text-xs text-muted flex flex-col sm:flex-row sm:items-center justify-between gap-2">
						<span>{result.disclaimer}</span>
						<span>Venue filter: <strong class="text-ink-2">{result.venue_filter}</strong></span>
					</div>
				</div>
			</div>
		{:else}
			<!-- Head-to-Head Comparison View -->
			{@const t1 = result.series[0]}
			{@const t2 = result.series[1]}

			<div class="space-y-8">
				{#if deltaDiff}
					<div class="border-y border-rule py-4 flex items-center justify-between flex-wrap gap-2 text-xs">
						<div class="flex items-center gap-2">
							<span class="text-muted">Result:</span>
							<span class="text-sm font-bold text-accent-2">{deltaDiff.text}</span>
						</div>
						<div class="text-muted">
							Comparing <strong class="text-ink">{t1.team_name}</strong> vs <strong class="text-ink">{t2.team_name}</strong> ({result.venue_filter} matches)
						</div>
					</div>
				{/if}

				<!-- Side-by-Side Stat Blocks -->
				<div class="grid grid-cols-1 md:grid-cols-2 gap-8">
					<div class="border-t-2 border-rule-2 pt-5 space-y-4">
						<div class="flex items-center justify-between">
							<h3 class="text-base font-bold text-ink">{t1.team_name}</h3>
							<span class="text-xs num font-outlier text-muted">{t1.matches_played} matches</span>
						</div>
						<div class="text-3xl font-bold num font-outlier text-ink">
							{t1.metric_value} <span class="text-base text-accent-2">{t1.unit}</span>
						</div>
						<div class="w-full bg-paper-2 h-2.5 rounded-card overflow-hidden">
							<div
								class="h-full bg-accent"
								style="width: {(Math.abs(t1.metric_value) / maxMetricVal) * 100}%;"
							></div>
						</div>
					</div>

					<div class="border-t-2 border-rule-2 pt-5 space-y-4">
						<div class="flex items-center justify-between">
							<h3 class="text-base font-bold text-ink">{t2.team_name}</h3>
							<span class="text-xs num font-outlier text-muted">{t2.matches_played} matches</span>
						</div>
						<div class="text-3xl font-bold num font-outlier text-ink">
							{t2.metric_value} <span class="text-base text-accent-2">{t2.unit}</span>
						</div>
						<div class="w-full bg-paper-2 h-2.5 rounded-card overflow-hidden">
							<div
								class="h-full bg-accent-2"
								style="width: {(Math.abs(t2.metric_value) / maxMetricVal) * 100}%;"
							></div>
						</div>
					</div>
				</div>

				<!-- Comparison Breakdown Table -->
				<div class="overflow-x-auto border-t border-rule">
					<table class="w-full text-xs text-left">
						<thead class="text-muted border-b border-rule">
							<tr>
								<th class="py-3 pr-4 font-semibold">Statistical metric</th>
								<th class="py-3 px-4 font-bold text-ink">{t1.team_name}</th>
								<th class="py-3 pl-4 font-bold text-ink">{t2.team_name}</th>
							</tr>
						</thead>
						<tbody class="divide-y divide-rule text-ink-2 num font-outlier">
							<tr>
								<td class="py-3 pr-4 font-body text-muted">Wins / draws / losses</td>
								<td class="py-3 px-4">{t1.wins}W / {t1.draws}D / {t1.losses}L</td>
								<td class="py-3 pl-4">{t2.wins}W / {t2.draws}D / {t2.losses}L</td>
							</tr>
							<tr>
								<td class="py-3 pr-4 font-body text-muted">Goals for / goals against</td>
								<td class="py-3 px-4">{t1.goals_for} GF / {t1.goals_against} GA</td>
								<td class="py-3 pl-4">{t2.goals_for} GF / {t2.goals_against} GA</td>
							</tr>
							<tr>
								<td class="py-3 pr-4 font-body text-muted">Goal difference</td>
								<td class="py-3 px-4 font-bold {t1.goal_difference >= 0 ? 'text-success' : 'text-error'}">
									{t1.goal_difference > 0 ? `+${t1.goal_difference}` : t1.goal_difference}
								</td>
								<td class="py-3 pl-4 font-bold {t2.goal_difference >= 0 ? 'text-success' : 'text-error'}">
									{t2.goal_difference > 0 ? `+${t2.goal_difference}` : t2.goal_difference}
								</td>
							</tr>
							<tr>
								<td class="py-3 pr-4 font-body text-muted">Clean sheets</td>
								<td class="py-3 px-4">{t1.clean_sheets || 0}</td>
								<td class="py-3 pl-4">{t2.clean_sheets || 0}</td>
							</tr>
							<tr>
								<td class="py-3 pr-4 font-body text-ink font-semibold">Selected metric ({getMetricLabel(metric)})</td>
								<td class="py-3 px-4 font-bold text-accent-2">{t1.metric_value} {t1.unit}</td>
								<td class="py-3 pl-4 font-bold text-accent-2">{t2.metric_value} {t2.unit}</td>
							</tr>
						</tbody>
					</table>
				</div>
			</div>
		{/if}
	{:else}
		<div class="py-12 border-t border-rule text-muted text-sm">
			No completed matches found matching the specified parameters.
		</div>
	{/if}

	<!-- Saved Insights Shelf -->
	<section class="border-t-2 border-rule-2 pt-8 space-y-6">
		<div class="space-y-1">
			<h2 class="text-xl font-bold text-ink">Recent shareable insights</h2>
			<p class="text-sm text-muted">Reproducible analysis snapshots published by Arsenal supporters.</p>
		</div>

		{#if insights.length === 0}
			<p class="text-sm text-muted py-4">No community insights saved yet. Publish the first one above.</p>
		{:else}
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
				{#each insights as ins}
					<article class="border-t border-rule pt-4 flex flex-col justify-between space-y-4">
						<div class="space-y-2">
							<div class="flex items-center justify-between gap-2 text-xs">
								<span class="text-accent-2 font-semibold">
									{getMetricLabel(ins.metric)}
								</span>
								<span class="text-muted num font-outlier">
									{new Date(ins.created_at).toLocaleDateString()}
								</span>
							</div>
							<h3 class="text-base font-bold text-ink leading-snug">{ins.title}</h3>
							{#if ins.description}
								<p class="text-sm text-ink-2 line-clamp-2">{ins.description}</p>
							{/if}
						</div>

						<div class="pt-3 border-t border-rule flex items-center justify-between text-xs">
							<span class="text-muted">By <strong class="text-ink-2">{ins.author_name}</strong></span>
							<button
								type="button"
								onclick={() => loadExistingInsight(ins)}
								class="font-semibold text-accent hover:text-ink transition-colors"
							>
								Open in Data Lab
							</button>
						</div>
					</article>
				{/each}
			</div>
		{/if}
	</section>

	<!-- Create Insight Modal -->
	{#if isModalOpen}
		<div class="fixed inset-0 z-50 bg-paper/85 flex items-center justify-center p-4">
			<div class="bg-paper-2 border-t-2 border-rule-2 max-w-lg w-full p-6 space-y-5">
				<div class="flex items-center justify-between border-b border-rule pb-3">
					<h3 class="text-base font-bold text-ink">Publish shareable insight</h3>
					<button
						type="button"
						onclick={() => (isModalOpen = false)}
						class="text-muted hover:text-ink text-xs font-semibold"
					>
						Close
					</button>
				</div>

				<div class="space-y-4 text-xs">
					<div>
						<label for="ins-title" class="block font-semibold text-ink-2 mb-1">Insight title</label>
						<input
							id="ins-title"
							type="text"
							bind:value={insightTitle}
							class="w-full h-10 bg-paper border border-rule rounded-card px-3 text-ink"
						/>
					</div>

					<div>
						<label for="ins-desc" class="block font-semibold text-ink-2 mb-1">Notes & description (optional)</label>
						<textarea
							id="ins-desc"
							rows="3"
							bind:value={insightDesc}
							class="w-full bg-paper border border-rule rounded-card p-3 text-ink"
						></textarea>
					</div>

					<div class="border-t border-rule pt-3 text-xs text-muted space-y-1">
						<p><strong class="text-ink-2">Metric:</strong> {getMetricLabel(metric)}</p>
						<p><strong class="text-ink-2">Venue filter:</strong> {venue}</p>
						<p>
							This insight stores the exact query parameters and current statistical snapshot as an immutable record.
						</p>
					</div>
				</div>

				<div class="flex items-center justify-end gap-3 pt-2">
					{#if modalError}
						<div role="alert" class="mr-auto text-xs text-error flex items-center gap-2">
							<span>{modalError.message}</span>
							{#if modalError.isAuth}
								<a href="/login" class="underline text-ink font-semibold hover:text-accent">Sign in</a>
							{/if}
						</div>
					{/if}
					<button
						type="button"
						onclick={() => (isModalOpen = false)}
						class="h-9 px-3 rounded-card text-xs font-semibold text-ink-2 hover:text-ink"
					>
						Cancel
					</button>
					<button
						type="button"
						onclick={submitInsight}
						disabled={isSavingInsight || !insightTitle}
						class="h-9 px-4 rounded-card text-xs font-semibold bg-accent hover:opacity-95 text-accent-ink transition-opacity"
					>
						{publishBtnLabel}
					</button>
				</div>
			</div>
		</div>
	{/if}
</div>
