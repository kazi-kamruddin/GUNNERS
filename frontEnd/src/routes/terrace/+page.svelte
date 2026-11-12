<script lang="ts">
	import {
		ApiError,
		fetchPosts,
		createPost,
		toggleReaction,
		fetchComments,
		createComment
	} from '$lib/api/football';
	import TacticalBoardComponent from '$lib/components/TacticalBoard.svelte';
	import type { Post, PostComment, Insight, TopicTag, TacticalBoard } from '$lib/types/football';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	let selectedTab = $state<'all' | 'tactics' | 'matchday' | 'squad'>('all');
	let posts = $state<Post[]>([]);
	let availableInsights = $state<Insight[]>([]);
	let availableTacticalBoards = $state<TacticalBoard[]>([]);
	let isLoadingFeed = $state(false);

	let newPostContent = $state('');
	let newPostImageUrl = $state('');
	let showImageInput = $state(false);
	let selectedInsightId = $state<string>('');
	let selectedTacticalBoardId = $state<string>('');
	let isSubmitting = $state(false);

	let showAuthModal = $state(false);
	let authModalReason = $state<'post' | 'comment' | 'react'>('post');
	let errorBanner = $state<{ message: string; isAuth?: boolean } | null>(null);
	let lightboxImageUrl = $state<string | null>(null);

	let expandedComments = $state<Record<string, boolean>>({});
	let postComments = $state<Record<string, PostComment[]>>({});
	let newCommentText = $state<Record<string, string>>({});
	let isSubmittingComment = $state<Record<string, boolean>>({});

	let searchQuery = $state('');
	let selectedTag = $state('');
	let trendingTags = $state<TopicTag[]>([]);

	let imageToggleLabel = $derived(showImageInput ? 'Hide photo input' : 'Add image');
	let publishPostLabel = $derived(isSubmitting ? 'Publishing…' : 'Publish to Terrace');
	let commentPlaceholder = $derived(
		data.user ? 'Write your debrief or reply…' : 'Sign in to reply to this debrief…'
	);

	$effect(() => {
		posts = data.initialPosts;
		availableInsights = data.availableInsights;
		availableTacticalBoards = data.availableTacticalBoards || [];
		searchQuery = data.initialSearch || '';
		selectedTag = data.initialTag || '';
		trendingTags = data.trendingTags || [];
	});

	function requireAuth(reason: 'post' | 'comment' | 'react'): boolean {
		if (!data.user || !data.session?.access_token) {
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
				tagVal !== undefined ? tagVal : selectedTag,
				data.session?.access_token
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
		errorBanner = null;
		try {
			const authorName = data.profile?.display_name || data.user?.email?.split('@')[0] || 'Gooner';
			const authorClub = 'arsenal';

			const created = await createPost(
				{
					content: newPostContent.trim(),
					club_id: 'arsenal',
					image_url: newPostImageUrl.trim() || null,
					insight_id: selectedInsightId || null,
					tactical_board_id: selectedTacticalBoardId || null,
					author_name: authorName,
					author_club_id: authorClub
				},
				data.session?.access_token
			);

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
		} catch (err) {
			const isAuth = err instanceof ApiError && err.status === 401;
			errorBanner = {
				message: isAuth
					? 'Please sign in to publish a post to The Terrace.'
					: err instanceof ApiError
						? err.detail
						: 'Could not publish your post. Please try again.',
				isAuth
			};
		} finally {
			isSubmitting = false;
		}
	}

	async function handleToggleReaction(post: Post) {
		if (!requireAuth('react')) return;

		errorBanner = null;
		const userId = data.user?.id || null;
		const wasReacted = post.user_reacted;
		post.user_reacted = !wasReacted;
		post.reactions_count += wasReacted ? -1 : 1;

		try {
			const res = await toggleReaction(post.id, userId, 'cheer', data.session?.access_token);
			post.reactions_count = res.total_reactions;
			post.user_reacted = res.action === 'added';
		} catch (err) {
			post.user_reacted = wasReacted;
			post.reactions_count += wasReacted ? 1 : -1;
			const isAuth = err instanceof ApiError && err.status === 401;
			errorBanner = {
				message: isAuth
					? 'Please sign in to cheer posts on The Terrace.'
					: err instanceof ApiError
						? err.detail
						: 'Could not update reaction. Please try again.',
				isAuth
			};
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

		errorBanner = null;
		isSubmittingComment[postId] = true;
		const authorName = data.profile?.display_name || data.user?.email?.split('@')[0] || 'Gooner';
		const authorClub = 'arsenal';

		try {
			const comment = await createComment(
				postId,
				text,
				authorName,
				authorClub,
				data.session?.access_token
			);
			if (comment) {
				const current = postComments[postId] || [];
				postComments[postId] = [...current, comment];
				newCommentText[postId] = '';

				const targetPost = posts.find((p) => p.id === postId);
				if (targetPost) targetPost.comments_count += 1;
			}
		} catch (err) {
			const isAuth = err instanceof ApiError && err.status === 401;
			errorBanner = {
				message: isAuth
					? 'Please sign in to reply on The Terrace.'
					: err instanceof ApiError
						? err.detail
						: 'Could not post your reply. Please try again.',
				isAuth
			};
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

<div class="container py-12 space-y-12 max-w-4xl">
	<!-- Page Header -->
	<div class="border-b-2 border-rule-2 pb-8 flex flex-col sm:flex-row sm:items-end justify-between gap-6">
		<div class="space-y-3">
			<h1>The Terrace</h1>
			<p class="lead text-ink-2">
				Share match observations, debate tactical lineups, attach Data Lab snapshots, and connect with fellow Gooners worldwide.
			</p>
		</div>

		{#if !data.user}
			<div class="border-t border-rule pt-3 text-xs text-ink-2 max-w-xs space-y-1">
				<div class="font-bold text-accent">Guest browsing mode</div>
				<p class="text-muted leading-snug">
					Read all posts, tactics, and debriefs freely. <a href="/login" class="text-ink underline font-semibold hover:text-accent">Sign in</a> to join debates or publish.
				</p>
			</div>
		{/if}
	</div>

	{#if errorBanner}
		<div role="alert" class="p-3.5 rounded-card bg-paper-2 border border-rule text-error text-xs flex items-center justify-between gap-4">
			<div class="flex items-center gap-3 flex-wrap">
				<span>{errorBanner.message}</span>
				{#if errorBanner.isAuth}
					<a href="/login" class="underline text-ink font-semibold hover:text-accent">Sign in</a>
				{/if}
			</div>
			<button
				type="button"
				onclick={() => (errorBanner = null)}
				class="text-muted hover:text-ink font-semibold shrink-0"
			>
				Dismiss
			</button>
		</div>
	{/if}

	<!-- Search & Category Filters -->
	<section class="space-y-5">
		<div class="flex items-center gap-3">
			<div class="relative flex-1">
				<input
					type="text"
					aria-label="Search Terrace discussions"
					bind:value={searchQuery}
					onkeydown={(e) => e.key === 'Enter' && handleSearch()}
					placeholder="Search discussions, tactics, player debriefs (#Saka, #Derby, #Arteta)…"
					class="w-full h-10 bg-paper-2 border border-rule rounded-card pl-9 pr-3 text-xs text-ink placeholder-muted"
				/>
				<svg class="w-4 h-4 text-muted absolute left-3 top-3" aria-hidden="true" fill="none" viewBox="0 0 24 24" stroke="currentColor">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
				</svg>
			</div>
			<button
				type="button"
				onclick={handleSearch}
				class="h-10 px-4 rounded-card bg-accent hover:opacity-95 text-accent-ink text-xs font-semibold transition-opacity"
			>
				Search
			</button>
			{#if searchQuery || selectedTag || selectedTab !== 'all'}
				<button
					type="button"
					onclick={clearFilters}
					class="h-10 px-3.5 rounded-card border border-rule bg-paper-2 hover:bg-paper-3 text-ink-2 hover:text-ink text-xs font-semibold transition-colors"
				>
					Reset
				</button>
			{/if}
		</div>

		<!-- Channel Navigation Tabs -->
		<div class="flex items-center gap-2 border-y border-rule py-3 flex-wrap">
			<button
				type="button"
				onclick={() => selectCategory('all')}
				class="h-9 px-3.5 rounded-card text-xs font-semibold transition-colors border {selectedTab === 'all' && !selectedTag ? 'bg-accent text-accent-ink border-accent' : 'text-ink-2 hover:text-ink border-rule bg-paper-2'}"
			>
				All Terrace
			</button>
			<button
				type="button"
				onclick={() => selectCategory('tactics')}
				class="h-9 px-3.5 rounded-card text-xs font-semibold transition-colors border {selectedTab === 'tactics' ? 'bg-accent text-accent-ink border-accent' : 'text-ink-2 hover:text-ink border-rule bg-paper-2'}"
			>
				Tactical debriefs
			</button>
			<button
				type="button"
				onclick={() => selectCategory('matchday')}
				class="h-9 px-3.5 rounded-card text-xs font-semibold transition-colors border {selectedTab === 'matchday' ? 'bg-accent text-accent-ink border-accent' : 'text-ink-2 hover:text-ink border-rule bg-paper-2'}"
			>
				Matchday & derby
			</button>
			<button
				type="button"
				onclick={() => selectCategory('squad')}
				class="h-9 px-3.5 rounded-card text-xs font-semibold transition-colors border {selectedTab === 'squad' ? 'bg-accent text-accent-ink border-accent' : 'text-ink-2 hover:text-ink border-rule bg-paper-2'}"
			>
				Squad & transfers
			</button>
		</div>

		{#if trendingTags && trendingTags.length > 0}
			<div class="flex items-center gap-2 flex-wrap text-xs">
				<span class="text-muted font-semibold">Topics:</span>
				{#each trendingTags as t}
					{@const cleanTag = t.tag.replace(/^#+/, '')}
					{@const tagLabel = `#${cleanTag} (${t.count})`}
					<button
						type="button"
						onclick={() => handleTagClick(cleanTag)}
						class="h-7 px-2.5 rounded-card text-xs transition-colors border {selectedTag === cleanTag ? 'bg-paper-3 text-accent border-rule-2 font-semibold' : 'bg-paper-2 text-ink-2 border-rule hover:text-ink'}"
					>
						{tagLabel}
					</button>
				{/each}
			</div>
		{/if}
	</section>

	<!-- Post Composer -->
	<section class="border-t-2 border-rule-2 pt-6 space-y-4">
		<div class="flex items-center justify-between text-xs">
			<div class="flex items-center gap-2">
				<span class="font-bold text-ink">
					{data.profile?.display_name || (data.user ? data.user.email?.split('@')[0] : 'Gooner guest')}
				</span>
				<span class="text-accent-2 font-semibold">Arsenal supporter</span>
			</div>
			<span class="text-muted">Emirates Stadium Terrace</span>
		</div>

		<textarea
			aria-label="Write a Terrace post"
			bind:value={newPostContent}
			onfocus={() => {
				if (!data.user) requireAuth('post');
			}}
			rows="3"
			placeholder="Share tactical observations, match reactions, lineup notes, or a photo link…"
			class="w-full bg-paper-2 border border-rule rounded-card p-3 text-xs text-ink placeholder-muted resize-none"
		></textarea>

		{#if showImageInput}
			<div class="border-t border-rule pt-3 space-y-2">
				<div class="flex items-center justify-between text-xs">
					<label for="image-url-input" class="font-semibold text-ink-2">
						Image attachment URL <span class="font-normal text-muted">(Cloudinary, Unsplash, or direct link)</span>
					</label>
					<button
						type="button"
						onclick={() => { showImageInput = false; newPostImageUrl = ''; }}
						class="text-muted hover:text-error font-semibold"
					>
						Cancel
					</button>
				</div>
				<input
					id="image-url-input"
					type="url"
					bind:value={newPostImageUrl}
					placeholder="https://images.unsplash.com/… or https://res.cloudinary.com/…"
					class="w-full h-10 bg-paper-2 border border-rule rounded-card px-3 text-xs text-ink placeholder-muted"
				/>
				{#if newPostImageUrl.trim()}
					<div class="relative w-36 h-20 overflow-hidden border border-rule mt-2">
						<img src={newPostImageUrl} alt="Attachment preview" class="w-full h-full object-cover" />
						<button
							type="button"
							onclick={() => (newPostImageUrl = '')}
							class="absolute top-1 right-1 bg-paper/90 hover:bg-accent text-ink rounded-card px-1.5 py-0.5 text-xs font-semibold"
							title="Remove photo"
						>
							Remove
						</button>
					</div>
				{/if}
			</div>
		{/if}

		{#if attachedInsightPreview}
			<div class="border-t border-rule pt-3 flex items-center justify-between gap-4 text-xs">
				<div class="space-y-1">
					<div class="flex items-center gap-2">
						<span class="text-accent-2 font-semibold">Insight attached</span>
						<span class="font-bold text-ink">{attachedInsightPreview.title}</span>
					</div>
					<p class="text-muted">
						Metric: {attachedInsightPreview.metric}, venue: {attachedInsightPreview.venue}
					</p>
				</div>
				<button
					type="button"
					onclick={() => (selectedInsightId = '')}
					class="text-muted hover:text-error font-semibold"
				>
					Detach
				</button>
			</div>
		{/if}

		{#if attachedTacticalBoardPreview}
			<div class="border-t border-rule pt-3 flex items-center justify-between gap-4 text-xs">
				<div class="space-y-1">
					<div class="flex items-center gap-2">
						<span class="text-accent font-semibold">
							Tactical board attached (<span class="num font-outlier">{attachedTacticalBoardPreview.formation}</span>)
						</span>
						<span class="font-bold text-ink">{attachedTacticalBoardPreview.title}</span>
					</div>
					<p class="text-muted num font-outlier">
						Players: {attachedTacticalBoardPreview.lineup.length}, vectors: {attachedTacticalBoardPreview.annotations.length}
					</p>
				</div>
				<button
					type="button"
					onclick={() => (selectedTacticalBoardId = '')}
					class="text-muted hover:text-error font-semibold"
				>
					Detach
				</button>
			</div>
		{/if}

		<div class="flex items-center justify-between pt-3 border-t border-rule flex-wrap gap-3">
			<div class="flex items-center gap-2.5 flex-wrap">
				<button
					type="button"
					onclick={() => {
						if (!requireAuth('post')) return;
						showImageInput = !showImageInput;
					}}
					class="h-9 px-3 rounded-card bg-paper-2 hover:bg-paper-3 border border-rule text-xs text-ink-2 font-semibold transition-colors {showImageInput ? 'border-accent text-accent' : ''}"
				>
					{imageToggleLabel}
				</button>

				<select
					aria-label="Attach Data Lab insight"
					bind:value={selectedInsightId}
					class="h-9 bg-paper-2 border border-rule text-xs text-ink-2 rounded-card px-2.5"
				>
					<option value="">Attach insight (optional)</option>
					{#each availableInsights as ins}
						<option value={ins.id}>{ins.title}</option>
					{/each}
				</select>

				<select
					aria-label="Attach tactical board"
					bind:value={selectedTacticalBoardId}
					class="h-9 bg-paper-2 border border-rule text-xs text-ink-2 rounded-card px-2.5"
				>
					<option value="">Attach tactic (optional)</option>
					{#each availableTacticalBoards as tb}
						<option value={tb.id}>{tb.title} ({tb.formation})</option>
					{/each}
				</select>

				<a
					href="/board"
					class="text-xs text-accent hover:text-ink font-semibold transition-colors"
				>
					Create tactic
				</a>
			</div>

			<button
				type="button"
				onclick={handlePublishPost}
				disabled={isSubmitting || (!newPostContent.trim() && !newPostImageUrl.trim())}
				class="h-9 px-5 rounded-card bg-accent hover:opacity-95 text-accent-ink font-semibold text-xs transition-opacity"
			>
				{publishPostLabel}
			</button>
		</div>
	</section>

	<!-- Feed Stream -->
	{#if isLoadingFeed}
		<div class="py-12 text-muted text-sm">
			Loading Terrace discussions…
		</div>
	{:else if posts.length === 0}
		<div class="py-12 border-t border-rule space-y-1">
			<p class="text-sm text-ink font-bold">No discussions found in this channel.</p>
			<p class="text-xs text-muted">Be the first Gooner to share your thoughts above.</p>
		</div>
	{:else}
		<div class="divide-y divide-rule border-t border-rule">
			{#each posts as post}
				{@const debateBtnLabel = `Debates (${post.comments_count})`}
				{@const cheerBtnLabel = `Cheer (${post.reactions_count})`}
				<article class="py-8 space-y-4">
					<!-- Post Author & Meta -->
					<div class="flex items-center justify-between text-xs">
						<div class="flex items-center gap-3">
							<a
								href="/supporters/{encodeURIComponent(post.author_name)}"
								class="font-bold text-ink hover:text-accent transition-colors"
							>
								{post.author_name}
							</a>
							<span class="text-muted">Arsenal</span>
							<a
								href="/messages?recipient={encodeURIComponent(post.author_id || post.author_name)}&name={encodeURIComponent(post.author_name)}&club=arsenal"
								class="text-accent-2 hover:text-ink font-semibold transition-colors"
								title="Challenge {post.author_name} to a private debate"
							>
								Direct debate
							</a>
						</div>
						<span class="text-muted num font-outlier">{formatTimestamp(post.created_at)}</span>
					</div>

					<!-- Post Content -->
					<p class="text-sm text-ink leading-relaxed whitespace-pre-line">
						{post.content}
					</p>

					<!-- Attached Image -->
					{#if post.image_url}
						<div class="rounded-card overflow-hidden border border-rule max-h-96 bg-paper-2">
							<button
								type="button"
								onclick={() => (lightboxImageUrl = post.image_url || null)}
								class="w-full text-left group relative"
							>
								<img
									src={post.image_url}
									alt="Post attachment"
									class="w-full max-h-96 object-cover hover:opacity-95 transition-opacity cursor-zoom-in"
									loading="lazy"
								/>
							</button>
						</div>
					{/if}

					<!-- Attached Insight -->
					{#if post.insight}
						{@const ins = post.insight}
						<div class="border-l-2 border-accent-2 pl-4 py-2 space-y-3 bg-paper-2 p-4">
							<div class="flex items-center justify-between gap-2 flex-wrap">
								<div class="space-y-0.5">
									<span class="text-xs font-semibold text-accent-2">Data Lab snapshot</span>
									<h3 class="text-sm font-bold text-ink">{ins.title}</h3>
								</div>
								<a
									href="/lab?metric={ins.metric}&teams={ins.team_ids.join(',')}&venue={ins.venue}"
									class="text-xs font-semibold text-accent-2 hover:text-ink transition-colors"
								>
									View in Data Lab
								</a>
							</div>

							{#if ins.snapshot && ins.snapshot.series}
								<div class="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2 border-t border-rule text-xs">
									{#each ins.snapshot.series as item}
										<div class="space-y-1">
											<div class="flex items-center justify-between">
												<span class="text-ink font-bold">{item.team_name}</span>
												<span class="num font-outlier font-bold text-ink">
													{item.metric_value} <span class="text-accent-2">{item.unit}</span>
												</span>
											</div>
											<div class="flex items-center justify-between text-muted num font-outlier">
												<span>{item.matches_played} matches</span>
												<span>{item.wins}W / {item.draws}D / {item.losses}L</span>
											</div>
										</div>
									{/each}
								</div>
							{/if}
						</div>
					{/if}

					<!-- Attached Tactical Board -->
					{#if post.tactical_board}
						{@const tb = post.tactical_board}
						<div class="border-l-2 border-accent pl-4 py-2 space-y-3 bg-paper-2 p-4">
							<div class="flex items-center justify-between gap-2 flex-wrap">
								<div class="space-y-0.5">
									<span class="text-xs font-semibold text-accent">
										Lineup blueprint (<span class="num font-outlier">{tb.formation}</span>)
									</span>
									<h3 class="text-sm font-bold text-ink">{tb.title}</h3>
								</div>
								<a
									href="/board"
									class="text-xs font-semibold text-accent hover:text-ink transition-colors"
								>
									Open in lineup studio
								</a>
							</div>

							{#if tb.tactical_notes}
								<p class="text-xs text-ink-2 leading-relaxed">
									“{tb.tactical_notes}”
								</p>
							{/if}

							<div class="max-w-md mx-auto">
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
					<div class="flex items-center gap-3 pt-2 text-xs">
						<button
							type="button"
							onclick={() => handleToggleReaction(post)}
							class="h-8 px-3 rounded-card transition-colors border flex items-center gap-1.5 {post.user_reacted ? 'bg-paper-3 text-accent-2 font-bold border-rule-2' : 'bg-paper-2 text-ink-2 border-rule hover:text-ink'}"
						>
							<span>{cheerBtnLabel}</span>
						</button>

						<button
							type="button"
							onclick={() => toggleCommentSection(post.id)}
							class="h-8 px-3 rounded-card bg-paper-2 border border-rule text-ink-2 hover:text-ink transition-colors font-semibold"
						>
							{debateBtnLabel}
						</button>
					</div>

					<!-- Comments Thread -->
					{#if expandedComments[post.id]}
						<div class="pt-4 border-t border-rule space-y-4">
							{#if postComments[post.id] && postComments[post.id].length > 0}
								<div class="divide-y divide-rule">
									{#each postComments[post.id] as comment}
										<div class="py-3 space-y-1 text-xs">
											<div class="flex items-center justify-between">
												<a
													href="/supporters/{encodeURIComponent(comment.author_name)}"
													class="font-bold text-ink hover:text-accent transition-colors"
												>
													{comment.author_name}
												</a>
												<span class="text-muted num font-outlier">{formatTimestamp(comment.created_at)}</span>
											</div>
											<p class="text-ink-2 leading-relaxed">{comment.content}</p>
										</div>
									{/each}
								</div>
							{:else}
								<p class="text-xs text-muted">No comments yet. Join the conversation below.</p>
							{/if}

							<div class="flex items-center gap-2">
								<input
									type="text"
									aria-label="Reply to discussion"
									bind:value={newCommentText[post.id]}
									placeholder={commentPlaceholder}
									class="flex-1 h-9 bg-paper-2 border border-rule rounded-card px-3 text-xs text-ink placeholder-muted"
									onfocus={() => {
										if (!data.user) requireAuth('comment');
									}}
									onkeydown={(e) => e.key === 'Enter' && handleAddComment(post.id)}
								/>
								<button
									type="button"
									onclick={() => handleAddComment(post.id)}
									disabled={isSubmittingComment[post.id] || !newCommentText[post.id]?.trim()}
									class="h-9 px-4 rounded-card bg-accent hover:opacity-95 text-xs font-semibold text-accent-ink transition-opacity"
								>
									Reply
								</button>
							</div>
						</div>
					{/if}
				</article>
			{/each}
		</div>
	{/if}
</div>

<!-- Guest Auth Gate Modal -->
{#if showAuthModal}
	<div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-paper/85">
		<div class="bg-paper-2 border-t-2 border-rule-2 p-6 max-w-md w-full space-y-5 relative">
			<button
				type="button"
				onclick={() => (showAuthModal = false)}
				class="absolute top-4 right-4 text-muted hover:text-ink text-xs font-semibold"
			>
				Close
			</button>

			<div class="space-y-2">
				<h2 class="text-lg font-bold text-ink">
					Join the Terrace discussion
				</h2>
				<p class="text-xs text-ink-2 leading-relaxed">
					{#if authModalReason === 'post'}
						Sign in to publish tactical debriefs, share lineup blueprints, and attach match photos.
					{:else if authModalReason === 'comment'}
						Sign in to debate match moments and reply to fellow Gooners on the Terrace.
					{:else}
						Sign in to cheer posts and participate in supporter debates.
					{/if}
				</p>
			</div>

			<p class="text-xs text-muted border-t border-rule pt-3">
				Browsing the Terrace and reading discussions is free for all visitors. Authenticated accounts keep our community authentic.
			</p>

			<div class="flex flex-col gap-2.5 pt-1">
				<a
					href="/login"
					class="w-full h-10 inline-flex items-center justify-center font-semibold text-xs bg-accent hover:opacity-95 text-accent-ink rounded-card transition-opacity"
				>
					Sign in
				</a>
				<a
					href="/signup"
					class="w-full h-10 inline-flex items-center justify-center font-semibold text-xs bg-paper border border-rule text-ink rounded-card transition-colors hover:bg-paper-3"
				>
					Create free Gooner account
				</a>
				<button
					type="button"
					onclick={() => (showAuthModal = false)}
					class="text-xs text-muted hover:text-ink pt-1"
				>
					Browse as guest
				</button>
			</div>
		</div>
	</div>
{/if}

<!-- Lightbox Modal for Post Images -->
{#if lightboxImageUrl}
	<div
		class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-paper/90 cursor-zoom-out"
		onclick={() => (lightboxImageUrl = null)}
		role="button"
		tabindex="0"
		onkeydown={(e) => e.key === 'Escape' && (lightboxImageUrl = null)}
	>
		<div class="relative max-w-5xl max-h-[90vh]">
			<button
				type="button"
				onclick={() => (lightboxImageUrl = null)}
				class="absolute -top-10 right-0 text-ink text-xs bg-paper-2 border border-rule px-3 py-1 rounded-card font-semibold"
			>
				Close
			</button>
			<img
				src={lightboxImageUrl}
				alt="Full size preview"
				class="max-w-full max-h-[85vh] object-contain rounded-card border border-rule"
			/>
		</div>
	</div>
{/if}
