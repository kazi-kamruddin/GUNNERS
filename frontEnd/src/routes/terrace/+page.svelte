<script lang="ts">
	import { fetchPosts, createPost, toggleReaction, fetchComments, createComment } from '$lib/api/football';
	import TacticalBoardComponent from '$lib/components/TacticalBoard.svelte';
	import type { Post, PostComment, Insight, TopicTag, TacticalBoard } from '$lib/types/football';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	// Reactive states
	let selectedTab = $state<'all' | 'tactics' | 'matchday' | 'squad'>('all');
	let posts = $state<Post[]>([]);
	let availableInsights = $state<Insight[]>([]);
	let availableTacticalBoards = $state<TacticalBoard[]>([]);
	let isLoadingFeed = $state(false);

	// Composer state
	let newPostContent = $state('');
	let newPostImageUrl = $state('');
	let showImageInput = $state(false);
	let selectedInsightId = $state<string>('');
	let selectedTacticalBoardId = $state<string>('');
	let isSubmitting = $state(false);

	// Guest Auth Gate Modal state
	let showAuthModal = $state(false);
	let authModalReason = $state<'post' | 'comment' | 'react'>('post');

	// Lightbox state
	let lightboxImageUrl = $state<string | null>(null);

	// Comments state: map post_id -> comments list & expanded flag
	let expandedComments = $state<Record<string, boolean>>({});
	let postComments = $state<Record<string, PostComment[]>>({});
	let newCommentText = $state<Record<string, string>>({});
	let isSubmittingComment = $state<Record<string, boolean>>({});

	// Search & Tag state
	let searchQuery = $state('');
	let selectedTag = $state('');
	let trendingTags = $state<TopicTag[]>([]);

	$effect(() => {
		posts = data.initialPosts;
		availableInsights = data.availableInsights;
		availableTacticalBoards = data.availableTacticalBoards || [];
		searchQuery = data.initialSearch || '';
		selectedTag = data.initialTag || '';
		trendingTags = data.trendingTags || [];
	});

	function requireAuth(reason: 'post' | 'comment' | 'react'): boolean {
		if (!data.user) {
			authModalReason = reason;
			showAuthModal = true;
			return false;
		}
		return true;
	}

	async function reloadFeed(searchVal?: string, tagVal?: string) {
		isLoadingFeed = true;
		try {
			posts = await fetchPosts(
				'arsenal',
				data.user?.id,
				searchVal !== undefined ? searchVal : searchQuery,
				tagVal !== undefined ? tagVal : selectedTag
			);
		} finally {
			isLoadingFeed = false;
		}
	}

	async function selectCategory(tab: 'all' | 'tactics' | 'matchday' | 'squad') {
		selectedTab = tab;
		if (tab === 'tactics') {
			selectedTag = 'Tactics';
			await reloadFeed(undefined, 'Tactics');
		} else if (tab === 'matchday') {
			selectedTag = 'NorthLondonDerby';
			await reloadFeed(undefined, 'NorthLondonDerby');
		} else if (tab === 'squad') {
			selectedTag = 'Arsenal';
			await reloadFeed(undefined, 'Arsenal');
		} else {
			selectedTag = '';
			await reloadFeed('', '');
		}
	}

	async function handleSearch() {
		await reloadFeed(searchQuery, selectedTag);
	}

	async function handleTagClick(tag: string) {
		const clean = tag.replace(/^#+/, '');
		if (selectedTag === clean) {
			selectedTag = '';
		} else {
			selectedTag = clean;
		}
		await reloadFeed(undefined, selectedTag);
	}

	async function clearFilters() {
		searchQuery = '';
		selectedTag = '';
		selectedTab = 'all';
		await reloadFeed('', '');
	}

	async function handlePublishPost() {
		if (!requireAuth('post')) return;
		if (!newPostContent.trim()) return;

		isSubmitting = true;
		try {
			const authorName = data.profile?.display_name || data.user?.email?.split('@')[0] || 'Gooner';
			const authorClub = 'arsenal';

			const created = await createPost({
				content: newPostContent.trim(),
				club_id: 'arsenal',
				image_url: newPostImageUrl.trim() || null,
				insight_id: selectedInsightId || null,
				tactical_board_id: selectedTacticalBoardId || null,
				author_name: authorName,
				author_club_id: authorClub
			});

			if (created) {
				if (selectedInsightId) {
					const insObj = availableInsights.find((i) => i.id === selectedInsightId);
					if (insObj) created.insight = insObj;
				}
				if (selectedTacticalBoardId) {
					const tbObj = availableTacticalBoards.find((b) => b.id === selectedTacticalBoardId);
					if (tbObj) created.tactical_board = tbObj;
				}
				posts = [created, ...posts];
				newPostContent = '';
				newPostImageUrl = '';
				showImageInput = false;
				selectedInsightId = '';
				selectedTacticalBoardId = '';
			}
		} finally {
			isSubmitting = false;
		}
	}

	async function handleToggleReaction(post: Post) {
		if (!requireAuth('react')) return;

		const userId = data.user?.id || 'anon_user';
		const wasReacted = post.user_reacted;
		post.user_reacted = !wasReacted;
		post.reactions_count += wasReacted ? -1 : 1;

		try {
			const res = await toggleReaction(post.id, userId, 'cheer');
			post.reactions_count = res.total_reactions;
			post.user_reacted = res.action === 'added';
		} catch {
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
		if (!requireAuth('comment')) return;

		const text = newCommentText[postId]?.trim();
		if (!text) return;

		isSubmittingComment[postId] = true;
		const authorName = data.profile?.display_name || data.user?.email?.split('@')[0] || 'Gooner';
		const authorClub = 'arsenal';

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

	let attachedTacticalBoardPreview = $derived(
		selectedTacticalBoardId ? availableTacticalBoards.find((b) => b.id === selectedTacticalBoardId) : null
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
	<title>The Terrace | Arsenal FC Supporter Community & Tactical Debriefs</title>
</svelte:head>

<div class="max-w-4xl mx-auto px-4 py-8 space-y-8">
	<!-- Page Header -->
	<div class="border-b border-red-900/30 pb-6 flex flex-col sm:flex-row sm:items-end justify-between gap-4">
		<div>
			<div class="inline-flex items-center gap-2 px-2.5 py-0.5 rounded text-[11px] font-semibold uppercase tracking-wider mb-2 bg-red-950/70 text-red-400 border border-red-800/40 font-mono">
				Emirates Community Hub
			</div>
			<h1 class="text-3xl font-black text-white uppercase tracking-tight flex items-center gap-2.5">
				<span>The Terrace</span>
				<span class="text-xs px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20 font-mono font-medium normal-case">
					Gooners Voice
				</span>
			</h1>
			<p class="text-sm text-gray-400 mt-1">
				The beating heart of Arsenal supporters. Share match observations, debate tactical lineups, analyze stats, and interact with fellow Gooners worldwide.
			</p>
		</div>

		{#if !data.user}
			<div class="p-3 rounded-lg bg-red-950/30 border border-red-900/40 text-xs text-gray-300 max-w-xs">
				<div class="flex items-center gap-1.5 font-bold text-red-400 mb-1">
					<span>👀 Guest Browsing Mode</span>
				</div>
				<p class="text-[11px] text-gray-400 leading-snug">
					You can freely read all posts, tactics, and debriefs. <a href="/login" class="text-red-400 underline font-semibold hover:text-red-300">Sign in</a> to join debates or publish.
				</p>
			</div>
		{/if}
	</div>

	<!-- Search & Category Filters -->
	<div class="p-4 rounded-xl border border-[#1e2430] bg-[#12161f] space-y-4">
		<div class="flex items-center gap-3">
			<div class="relative flex-1">
				<input
					type="text"
					bind:value={searchQuery}
					onkeydown={(e) => e.key === 'Enter' && handleSearch()}
					placeholder="Search discussions, tactics, player debriefs (#Saka, #Derby, #Arteta)..."
					class="w-full bg-[#0a0c10] border border-[#1e2430] rounded-lg pl-9 pr-3 py-2 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-red-500 transition"
				/>
				<svg class="w-4 h-4 text-gray-500 absolute left-3 top-2.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
				</svg>
			</div>
			<button
				type="button"
				onclick={handleSearch}
				class="px-4 py-2 rounded-lg bg-red-600 hover:bg-red-700 text-white text-xs font-bold transition shadow-sm"
			>
				Search
			</button>
			{#if searchQuery || selectedTag || selectedTab !== 'all'}
				<button
					type="button"
					onclick={clearFilters}
					class="px-3 py-2 rounded-lg border border-gray-700 hover:border-gray-500 text-gray-400 hover:text-white text-xs font-medium transition"
				>
					Reset
				</button>
			{/if}
		</div>

		<!-- Channel Navigation Tabs -->
		<div class="flex items-center gap-2 border-t border-[#1e2430]/60 pt-3 flex-wrap">
			<button
				type="button"
				onclick={() => selectCategory('all')}
				class="px-3.5 py-1.5 rounded-lg text-xs font-bold transition flex items-center gap-1.5 border {selectedTab === 'all' && !selectedTag ? 'bg-red-600 text-white border-red-500' : 'text-gray-400 hover:text-white border-[#1e2430] bg-[#0a0c10]'}"
			>
				<span>🔴 All Terrace</span>
			</button>
			<button
				type="button"
				onclick={() => selectCategory('tactics')}
				class="px-3.5 py-1.5 rounded-lg text-xs font-bold transition flex items-center gap-1.5 border {selectedTab === 'tactics' ? 'bg-red-600 text-white border-red-500' : 'text-gray-400 hover:text-white border-[#1e2430] bg-[#0a0c10]'}"
			>
				<span>📋 Tactical Debriefs</span>
			</button>
			<button
				type="button"
				onclick={() => selectCategory('matchday')}
				class="px-3.5 py-1.5 rounded-lg text-xs font-bold transition flex items-center gap-1.5 border {selectedTab === 'matchday' ? 'bg-red-600 text-white border-red-500' : 'text-gray-400 hover:text-white border-[#1e2430] bg-[#0a0c10]'}"
			>
				<span>⚽ Matchday & Derby</span>
			</button>
			<button
				type="button"
				onclick={() => selectCategory('squad')}
				class="px-3.5 py-1.5 rounded-lg text-xs font-bold transition flex items-center gap-1.5 border {selectedTab === 'squad' ? 'bg-red-600 text-white border-red-500' : 'text-gray-400 hover:text-white border-[#1e2430] bg-[#0a0c10]'}"
			>
				<span>👥 Squad & Transfers</span>
			</button>
		</div>

		{#if trendingTags && trendingTags.length > 0}
			<!-- Trending Topic Hashtags -->
			<div class="flex items-center gap-2 flex-wrap text-xs pt-1">
				<span class="text-[11px] font-mono text-gray-500 uppercase font-semibold">Hot Topics:</span>
				{#each trendingTags as t}
					{@const cleanTag = t.tag.replace(/^#+/, '')}
					<button
						type="button"
						onclick={() => handleTagClick(cleanTag)}
						class="px-2.5 py-1 rounded-full text-xs font-mono transition border {selectedTag === cleanTag ? 'bg-red-950/80 text-red-300 border-red-500' : 'bg-[#0a0c10] text-gray-400 border-[#1e2430] hover:border-gray-600 hover:text-gray-200'}"
					>
						#{cleanTag} <span class="text-[10px] text-gray-500 font-sans">({t.count})</span>
					</button>
				{/each}
			</div>
		{/if}
	</div>

	<!-- Post Composer (Interactive for Authenticated, Gentle Prompt for Guests) -->
	<div class="p-5 rounded-xl border border-red-900/30 bg-[#12161f] space-y-4 shadow-sm">
		<div class="flex items-center justify-between">
			<div class="flex items-center gap-2">
				<span class="w-2.5 h-2.5 rounded-full bg-red-600"></span>
				<span class="text-xs font-bold text-white">
					{data.profile?.display_name || (data.user ? data.user.email?.split('@')[0] : 'Gooner Guest')}
				</span>
				<span class="text-[10px] text-amber-400/90 font-mono uppercase bg-amber-500/10 px-1.5 py-0.5 rounded border border-amber-500/20">
					Arsenal Supporter
				</span>
			</div>
			<div class="text-[11px] text-gray-500 font-mono">
				Emirates Stadium Terrace
			</div>
		</div>

		<!-- Post Text Input -->
		<textarea
			bind:value={newPostContent}
			onfocus={() => {
				if (!data.user) requireAuth('post');
			}}
			rows="3"
			placeholder="Share tactical observations, match reactions, lineup notes, or photo link..."
			class="w-full bg-[#0a0c10] border border-[#1e2430] rounded-lg p-3 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-red-500 transition resize-none"
		></textarea>

		<!-- Image Attachment Input (Optional URL / Cloudinary) -->
		{#if showImageInput}
			<div class="p-3 rounded-lg bg-[#0a0c10] border border-[#1e2430] space-y-2">
				<div class="flex items-center justify-between">
					<label for="image-url-input" class="text-xs font-bold text-gray-300 flex items-center gap-1.5">
						<span>🖼️ Image Attachment URL</span>
						<span class="text-[10px] font-normal text-gray-500">(Cloudinary, Unsplash, or direct image link)</span>
					</label>
					<button
						type="button"
						onclick={() => { showImageInput = false; newPostImageUrl = ''; }}
						class="text-xs text-gray-500 hover:text-red-400"
					>
						✕ Cancel
					</button>
				</div>
				<input
					id="image-url-input"
					type="url"
					bind:value={newPostImageUrl}
					placeholder="https://images.unsplash.com/... or https://res.cloudinary.com/..."
					class="w-full bg-[#12161f] border border-[#1e2430] rounded p-2 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-red-500"
				/>
				{#if newPostImageUrl.trim()}
					<div class="relative w-36 h-20 rounded-md overflow-hidden border border-[#1e2430] mt-2 group">
						<img src={newPostImageUrl} alt="Attachment preview" class="w-full h-full object-cover" />
						<button
							type="button"
							onclick={() => (newPostImageUrl = '')}
							class="absolute top-1 right-1 bg-black/80 hover:bg-red-600 text-white rounded-full w-5 h-5 flex items-center justify-center text-[10px]"
							title="Remove photo"
						>
							✕
						</button>
					</div>
				{/if}
			</div>
		{/if}

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

		<!-- Attached Tactical Board Preview -->
		{#if attachedTacticalBoardPreview}
			<div class="p-3.5 rounded-lg bg-[#0a0c10] border border-red-500/30 flex items-center justify-between gap-4">
				<div class="space-y-1">
					<div class="flex items-center gap-2">
						<span class="text-[10px] uppercase font-mono font-bold px-1.5 py-0.5 rounded bg-red-950/70 text-red-400 border border-red-800/40">
							Tactical Board Attached ({attachedTacticalBoardPreview.formation})
						</span>
						<span class="text-xs font-bold text-white">{attachedTacticalBoardPreview.title}</span>
					</div>
					<p class="text-[11px] text-gray-400 font-mono">
						Players: {attachedTacticalBoardPreview.lineup.length} · Annotations: {attachedTacticalBoardPreview.annotations.length}
					</p>
				</div>
				<button
					type="button"
					onclick={() => (selectedTacticalBoardId = '')}
					class="text-xs text-gray-500 hover:text-red-400 px-2 py-1 rounded transition"
				>
					Detach
				</button>
			</div>
		{/if}

		<!-- Composer Footer Controls -->
		<div class="flex items-center justify-between pt-2 border-t border-[#1e2430] flex-wrap gap-2">
			<!-- Attach Buttons / Dropdowns -->
			<div class="flex items-center gap-2 flex-wrap">
				<button
					type="button"
					onclick={() => {
						if (!requireAuth('post')) return;
						showImageInput = !showImageInput;
					}}
					class="px-2.5 py-1.5 rounded bg-[#0a0c10] hover:bg-white/5 border border-[#1e2430] text-xs text-gray-300 font-medium transition flex items-center gap-1.5 {showImageInput ? 'border-red-500 text-red-400' : ''}"
				>
					<span>📷</span>
					<span>{showImageInput ? 'Hide Photo Input' : 'Add Image'}</span>
				</button>

				<select
					bind:value={selectedInsightId}
					class="bg-[#0a0c10] border border-[#1e2430] text-xs text-gray-300 rounded px-2.5 py-1.5 focus:outline-none focus:border-red-500"
				>
					<option value="">Attach Insight (Optional)</option>
					{#each availableInsights as ins}
						<option value={ins.id}>{ins.title}</option>
					{/each}
				</select>

				<select
					bind:value={selectedTacticalBoardId}
					class="bg-[#0a0c10] border border-[#1e2430] text-xs text-gray-300 rounded px-2.5 py-1.5 focus:outline-none focus:border-red-500"
				>
					<option value="">Attach Tactic (Optional)</option>
					{#each availableTacticalBoards as tb}
						<option value={tb.id}>{tb.title} ({tb.formation})</option>
					{/each}
				</select>

				<a
					href="/board"
					class="text-[11px] text-red-400 hover:text-red-300 hover:underline hidden sm:inline"
				>
					+ Create Tactic
				</a>
			</div>

			<!-- Submit Post Button -->
			<button
				type="button"
				onclick={handlePublishPost}
				disabled={isSubmitting || (!newPostContent.trim() && !newPostImageUrl.trim())}
				class="px-5 py-2 rounded-lg bg-red-600 hover:bg-red-500 text-white font-bold text-xs transition disabled:opacity-50 shadow-sm"
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
		<div class="py-16 text-center border border-dashed border-[#1e2430] rounded-xl bg-[#12161f]/50">
			<div class="text-3xl mb-2">🔴</div>
			<p class="text-sm text-gray-300 font-bold">No discussions found in this channel.</p>
			<p class="text-xs text-gray-500 mt-1">Be the first Gooner to share your thoughts above!</p>
		</div>
	{:else}
		<div class="space-y-4">
			{#each posts as post}
				<div class="p-5 rounded-xl border border-[#1e2430] bg-[#12161f] space-y-3.5 hover:border-gray-700/60 transition">
					<!-- Post Author & Meta -->
					<div class="flex items-center justify-between">
						<div class="flex items-center gap-2.5">
							<span class="w-3 h-3 rounded-full bg-red-600"></span>
							<a
								href="/supporters/{encodeURIComponent(post.author_name)}"
								class="text-xs font-bold text-white hover:text-red-400 hover:underline transition"
							>
								{post.author_name}
							</a>
							<span class="text-[10px] font-mono px-2 py-0.5 rounded bg-red-950/60 border border-red-900/40 text-red-300 font-semibold">
								Arsenal
							</span>
							<a
								href="/messages?recipient={encodeURIComponent(post.author_id || post.author_name)}&name={encodeURIComponent(post.author_name)}&club=arsenal"
								class="text-[10px] text-gray-400 hover:text-amber-400 font-semibold transition flex items-center gap-0.5 ml-1"
								title="Challenge {post.author_name} to a private debate"
							>
								<span>💬</span>
								<span>DM</span>
							</a>
						</div>
						<span class="text-[11px] text-gray-500 font-mono">{formatTimestamp(post.created_at)}</span>
					</div>

					<!-- Post Content -->
					<p class="text-xs text-gray-200 leading-relaxed whitespace-pre-line font-sans">
						{post.content}
					</p>

					<!-- Attached Image (With Lightbox Click) -->
					{#if post.image_url}
						<div class="rounded-lg overflow-hidden border border-[#1e2430] max-h-96 bg-black/40">
							<button
								type="button"
								onclick={() => (lightboxImageUrl = post.image_url || null)}
								class="w-full text-left focus:outline-none group relative"
							>
								<img
									src={post.image_url}
									alt="Post attachment"
									class="w-full max-h-96 object-cover hover:opacity-95 transition cursor-zoom-in"
									loading="lazy"
								/>
								<div class="absolute bottom-2 right-2 px-2 py-1 bg-black/70 backdrop-blur rounded text-[10px] text-white opacity-0 group-hover:opacity-100 transition flex items-center gap-1">
									<span>🔍</span>
									<span>Enlarge</span>
								</div>
							</button>
						</div>
					{/if}

					<!-- Attached Insight Post Card -->
					{#if post.insight}
						{@const ins = post.insight}
						<div class="p-4 rounded-lg bg-[#0a0c10] border border-amber-500/30 space-y-3">
							<div class="flex items-center justify-between gap-2">
								<div class="flex items-center gap-2">
									<span class="text-[10px] font-mono font-bold uppercase px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20">
										Data Lab Proof
									</span>
									<h4 class="text-xs font-bold text-white">{ins.title}</h4>
								</div>
								<a
									href="/lab?metric={ins.metric}&teams={ins.team_ids.join(',')}&venue={ins.venue}"
									class="text-[11px] font-bold px-2.5 py-1 rounded bg-white/5 hover:bg-white/10 text-amber-300 border border-amber-500/30 transition flex items-center gap-1"
								>
									<span>View in Lab</span>
									<span>→</span>
								</a>
							</div>

							{#if ins.snapshot && ins.snapshot.series}
								<div class="grid grid-cols-1 sm:grid-cols-{Math.min(ins.snapshot.series.length, 2)} gap-3 pt-2 border-t border-[#1e2430]">
									{#each ins.snapshot.series as item}
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
							{/if}
						</div>
					{/if}

					<!-- Attached Tactical Board Post Card -->
					{#if post.tactical_board}
						{@const tb = post.tactical_board}
						<div class="p-4 rounded-lg bg-[#0a0c10] border border-red-500/30 space-y-3">
							<div class="flex items-center justify-between gap-2">
								<div class="flex items-center gap-2">
									<span class="text-[10px] font-mono font-bold uppercase px-2 py-0.5 rounded bg-red-950/80 text-red-300 border border-red-800/40">
										Lineup Blueprint ({tb.formation})
									</span>
									<h4 class="text-xs font-bold text-white">{tb.title}</h4>
								</div>
								<a
									href="/board"
									class="text-[11px] font-bold px-2.5 py-1 rounded bg-white/5 hover:bg-white/10 text-red-300 border border-red-500/30 transition flex items-center gap-1"
								>
									<span>Open in Dugout</span>
									<span>→</span>
								</a>
							</div>

							{#if tb.tactical_notes}
								<p class="text-[11px] text-gray-300 leading-relaxed italic bg-[#12161f] p-2.5 rounded border border-[#1e2430]">
									"{tb.tactical_notes}"
								</p>
							{/if}

							<!-- Embedded Mini Pitch -->
							<div class="max-w-md mx-auto rounded-lg overflow-hidden border border-emerald-950/80">
								<TacticalBoardComponent
									lineup={tb.lineup}
									annotations={tb.annotations}
									readonly={true}
									showGuides={false}
								/>
							</div>
						</div>
					{/if}

					<!-- Post Action Bar -->
					<div class="flex items-center gap-4 pt-2 border-t border-[#1e2430] text-xs">
						<!-- Cheer Reaction -->
						<button
							type="button"
							onclick={() => handleToggleReaction(post)}
							class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition {post.user_reacted ? 'bg-amber-500/10 text-amber-400 font-bold border border-amber-500/30' : 'text-gray-400 hover:text-white hover:bg-white/5'}"
						>
							<span>⚽ Cheer</span>
							<span class="font-mono">{post.reactions_count}</span>
						</button>

						<!-- Comments Toggle -->
						<button
							type="button"
							onclick={() => toggleCommentSection(post.id)}
							class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-gray-400 hover:text-white hover:bg-white/5 transition"
						>
							<span>💬 Debates ({post.comments_count})</span>
						</button>
					</div>

					<!-- Comments Thread (Expandable) -->
					{#if expandedComments[post.id]}
						<div class="pt-3 border-t border-[#1e2430] space-y-3">
							<!-- Comments List -->
							{#if postComments[post.id] && postComments[post.id].length > 0}
								<div class="space-y-2">
									{#each postComments[post.id] as comment}
										<div class="p-2.5 rounded bg-[#0a0c10] border border-[#1e2430] space-y-1">
											<div class="flex items-center justify-between">
												<div class="flex items-center gap-1.5">
													<span class="w-1.5 h-1.5 rounded-full bg-red-600"></span>
													<a
														href="/supporters/{encodeURIComponent(comment.author_name)}"
														class="text-[11px] font-bold text-gray-300 hover:text-white hover:underline transition"
													>
														{comment.author_name}
													</a>
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
									placeholder={data.user ? "Write your debrief or reply..." : "Sign in to reply to this debrief..."}
									class="flex-1 bg-[#0a0c10] border border-[#1e2430] rounded p-2 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-red-500"
									onfocus={() => {
										if (!data.user) requireAuth('comment');
									}}
									onkeydown={(e) => e.key === 'Enter' && handleAddComment(post.id)}
								/>
								<button
									type="button"
									onclick={() => handleAddComment(post.id)}
									disabled={isSubmittingComment[post.id] || !newCommentText[post.id]?.trim()}
									class="px-3.5 py-2 rounded bg-red-600 hover:bg-red-500 text-xs font-bold text-white transition disabled:opacity-50"
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

<!-- Guest Auth Gate Modal -->
{#if showAuthModal}
	<div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fade-in">
		<div class="bg-[#12161f] border border-red-800/40 rounded-2xl p-6 max-w-md w-full space-y-5 shadow-2xl relative">
			<button
				type="button"
				onclick={() => (showAuthModal = false)}
				class="absolute top-4 right-4 text-gray-400 hover:text-white text-lg p-1"
			>
				✕
			</button>

			<div class="text-center space-y-2">
				<div class="w-12 h-12 mx-auto rounded-full bg-red-950/80 border border-red-800/60 flex items-center justify-center text-xl">
					🔴
				</div>
				<h3 class="text-lg font-black text-white uppercase tracking-tight">
					Join the Terrace Discussion
				</h3>
				<p class="text-xs text-gray-300 leading-relaxed">
					{#if authModalReason === 'post'}
						Sign in to publish tactical debriefs, share lineup blueprints, and attach match photos.
					{:else if authModalReason === 'comment'}
						Sign in to debate match moments and reply to fellow Gooners on the Terrace.
					{:else}
						Sign in to cheer posts and participate in supporter debates.
					{/if}
				</p>
			</div>

			<div class="p-3 rounded-lg bg-[#0a0c10] border border-[#1e2430] text-[11px] text-gray-400 text-center">
				Browsing the Terrace and reading discussions is free for all visitors. Authenticated accounts keep our community authentic and spam-free!
			</div>

			<div class="flex flex-col gap-2.5">
				<a
					href="/login"
					class="w-full py-2.5 text-center font-bold text-xs bg-red-600 hover:bg-red-500 text-white rounded-lg transition shadow-md"
				>
					Sign In
				</a>
				<a
					href="/signup"
					class="w-full py-2.5 text-center font-bold text-xs bg-white/5 hover:bg-white/10 text-gray-200 border border-[#1e2430] rounded-lg transition"
				>
					Create Free Gooner Account
				</a>
				<button
					type="button"
					onclick={() => (showAuthModal = false)}
					class="text-[11px] text-gray-500 hover:text-gray-300 pt-1"
				>
					Continue browsing as Guest
				</button>
			</div>
		</div>
	</div>
{/if}

<!-- Lightbox Modal for Post Images -->
{#if lightboxImageUrl}
	<div
		class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/90 backdrop-blur-md cursor-zoom-out"
		onclick={() => (lightboxImageUrl = null)}
		role="button"
		tabindex="0"
		onkeydown={(e) => e.key === 'Escape' && (lightboxImageUrl = null)}
	>
		<div class="relative max-w-5xl max-h-[90vh]">
			<button
				type="button"
				onclick={() => (lightboxImageUrl = null)}
				class="absolute -top-10 right-0 text-white text-sm bg-white/10 hover:bg-white/20 px-3 py-1 rounded"
			>
				✕ Close
			</button>
			<img
				src={lightboxImageUrl}
				alt="Full size preview"
				class="max-w-full max-h-[85vh] object-contain rounded-lg border border-white/20 shadow-2xl"
			/>
		</div>
	</div>
{/if}
