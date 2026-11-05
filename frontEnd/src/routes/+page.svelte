<script lang="ts">
	import { fetchMatchSummary } from '$lib/api/football';
	import type { MatchSummary } from '$lib/types/football';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	let summary = $state<MatchSummary | null>(null);
	let isInitialized = false;

	$effect(() => {
		if (!isInitialized && data.summary) {
			summary = data.summary;
			isInitialized = true;
		}
	});

	function formatDate(utcString?: string): string {
		if (!utcString) return 'TBD';
		try {
			const d = new Date(utcString);
			return d.toLocaleDateString(undefined, {
				month: 'short',
				day: 'numeric',
				hour: '2-digit',
				minute: '2-digit'
			});
		} catch {
			return utcString;
		}
	}
</script>

<svelte:head>
	<title>GUNNERS | Arsenal FC Fan & Tactical Intelligence Platform</title>
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 py-8 space-y-10">
	<!-- Hero Section -->
	<section class="relative rounded-3xl p-6 sm:p-12 overflow-hidden border border-red-900/40 bg-gradient-to-br from-[#12161f] via-[#1a0c0e] to-[#0d1017] shadow-2xl">
		<div class="absolute -right-16 -top-16 w-96 h-96 rounded-full bg-red-600/15 blur-3xl pointer-events-none"></div>
		<div class="absolute right-1/3 -bottom-20 w-80 h-80 rounded-full bg-amber-500/10 blur-3xl pointer-events-none"></div>

		<div class="relative z-10 max-w-3xl space-y-5">
			<div class="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wider bg-red-950/80 border border-red-800/50 text-red-300 font-mono">
				<span class="w-2 h-2 rounded-full bg-red-500 animate-pulse"></span>
				<span>Arsenal FC • Emirates Tactical Command</span>
			</div>

			<h1 class="text-3xl sm:text-5xl font-black tracking-tight text-white leading-tight">
				Victoria Concordia Crescit.<br />
				<span class="bg-gradient-to-r from-red-500 via-amber-400 to-amber-200 bg-clip-text text-transparent">
					The Ultimate Gooners Hub.
				</span>
			</h1>

			<p class="text-sm sm:text-base text-gray-300 leading-relaxed max-w-2xl">
				Aggregated real-time news from top Arsenal publications, fluid tactical lineup studio with bench swaps and canvas export, authentic Terrace debriefs with match photos, and verified Data Lab metrics.
			</p>

			<div class="flex flex-wrap items-center gap-3 pt-2">
				<a
					href="/news"
					class="px-5 py-2.5 rounded-xl bg-red-600 hover:bg-red-500 font-bold text-xs sm:text-sm text-white transition shadow-lg shadow-red-600/25 flex items-center gap-2"
				>
					<span>📰 The Armory News</span>
					<span>→</span>
				</a>
				<a
					href="/board"
					class="px-5 py-2.5 rounded-xl bg-white/5 hover:bg-white/10 border border-red-800/40 text-xs sm:text-sm font-semibold text-gray-200 transition flex items-center gap-1.5"
				>
					<span>📋 The Dugout Lineup</span>
				</a>
				<a
					href="/terrace"
					class="px-5 py-2.5 rounded-xl bg-white/5 hover:bg-white/10 border border-[#1e2430] text-xs sm:text-sm font-semibold text-amber-400 transition flex items-center gap-1.5"
				>
					<span>💬 The Terrace Feed</span>
				</a>
				<a
					href="/squad"
					class="px-5 py-2.5 rounded-xl bg-white/5 hover:bg-white/10 border border-[#1e2430] text-xs sm:text-sm font-semibold text-gray-300 transition"
				>
					👥 2024/25 Squad
				</a>
			</div>
		</div>
	</section>

	<!-- Feature Pillar Grid -->
	<section class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
		<!-- 1. The Armory -->
		<a
			href="/news"
			class="p-5 rounded-2xl border border-[#1e2430] bg-[#12161f] hover:border-red-600/50 transition group flex flex-col justify-between space-y-4"
		>
			<div class="space-y-2">
				<div class="w-10 h-10 rounded-xl bg-red-950/80 border border-red-800/40 flex items-center justify-center text-lg">
					📰
				</div>
				<h3 class="text-base font-bold text-white group-hover:text-red-400 transition">The Armory</h3>
				<p class="text-xs text-gray-400 leading-relaxed">
					Live news aggregation from Pain in the Arsenal, Arseblog, BBC Sport, Reddit r/Gunners, and Daily Cannon.
				</p>
			</div>
			<div class="text-[11px] font-mono text-red-400 flex items-center gap-1 pt-2 border-t border-[#1e2430]">
				<span>Read Latest Articles</span>
				<span>→</span>
			</div>
		</a>

		<!-- 2. The Dugout -->
		<a
			href="/board"
			class="p-5 rounded-2xl border border-[#1e2430] bg-[#12161f] hover:border-red-600/50 transition group flex flex-col justify-between space-y-4"
		>
			<div class="space-y-2">
				<div class="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-lg">
					📋
				</div>
				<h3 class="text-base font-bold text-white group-hover:text-amber-400 transition">The Dugout</h3>
				<p class="text-xs text-gray-400 leading-relaxed">
					Interactive pitch with starting XI and bench pool. Preset snapping or fluid movement with high-res PNG export.
				</p>
			</div>
			<div class="text-[11px] font-mono text-amber-400 flex items-center gap-1 pt-2 border-t border-[#1e2430]">
				<span>Build & Export Lineup</span>
				<span>→</span>
			</div>
		</a>

		<!-- 3. The Terrace -->
		<a
			href="/terrace"
			class="p-5 rounded-2xl border border-[#1e2430] bg-[#12161f] hover:border-red-600/50 transition group flex flex-col justify-between space-y-4"
		>
			<div class="space-y-2">
				<div class="w-10 h-10 rounded-xl bg-red-950/80 border border-red-800/40 flex items-center justify-center text-lg">
					💬
				</div>
				<h3 class="text-base font-bold text-white group-hover:text-red-400 transition">The Terrace</h3>
				<p class="text-xs text-gray-400 leading-relaxed">
					Guest-accessible community feed with matchday photo sharing, tactical debriefs, and cheering.
				</p>
			</div>
			<div class="text-[11px] font-mono text-red-400 flex items-center gap-1 pt-2 border-t border-[#1e2430]">
				<span>Join Match Discussions</span>
				<span>→</span>
			</div>
		</a>

		<!-- 4. Data Lab -->
		<a
			href="/lab"
			class="p-5 rounded-2xl border border-[#1e2430] bg-[#12161f] hover:border-red-600/50 transition group flex flex-col justify-between space-y-4"
		>
			<div class="space-y-2">
				<div class="w-10 h-10 rounded-xl bg-purple-500/10 border border-purple-500/30 flex items-center justify-center text-lg">
					📊
				</div>
				<h3 class="text-base font-bold text-white group-hover:text-purple-400 transition">The Data Lab</h3>
				<p class="text-xs text-gray-400 leading-relaxed">
					Emirates home vs away form, player statistical breakdowns, and shareable reproducible analytics.
				</p>
			</div>
			<div class="text-[11px] font-mono text-purple-400 flex items-center gap-1 pt-2 border-t border-[#1e2430]">
				<span>Explore Arsenal Metrics</span>
				<span>→</span>
			</div>
		</a>
	</section>

	<!-- Match Hub: Arsenal Schedule & Form -->
	<section class="grid grid-cols-1 md:grid-cols-3 gap-6">
		<!-- Next Fixture -->
		<div class="p-5 rounded-2xl border border-[#1e2430] bg-[#12161f] flex flex-col justify-between">
			<div>
				<div class="flex items-center justify-between mb-3">
					<span class="text-[10px] font-bold font-mono uppercase tracking-wider text-amber-400 bg-amber-400/10 px-2 py-0.5 rounded border border-amber-400/20">
						Next Match
					</span>
					<a href="/matches" class="text-[11px] text-gray-400 hover:text-white transition">Schedule →</a>
				</div>

				{#if summary?.next_fixture}
					<div class="space-y-3 mt-4">
						<div class="text-xs font-mono text-gray-400">
							{summary.next_fixture.competition_name || 'Premier League'} • {formatDate(summary.next_fixture.utc_date)}
						</div>
						<div class="flex items-center justify-between gap-3 bg-[#0a0c10] p-3 rounded-xl border border-[#1e2430]">
							<div class="text-center flex-1">
								<p class="text-xs font-bold text-white truncate">{summary.next_fixture.home_team_name}</p>
								<p class="text-[10px] text-gray-500">Home</p>
							</div>
							<span class="text-xs font-bold text-gray-500 font-mono">VS</span>
							<div class="text-center flex-1">
								<p class="text-xs font-bold text-white truncate">{summary.next_fixture.away_team_name}</p>
								<p class="text-[10px] text-gray-500">Away</p>
							</div>
						</div>
						<p class="text-[11px] text-gray-400 text-center font-mono">
							📍 {summary.next_fixture.venue || 'Emirates Stadium'}
						</p>
					</div>
				{:else}
					<div class="py-8 text-center text-gray-500 text-xs">
						No upcoming matches scheduled.
					</div>
				{/if}
			</div>

			<div class="mt-4 pt-3 border-t border-[#1e2430] flex items-center justify-between text-[11px] text-gray-400">
				<span>Completed: {summary?.total_completed ?? 0}</span>
				<span>Scheduled: {summary?.total_scheduled ?? 0}</span>
			</div>
		</div>

		<!-- Last Result -->
		<div class="p-5 rounded-2xl border border-[#1e2430] bg-[#12161f] flex flex-col justify-between">
			<div>
				<div class="flex items-center justify-between mb-3">
					<span class="text-[10px] font-bold font-mono uppercase tracking-wider text-emerald-400 bg-emerald-400/10 px-2 py-0.5 rounded border border-emerald-400/20">
						Latest Result
					</span>
					<span class="text-[11px] font-mono text-gray-500">{summary?.last_result ? formatDate(summary.last_result.utc_date) : ''}</span>
				</div>

				{#if summary?.last_result}
					<div class="space-y-3 mt-4">
						<div class="flex items-center justify-between gap-3 bg-[#0a0c10] p-3 rounded-xl border border-[#1e2430]">
							<div class="text-center flex-1">
								<p class="text-xs font-bold text-white truncate">{summary.last_result.home_team_name}</p>
								<span class="text-2xl font-black text-white font-mono">{summary.last_result.home_score ?? 0}</span>
							</div>
							<span class="text-xs font-bold text-gray-600">-</span>
							<div class="text-center flex-1">
								<p class="text-xs font-bold text-white truncate">{summary.last_result.away_team_name}</p>
								<span class="text-2xl font-black text-white font-mono">{summary.last_result.away_score ?? 0}</span>
							</div>
						</div>
						<p class="text-[11px] text-gray-400 text-center font-mono">
							{summary.last_result.competition_name || 'Premier League'}
						</p>
					</div>
				{:else}
					<div class="py-8 text-center text-gray-500 text-xs">
						No completed results found.
					</div>
				{/if}
			</div>

			<!-- Recent Form Guide -->
			<div class="mt-4 pt-3 border-t border-[#1e2430] flex items-center justify-between">
				<span class="text-[11px] text-gray-400">Form (Last 5):</span>
				<div class="flex items-center gap-1.5">
					{#if summary?.recent_form && summary.recent_form.length > 0}
						{#each summary.recent_form as item}
							<span
								class="w-5 h-5 rounded flex items-center justify-center text-[10px] font-bold font-mono {item === 'W' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40' : item === 'D' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/40' : 'bg-red-500/20 text-red-400 border border-red-500/40'}"
							>
								{item}
							</span>
						{/each}
					{:else}
						<span class="text-xs text-gray-500 font-mono">-</span>
					{/if}
				</div>
			</div>
		</div>

		<!-- Fast Analytics Query Teaser -->
		<div class="p-5 rounded-2xl border border-[#1e2430] bg-[#12161f] flex flex-col justify-between">
			<div>
				<div class="flex items-center justify-between mb-3">
					<span class="text-[10px] font-bold font-mono uppercase tracking-wider text-purple-400 bg-purple-400/10 px-2 py-0.5 rounded border border-purple-400/20">
						Data Lab Quick Launch
					</span>
				</div>
				<h3 class="text-sm font-bold text-white mb-2">Arsenal Form & Metrics</h3>
				<p class="text-xs text-gray-400 leading-relaxed">
					Examine Emirates win rate, Declan Rice ground duel win percentage, and goals per match across the 2024/25 campaign.
				</p>
				<div class="mt-4 flex flex-wrap gap-1.5">
					<a
						href="/lab?metric=win_rate&teams=arsenal&venue=home"
						class="text-[10px] px-2 py-1 rounded bg-[#0a0c10] border border-[#1e2430] text-gray-300 hover:text-white hover:border-red-500 transition"
					>
						Home Win Rate (83.3%)
					</a>
					<a
						href="/lab?metric=clean_sheet_rate&teams=arsenal&venue=all"
						class="text-[10px] px-2 py-1 rounded bg-[#0a0c10] border border-[#1e2430] text-gray-300 hover:text-white hover:border-red-500 transition"
					>
						Clean Sheet (50%)
					</a>
					<a
						href="/lab?metric=goals_per_match&teams=arsenal&venue=all"
						class="text-[10px] px-2 py-1 rounded bg-[#0a0c10] border border-[#1e2430] text-gray-300 hover:text-white hover:border-red-500 transition"
					>
						Goals / Match (2.18)
					</a>
				</div>
			</div>

			<a
				href="/lab?teams=arsenal"
				class="mt-6 w-full py-2.5 text-center rounded-xl bg-white/5 hover:bg-white/10 border border-[#1e2430] text-xs font-bold text-white transition"
			>
				Open Full Analytics Engine →
			</a>
		</div>
	</section>

	<!-- The Terrace Pulse -->
	<section class="space-y-4">
		<div class="flex items-center justify-between">
			<div>
				<h2 class="text-lg font-bold text-white uppercase tracking-tight">The Terrace Pulse</h2>
				<p class="text-xs text-gray-400">Live debriefs and supporter debriefs from the Emirates community</p>
			</div>
			<a href="/terrace" class="text-xs text-red-400 hover:text-red-300 font-semibold transition">
				Visit Terrace →
			</a>
		</div>

		<div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
			{#if data.posts && data.posts.length > 0}
				{#each data.posts.slice(0, 4) as post}
					<div class="p-4 rounded-xl border border-[#1e2430] bg-[#12161f] space-y-2.5 hover:border-gray-700 transition">
						<div class="flex items-center justify-between">
							<div class="flex items-center gap-2">
								<span class="w-2.5 h-2.5 rounded-full bg-red-600"></span>
								<span class="text-xs font-bold text-white">{post.author_name}</span>
								<span class="text-[10px] font-mono px-1.5 py-0.5 rounded bg-red-950/60 text-red-300 border border-red-900/40">
									Arsenal
								</span>
							</div>
							<a
								href="/messages?recipient={encodeURIComponent(post.author_id || post.author_name)}&name={encodeURIComponent(post.author_name)}&club=arsenal"
								class="text-[10px] text-gray-400 hover:text-amber-400 font-semibold transition flex items-center gap-0.5"
								title="Direct message {post.author_name}"
							>
								<span>💬</span>
								<span>DM</span>
							</a>
						</div>

						<p class="text-xs text-gray-300 line-clamp-2 leading-relaxed">
							{post.content}
						</p>

						<div class="pt-2 border-t border-[#1e2430] flex items-center justify-between text-[10px] text-gray-500 font-mono">
							<span>🔥 {post.reactions_count} cheers • 💬 {post.comments_count} replies</span>
							<a href="/terrace" class="text-red-400 hover:underline transition">Join Debate →</a>
						</div>
					</div>
				{/each}
			{:else}
				<div class="col-span-full p-6 rounded-xl border border-[#1e2430] bg-[#12161f] text-center space-y-2">
					<p class="text-sm font-semibold text-gray-300">Debates are heating up on The Terrace</p>
					<p class="text-xs text-gray-500">Join Arsenal supporters worldwide and share match observations.</p>
					<a href="/terrace" class="inline-block mt-2 px-4 py-1.5 rounded-lg bg-red-600 hover:bg-red-700 text-white font-bold text-xs transition">
						Open The Terrace →
					</a>
				</div>
			{/if}
		</div>
	</section>
</div>
