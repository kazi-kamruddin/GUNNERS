<script lang="ts">
	import { CLUBS } from '$lib/stores/theme.svelte';
	import { formatMetricLabel } from '$lib/utils/format';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	const profile = $derived(data.supporterProfile);
	const name = $derived(profile.display_name);
	const club = $derived(CLUBS[profile.favorite_club_id] || CLUBS.arsenal);
	const isOwnProfile = $derived(Boolean(data.user?.id && data.user.id === profile.user_id));
	const initials = $derived(
		(profile.display_name || profile.username || 'G')
			.split(/\s+/)
			.map((p: string) => p[0] || '')
			.join('')
			.slice(0, 2)
			.toUpperCase()
	);

	let avatarFailed = $state(false);

	$effect(() => {
		if (profile.avatar_url !== undefined) {
			avatarFailed = false;
		}
	});

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
	<title>@{profile.username} | Supporter Portfolio | GUNNERS</title>
</svelte:head>

<div class="container py-12 space-y-12 max-w-5xl">
	<!-- Supporter Profile Header -->
	<section class="border-t-2 border-rule-2 pt-8 space-y-8">
		<div class="flex flex-col sm:flex-row sm:items-end justify-between gap-6">
			<div class="flex items-start gap-5 min-w-0">
				<div class="w-20 h-20 rounded-card border border-rule bg-paper-2 overflow-hidden shrink-0 flex items-center justify-center">
					{#if profile.avatar_url && !avatarFailed}
						<img
							src={profile.avatar_url}
							alt="{name} avatar"
							width="80"
							height="80"
							class="w-full h-full object-cover"
							onerror={() => (avatarFailed = true)}
						/>
					{:else}
						<span class="font-display font-bold text-2xl text-accent-text">{initials}</span>
					{/if}
				</div>

				<div class="space-y-3 min-w-0">
					<div class="flex items-baseline gap-3 flex-wrap">
						<h1 class="break-words min-w-0">{name}</h1>
						<span class="text-sm text-muted">
							@{profile.username}
						</span>
					</div>
					<div class="flex items-center gap-4 flex-wrap text-xs text-muted">
						<span>Affiliation: <strong class="text-ink">{club.name}</strong></span>
						<span>Joined <span class="num font-outlier">{formatDate(profile.joined_at)}</span></span>
					</div>
					{#if profile.bio}
						<p class="text-sm text-ink-2 max-w-xl leading-relaxed">
							{profile.bio}
						</p>
					{/if}
				</div>
			</div>

			<div class="self-start sm:self-end shrink-0">
				{#if isOwnProfile}
					<a
						href="/profile"
						class="min-h-[44px] px-4 rounded-card border border-rule bg-paper-2 hover:bg-paper-3 text-ink font-semibold text-xs transition-colors inline-flex items-center whitespace-nowrap"
					>
						Edit profile
					</a>
				{:else}
					<a
						href="/messages?recipient={encodeURIComponent(profile.user_id)}&name={encodeURIComponent(profile.display_name)}&club={encodeURIComponent(profile.favorite_club_id)}"
						class="min-h-[44px] px-4 rounded-card bg-accent hover:opacity-95 text-accent-ink font-semibold text-xs transition-opacity inline-flex items-center whitespace-nowrap"
					>
						Challenge to debate
					</a>
				{/if}
			</div>
		</div>

		<!-- Performance Stats Row -->
		<div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-6 pt-6 border-t border-rule text-xs">
			<div>
				<p class="text-muted">Predictor points</p>
				<p class="text-2xl font-bold text-success num font-outlier mt-1">{profile.stats.prediction_points} pts</p>
			</div>
			<div>
				<p class="text-muted">Predictor rank</p>
				<p class="text-2xl font-bold text-accent-2 num font-outlier mt-1">
					{profile.stats.prediction_rank === 0 ? 'Unranked' : `#${profile.stats.prediction_rank}`}
				</p>
				{#if profile.stats.prediction_rank === 0}
					<p class="text-xs text-muted mt-1">
						0 scored predictions
						{#if isOwnProfile}
							· <a href="/predictions" class="text-accent-text hover:text-ink font-semibold">Open Predictor</a>
						{/if}
					</p>
				{/if}
			</div>
			<div>
				<p class="text-muted">Predictions</p>
				<p class="text-2xl font-bold text-ink num font-outlier mt-1">{profile.stats.total_predictions}</p>
			</div>
			<div>
				<p class="text-muted">Exact scores</p>
				<p class="text-2xl font-bold text-ink num font-outlier mt-1">{profile.stats.exact_scores}</p>
			</div>
			<div>
				<p class="text-muted">Debates &amp; insights</p>
				<p class="text-2xl font-bold text-ink num font-outlier mt-1">{profile.stats.posts_count + profile.stats.insights_published}</p>
			</div>
			<div>
				<p class="text-muted">Cheers received</p>
				<p class="text-2xl font-bold text-accent-text num font-outlier mt-1">{profile.stats.cheers_received}</p>
			</div>
		</div>
	</section>

	<!-- Published Data Lab Insights Shelf -->
	<section class="border-t-2 border-rule-2 pt-8 space-y-6">
		<div class="flex flex-wrap items-end justify-between gap-4 border-b border-rule pb-4">
			<div class="space-y-1">
				<h2 class="text-xl font-bold text-ink">Published tactical insights</h2>
				<p class="text-xs text-muted">Reproducible analysis created by @{profile.username}</p>
			</div>
			<span class="text-xs num font-outlier text-muted">{profile.featured_insights.length} insights</span>
		</div>

		{#if profile.featured_insights.length === 0}
			<div class="py-10 text-muted text-sm">
				No public insights published yet by this supporter.
			</div>
		{:else}
			<div class="grid grid-cols-1 md:grid-cols-2 gap-8">
				{#each profile.featured_insights as ins (ins.id)}
					<article class="border-t border-rule pt-4 flex flex-col justify-between space-y-4">
						<div class="space-y-2">
							<div class="flex items-center justify-between gap-2 text-xs">
								<span class="text-accent-2 font-semibold">
									{formatMetricLabel(ins.metric)}
								</span>
								<span class="num font-outlier text-muted">{formatDate(ins.created_at)}</span>
							</div>
							<h3 class="text-base font-bold text-ink card-headline">{ins.title}</h3>
							{#if ins.description}
								<p class="text-sm text-ink-2 line-clamp-2">{ins.description}</p>
							{/if}
						</div>

						<div class="pt-3 border-t border-rule flex flex-wrap items-center justify-between gap-2 text-xs">
							<span class="text-muted">
								{ins.team_ids.join(', ')} ({ins.venue})
							</span>
							<a
								href="/lab?metric={ins.metric}&teams={ins.team_ids.join(',')}&venue={ins.venue}"
								class="inline-flex items-center min-h-[36px] text-accent-text hover:text-ink font-semibold transition-colors"
							>
								Open in Data Lab
							</a>
						</div>
					</article>
				{/each}
			</div>
		{/if}
	</section>

	<!-- Recent Terrace Debates -->
	<section class="border-t-2 border-rule-2 pt-8 space-y-6">
		<div class="flex flex-wrap items-end justify-between gap-4 border-b border-rule pb-4">
			<div class="space-y-1">
				<h2 class="text-xl font-bold text-ink">Terrace community debates</h2>
				<p class="text-xs text-muted">Recent posts and tactical observations</p>
			</div>
			<a href="/terrace" class="inline-flex items-center min-h-[36px] text-xs text-accent-text hover:text-ink font-semibold transition-colors">Browse all debates</a>
		</div>

		{#if profile.recent_posts.length === 0}
			<div class="py-10 text-muted text-sm">
				No Terrace debates published yet.
			</div>
		{:else}
			<div class="divide-y divide-rule">
				{#each profile.recent_posts as post (post.id)}
					<article class="py-5 space-y-3">
						<p class="text-sm text-ink leading-relaxed whitespace-pre-line">
							{post.content}
						</p>
						<div class="flex flex-wrap items-center justify-between gap-3 text-xs text-muted num font-outlier">
							<span>{post.reactions_count} cheers, {post.comments_count} replies</span>
							<div class="flex items-center gap-4">
								<span>{formatDate(post.created_at)}</span>
								<a
									href="/terrace#post-{encodeURIComponent(post.id)}"
									class="inline-flex items-center min-h-[36px] text-accent-text hover:text-ink font-sans font-semibold transition-colors"
								>
									View on Terrace
								</a>
							</div>
						</div>
					</article>
				{/each}
			</div>
		{/if}
	</section>
</div>
