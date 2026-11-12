<script lang="ts">
	import type { MatchLineupPlayer } from '$lib/types/football';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	const match = $derived(data.match);
	const homeName = $derived(match.home_team_name);
	const awayName = $derived(match.away_team_name);
	const goalscorers = $derived(match.goalscorers ?? []);
	const homeLineup = $derived(match.lineups?.home ?? null);
	const awayLineup = $derived(match.lineups?.away ?? null);
	const highlights = $derived(match.highlights ?? []);

	const statusLabel = $derived.by(() => {
		if (match.status === 'FINISHED') return 'Full time';
		if (match.status === 'IN_PLAY' || match.status === 'LIVE') return 'Live';
		if (match.status === 'POSTPONED') return 'Postponed';
		return 'Scheduled';
	});

	function formatUtcKickoff(isoStr: string): string {
		try {
			const d = new Date(isoStr);
			return (
				d.toLocaleString(undefined, {
					weekday: 'short',
					month: 'short',
					day: 'numeric',
					year: 'numeric',
					hour: '2-digit',
					minute: '2-digit',
					timeZone: 'UTC'
				}) + ' UTC'
			);
		} catch {
			return isoStr;
		}
	}

	function formatLineupPlayer(entry: string | MatchLineupPlayer): { name: string; meta: string } {
		if (typeof entry === 'string') {
			return { name: entry, meta: '' };
		}
		const parts: string[] = [];
		if (entry.number !== undefined && entry.number !== null) {
			parts.push(`#${entry.number}`);
		}
		if (entry.position) {
			parts.push(entry.position);
		}
		return { name: entry.name, meta: parts.join(' ') };
	}
</script>

<svelte:head>
	<title>{match.home_team_name} vs {match.away_team_name} | Match Center | GUNNERS</title>
</svelte:head>

<div class="container py-12 space-y-12 max-w-5xl">
	<!-- Breadcrumb & Quick Nav -->
	<div class="flex items-center justify-between gap-4 flex-wrap">
		<a
			href="/matches"
			class="inline-flex items-center h-9 px-3 rounded-card border border-rule bg-paper-2 hover:bg-paper-3 text-xs font-semibold text-ink-2 hover:text-ink transition-colors"
		>
			Back to match ledger
		</a>

		<div class="flex items-center gap-2.5 flex-wrap">
			<a
				href="/predictions"
				class="inline-flex items-center h-9 px-3.5 rounded-card bg-accent text-accent-ink hover:opacity-90 text-xs font-semibold transition-opacity"
			>
				Match predictor
			</a>
			<a
				href="/terrace"
				class="inline-flex items-center h-9 px-3.5 rounded-card border border-rule bg-paper-2 hover:bg-paper-3 text-xs font-semibold text-ink transition-colors"
			>
				Terrace debrief
			</a>
			<a
				href="/board"
				class="inline-flex items-center h-9 px-3.5 rounded-card border border-rule bg-paper-2 hover:bg-paper-3 text-xs font-semibold text-ink transition-colors"
			>
				Dugout tactics
			</a>
		</div>
	</div>

	<!-- Scoreboard Header -->
	<section class="bg-paper-2 border-t-2 border-rule-2 p-6 sm:p-8 space-y-6">
		<div class="flex items-center justify-between flex-wrap gap-3 text-xs border-b border-rule pb-4">
			<div class="flex items-center gap-3 flex-wrap text-muted">
				<span class="font-semibold text-ink">{match.competition_name || match.competition_id || 'Competition'}</span>
				{#if match.matchday}
					<span class="num font-outlier">Matchday {match.matchday}</span>
				{/if}
				<span class="num font-outlier">{match.season_id}</span>
			</div>

			<span
				role="status"
				class="px-2.5 py-1 rounded-card border border-rule bg-paper-3 text-xs font-semibold {match.status === 'FINISHED' ? 'text-success' : 'text-accent-2'}"
			>
				{statusLabel}
			</span>
		</div>

		<div class="grid grid-cols-1 md:grid-cols-12 items-center gap-6 py-2">
			<!-- Home Club -->
			<div class="md:col-span-4 flex items-center md:justify-end gap-3 md:text-right min-w-0">
				{#if match.home_team_crest}
					<img
						src={match.home_team_crest}
						alt="{match.home_team_name} crest"
						width="48"
						height="48"
						class="w-12 h-12 object-contain shrink-0 md:order-2"
					/>
				{/if}
				<div class="min-w-0 md:order-1">
					<h1 class="text-2xl sm:text-3xl font-bold text-ink break-words min-w-0">{homeName}</h1>
					<span class="text-xs text-muted">Home</span>
				</div>
			</div>

			<!-- Scoreline -->
			<div class="md:col-span-4 flex flex-col items-center justify-center text-center">
				{#if match.status === 'FINISHED' && match.home_score !== null && match.home_score !== undefined}
					<div class="num font-display font-bold text-4xl sm:text-5xl text-ink px-5 py-2 rounded-card bg-paper border border-rule">
						{match.home_score} : {match.away_score}
					</div>
				{:else}
					<div class="font-display font-bold text-2xl text-accent-2 px-5 py-2 rounded-card bg-paper border border-rule">
						vs
					</div>
				{/if}
			</div>

			<!-- Away Club -->
			<div class="md:col-span-4 flex items-center justify-start gap-3 text-left min-w-0">
				{#if match.away_team_crest}
					<img
						src={match.away_team_crest}
						alt="{match.away_team_name} crest"
						width="48"
						height="48"
						class="w-12 h-12 object-contain shrink-0"
					/>
				{/if}
				<div class="min-w-0">
					<h1 class="text-2xl sm:text-3xl font-bold text-ink break-words min-w-0">{awayName}</h1>
					<span class="text-xs text-muted">Away</span>
				</div>
			</div>
		</div>

		<!-- Match Metadata Bar -->
		<dl class="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-4 border-t border-rule text-xs">
			<div>
				<dt class="text-muted">Kickoff (UTC)</dt>
				<dd class="text-ink font-semibold num font-outlier mt-0.5">{formatUtcKickoff(match.utc_date)}</dd>
			</div>
			<div>
				<dt class="text-muted">Venue</dt>
				<dd class="text-ink font-semibold mt-0.5">{match.venue || 'Confirmed venue pending'}</dd>
			</div>
			<div>
				<dt class="text-muted">Match official</dt>
				<dd class="text-ink font-semibold mt-0.5">{match.referee || 'Appointed by competition'}</dd>
			</div>
		</dl>
	</section>

	<!-- Goalscorers Timeline -->
	<section class="border-t-2 border-rule-2 pt-8 space-y-5">
		<div class="flex items-end justify-between border-b border-rule pb-3">
			<h2 class="text-xl font-bold text-ink">Goalscorers timeline</h2>
			<span class="text-xs num font-outlier text-muted">{goalscorers.length} events</span>
		</div>

		{#if goalscorers.length === 0}
			<p class="text-sm text-muted py-4">
				{match.status === 'FINISHED'
					? 'No goal events recorded for this fixture.'
					: 'Goal events will appear here after kickoff.'}
			</p>
		{:else}
			<ol class="divide-y divide-rule border-y border-rule">
				{#each goalscorers as goal}
					<li class="py-3.5 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-sm">
						<div class="flex items-center gap-4 min-w-0">
							<span class="num font-outlier font-semibold text-accent min-w-[44px]">
								{goal.minute}'
							</span>
							<div class="min-w-0">
								<span class="font-semibold text-ink">{goal.player}</span>
								{#if goal.type}
									<span class="ml-2 text-xs text-accent-2">({goal.type})</span>
								{/if}
								{#if goal.assist}
									<span class="block text-xs text-muted">Assist: {goal.assist}</span>
								{/if}
							</div>
						</div>
						<span class="text-xs font-semibold text-ink-2 shrink-0">{goal.team}</span>
					</li>
				{/each}
			</ol>
		{/if}
	</section>

	<!-- Side-by-Side Lineups & Formations -->
	<section class="border-t-2 border-rule-2 pt-8 space-y-6">
		<div class="border-b border-rule pb-3">
			<h2 class="text-xl font-bold text-ink">Starting lineups & formations</h2>
		</div>

		{#if !homeLineup && !awayLineup}
			<p class="text-sm text-muted py-4">
				Confirmed starting XIs are released approximately 60 minutes prior to kickoff.
			</p>
		{:else}
			<div class="grid grid-cols-1 md:grid-cols-2 gap-8">
				<!-- Home XI -->
				<div class="bg-paper-2 border-t-2 border-rule-2 p-5 space-y-4">
					<div class="flex items-baseline justify-between border-b border-rule pb-3 gap-2">
						<h3 class="text-base font-bold text-ink">{match.home_team_name}</h3>
						{#if homeLineup?.formation}
							<span class="num font-outlier text-xs font-semibold text-accent-2">
								Formation {homeLineup.formation}
							</span>
						{/if}
					</div>

					{#if homeLineup?.xi && homeLineup.xi.length > 0}
						<ol class="divide-y divide-rule text-sm">
							{#each homeLineup.xi as player, idx}
								{@const info = formatLineupPlayer(player)}
								<li class="py-2 flex items-center justify-between gap-3">
									<div class="flex items-center gap-3 min-w-0">
										<span class="num font-outlier text-xs text-muted w-5">{idx + 1}</span>
										<span class="text-ink font-medium truncate">{info.name}</span>
									</div>
									{#if info.meta}
										<span class="num font-outlier text-xs text-muted shrink-0">{info.meta}</span>
									{/if}
								</li>
							{/each}
						</ol>
					{:else}
						<p class="text-xs text-muted">Lineup unavailable.</p>
					{/if}
				</div>

				<!-- Away XI -->
				<div class="bg-paper-2 border-t-2 border-rule-2 p-5 space-y-4">
					<div class="flex items-baseline justify-between border-b border-rule pb-3 gap-2">
						<h3 class="text-base font-bold text-ink">{match.away_team_name}</h3>
						{#if awayLineup?.formation}
							<span class="num font-outlier text-xs font-semibold text-accent-2">
								Formation {awayLineup.formation}
							</span>
						{/if}
					</div>

					{#if awayLineup?.xi && awayLineup.xi.length > 0}
						<ol class="divide-y divide-rule text-sm">
							{#each awayLineup.xi as player, idx}
								{@const info = formatLineupPlayer(player)}
								<li class="py-2 flex items-center justify-between gap-3">
									<div class="flex items-center gap-3 min-w-0">
										<span class="num font-outlier text-xs text-muted w-5">{idx + 1}</span>
										<span class="text-ink font-medium truncate">{info.name}</span>
									</div>
									{#if info.meta}
										<span class="num font-outlier text-xs text-muted shrink-0">{info.meta}</span>
									{/if}
								</li>
							{/each}
						</ol>
					{:else}
						<p class="text-xs text-muted">Lineup unavailable.</p>
					{/if}
				</div>
			</div>
		{/if}
	</section>

	<!-- Highlights & Coverage -->
	<section class="border-t-2 border-rule-2 pt-8 space-y-5">
		<div class="flex items-end justify-between border-b border-rule pb-3">
			<h2 class="text-xl font-bold text-ink">Match highlights & reports</h2>
			<span class="text-xs num font-outlier text-muted">{highlights.length} links</span>
		</div>

		{#if highlights.length === 0}
			<p class="text-sm text-muted py-4">
				No external highlight dispatches linked for this match yet.
			</p>
		{:else}
			<div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
				{#each highlights as hl}
					<a
						href={hl.url}
						target="_blank"
						rel="noopener noreferrer"
						class="p-4 rounded-card border border-rule bg-paper-2 hover:bg-paper-3 flex items-center justify-between gap-4 transition-colors"
					>
						<div class="min-w-0 space-y-1">
							<span class="block text-sm font-semibold text-ink truncate">{hl.label}</span>
							{#if hl.source}
								<span class="block text-xs text-muted">{hl.source}</span>
							{/if}
						</div>
						<span class="text-xs font-semibold text-accent shrink-0">Watch</span>
					</a>
				{/each}
			</div>
		{/if}
	</section>
</div>
