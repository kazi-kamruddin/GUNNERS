<script lang="ts">
	import { CLUBS, themeState } from '$lib/stores/theme.svelte';
	import { fetchPosts, createPost, toggleReaction, fetchComments, createComment } from '$lib/api/football';
	import type { Post, PostComment, Insight } from '$lib/types/football';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	// Reactive states
	let selectedTab = $state<'global' | string>('global');
	let posts = $state<Post[]>([]);
	let availableInsights = $state<Insight[]>([]);
	let isLoadingFeed = $state(false);

	// Composer state
	let newPostContent = $state('');
	let selectedInsightId = $state<string>('');
	let targetClub = $state<'global' | string>('global');
	let isSubmitting = $state(false);

	// Comments state: map post_id -> comments list & expanded flag
	let expandedComments = $state<Record<string, boolean>>({});
	let postComments = $state<Record<string, PostComment[]>>({});
	let newCommentText = $state<Record<string, string>>({});
	let isSubmittingComment = $state<Record<string, boolean>>({});

	const clubList = Object.values(CLUBS);

	$effect(() => {
		posts = data.initialPosts;
		availableInsights = data.availableInsights;
		selectedTab = data.initialClub || 'global';
	});

	async function selectTab(tab: 'global' | string) {
		selectedTab = tab;
		isLoadingFeed = true;
		try {
			posts = await fetchPosts(tab, data.user?.id);
		} finally {
			isLoadingFeed = false;
		}
	}

	async function handlePublishPost() {
		if (!newPostContent.trim()) return;
		isSubmitting = true;
		try {
			const authorName = data.profile?.display_name || data.user?.email?.split('@')[0] || 'Supporter';
			const authorClub = data.profile?.favorite_club_id || themeState.viewingClubId;

			const created = await createPost({
				content: newPostContent.trim(),
				club_id: targetClub === 'global' ? null : targetClub,
				insight_id: selectedInsightId || null,
				author_name: authorName,
				author_club_id: authorClub
			});

			if (created) {
				// Attach the insight object for instant feed display if attached
				if (selectedInsightId) {
					const insObj = availableInsights.find((i) => i.id === selectedInsightId);
					if (insObj) created.insight = insObj;
				}
				posts = [created, ...posts];
				newPostContent = '';
				selectedInsightId = '';
			}
		} finally {
			isSubmitting = false;
		}
	}

	async function handleToggleReaction(post: Post) {
		const userId = data.user?.id || 'anon_user';
		const wasReacted = post.user_reacted;
		// Optimistic update
		post.user_reacted = !wasReacted;
		post.reactions_count += wasReacted ? -1 : 1;

		try {
			const res = await toggleReaction(post.id, userId, 'cheer');
			post.reactions_count = res.total_reactions;
			post.user_reacted = res.action === 'added';
		} catch (err) {
			// Revert on failure
			post.user_reacted = wasReacted;
			post.reactions_count += wasReacted ? 1 : -1;
		}
	}

	async function toggleCommentSection(postId: string) {
		const isOpen = !!expandedComments[postId];
		expandedComments[postId] = !isOpen;

		if (!isOpen && !postComments[postId]) {
			postComments[postId] = await fetchComments(postId);
		}
	}

	async function handleAddComment(postId: string) {
		const text = newCommentText[postId]?.trim();
		if (!text) return;

		isSubmittingComment[postId] = true;
		const authorName = data.profile?.display_name || data.user?.email?.split('@')[0] || 'Supporter';
		const authorClub = data.profile?.favorite_club_id || themeState.viewingClubId;

		try {
			const comment = await createComment(postId, text, authorName, authorClub);
			if (comment) {
				const current = postComments[postId] || [];
				postComments[postId] = [...current, comment];
				newCommentText[postId] = '';

				const targetPost = posts.find((p) => p.id === postId);
				if (targetPost) targetPost.comments_count += 1;
			}
		} finally {
			isSubmittingComment[postId] = false;
		}
	}

	let attachedInsightPreview = $derived(
		selectedInsightId ? availableInsights.find((i) => i.id === selectedInsightId) : null
	);

	function formatTimestamp(isoStr: string): string {
		try {
			const d = new Date(isoStr);
			return d.toLocaleDateString(undefined, {
				month: 'short',
				day: 'numeric',
				hour: '2-digit',
				minute: '2-digit'
			});
		} catch {
			return isoStr;
		}
	}
</script>

<svelte:head>
	<title>The Terrace | GUNNERS Reborn Fan Community</title>
</svelte:head>

<div class="max-w-4xl mx-auto px-4 py-8 space-y-8">
	<!-- Page Header -->
	<div class="border-b border-[#1e2430] pb-6">
		<div class="inline-flex items-center gap-2 px-2.5 py-0.5 rounded text-[11px] font-semibold uppercase tracking-wider mb-2 bg-red-950/70 text-red-400 border border-red-800/40 font-mono">
			Supporter Terrace & Debates
		</div>
		<h1 class="text-2xl font-black text-white uppercase tracking-tight">The Terrace</h1>
		<p class="text-sm text-gray-400 mt-1">
			Debate the game with supporters across clubs. Publish opinions and back your claims with reproducible Data Lab insights.
		</p>
	</div>

	<!-- Feed Filter Tabs -->
	<div class="flex items-center gap-2 border-b border-[#1e2430] pb-4 flex-wrap">
		<button
			type="button"
			onclick={() => selectTab('global')}
			class="px-4 py-2 rounded-lg text-xs font-bold transition flex items-center gap-2 border {selectedTab === 'global' ? 'bg-white/10 text-white border-white/20' : 'text-gray-400 hover:text-white border-[#1e2430] bg-[#12161f]'}"
		>
			<span>Global Terrace</span>
		</button>
		{#each clubList as club}
			<button
				type="button"
				onclick={() => selectTab(club.id)}
				class="px-3.5 py-2 rounded-lg text-xs font-bold transition flex items-center gap-1.5 border {selectedTab === club.id ? 'bg-white/10 text-white border-white/20' : 'text-gray-400 hover:text-white border-[#1e2430] bg-[#12161f]'}"
			>
				<span class="w-2 h-2 rounded-full" style="background-color: {club.primary_color}"></span>
				<span>{club.short_name} Terrace</span>
			</button>
		{/each}
	</div>

	<!-- Post Composer -->
	<div class="p-5 rounded-lg border border-[#1e2430] bg-[#12161f] space-y-4">
		<div class="flex items-center justify-between">
			<div class="flex items-center gap-2">
				<span class="w-2.5 h-2.5 rounded-full" style="background-color: {themeState.currentTheme.primary_color}"></span>
				<span class="text-xs font-bold text-white">
					{data.profile?.display_name || (data.user ? data.user.email?.split('@')[0] : 'Supporter')}
				</span>
				<span class="text-[10px] text-gray-500 font-mono uppercase">
					({themeState.currentTheme.short_name} Affiliation)
				</span>
			</div>

			<!-- Target Terrace Selector -->
			<div class="flex items-center gap-1.5 text-xs">
				<label for="post-destination" class="text-gray-400 text-[11px]">Post to:</label>
				<select
					id="post-destination"
					bind:value={targetClub}
					class="bg-[#0a0c10] border border-[#1e2430] text-gray-300 text-xs rounded px-2 py-1 focus:outline-none focus:border-gray-500"
				>
					<option value="global">Global Terrace</option>
					{#each clubList as c}
						<option value={c.id}>{c.short_name} Terrace</option>
					{/each}
				</select>
			</div>
		</div>

		<!-- Post Input -->
		<textarea
			bind:value={newPostContent}
			rows="3"
			placeholder="Share tactical observations, match reactions, or link a reproducible Data Lab analysis..."
			class="w-full bg-[#0a0c10] border border-[#1e2430] rounded-lg p-3 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-red-500 transition resize-none"
		></textarea>

		<!-- Attached Insight Preview -->
		{#if attachedInsightPreview}
			<div class="p-3.5 rounded-lg bg-[#0a0c10] border border-amber-500/30 flex items-center justify-between gap-4">
				<div class="space-y-1">
					<div class="flex items-center gap-2">
						<span class="text-[10px] uppercase font-mono font-bold px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20">
							Insight Attached
						</span>
						<span class="text-xs font-bold text-white">{attachedInsightPreview.title}</span>
					</div>
					<p class="text-[11px] text-gray-400 font-mono">
						Metric: {attachedInsightPreview.metric} · Venue: {attachedInsightPreview.venue}
					</p>
				</div>
				<button
					type="button"
					onclick={() => (selectedInsightId = '')}
					class="text-xs text-gray-500 hover:text-red-400 px-2 py-1 rounded transition"
				>
					Detach
				</button>
			</div>
		{/if}

		<!-- Composer Footer -->
		<div class="flex items-center justify-between pt-2 border-t border-[#1e2430] flex-wrap gap-2">
			<!-- Attach Insight Dropdown -->
			<div class="flex items-center gap-2">
				<select
					bind:value={selectedInsightId}
					class="bg-[#0a0c10] border border-[#1e2430] text-xs text-gray-300 rounded px-2.5 py-1.5 focus:outline-none focus:border-gray-500"
				>
					<option value="">Attach Data Lab Insight (Optional)</option>
					{#each availableInsights as ins}
						<option value={ins.id}>{ins.title}</option>
					{/each}
				</select>
				<a
					href="/lab"
					class="text-[11px] text-amber-400 hover:underline hidden sm:inline"
				>
					+ Create new in Data Lab
				</a>
			</div>

			<!-- Submit Post Button -->
			<button
				type="button"
				onclick={handlePublishPost}
				disabled={isSubmitting || !newPostContent.trim()}
				class="px-4 py-2 rounded-lg bg-red-600 hover:bg-red-500 text-white font-bold text-xs transition disabled:opacity-50 shadow-sm"
			>
				{isSubmitting ? 'Publishing...' : 'Publish to Terrace'}
			</button>
		</div>
	</div>

	<!-- Feed Stream -->
	{#if isLoadingFeed}
		<div class="py-16 text-center text-gray-500 text-sm">
			Loading Terrace discussions...
		</div>
	{:else if posts.length === 0}
		<div class="py-16 text-center border border-dashed border-[#1e2430] rounded-lg">
			<p class="text-sm text-gray-400">No posts in this Terrace yet.</p>
			<p class="text-xs text-gray-500 mt-1">Start the debate by writing the first post above!</p>
		</div>
	{:else}
		<div class="space-y-4">
			{#each posts as post}
				{@const authorClub = CLUBS[post.author_club_id] || CLUBS['arsenal']}
				<div class="p-5 rounded-lg border border-[#1e2430] bg-[#12161f] space-y-3">
					<!-- Post Author & Meta -->
					<div class="flex items-center justify-between">
						<div class="flex items-center gap-2.5">
							<span class="w-3 h-3 rounded-full" style="background-color: {authorClub.primary_color}"></span>
							<span class="text-xs font-bold text-white">{post.author_name}</span>
							<span class="text-[10px] font-mono px-1.5 py-0.5 rounded bg-black/40 border border-[#1e2430] text-gray-400">
								{authorClub.short_name}
							</span>
							{#if post.club_id}
								<span class="text-[10px] text-gray-500 hidden sm:inline">
									in {CLUBS[post.club_id]?.short_name || post.club_id} Terrace
								</span>
							{/if}
						</div>
						<span class="text-[11px] text-gray-500 font-mono">{formatTimestamp(post.created_at)}</span>
					</div>

					<!-- Post Content -->
					<p class="text-xs text-gray-200 leading-relaxed whitespace-pre-line">
						{post.content}
					</p>

					<!-- Attached Insight Post Card (Centerpiece) -->
					{#if post.insight}
						{@const ins = post.insight}
						<div class="p-4 rounded-lg bg-[#0a0c10] border border-[#1e2430] space-y-3">
							<div class="flex items-center justify-between gap-2">
								<div class="flex items-center gap-2">
									<span class="text-[10px] font-mono font-bold uppercase px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20">
										Insight Post
									</span>
									<h4 class="text-xs font-bold text-white">{ins.title}</h4>
								</div>
								<a
									href="/lab?metric={ins.metric}&teams={ins.team_ids.join(',')}&venue={ins.venue}"
									class="text-[11px] font-bold px-2.5 py-1 rounded bg-white/5 hover:bg-white/10 text-amber-300 border border-amber-500/30 transition flex items-center gap-1"
								>
									<span>Open in Data Lab</span>
									<span>→</span>
								</a>
							</div>

							<!-- Visual Snapshot Bar / Numbers -->
							{#if ins.snapshot && ins.snapshot.series}
								<div class="grid grid-cols-1 sm:grid-cols-{Math.min(ins.snapshot.series.length, 2)} gap-3 pt-2 border-t border-[#1e2430]">
									{#each ins.snapshot.series as item}
										{@const itemClub = CLUBS[item.team_id] || CLUBS['arsenal']}
										<div class="p-2.5 rounded bg-[#12161f] border border-[#1e2430] space-y-1">
											<div class="flex items-center justify-between text-[11px]">
												<span class="text-gray-300 font-bold">{item.team_name}</span>
												<span class="font-mono font-bold text-white">
													{item.metric_value} <span class="text-amber-400">{item.unit}</span>
												</span>
											</div>
											<div class="flex items-center justify-between text-[10px] text-gray-500 font-mono">
												<span>{item.matches_played} matches</span>
												<span>{item.wins}W - {item.draws}D - {item.losses}L</span>
											</div>
										</div>
									{/each}
								</div>
								<div class="text-[10px] text-gray-500 font-mono">
									Formula: {ins.snapshot.formula} (Venue: {ins.venue})
								</div>
							{/if}
						</div>
					{/if}

					<!-- Post Action Bar -->
					<div class="flex items-center gap-4 pt-2 border-t border-[#1e2430] text-xs">
						<!-- Cheer Reaction -->
						<button
							type="button"
							onclick={() => handleToggleReaction(post)}
							class="flex items-center gap-1.5 px-2.5 py-1 rounded transition {post.user_reacted ? 'bg-amber-500/10 text-amber-400 font-bold border border-amber-500/30' : 'text-gray-400 hover:text-white'}"
						>
							<span>⚽ Cheer</span>
							<span class="font-mono">{post.reactions_count}</span>
						</button>

						<!-- Comments Toggle -->
						<button
							type="button"
							onclick={() => toggleCommentSection(post.id)}
							class="flex items-center gap-1.5 px-2.5 py-1 rounded text-gray-400 hover:text-white transition"
						>
							<span>💬 Debate ({post.comments_count})</span>
						</button>
					</div>

					<!-- Comments Thread (Expandable) -->
					{#if expandedComments[post.id]}
						<div class="pt-3 border-t border-[#1e2430] space-y-3">
							<!-- Comments List -->
							{#if postComments[post.id] && postComments[post.id].length > 0}
								<div class="space-y-2">
									{#each postComments[post.id] as comment}
										{@const cClub = CLUBS[comment.author_club_id] || CLUBS['arsenal']}
										<div class="p-2.5 rounded bg-[#0a0c10] border border-[#1e2430] space-y-1">
											<div class="flex items-center justify-between">
												<div class="flex items-center gap-1.5">
													<span class="w-1.5 h-1.5 rounded-full" style="background-color: {cClub.primary_color}"></span>
													<span class="text-[11px] font-bold text-gray-300">{comment.author_name}</span>
												</div>
												<span class="text-[10px] text-gray-500 font-mono">{formatTimestamp(comment.created_at)}</span>
											</div>
											<p class="text-xs text-gray-300 leading-relaxed">{comment.content}</p>
										</div>
									{/each}
								</div>
							{:else}
								<p class="text-xs text-gray-500">No comments yet. Join the conversation below!</p>
							{/if}

							<!-- Inline Reply Form -->
							<div class="flex items-center gap-2">
								<input
									type="text"
									bind:value={newCommentText[post.id]}
									placeholder="Write your response..."
									class="flex-1 bg-[#0a0c10] border border-[#1e2430] rounded p-2 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-gray-500"
									onkeydown={(e) => e.key === 'Enter' && handleAddComment(post.id)}
								/>
								<button
									type="button"
									onclick={() => handleAddComment(post.id)}
									disabled={isSubmittingComment[post.id] || !newCommentText[post.id]?.trim()}
									class="px-3 py-2 rounded bg-white/10 hover:bg-white/20 text-xs font-bold text-white transition disabled:opacity-50"
								>
									Reply
								</button>
							</div>
						</div>
					{/if}
				</div>
			{/each}
		</div>
	{/if}
</div>
