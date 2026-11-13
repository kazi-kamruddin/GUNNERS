<script lang="ts">
	import { invalidateAll } from '$app/navigation';
	import StateBanner from '$lib/components/StateBanner.svelte';
	import { formatMatchDateTime } from '$lib/utils/format';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	let summary = $derived(data.summary);
	let retrying = $state(false);

	async function handleRetry() {
		retrying = true;
		try {
			await invalidateAll();
		} finally {
			retrying = false;
		}
	}
</script>

<svelte:head>
	<title>GUNNERS | Arsenal FC Fan & Tactical Intelligence Platform</title>
</svelte:head>

<div class="container py-12 space-y-20">
	<!-- Stage Hero: Headline + Signature Matchday Ledger -->
	<section class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start border-b border-rule pb-16">
		<div class="lg:col-span-7 space-y-6 pt-2">
			<h1 class="text-ink">Victoria Concordia Crescit.</h1>
			<p class="lead text-ink-2">
				Arsenal tactical intelligence, Arteta era match records, and supporter debates.
			</p>
			<div class="flex flex-wrap items-center gap-3 pt-2">
				<a
					href="/news"
					class="inline-flex items-center min-h-[44px] px-5 rounded-card bg-accent text-accent-ink hover:opacity-90 font-semibold text-sm transition-opacity whitespace-nowrap"
				>
					Read The Armory
				</a>
				<a
					href="/board"
					class="inline-flex items-center min-h-[44px] px-4 rounded-card border border-rule bg-paper-2 hover:bg-paper-3 text-sm font-semibold text-ink transition-colors whitespace-nowrap"
				>
					Open The Dugout
				</a>
				<a
					href="/terrace"
					class="inline-flex items-center min-h-[44px] px-4 rounded-card border border-rule bg-paper-2 hover:bg-paper-3 text-sm font-semibold text-ink transition-colors whitespace-nowrap"
				>
					Join The Terrace
				</a>
				<a
					href="/squad"
					class="inline-flex items-center min-h-[44px] px-4 rounded-card text-sm font-semibold text-ink-2 hover:text-ink transition-colors whitespace-nowrap"
				>
					View first-team squad
				</a>
			</div>
		</div>

		<!-- Signature: Live Matchday Ledger in Hero -->
		<div class="lg:col-span-5 bg-paper-2 border-t-2 border-rule-2 p-6 space-y-6">
			<div class="flex items-baseline justify-between border-b border-rule pb-3 gap-4">
				<h2 class="text-lg font-display font-bold text-ink card-headline">Emirates matchday ledger</h2>
				<a
					href="/matches"
					class="inline-flex items-center min-h-[44px] text-sm font-semibold text-accent-text hover:underline whitespace-nowrap"
				>
					Full schedule
				</a>
			</div>

			{#if data.summaryError && !summary}
				<StateBanner
					variant="error"
					title="Live matchday ledger unavailable"
					message={data.summaryError}
					busy={retrying}
					onretry={handleRetry}
				/>
			{:else}
				<!-- Next Fixture Row -->
				<div class="border-b border-rule pb-5">
					{#if summary?.next_fixture}
						<a
							href="/matches/{encodeURIComponent(summary.next_fixture.id)}"
							class="group block space-y-2 rounded-card hover:bg-paper-3 p-2 -m-2 transition-colors"
						>
							<div class="flex items-center justify-between gap-2 text-xs text-muted">
								<span>Next fixture ({summary.next_fixture.competition_name || 'Premier League'})</span>
								<time class="num">{formatMatchDateTime(summary.next_fixture.utc_date)}</time>
							</div>
							<div class="flex items-baseline justify-between gap-3 pt-1">
								<span class="font-semibold text-ink group-hover:text-accent-text transition-colors text-base truncate">{summary.next_fixture.home_team_name}</span>
								<span class="text-xs text-muted shrink-0">vs</span>
								<span class="font-semibold text-ink group-hover:text-accent-text transition-colors text-base truncate text-right">{summary.next_fixture.away_team_name}</span>
							</div>
							<div class="flex items-center justify-between gap-2 text-xs text-muted">
								<span class="truncate">{summary.next_fixture.venue || 'Emirates Stadium'}</span>
								<span class="text-accent-text font-semibold group-hover:underline shrink-0">Match center</span>
							</div>
						</a>
					{:else}
						<div class="space-y-2">
							<div class="flex items-center justify-between text-xs text-muted">
								<span>Next fixture (Premier League)</span>
								<span>Scheduled</span>
							</div>
							<p class="text-sm text-muted py-2">No upcoming matches scheduled.</p>
						</div>
					{/if}
				</div>

				<!-- Latest Result Row -->
				<div>
					{#if summary?.last_result}
						<a
							href="/matches/{encodeURIComponent(summary.last_result.id)}"
							class="group block space-y-2 rounded-card hover:bg-paper-3 p-2 -m-2 transition-colors"
						>
							<div class="flex items-center justify-between gap-2 text-xs text-muted">
								<span>Latest result ({summary.last_result.competition_name || 'Premier League'})</span>
								<time class="num">{formatMatchDateTime(summary.last_result.utc_date)}</time>
							</div>
							<div class="flex items-baseline justify-between gap-3 pt-1">
								<span class="font-semibold text-ink group-hover:text-accent-text transition-colors text-base truncate">{summary.last_result.home_team_name}</span>
								<span class="num font-outlier font-semibold text-xl text-ink shrink-0">
									{summary.last_result.home_score ?? 0} : {summary.last_result.away_score ?? 0}
								</span>
								<span class="font-semibold text-ink group-hover:text-accent-text transition-colors text-base truncate text-right">{summary.last_result.away_team_name}</span>
							</div>
							<div class="flex items-center justify-between gap-2 text-xs text-muted">
								<span class="truncate">{summary.last_result.venue || 'Emirates Stadium'}</span>
								<span class="text-accent-text font-semibold group-hover:underline shrink-0">Match center</span>
							</div>
						</a>
					{:else}
						<div class="space-y-2">
							<div class="flex items-center justify-between text-xs text-muted">
								<span>Latest result (Premier League)</span>
								<span></span>
							</div>
							<p class="text-sm text-muted py-2">No completed results recorded.</p>
						</div>
					{/if}
				</div>

				<!-- Form & Tallies -->
				<div class="pt-4 border-t border-rule flex flex-wrap items-center justify-between gap-4 text-xs text-muted">
					<div class="flex items-center gap-3">
						<span class="num">Completed: <strong class="text-ink font-semibold">{summary?.total_completed ?? 0}</strong></span>
						<span class="num">Scheduled: <strong class="text-ink font-semibold">{summary?.total_scheduled ?? 0}</strong></span>
					</div>
					<div class="flex items-center gap-1.5">
						<span>Last 5:</span>
						{#if summary?.recent_form && summary.recent_form.length > 0}
							{#each summary.recent_form as item, idx (idx)}
								<span
									class="num w-6 h-6 rounded-card inline-flex items-center justify-center text-xs font-semibold border border-rule bg-paper-3 {item === 'W' ? 'text-success' : item === 'D' ? 'text-accent-2' : 'text-error'}"
								>
									{item}
								</span>
							{/each}
						{:else}
							<span class="num text-muted">None</span>
						{/if}
					</div>
				</div>
			{/if}
		</div>
	</section>

	<!-- Editorial Desks Index -->
	<section class="space-y-8">
		<div class="flex flex-col sm:flex-row sm:items-end justify-between gap-4 border-b-2 border-rule-2 pb-4">
			<h2>Four desks, one club</h2>
			<p class="text-sm text-muted">Direct access to Arsenal journalism, tactical boards, supporter discussions, and verified match telemetry.</p>
		</div>

		<div class="grid grid-cols-1 md:grid-cols-2 gap-8">
			<article class="border-t border-rule pt-5 flex flex-col justify-between space-y-4">
				<div class="space-y-2">
					<h3 class="text-ink"><a href="/news" class="hover:text-accent-text transition-colors">The Armory</a></h3>
					<p class="text-sm text-ink-2">
						Live news aggregation from Pain in the Arsenal, Arseblog, BBC Sport, Reddit r/Gunners, and Daily Cannon with automated player and tactical tags.
					</p>
				</div>
				<div>
					<a href="/news" class="inline-flex items-center min-h-[44px] text-sm font-semibold text-accent-text hover:underline">Read latest articles</a>
				</div>
			</article>

			<article class="border-t border-rule pt-5 flex flex-col justify-between space-y-4">
				<div class="space-y-2">
					<h3 class="text-ink"><a href="/board" class="hover:text-accent-text transition-colors">The Dugout</a></h3>
					<p class="text-sm text-ink-2">
						Interactive pitch with starting XI and reserve bench pool. Switch between formation grid and free-roam movement with PNG lineup export.
					</p>
				</div>
				<div>
					<a href="/board" class="inline-flex items-center min-h-[44px] text-sm font-semibold text-accent-text hover:underline">Build and export lineup</a>
				</div>
			</article>

			<article class="border-t border-rule pt-5 flex flex-col justify-between space-y-4">
				<div class="space-y-2">
					<h3 class="text-ink"><a href="/terrace" class="hover:text-accent-text transition-colors">The Terrace</a></h3>
					<p class="text-sm text-ink-2">
						Supporter community feed with matchday photo sharing, attached tactical blueprints, Data Lab insights, and post cheering.
					</p>
				</div>
				<div>
					<a href="/terrace" class="inline-flex items-center min-h-[44px] text-sm font-semibold text-accent-text hover:underline">Join match discussions</a>
				</div>
			</article>

			<article class="border-t border-rule pt-5 flex flex-col justify-between space-y-4">
				<div class="space-y-2">
					<h3 class="text-ink"><a href="/lab" class="hover:text-accent-text transition-colors">The Data Lab</a></h3>
					<p class="text-sm text-ink-2">
						Emirates home and away form across the Mikel Arteta timeline, player statistical breakdowns, and reproducible queries.
					</p>
				</div>
				<div>
					<a href="/lab" class="inline-flex items-center min-h-[44px] text-sm font-semibold text-accent-text hover:underline">Explore Arsenal metrics</a>
				</div>
			</article>
		</div>
	</section>

	<!-- Data Lab Telemetry Benchmarks -->
	<section class="bg-paper-2 border-t-2 border-rule-2 p-6 sm:p-8 space-y-6">
		<div class="flex flex-col md:flex-row md:items-end justify-between gap-4">
			<div class="space-y-1">
				<h2 class="card-headline">Arsenal campaign benchmarks</h2>
				<p class="text-sm text-ink-2">
					Examine Emirates win rate, clean sheet ratio, and goals per match in the Data Lab query workbench.
				</p>
			</div>
			<a
				href="/lab?teams=arsenal"
				class="inline-flex items-center min-h-[44px] px-4 rounded-card border border-rule bg-paper-3 hover:bg-paper text-sm font-semibold text-ink transition-colors whitespace-nowrap self-start md:self-auto"
			>
				Open full analytics engine
			</a>
		</div>

		{#if data.benchmarksUnavailable}
			<StateBanner
				variant="warning"
				title="Live campaign benchmarks unavailable"
				message="The analytics service could not be reached. Open Data Lab or retry to refresh benchmark ratios."
				busy={retrying}
				onretry={handleRetry}
			/>
		{/if}

		<div class="grid grid-cols-1 md:grid-cols-3 gap-8 pt-4 border-t border-rule">
			<a
				href="/lab?metric=win_rate&teams=arsenal&venue=home"
				class="group block space-y-1"
			>
				<div class="num font-display font-bold text-3xl text-ink group-hover:text-accent-text transition-colors">{data.benchmarks.homeWinRate}</div>
				<div class="text-sm font-semibold text-ink-2">Emirates home win rate</div>
				<p class="text-xs text-muted num">
					{data.benchmarks.homeWinSamples > 0
						? `Across ${data.benchmarks.homeWinSamples} completed home matches`
						: 'Inspect home dominance query in Data Lab'}
				</p>
			</a>

			<a
				href="/lab?metric=clean_sheet_rate&teams=arsenal&venue=all"
				class="group block space-y-1 md:border-l md:border-rule md:pl-8"
			>
				<div class="num font-display font-bold text-3xl text-ink group-hover:text-accent-text transition-colors">{data.benchmarks.cleanSheetRate}</div>
				<div class="text-sm font-semibold text-ink-2">Clean sheet rate</div>
				<p class="text-xs text-muted num">
					{data.benchmarks.cleanSheetSamples > 0
						? `Across ${data.benchmarks.cleanSheetSamples} completed matches`
						: 'Inspect defensive shutout ratio across venues'}
				</p>
			</a>

			<a
				href="/lab?metric=goals_per_match&teams=arsenal&venue=all"
				class="group block space-y-1 md:border-l md:border-rule md:pl-8"
			>
				<div class="num font-display font-bold text-3xl text-ink group-hover:text-accent-text transition-colors">{data.benchmarks.goalsPerMatch}</div>
				<div class="text-sm font-semibold text-ink-2">Goals per match</div>
				<p class="text-xs text-muted num">
					{data.benchmarks.goalsPerMatchSamples > 0
						? `Across ${data.benchmarks.goalsPerMatchSamples} completed matches`
						: 'Inspect attacking output per 90 minutes'}
				</p>
			</a>
		</div>
	</section>

	<!-- The Terrace Pulse -->
	<section class="space-y-6">
		<div class="flex flex-wrap items-baseline justify-between gap-4 border-b-2 border-rule-2 pb-4">
			<div class="space-y-1">
				<h2>The Terrace pulse</h2>
				<p class="text-sm text-muted">Live tactical debriefs from the Emirates supporter community.</p>
			</div>
			<a href="/terrace" class="inline-flex items-center min-h-[44px] text-sm font-semibold text-accent-text hover:underline whitespace-nowrap">
				Visit The Terrace
			</a>
		</div>

		{#if data.postsError}
			<StateBanner
				variant="error"
				title="Terrace dispatches unavailable"
				message={data.postsError}
				busy={retrying}
				onretry={handleRetry}
			/>
		{:else}
			<div class="grid grid-cols-1 md:grid-cols-2 gap-8">
				{#if data.posts && data.posts.length > 0}
					{#each data.posts.slice(0, 4) as post (post.id)}
						<article class="border-t border-rule pt-5 flex flex-col justify-between space-y-4">
							<div class="space-y-3">
								<div class="flex items-center justify-between gap-2">
									<div class="flex items-baseline gap-2 min-w-0">
										<h3 class="text-base font-semibold text-ink truncate">{post.author_name}</h3>
										<span class="text-xs text-muted shrink-0">Arsenal supporter</span>
									</div>
									<a
										href="/messages?recipient={encodeURIComponent(post.author_id || post.author_name)}&name={encodeURIComponent(post.author_name)}&club=arsenal"
										class="inline-flex items-center min-h-[44px] text-xs text-ink-2 hover:text-ink transition-colors whitespace-nowrap shrink-0"
										title="Direct message {post.author_name}"
									>
										Message author
									</a>
								</div>

								<p class="text-sm text-ink-2 line-clamp-3">
									{post.content}
								</p>
							</div>

							<div class="pt-3 border-t border-rule flex items-center justify-between text-xs text-muted">
								<div class="flex items-center gap-4 num">
									<span>{post.reactions_count} cheers</span>
									<span>{post.comments_count} replies</span>
								</div>
								<a href="/terrace" class="inline-flex items-center min-h-[44px] font-semibold text-accent-text hover:underline whitespace-nowrap">Join debate</a>
							</div>
						</article>
					{/each}
				{:else}
					<div class="col-span-full border-t border-rule pt-6 space-y-3">
						<h3 class="text-base font-semibold text-ink">No supporter debriefs published yet</h3>
						<p class="text-sm text-muted">Share your post-match observations and tactical boards with fellow Gooners.</p>
						<a href="/terrace" class="inline-flex items-center min-h-[44px] px-4 rounded-card bg-accent text-accent-ink text-sm font-semibold hover:opacity-90 transition-opacity">
							Open The Terrace
						</a>
					</div>
				{/if}
			</div>
		{/if}
	</section>
</div>
