<script lang="ts">
	import { page } from '$app/state';
	import { focusTrap } from '$lib/actions/focusTrap';
	import StateBanner from '$lib/components/StateBanner.svelte';
	import {
		ApiError,
		fetchPostsResult,
		fetchTrendingTags,
		createPost,
		toggleReaction,
		fetchCommentsStrict,
		createComment
	} from '$lib/api/football';
	import {
		deleteTerracePost,
		deleteTerraceComment,
		updateTerracePost,
		updateTerraceComment
	} from '$lib/api/community';
	import TacticalBoardComponent from '$lib/components/TacticalBoard.svelte';
	import type { Post, PostComment, Insight, TopicTag, TacticalBoard } from '$lib/types/football';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	let selectedTab = $state<'all' | 'insights' | 'tactics' | 'photos'>('all');
	let posts = $state<Post[]>([]);
	let postsError = $state<string | null>(null);
	let availableInsights = $state<Insight[]>([]);
	let availableTacticalBoards = $state<TacticalBoard[]>([]);
	let isLoadingFeed = $state(false);

	let newPostContent = $state('');
	let newPostImageUrl = $state('');
	let showImageInput = $state(false);
	let isUploadingImage = $state(false);
	let imageUploadStatus = $state<string | null>(null);
	let imageUploadError = $state<string | null>(null);
	let newPostPreviewFailed = $state(false);
	let imageFileInput = $state<HTMLInputElement | null>(null);
	let selectedInsightId = $state<string>('');
	let selectedTacticalBoardId = $state<string>('');
	let isSubmitting = $state(false);
	let hadImageAttachment = false;

	let confirmDeletePostId = $state<string | null>(null);
	let deletingPostId = $state<string | null>(null);
	let confirmDeleteCommentId = $state<string | null>(null);
	let deletingCommentId = $state<string | null>(null);

	let editingPostId = $state<string | null>(null);
	let editPostContent = $state('');
	let editPostImageUrl = $state('');
	let editPostPreviewFailed = $state(false);
	let isUploadingEditImage = $state(false);
	let editImageUploadError = $state<string | null>(null);
	let savingPostId = $state<string | null>(null);
	let editPostError = $state<string | null>(null);

	let editingCommentId = $state<string | null>(null);
	let editCommentContent = $state('');
	let savingCommentId = $state<string | null>(null);
	let editCommentError = $state<string | null>(null);

	let showAuthModal = $state(false);
	let authModalReason = $state<'post' | 'comment' | 'react'>('post');
	let errorBanner = $state<{ message: string; isAuth?: boolean } | null>(null);
	let postActionErrors = $state<Record<string, string | null>>({});
	let brokenPostImages = $state<Record<string, boolean>>({});
	let lightboxImageUrl = $state<string | null>(null);

	let expandedComments = $state<Record<string, boolean>>({});
	let postComments = $state<Record<string, PostComment[]>>({});
	let loadingComments = $state<Record<string, boolean>>({});
	let commentLoadErrors = $state<Record<string, string | null>>({});
	let newCommentText = $state<Record<string, string>>({});
	let isSubmittingComment = $state<Record<string, boolean>>({});

	let searchQuery = $state('');
	let selectedTag = $state('');
	let trendingTags = $state<TopicTag[]>([]);

	const ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'image/gif'];
	const MAX_IMAGE_BYTES = 5 * 1024 * 1024;
	const MAX_POST_CHARS = 2000;
	const MAX_COMMENT_CHARS = 1000;

	let imageToggleLabel = $derived(showImageInput ? 'Hide photo input' : 'Add image');
	let publishPostLabel = $derived(
		isUploadingImage ? 'Uploading photo…' : isSubmitting ? 'Publishing…' : 'Publish to Terrace'
	);
	let editSaveLabel = $derived(
		isUploadingEditImage
			? 'Uploading…'
			: savingPostId && savingPostId === editingPostId
				? 'Saving…'
				: 'Save'
	);
	let authNext = $derived(encodeURIComponent(page.url.pathname + page.url.search));
	let needsCaptionHint = $derived(Boolean(newPostImageUrl.trim() && !newPostContent.trim()));
	let lightboxAuthor = $derived(
		lightboxImageUrl
			? posts.find((p) => p.image_url === lightboxImageUrl)?.author_name || 'supporter'
			: 'supporter'
	);

	$effect(() => {
		const trimmed = newPostImageUrl.trim();
		if (trimmed) {
			hadImageAttachment = true;
			newPostPreviewFailed = false;
		} else {
			imageUploadStatus = null;
			newPostPreviewFailed = false;
			if (hadImageAttachment || !showImageInput) {
				imageUploadError = null;
				hadImageAttachment = false;
			}
			if (imageFileInput) imageFileInput.value = '';
		}
	});

	$effect(() => {
		if (editPostImageUrl !== undefined) {
			editPostPreviewFailed = false;
		}
	});

	$effect(() => {
		posts = data.initialPosts;
		postsError = data.postsError ?? null;
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
		postsError = null;
		try {
			const result = await fetchPostsResult(
				'arsenal',
				data.user?.id,
				searchVal !== undefined ? searchVal : searchQuery,
				tagVal !== undefined ? tagVal : selectedTag,
				data.session?.access_token
			);
			if (result.error) {
				postsError = result.error;
				return;
			}
			posts = result.data;
		} finally {
			isLoadingFeed = false;
		}
	}

	async function refreshTrendingTags() {
		try {
			trendingTags = await fetchTrendingTags();
		} catch {
			// Keep existing tags if tag refresh fails
		}
	}

	function selectCategory(tab: 'all' | 'insights' | 'tactics' | 'photos') {
		selectedTab = tab;
	}

	async function handleSearch() {
		await reloadFeed(searchQuery, selectedTag);
	}

	async function handleTagClick(tag: string) {
		const clean = tag.replace(/^#+/, '');
		if (selectedTag.toLowerCase() === clean.toLowerCase()) {
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

	function clearImageAttachment() {
		newPostImageUrl = '';
		imageUploadStatus = null;
		imageUploadError = null;
		newPostPreviewFailed = false;
		hadImageAttachment = false;
		if (imageFileInput) imageFileInput.value = '';
	}

	async function handlePublishPost() {
		if (!requireAuth('post')) return;
		if (!newPostContent.trim()) {
			errorBanner = {
				message: 'Write a short observation or caption before publishing to The Terrace.'
			};
			return;
		}

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
				clearImageAttachment();
				showImageInput = false;
				selectedInsightId = '';
				selectedTacticalBoardId = '';
				await refreshTrendingTags();
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

	async function uploadTerraceImage(file: File): Promise<string> {
		if (!data.user || !data.supabase) {
			throw new Error('Sign in required to upload images.');
		}
		if (!ALLOWED_IMAGE_TYPES.includes(file.type)) {
			throw new Error('Unsupported file format. Choose a JPEG, PNG, WebP, or GIF image.');
		}
		if (file.size > MAX_IMAGE_BYTES) {
			throw new Error('Image exceeds the 5 MB file size limit.');
		}

		const safeName = file.name.replace(/[^a-zA-Z0-9._-]/g, '_').replace(/_+/g, '_') || 'image';
		const storagePath = `${data.user.id}/${Date.now()}-${safeName}`;

		const { error: uploadErr } = await data.supabase.storage
			.from('terrace-media')
			.upload(storagePath, file, {
				cacheControl: '3600',
				contentType: file.type,
				upsert: false
			});

		if (uploadErr) {
			throw new Error(uploadErr.message || 'Image upload failed.');
		}

		const { data: publicUrlData } = data.supabase.storage
			.from('terrace-media')
			.getPublicUrl(storagePath);

		return publicUrlData.publicUrl;
	}

	async function handleImageFileSelected(event: Event) {
		const input = event.currentTarget as HTMLInputElement;
		const file = input.files?.[0];
		if (!file) return;

		imageUploadError = null;
		imageUploadStatus = null;

		if (!requireAuth('post')) {
			input.value = '';
			return;
		}

		isUploadingImage = true;
		imageUploadStatus = 'Uploading photo to Terrace media…';
		try {
			newPostImageUrl = await uploadTerraceImage(file);
			newPostPreviewFailed = false;
			imageUploadStatus = `Uploaded ${file.name}`;
		} catch (err) {
			imageUploadStatus = null;
			imageUploadError =
				err instanceof Error ? err.message : 'Could not upload image. Please try again.';
		} finally {
			isUploadingImage = false;
			input.value = '';
		}
	}

	async function handleEditImageFileSelected(event: Event) {
		const input = event.currentTarget as HTMLInputElement;
		const file = input.files?.[0];
		if (!file) return;

		editImageUploadError = null;
		if (!requireAuth('post')) {
			input.value = '';
			return;
		}

		isUploadingEditImage = true;
		try {
			editPostImageUrl = await uploadTerraceImage(file);
			editPostPreviewFailed = false;
		} catch (err) {
			editImageUploadError =
				err instanceof Error ? err.message : 'Could not upload replacement image.';
		} finally {
			isUploadingEditImage = false;
			input.value = '';
		}
	}

	async function handleDeletePost(postId: string) {
		if (!requireAuth('post')) return;
		deletingPostId = postId;
		postActionErrors = { ...postActionErrors, [postId]: null };
		try {
			await deleteTerracePost(postId, data.session?.access_token);
			posts = posts.filter((p) => p.id !== postId);
			confirmDeletePostId = null;
			if (editingPostId === postId) {
				editingPostId = null;
			}
			await refreshTrendingTags();
		} catch (err) {
			if (err instanceof ApiError && err.status === 401) {
				errorBanner = {
					message: 'Please sign in to delete posts on The Terrace.',
					isAuth: true
				};
			} else {
				postActionErrors = {
					...postActionErrors,
					[postId]:
						err instanceof ApiError
							? err.detail
							: 'Could not delete post. Please try again.'
				};
			}
		} finally {
			deletingPostId = null;
		}
	}

	function startEditPost(post: Post) {
		confirmDeletePostId = null;
		editingPostId = post.id;
		editPostContent = post.content;
		editPostImageUrl = post.image_url || '';
		editPostError = null;
		editImageUploadError = null;
		editPostPreviewFailed = false;
	}

	function cancelEditPost() {
		editingPostId = null;
		editPostContent = '';
		editPostImageUrl = '';
		editPostError = null;
		editImageUploadError = null;
		editPostPreviewFailed = false;
	}

	async function handleSavePostEdit(post: Post) {
		if (!requireAuth('post')) return;
		const trimmed = editPostContent.trim();
		if (!trimmed) {
			editPostError = 'Post content cannot be empty.';
			return;
		}
		savingPostId = post.id;
		editPostError = null;
		try {
			const updated = await updateTerracePost(
				post.id,
				{
					content: trimmed,
					image_url: editPostImageUrl.trim() || null
				},
				data.session?.access_token
			);
			posts = posts.map((p) => (p.id === post.id ? updated : p));
			brokenPostImages = { ...brokenPostImages, [post.id]: false };
			editingPostId = null;
			editPostContent = '';
			editPostImageUrl = '';
			await refreshTrendingTags();
		} catch (err) {
			if (err instanceof ApiError && err.status === 401) {
				errorBanner = {
					message: 'Please sign in to edit posts on The Terrace.',
					isAuth: true
				};
			} else {
				editPostError =
					err instanceof ApiError
						? err.detail
						: 'Could not save post changes. Please try again.';
			}
		} finally {
			savingPostId = null;
		}
	}

	function startEditComment(comment: PostComment) {
		confirmDeleteCommentId = null;
		editingCommentId = comment.id;
		editCommentContent = comment.content;
		editCommentError = null;
	}

	function cancelEditComment() {
		editingCommentId = null;
		editCommentContent = '';
		editCommentError = null;
	}

	async function handleSaveCommentEdit(postId: string, comment: PostComment) {
		if (!requireAuth('comment')) return;
		const trimmed = editCommentContent.trim();
		if (!trimmed) {
			editCommentError = 'Reply content cannot be empty.';
			return;
		}
		savingCommentId = comment.id;
		editCommentError = null;
		try {
			const updated = await updateTerraceComment(
				postId,
				comment.id,
				trimmed,
				data.session?.access_token
			);
			postComments[postId] = (postComments[postId] || []).map((c) =>
				c.id === comment.id ? updated : c
			);
			editingCommentId = null;
			editCommentContent = '';
		} catch (err) {
			if (err instanceof ApiError && err.status === 401) {
				errorBanner = {
					message: 'Please sign in to edit replies on The Terrace.',
					isAuth: true
				};
			} else {
				editCommentError =
					err instanceof ApiError
						? err.detail
						: 'Could not save reply changes. Please try again.';
			}
		} finally {
			savingCommentId = null;
		}
	}

	async function handleDeleteComment(postId: string, commentId: string) {
		if (!requireAuth('comment')) return;
		deletingCommentId = commentId;
		postActionErrors = { ...postActionErrors, [postId]: null };
		try {
			await deleteTerraceComment(postId, commentId, data.session?.access_token);
			postComments[postId] = (postComments[postId] || []).filter((c) => c.id !== commentId);
			const targetPost = posts.find((p) => p.id === postId);
			if (targetPost) {
				targetPost.comments_count = Math.max(0, targetPost.comments_count - 1);
			}
			confirmDeleteCommentId = null;
		} catch (err) {
			if (err instanceof ApiError && err.status === 401) {
				errorBanner = {
					message: 'Please sign in to delete replies on The Terrace.',
					isAuth: true
				};
			} else {
				postActionErrors = {
					...postActionErrors,
					[postId]:
						err instanceof ApiError
							? err.detail
							: 'Could not delete comment. Please try again.'
				};
			}
		} finally {
			deletingCommentId = null;
		}
	}

	async function handleToggleReaction(post: Post) {
		if (!requireAuth('react')) return;

		postActionErrors = { ...postActionErrors, [post.id]: null };
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
			if (err instanceof ApiError && err.status === 401) {
				errorBanner = {
					message: 'Please sign in to cheer posts on The Terrace.',
					isAuth: true
				};
			} else {
				postActionErrors = {
					...postActionErrors,
					[post.id]:
						err instanceof ApiError
							? err.detail
							: 'Could not update cheer. Please try again.'
				};
			}
		}
	}

	async function loadPostComments(postId: string) {
		loadingComments = { ...loadingComments, [postId]: true };
		commentLoadErrors = { ...commentLoadErrors, [postId]: null };
		try {
			const items = await fetchCommentsStrict(postId);
			postComments = { ...postComments, [postId]: items };
		} catch (err) {
			commentLoadErrors = {
				...commentLoadErrors,
				[postId]:
					err instanceof ApiError
						? err.detail
						: 'Unable to load replies right now.'
			};
		} finally {
			loadingComments = { ...loadingComments, [postId]: false };
		}
	}

	async function toggleCommentSection(postId: string) {
		const isOpen = !!expandedComments[postId];
		expandedComments[postId] = !isOpen;

		if (!isOpen && (!postComments[postId] || commentLoadErrors[postId])) {
			await loadPostComments(postId);
		}
	}

	async function handleAddComment(postId: string) {
		if (!requireAuth('comment')) return;

		const text = newCommentText[postId]?.trim();
		if (!text) return;

		postActionErrors = { ...postActionErrors, [postId]: null };
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
			if (err instanceof ApiError && err.status === 401) {
				errorBanner = {
					message: 'Please sign in to reply on The Terrace.',
					isAuth: true
				};
			} else {
				postActionErrors = {
					...postActionErrors,
					[postId]:
						err instanceof ApiError
							? err.detail
							: 'Could not post your reply. Please try again.'
				};
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

	let visiblePosts = $derived.by(() => {
		if (selectedTab === 'insights') {
			return posts.filter((p) => Boolean(p.insight_id || p.insight));
		}
		if (selectedTab === 'tactics') {
			return posts.filter((p) => Boolean(p.tactical_board_id || p.tactical_board));
		}
		if (selectedTab === 'photos') {
			return posts.filter((p) => Boolean(p.image_url));
		}
		return posts;
	});

	type TextSegment = { text: string; tag?: string };

	function parsePostSegments(content: string): TextSegment[] {
		const segments: TextSegment[] = [];
		const regex = /#[A-Za-z0-9_]+/g;
		let lastIndex = 0;
		let match: RegExpExecArray | null;
		while ((match = regex.exec(content)) !== null) {
			if (match.index > lastIndex) {
				segments.push({ text: content.slice(lastIndex, match.index) });
			}
			const full = match[0];
			segments.push({ text: full, tag: full.slice(1) });
			lastIndex = regex.lastIndex;
		}
		if (lastIndex < content.length) {
			segments.push({ text: content.slice(lastIndex) });
		}
		return segments;
	}

	function isPostEdited(post: Post): boolean {
		if (!post.updated_at) return false;
		const createdMs = new Date(post.created_at).getTime();
		const updatedMs = new Date(post.updated_at).getTime();
		if (Number.isNaN(createdMs) || Number.isNaN(updatedMs)) return false;
		return updatedMs - createdMs > 2000;
	}

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
				<div class="font-bold text-accent-text">Guest browsing mode</div>
				<p class="text-muted leading-snug">
					Read all posts, tactics, and debriefs freely. <a href="/login?next={authNext}" class="text-ink underline font-semibold hover:text-accent-text">Sign in</a> to join debates or publish.
				</p>
			</div>
		{/if}
	</div>

	{#if errorBanner}
		<div role="alert" class="p-3.5 rounded-card bg-paper-2 border border-rule text-error text-xs flex items-center justify-between gap-4">
			<div class="flex items-center gap-3 flex-wrap">
				<span>{errorBanner.message}</span>
				{#if errorBanner.isAuth}
					<a href="/login?next={authNext}" class="underline text-ink font-semibold hover:text-accent-text">Sign in</a>
				{/if}
			</div>
			<button
				type="button"
				onclick={() => (errorBanner = null)}
				class="min-h-[44px] px-2 text-muted hover:text-ink font-semibold shrink-0"
			>
				Dismiss
			</button>
		</div>
	{/if}

	<!-- Search & Category Filters -->
	<section class="space-y-5">
		<div class="flex flex-wrap sm:flex-nowrap items-center gap-2.5">
			<div class="relative flex-1 min-w-[200px]">
				<input
					type="text"
					aria-label="Search Terrace discussions"
					bind:value={searchQuery}
					onkeydown={(e) => e.key === 'Enter' && handleSearch()}
					placeholder="Search discussions, tactics, player debriefs (#Saka, #Derby, #Arteta)…"
					class="w-full min-h-[44px] bg-paper-2 border border-rule rounded-card pl-9 pr-3 text-xs text-ink placeholder-muted"
				/>
				<svg class="w-4 h-4 text-muted absolute left-3 top-3.5" aria-hidden="true" fill="none" viewBox="0 0 24 24" stroke="currentColor">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
				</svg>
			</div>
			<button
				type="button"
				onclick={handleSearch}
				class="min-h-[44px] px-4 rounded-card bg-accent hover:opacity-95 text-accent-ink text-xs font-semibold transition-opacity"
			>
				Search
			</button>
			{#if searchQuery || selectedTag || selectedTab !== 'all'}
				<button
					type="button"
					onclick={clearFilters}
					class="min-h-[44px] px-3.5 rounded-card border border-rule bg-paper-2 hover:bg-paper-3 text-ink-2 hover:text-ink text-xs font-semibold transition-colors"
				>
					Reset
				</button>
			{/if}
		</div>

		<!-- Structural Feed Filter Tabs -->
		<div class="flex items-center gap-2 border-y border-rule py-3 flex-wrap">
			<button
				type="button"
				aria-pressed={selectedTab === 'all'}
				onclick={() => selectCategory('all')}
				class="min-h-[44px] px-3.5 rounded-card text-xs font-semibold transition-colors border {selectedTab === 'all' ? 'bg-accent text-accent-ink border-accent' : 'text-ink-2 hover:text-ink border-rule bg-paper-2'}"
			>
				All Terrace
			</button>
			<button
				type="button"
				aria-pressed={selectedTab === 'insights'}
				onclick={() => selectCategory('insights')}
				class="min-h-[44px] px-3.5 rounded-card text-xs font-semibold transition-colors border {selectedTab === 'insights' ? 'bg-accent text-accent-ink border-accent' : 'text-ink-2 hover:text-ink border-rule bg-paper-2'}"
			>
				With insights
			</button>
			<button
				type="button"
				aria-pressed={selectedTab === 'tactics'}
				onclick={() => selectCategory('tactics')}
				class="min-h-[44px] px-3.5 rounded-card text-xs font-semibold transition-colors border {selectedTab === 'tactics' ? 'bg-accent text-accent-ink border-accent' : 'text-ink-2 hover:text-ink border-rule bg-paper-2'}"
			>
				With tactics
			</button>
			<button
				type="button"
				aria-pressed={selectedTab === 'photos'}
				onclick={() => selectCategory('photos')}
				class="min-h-[44px] px-3.5 rounded-card text-xs font-semibold transition-colors border {selectedTab === 'photos' ? 'bg-accent text-accent-ink border-accent' : 'text-ink-2 hover:text-ink border-rule bg-paper-2'}"
			>
				With photos
			</button>
		</div>

		{#if trendingTags && trendingTags.length > 0}
			<div class="flex items-center gap-2 flex-wrap text-xs">
				<span class="text-muted font-semibold">Trending topics:</span>
				{#each trendingTags as t (t.tag)}
					{@const cleanTag = t.tag.replace(/^#+/, '')}
					{@const isTagActive = selectedTag.toLowerCase() === cleanTag.toLowerCase()}
					{@const tagLabel = `#${cleanTag} (${t.count})`}
					<button
						type="button"
						aria-pressed={isTagActive}
						onclick={() => handleTagClick(cleanTag)}
						class="min-h-[36px] px-3 rounded-card text-xs transition-colors border {isTagActive ? 'bg-paper-3 text-accent-text border-rule-2 font-semibold' : 'bg-paper-2 text-ink-2 border-rule hover:text-ink'}"
					>
						{tagLabel}
					</button>
				{/each}
			</div>
		{/if}
	</section>

	<!-- Post Composer -->
	<section class="border-t-2 border-rule-2 pt-6 space-y-4">
		<div class="flex flex-wrap items-center justify-between gap-2 text-xs">
			<div class="flex items-center gap-2">
				<span class="font-bold text-ink">
					{data.profile?.display_name || (data.user ? data.user.email?.split('@')[0] : 'Gooner guest')}
				</span>
				<span class="text-accent-2 font-semibold">Arsenal supporter</span>
			</div>
			<span class="text-muted">Emirates Stadium Terrace</span>
		</div>

		{#if !data.user}
			<div class="p-4 bg-paper-2 border-y border-rule flex flex-wrap items-center justify-between gap-4">
				<p class="text-xs text-ink-2">
					Sign in with your Gunners supporter account to publish tactical debriefs, attach boards, or share match photos.
				</p>
				<div class="flex items-center gap-2.5 shrink-0">
					<button
						type="button"
						onclick={() => requireAuth('post')}
						class="min-h-[44px] px-4 rounded-card bg-accent hover:opacity-95 text-accent-ink text-xs font-semibold transition-opacity"
					>
						Sign in to publish
					</button>
					<a
						href="/signup?next={authNext}"
						class="inline-flex items-center min-h-[44px] px-3.5 rounded-card border border-rule bg-paper hover:bg-paper-3 text-ink text-xs font-semibold transition-colors"
					>
						Create account
					</a>
				</div>
			</div>
		{:else}
			<div class="space-y-1.5">
				<textarea
					aria-label="Write a Terrace post"
					aria-describedby={needsCaptionHint ? 'terrace-caption-hint' : undefined}
					bind:value={newPostContent}
					maxlength={MAX_POST_CHARS}
					rows="3"
					placeholder="Share tactical observations, match reactions, lineup notes, or a photo caption…"
					class="w-full bg-paper-2 border border-rule rounded-card p-3 text-xs text-ink placeholder-muted resize-y"
				></textarea>
				<div class="flex flex-wrap items-center justify-between gap-2 text-xs">
					{#if needsCaptionHint}
						<p id="terrace-caption-hint" role="status" class="text-accent-2 font-semibold">
							Add a short observation or caption above to publish your photo.
						</p>
					{:else}
						<span></span>
					{/if}
					{#if newPostContent.length > 1600}
						<span class="num font-outlier text-muted">
							{newPostContent.length}/{MAX_POST_CHARS}
						</span>
					{/if}
				</div>
			</div>

			{#if showImageInput}
				<div class="border-t border-rule pt-3 space-y-3">
					<div class="flex items-center justify-between text-xs gap-4">
						<span class="font-semibold text-ink-2">
							Photo attachment <span class="font-normal text-muted">(Upload JPEG, PNG, WebP, GIF up to 5 MB or paste a direct URL)</span>
						</span>
						<button
							type="button"
							onclick={() => { showImageInput = false; newPostImageUrl = ''; }}
							class="min-h-[36px] px-2 text-muted hover:text-error font-semibold shrink-0"
						>
							Cancel
						</button>
					</div>

					<div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
						<div class="space-y-1">
							<label for="terrace-image-file" class="block text-xs font-semibold text-ink-2">
								Upload from device
							</label>
							<input
								id="terrace-image-file"
								bind:this={imageFileInput}
								type="file"
								accept="image/jpeg,image/png,image/webp,image/gif"
								disabled={isUploadingImage}
								onchange={handleImageFileSelected}
								class="block w-full min-h-[44px] bg-paper-2 border border-rule rounded-card px-3 py-2 text-xs text-ink-2 file:mr-3 file:border-0 file:bg-paper-3 file:text-ink file:text-xs file:font-semibold file:px-2.5 file:py-1 file:rounded-card hover:file:bg-accent hover:file:text-accent-ink disabled:opacity-50"
							/>
						</div>

						<div class="space-y-1">
							<label for="image-url-input" class="block text-xs font-semibold text-ink-2">
								Or paste image URL
							</label>
							<input
								id="image-url-input"
								type="url"
								bind:value={newPostImageUrl}
								placeholder="https://images.unsplash.com/…"
								class="w-full min-h-[44px] bg-paper-2 border border-rule rounded-card px-3 text-xs text-ink placeholder-muted"
							/>
						</div>
					</div>

					{#if imageUploadStatus}
						<p aria-live="polite" class="text-xs text-success font-semibold">{imageUploadStatus}</p>
					{/if}

					{#if imageUploadError}
						<p role="alert" class="text-xs text-error font-semibold">{imageUploadError}</p>
					{/if}

					{#if newPostImageUrl.trim()}
						<div class="relative w-44 h-28 rounded-card overflow-hidden border border-rule bg-paper-2 mt-2 flex items-center justify-center">
							{#if newPostPreviewFailed}
								<p class="text-xs text-error px-3 text-center">Preview could not be loaded.</p>
							{:else}
								<img
									src={newPostImageUrl}
									alt="Attachment preview"
									class="w-full h-full object-cover"
									onerror={() => (newPostPreviewFailed = true)}
								/>
							{/if}
							<button
								type="button"
								onclick={() => (newPostImageUrl = '')}
								aria-label="Remove attached photo"
								class="absolute top-1.5 right-1.5 min-h-[32px] bg-paper/90 hover:bg-accent hover:text-accent-ink text-ink border border-rule rounded-pill px-2.5 py-0.5 text-xs font-semibold"
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
						class="min-h-[36px] px-2 text-muted hover:text-error font-semibold"
					>
						Detach
					</button>
				</div>
			{/if}

			{#if attachedTacticalBoardPreview}
				<div class="border-t border-rule pt-3 flex items-center justify-between gap-4 text-xs">
					<div class="space-y-1">
						<div class="flex items-center gap-2">
							<span class="text-accent-text font-semibold">
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
						class="min-h-[36px] px-2 text-muted hover:text-error font-semibold"
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
						aria-expanded={showImageInput}
						class="min-h-[44px] px-3 rounded-card bg-paper-2 hover:bg-paper-3 border border-rule text-xs text-ink-2 font-semibold transition-colors {showImageInput ? 'border-accent text-accent-text' : ''}"
					>
						{imageToggleLabel}
					</button>

					<select
						aria-label="Attach Data Lab insight"
						bind:value={selectedInsightId}
						class="min-h-[44px] bg-paper-2 border border-rule text-xs text-ink-2 rounded-card px-2.5"
					>
						<option value="">Attach insight (optional)</option>
						{#each availableInsights as ins (ins.id)}
							<option value={ins.id}>{ins.title}</option>
						{/each}
					</select>

					<select
						aria-label="Attach tactical board"
						bind:value={selectedTacticalBoardId}
						class="min-h-[44px] bg-paper-2 border border-rule text-xs text-ink-2 rounded-card px-2.5"
					>
						<option value="">Attach tactic (optional)</option>
						{#each availableTacticalBoards as tb (tb.id)}
							<option value={tb.id}>{tb.title} ({tb.formation})</option>
						{/each}
					</select>

					<a
						href="/board"
						class="inline-flex items-center min-h-[44px] px-1.5 text-xs text-accent-text hover:text-ink font-semibold transition-colors"
					>
						Create tactic
					</a>
				</div>

				<button
					type="button"
					onclick={handlePublishPost}
					disabled={isSubmitting || isUploadingImage || !newPostContent.trim()}
					class="min-h-[44px] px-5 rounded-card bg-accent hover:opacity-95 text-accent-ink font-semibold text-xs transition-opacity disabled:opacity-50"
				>
					{publishPostLabel}
				</button>
			</div>
		{/if}
	</section>

	<!-- Feed Stream -->
	{#if isLoadingFeed}
		<div role="status" class="py-12 text-muted text-sm">
			Loading Terrace discussions…
		</div>
	{:else if postsError && posts.length === 0}
		<StateBanner
			variant="error"
			title="Terrace feed unavailable"
			message={postsError}
			onretry={() => reloadFeed()}
			busy={isLoadingFeed}
		/>
	{:else if visiblePosts.length === 0}
		<div class="py-12 border-t border-rule space-y-2">
			<p class="text-sm text-ink font-bold">No discussions match the active filters.</p>
			<p class="text-xs text-muted">Be the first Gooner to share your thoughts above, or reset your active filters.</p>
		</div>
	{:else}
		{#if postsError}
			<StateBanner
				variant="warning"
				title="Feed refresh issue"
				message={postsError}
				onretry={() => reloadFeed()}
				busy={isLoadingFeed}
			/>
		{/if}

		<div class="divide-y divide-rule border-t border-rule">
			{#each visiblePosts as post (post.id)}
				{@const debateBtnLabel = `Debates (${post.comments_count})`}
				{@const cheerBtnLabel = `Cheer (${post.reactions_count})`}
				{@const isPostOwner = Boolean(data.user?.id && post.author_id === data.user.id)}
				{@const edited = isPostEdited(post)}
				<article id="post-{post.id}" class="py-8 space-y-4">
					<!-- Post Author & Meta -->
					<div class="flex items-center justify-between text-xs gap-3 flex-wrap">
						<div class="flex items-center gap-3 flex-wrap">
							<a
								href="/supporters/{encodeURIComponent(post.author_name)}"
								class="font-bold text-ink hover:text-accent-text transition-colors"
							>
								{post.author_name}
							</a>
							<span class="text-muted">Arsenal</span>
							{#if !isPostOwner}
								<a
									href="/messages?recipient={encodeURIComponent(post.author_id || post.author_name)}&name={encodeURIComponent(post.author_name)}&club=arsenal"
									class="text-accent-2 hover:text-ink font-semibold transition-colors"
									title="Challenge {post.author_name} to a private debate"
								>
									Direct debate
								</a>
							{/if}
						</div>
						<div class="flex items-center gap-3 flex-wrap">
							<span class="text-muted num font-outlier">{formatTimestamp(post.created_at)}</span>
							{#if edited}
								<span class="text-muted">(edited)</span>
							{/if}
							{#if isPostOwner}
								{#if confirmDeletePostId === post.id}
									{@const confirmPostBtn = deletingPostId === post.id ? 'Deleting…' : 'Confirm delete'}
									<div class="flex items-center gap-1.5">
										<button
											type="button"
											onclick={() => handleDeletePost(post.id)}
											disabled={deletingPostId === post.id}
											class="min-h-[36px] px-2.5 rounded-card bg-accent text-accent-ink font-semibold text-xs whitespace-nowrap disabled:opacity-50"
										>
											{confirmPostBtn}
										</button>
										<button
											type="button"
											onclick={() => (confirmDeletePostId = null)}
											disabled={deletingPostId === post.id}
											class="min-h-[36px] px-2.5 rounded-card border border-rule bg-paper-2 text-ink-2 hover:text-ink font-semibold text-xs"
										>
											Cancel
										</button>
									</div>
								{:else if editingPostId !== post.id}
									<button
										type="button"
										onclick={() => startEditPost(post)}
										aria-label="Edit post by {post.author_name}"
										class="min-h-[36px] px-2 text-muted hover:text-ink font-semibold transition-colors"
									>
										Edit
									</button>
									<button
										type="button"
										onclick={() => (confirmDeletePostId = post.id)}
										aria-label="Delete post by {post.author_name}"
										class="min-h-[36px] px-2 text-muted hover:text-error font-semibold transition-colors"
									>
										Delete
									</button>
								{/if}
							{/if}
						</div>
					</div>

					<!-- Post Content or Inline Editor -->
					{#if editingPostId === post.id}
						<div class="space-y-3 border-l-2 border-accent-2 pl-4 py-2">
							<div class="flex items-center justify-between gap-2">
								<label for="edit-post-{post.id}" class="block text-xs font-semibold text-ink-2">
									Edit post
								</label>
								{#if editPostContent.length > 1600}
									<span class="text-xs num font-outlier text-muted">
										{editPostContent.length}/{MAX_POST_CHARS}
									</span>
								{/if}
							</div>
							<textarea
								id="edit-post-{post.id}"
								aria-label="Edit post content"
								bind:value={editPostContent}
								maxlength={MAX_POST_CHARS}
								rows="3"
								disabled={savingPostId === post.id}
								class="w-full bg-paper-2 border border-rule rounded-card p-3 text-xs text-ink placeholder-muted resize-y"
							></textarea>

							<div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
								<div class="space-y-1">
									<label for="edit-post-file-{post.id}" class="block text-xs font-semibold text-ink-2">
										Replace photo from device
									</label>
									<input
										id="edit-post-file-{post.id}"
										type="file"
										accept="image/jpeg,image/png,image/webp,image/gif"
										disabled={savingPostId === post.id || isUploadingEditImage}
										onchange={handleEditImageFileSelected}
										class="block w-full min-h-[44px] bg-paper-2 border border-rule rounded-card px-3 py-2 text-xs text-ink-2 file:mr-3 file:border-0 file:bg-paper-3 file:text-ink file:text-xs file:font-semibold file:px-2.5 file:py-1 file:rounded-card hover:file:bg-accent hover:file:text-accent-ink disabled:opacity-50"
									/>
								</div>

								<div class="space-y-1">
									<label for="edit-post-img-{post.id}" class="block text-xs font-semibold text-ink-2">
										Image URL (optional)
									</label>
									<input
										id="edit-post-img-{post.id}"
										type="url"
										bind:value={editPostImageUrl}
										disabled={savingPostId === post.id || isUploadingEditImage}
										placeholder="https://…"
										class="w-full min-h-[44px] bg-paper-2 border border-rule rounded-card px-3 text-xs text-ink placeholder-muted"
									/>
								</div>
							</div>

							{#if editImageUploadError}
								<p role="alert" class="text-xs text-error font-semibold">{editImageUploadError}</p>
							{/if}

							{#if editPostImageUrl.trim()}
								<div class="relative w-44 h-28 rounded-card overflow-hidden border border-rule bg-paper-2 flex items-center justify-center">
									{#if editPostPreviewFailed}
										<p class="text-xs text-error px-3 text-center">Preview could not be loaded.</p>
									{:else}
										<img
											src={editPostImageUrl}
											alt="Edited attachment preview"
											class="w-full h-full object-cover"
											onerror={() => (editPostPreviewFailed = true)}
										/>
									{/if}
									<button
										type="button"
										onclick={() => {
											editPostImageUrl = '';
											editImageUploadError = null;
											editPostPreviewFailed = false;
										}}
										class="absolute top-1.5 right-1.5 min-h-[32px] bg-paper/90 hover:bg-accent hover:text-accent-ink text-ink border border-rule rounded-pill px-2.5 py-0.5 text-xs font-semibold"
									>
										Remove image
									</button>
								</div>
							{/if}

							{#if editPostError}
								<p role="alert" class="text-xs text-error font-semibold">{editPostError}</p>
							{/if}
							<div class="flex items-center justify-end gap-2">
								<button
									type="button"
									onclick={cancelEditPost}
									disabled={savingPostId === post.id || isUploadingEditImage}
									class="min-h-[36px] px-3 rounded-card border border-rule bg-paper-2 text-ink-2 hover:text-ink text-xs font-semibold disabled:opacity-50"
								>
									Cancel
								</button>
								<button
									type="button"
									onclick={() => handleSavePostEdit(post)}
									disabled={savingPostId === post.id || isUploadingEditImage || !editPostContent.trim()}
									class="min-h-[36px] px-3.5 rounded-card bg-accent hover:opacity-95 text-accent-ink text-xs font-semibold whitespace-nowrap disabled:opacity-50"
								>
									{editSaveLabel}
								</button>
							</div>
						</div>
					{:else}
						<p class="text-sm text-ink leading-relaxed whitespace-pre-line">
							{#each parsePostSegments(post.content) as seg}{#if seg.tag}<button
									type="button"
									onclick={() => handleTagClick(seg.tag!)}
									class="font-semibold underline decoration-rule-2 underline-offset-2 transition-colors {selectedTag.toLowerCase() === seg.tag.toLowerCase() ? 'text-accent-text' : 'text-accent-2 hover:text-accent-text'}"
								>{seg.text}</button>{:else}{seg.text}{/if}{/each}
						</p>
					{/if}

					<!-- Attached Image -->
					{#if post.image_url}
						<div class="rounded-card overflow-hidden border border-rule max-h-96 bg-paper-2">
							{#if brokenPostImages[post.id]}
								<div class="p-4 text-xs text-muted">
									Attached photo could not be loaded.
								</div>
							{:else}
								<button
									type="button"
									onclick={() => (lightboxImageUrl = post.image_url || null)}
									aria-label="Enlarge photo shared by {post.author_name}"
									class="w-full text-left group relative block"
								>
									<img
										src={post.image_url}
										alt="Photo shared by {post.author_name}"
										class="w-full max-h-96 object-cover hover:opacity-95 transition-opacity cursor-zoom-in"
										loading="lazy"
										onerror={() => (brokenPostImages = { ...brokenPostImages, [post.id]: true })}
									/>
								</button>
							{/if}
						</div>
					{/if}

					<!-- Attached Insight -->
					{#if post.insight}
						{@const ins = post.insight}
						<div class="border-l-2 border-accent-2 space-y-3 bg-paper-2 p-4">
							<div class="flex items-center justify-between gap-2 flex-wrap">
								<div class="space-y-0.5">
									<span class="text-xs font-semibold text-accent-2">Data Lab snapshot</span>
									<h3 class="text-sm font-bold text-ink card-headline">{ins.title}</h3>
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
									{#each ins.snapshot.series as item (item.team_id)}
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
						<div class="border-l-2 border-accent space-y-3 bg-paper-2 p-4">
							<div class="flex items-center justify-between gap-2 flex-wrap">
								<div class="space-y-0.5">
									<span class="text-xs font-semibold text-accent-text">
										Lineup blueprint (<span class="num font-outlier">{tb.formation}</span>)
									</span>
									<h3 class="text-sm font-bold text-ink card-headline">{tb.title}</h3>
								</div>
								<a
									href="/board"
									class="text-xs font-semibold text-accent-text hover:text-ink transition-colors"
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
					<div class="flex items-center gap-3 pt-2 text-xs flex-wrap">
						<button
							type="button"
							aria-pressed={post.user_reacted}
							onclick={() => handleToggleReaction(post)}
							class="min-h-[44px] px-3.5 rounded-card transition-colors border flex items-center gap-1.5 {post.user_reacted ? 'bg-paper-3 text-accent-2 font-bold border-rule-2' : 'bg-paper-2 text-ink-2 border-rule hover:text-ink'}"
						>
							<span>{cheerBtnLabel}</span>
						</button>

						<button
							type="button"
							aria-expanded={!!expandedComments[post.id]}
							aria-controls="comments-{post.id}"
							onclick={() => toggleCommentSection(post.id)}
							class="min-h-[44px] px-3.5 rounded-card bg-paper-2 border border-rule text-ink-2 hover:text-ink transition-colors font-semibold"
						>
							{debateBtnLabel}
						</button>
					</div>

					{#if postActionErrors[post.id]}
						<div role="alert" class="p-3 rounded-card bg-paper-2 border border-rule text-error text-xs flex items-center justify-between gap-3">
							<span>{postActionErrors[post.id]}</span>
							<button
								type="button"
								onclick={() => (postActionErrors = { ...postActionErrors, [post.id]: null })}
								class="min-h-[36px] px-2 text-muted hover:text-ink font-semibold shrink-0"
							>
								Dismiss
							</button>
						</div>
					{/if}

					<!-- Comments Thread -->
					{#if expandedComments[post.id]}
						<div id="comments-{post.id}" class="pt-4 border-t border-rule space-y-4">
							{#if loadingComments[post.id]}
								<p role="status" class="text-xs text-muted">Loading replies…</p>
							{:else if commentLoadErrors[post.id]}
								<div role="alert" class="p-3 bg-paper-2 border-l-2 border-l-error border-y border-r border-rule text-xs flex flex-wrap items-center justify-between gap-3">
									<span class="text-error">{commentLoadErrors[post.id]}</span>
									<button
										type="button"
										onclick={() => loadPostComments(post.id)}
										class="min-h-[36px] px-3 rounded-card border border-rule bg-paper text-ink font-semibold"
									>
										Retry
									</button>
								</div>
							{:else if postComments[post.id] && postComments[post.id].length > 0}
								<div class="divide-y divide-rule">
									{#each postComments[post.id] as comment (comment.id)}
										{@const isCommentOwner = Boolean(data.user?.id && comment.author_id === data.user.id)}
										<div class="py-3 space-y-1 text-xs">
											<div class="flex items-center justify-between gap-2 flex-wrap">
												<a
													href="/supporters/{encodeURIComponent(comment.author_name)}"
													class="font-bold text-ink hover:text-accent-text transition-colors"
												>
													{comment.author_name}
												</a>
												<div class="flex items-center gap-3">
													<span class="text-muted num font-outlier">{formatTimestamp(comment.created_at)}</span>
													{#if isCommentOwner}
														{#if confirmDeleteCommentId === comment.id}
															{@const confirmCommentBtn = deletingCommentId === comment.id ? 'Deleting…' : 'Confirm'}
															<div class="flex items-center gap-1.5">
																<button
																	type="button"
																	onclick={() => handleDeleteComment(post.id, comment.id)}
																	disabled={deletingCommentId === comment.id}
																	class="min-h-[36px] px-2.5 rounded-card bg-accent text-accent-ink font-semibold text-xs whitespace-nowrap disabled:opacity-50"
																>
																	{confirmCommentBtn}
																</button>
																<button
																	type="button"
																	onclick={() => (confirmDeleteCommentId = null)}
																	disabled={deletingCommentId === comment.id}
																	class="min-h-[36px] px-2.5 rounded-card border border-rule bg-paper-2 text-ink-2 hover:text-ink font-semibold text-xs"
																>
																	Cancel
																</button>
															</div>
														{:else if editingCommentId !== comment.id}
															<button
																type="button"
																onclick={() => startEditComment(comment)}
																aria-label="Edit comment"
																class="min-h-[36px] px-2 text-muted hover:text-ink font-semibold transition-colors"
															>
																Edit
															</button>
															<button
																type="button"
																onclick={() => (confirmDeleteCommentId = comment.id)}
																aria-label="Delete comment"
																class="min-h-[36px] px-2 text-muted hover:text-error font-semibold transition-colors"
															>
																Delete
															</button>
														{/if}
													{/if}
												</div>
											</div>
											{#if editingCommentId === comment.id}
												{@const saveCommentLabel = savingCommentId === comment.id ? 'Saving…' : 'Save'}
												<div class="space-y-2 pt-1">
													<textarea
														aria-label="Edit comment content"
														bind:value={editCommentContent}
														maxlength={MAX_COMMENT_CHARS}
														rows="2"
														disabled={savingCommentId === comment.id}
														class="w-full bg-paper-2 border border-rule rounded-card p-2 text-xs text-ink resize-y"
													></textarea>
													{#if editCommentError}
														<p role="alert" class="text-xs text-error font-semibold">{editCommentError}</p>
													{/if}
													<div class="flex items-center justify-end gap-1.5">
														<button
															type="button"
															onclick={cancelEditComment}
															disabled={savingCommentId === comment.id}
															class="min-h-[36px] px-2.5 rounded-card border border-rule bg-paper-2 text-ink-2 hover:text-ink font-semibold text-xs disabled:opacity-50"
														>
															Cancel
														</button>
														<button
															type="button"
															onclick={() => handleSaveCommentEdit(post.id, comment)}
															disabled={savingCommentId === comment.id || !editCommentContent.trim()}
															class="min-h-[36px] px-2.5 rounded-card bg-accent text-accent-ink font-semibold text-xs disabled:opacity-50"
														>
															{saveCommentLabel}
														</button>
													</div>
												</div>
											{:else}
												<p class="text-ink-2 leading-relaxed">{comment.content}</p>
											{/if}
										</div>
									{/each}
								</div>
							{:else}
								<p class="text-xs text-muted">No comments yet. Join the conversation below.</p>
							{/if}

							{#if !data.user}
								<div class="pt-1 flex items-center justify-between gap-3 flex-wrap">
									<span class="text-xs text-muted">Sign in to reply to this debate.</span>
									<button
										type="button"
										onclick={() => requireAuth('comment')}
										class="min-h-[44px] px-4 rounded-card border border-rule bg-paper-2 hover:bg-paper-3 text-xs font-semibold text-ink transition-colors"
									>
										Sign in to reply
									</button>
								</div>
							{:else}
								{@const replyBtnLabel = isSubmittingComment[post.id] ? 'Sending…' : 'Reply'}
								<div class="flex items-center gap-2">
									<input
										type="text"
										aria-label="Reply to discussion"
										maxlength={MAX_COMMENT_CHARS}
										bind:value={newCommentText[post.id]}
										placeholder="Write your debrief or reply…"
										class="flex-1 min-w-0 min-h-[44px] bg-paper-2 border border-rule rounded-card px-3 text-xs text-ink placeholder-muted"
										onkeydown={(e) => e.key === 'Enter' && handleAddComment(post.id)}
									/>
									<button
										type="button"
										onclick={() => handleAddComment(post.id)}
										disabled={isSubmittingComment[post.id] || !newCommentText[post.id]?.trim()}
										class="min-h-[44px] px-4 rounded-card bg-accent hover:opacity-95 text-xs font-semibold text-accent-ink whitespace-nowrap transition-opacity disabled:opacity-50"
									>
										{replyBtnLabel}
									</button>
								</div>
							{/if}
						</div>
					{/if}
				</article>
			{/each}
		</div>
	{/if}
</div>

<!-- Guest Auth Gate Modal -->
{#if showAuthModal}
	<div
		class="fixed inset-0 z-[var(--z-modal)] flex items-center justify-center p-4 bg-paper/85"
		role="presentation"
		onclick={(e) => {
			if (e.target === e.currentTarget) showAuthModal = false;
		}}
	>
		<div
			role="dialog"
			aria-modal="true"
			aria-labelledby="terrace-auth-modal-title"
			use:focusTrap={{
				active: showAuthModal,
				onEscape: () => (showAuthModal = false)
			}}
			class="bg-paper-2 border-t-2 border-rule-2 p-6 max-w-md w-full space-y-5 relative"
		>
			<button
				type="button"
				onclick={() => (showAuthModal = false)}
				class="absolute top-3 right-3 min-h-[36px] px-2 text-muted hover:text-ink text-xs font-semibold"
			>
				Close
			</button>

			<div class="space-y-2 pr-12">
				<h2 id="terrace-auth-modal-title" class="text-lg font-bold text-ink">
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
					href="/login?next={authNext}"
					class="w-full min-h-[44px] inline-flex items-center justify-center font-semibold text-xs bg-accent hover:opacity-95 text-accent-ink rounded-card transition-opacity"
				>
					Sign in
				</a>
				<a
					href="/signup?next={authNext}"
					class="w-full min-h-[44px] inline-flex items-center justify-center font-semibold text-xs bg-paper border border-rule text-ink rounded-card transition-colors hover:bg-paper-3"
				>
					Create free Gooner account
				</a>
				<button
					type="button"
					onclick={() => (showAuthModal = false)}
					class="min-h-[44px] text-xs text-muted hover:text-ink"
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
		class="fixed inset-0 z-[var(--z-modal)] flex items-center justify-center p-4 bg-paper/90 cursor-zoom-out"
		role="presentation"
		onclick={(e) => {
			if (e.target === e.currentTarget) lightboxImageUrl = null;
		}}
	>
		<div
			role="dialog"
			aria-modal="true"
			aria-labelledby="terrace-lightbox-title"
			use:focusTrap={{
				active: Boolean(lightboxImageUrl),
				onEscape: () => (lightboxImageUrl = null)
			}}
			class="relative max-w-5xl max-h-[90vh] flex flex-col items-end gap-2 cursor-default"
		>
			<h2 id="terrace-lightbox-title" class="visually-hidden">
				Photo shared by {lightboxAuthor}
			</h2>
			<button
				type="button"
				onclick={() => (lightboxImageUrl = null)}
				class="min-h-[44px] text-ink text-xs bg-paper-2 border border-rule px-3.5 rounded-card font-semibold"
			>
				Close
			</button>
			<img
				src={lightboxImageUrl}
				alt="Photo shared by {lightboxAuthor}"
				class="max-w-full max-h-[82vh] object-contain rounded-card border border-rule"
			/>
		</div>
	</div>
{/if}

<style>
	/* Hallmark · dropped selectCategory('matchday'), selectCategory('squad') · replaced hardcoded tag category tabs with structural feed filter tabs and dynamic DB trending tags */
</style>
