<script lang="ts">
	import { CLUBS } from '$lib/stores/theme.svelte';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	const profile = $derived(data.profile);
	const club = $derived(CLUBS[profile.favorite_club_id] || CLUBS.arsenal);

	function formatDate(isoStr: string): string {
		try {
			const d = new Date(isoStr);
			return d.toLocaleDateString(undefined, {
				month: 'short',
				day: 'numeric',
				year: 'numeric'
			});
		} catch {
			return isoStr;
		}
	}
</script>

<svelte:head>
	<title>@{profile.username} | Supporter Portfolio | GUNNERS Reborn</title>
</svelte:head>

<div class="max-w-5xl mx-auto px-4 sm:px-6 py-8 space-y-8">
	<!-- Supporter Profile Header Card -->
	<div class="relative rounded-2xl overflow-hidden border border-[#1e2430] bg-[#12161f] p-6 sm:p-8">
		<div
			class="absolute top-0 left-0 right-0 h-2"
			style="background-color: {club.primary_color}"
		></div>

		<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-6 pt-2">
			<!-- Identity Meta -->
			<div class="flex items-center gap-4">
				<div
					class="w-16 h-16 rounded-full flex items-center justify-center font-black text-2xl text-white shadow-lg shrink-0"
					style="background-color: {club.primary_color}"
				>
					{profile.display_name.charAt(0).toUpperCase()}
				</div>
				<div>
					<div class="flex items-center gap-2">
						<h1 class="text-xl sm:text-2xl font-black text-white">{profile.display_name}</h1>
						<span class="text-xs font-mono px-2 py-0.5 rounded bg-black/40 text-gray-400 border border-[#1e2430]">
							@{profile.username}
						</span>
					</div>
					<div class="flex items-center gap-2 text-xs text-gray-400 mt-1 font-mono">
						<span>Affiliation: <strong class="text-white">{club.name}</strong></span>
						<span>•</span>
						<span>Joined {formatDate(profile.joined_at)}</span>
					</div>
					{#if profile.bio}
						<p class="text-xs text-gray-300 mt-2 max-w-xl leading-relaxed">
							{profile.bio}
						</p>
					{/if}
				</div>
			</div>

			<!-- DM Challenge Action -->
			<div class="flex items-center gap-3 self-start sm:self-center">
				<a
					href="/messages?recipient={encodeURIComponent(profile.user_id)}&name={encodeURIComponent(profile.display_name)}&club={encodeURIComponent(profile.favorite_club_id)}"
					class="px-4 py-2 rounded-lg bg-amber-500 hover:bg-amber-400 text-black font-bold text-xs transition shadow-sm flex items-center gap-1.5"
				>
					<span>💬</span>
					<span>Challenge to Debate (DM)</span>
				</a>
			</div>
		</div>

		<!-- Performance Stats Row -->
		<div class="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-8 pt-6 border-t border-[#1e2430]">
			<div class="bg-[#0d1017] p-3 rounded-xl border border-[#1e2430] text-center">
				<p class="text-[10px] text-gray-500 uppercase font-mono">Predictor Points</p>
				<p class="text-lg font-black text-emerald-400 font-mono mt-0.5">{profile.stats.prediction_points} pts</p>
			</div>
			<div class="bg-[#0d1017] p-3 rounded-xl border border-[#1e2430] text-center">
				<p class="text-[10px] text-gray-500 uppercase font-mono">Predictor Rank</p>
				<p class="text-lg font-black text-amber-400 font-mono mt-0.5">#{profile.stats.prediction_rank}</p>
			</div>
			<div class="bg-[#0d1017] p-3 rounded-xl border border-[#1e2430] text-center">
				<p class="text-[10px] text-gray-500 uppercase font-mono">Exact Scores</p>
				<p class="text-lg font-black text-purple-400 font-mono mt-0.5">{profile.stats.exact_scores}</p>
			</div>
			<div class="bg-[#0d1017] p-3 rounded-xl border border-[#1e2430] text-center">
				<p class="text-[10px] text-gray-500 uppercase font-mono">Cheers Received</p>
				<p class="text-lg font-black text-rose-400 font-mono mt-0.5">{profile.stats.cheers_received} 🔥</p>
			</div>
		</div>
	</div>

	<!-- Published Data Lab Insights Shelf -->
	<section class="space-y-4">
		<div class="flex items-center justify-between border-b border-[#1e2430] pb-3">
			<div>
				<h2 class="text-base font-bold text-white uppercase tracking-wider">Published Tactical Insights</h2>
				<p class="text-[11px] text-gray-400">Reproducible analysis created by @{profile.username}</p>
			</div>
			<span class="text-xs font-mono text-gray-500">{profile.featured_insights.length} insights</span>
		</div>

		{#if profile.featured_insights.length === 0}
			<div class="py-12 text-center border border-dashed border-[#1e2430] rounded-xl text-gray-500 text-xs">
				No public insights published yet by this supporter.
			</div>
		{:else}
			<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
				{#each profile.featured_insights as ins}
					<div class="p-4 rounded-xl border border-[#1e2430] bg-[#12161f] flex flex-col justify-between space-y-3">
						<div>
							<div class="flex items-center justify-between mb-1.5">
								<span class="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20 uppercase font-bold">
									{ins.metric.replace('_', ' ')}
								</span>
								<span class="text-[10px] font-mono text-gray-500">{formatDate(ins.created_at)}</span>
							</div>
							<h4 class="text-xs font-bold text-white mb-1">{ins.title}</h4>
							{#if ins.description}
								<p class="text-xs text-gray-400 line-clamp-2">{ins.description}</p>
							{/if}
						</div>

						<div class="pt-2 border-t border-[#1e2430] flex items-center justify-between text-xs">
							<span class="text-[11px] text-gray-500 font-mono">
								{ins.team_ids.join(', ')} • {ins.venue}
							</span>
							<a
								href="/lab?metric={ins.metric}&teams={ins.team_ids.join(',')}&venue={ins.venue}"
								class="text-[11px] text-amber-400 hover:text-amber-300 font-bold transition"
							>
								Open in Data Lab →
							</a>
						</div>
					</div>
				{/each}
			</div>
		{/if}
	</section>

	<!-- Recent Terrace Debates -->
	<section class="space-y-4">
		<div class="flex items-center justify-between border-b border-[#1e2430] pb-3">
			<div>
				<h2 class="text-base font-bold text-white uppercase tracking-wider">Terrace Community Debates</h2>
				<p class="text-[11px] text-gray-400">Recent posts and opinions</p>
			</div>
			<a href="/terrace" class="text-xs text-gray-400 hover:text-white transition">Browse All Debates →</a>
		</div>

		{#if profile.recent_posts.length === 0}
			<div class="py-12 text-center border border-dashed border-[#1e2430] rounded-xl text-gray-500 text-xs">
				No Terrace debates published yet.
			</div>
		{:else}
			<div class="space-y-3">
				{#each profile.recent_posts as post}
					<div class="p-4 rounded-xl border border-[#1e2430] bg-[#12161f] space-y-2">
						<p class="text-xs text-gray-200 leading-relaxed whitespace-pre-line">
							{post.content}
						</p>
						<div class="pt-2 border-t border-[#1e2430] flex items-center justify-between text-[10px] text-gray-500 font-mono">
							<span>🔥 {post.reactions_count} cheers • 💬 {post.comments_count} replies</span>
							<span>{formatDate(post.created_at)}</span>
						</div>
					</div>
				{/each}
			</div>
		{/if}
	</section>
</div>
