<script lang="ts">
	import { onDestroy } from 'svelte';
	import { CLUBS, themeState } from '$lib/stores/theme.svelte';
	import {
		ApiError,
		fetchMessages,
		sendMessage,
		createConversation
	} from '$lib/api/football';
	import { searchSupporters, markConversationRead } from '$lib/api/community';
	import type { DirectMessage, Conversation, SupporterSummary } from '$lib/types/football';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	let conversations = $state<Conversation[]>([]);
	let activeConvId = $state<string | null>(null);
	let messages = $state<DirectMessage[]>([]);
	let isLoadingMessages = $state(false);
	let isSending = $state(false);
	let messageInput = $state('');
	let errorBanner = $state<string | null>(null);

	let showStartModal = $state(false);
	let targetUserId = $state('');
	let targetUserName = $state('');
	let targetUsername = $state('');
	let targetClubId = $state('arsenal');
	let initialNote = $state('');
	let isStartingDebate = $state(false);
	let modalError = $state<string | null>(null);

	let supporterQuery = $state('');
	let supporterResults = $state<SupporterSummary[]>([]);
	let isSearchingSupporters = $state(false);
	let supporterSearchError = $state<string | null>(null);

	let isInitialized = false;
	let hasInitializedSearch = false;
	let realtimeChannel: ReturnType<typeof data.supabase.channel> | null = null;

	let sendBtnLabel = $derived(isSending ? 'Sending…' : 'Send');
	let launchBtnLabel = $derived(isStartingDebate ? 'Connecting…' : 'Launch debate');
	let isSignedIn = $derived(Boolean(data.user && data.session?.access_token && data.currentUserId));

	const viewingClub = $derived(themeState.currentTheme);
	const activeConv = $derived(
		activeConvId ? conversations.find((c) => c.id === activeConvId) : null
	);

	const filteredSupporters = $derived(
		supporterResults.filter((s) => s.user_id !== data.currentUserId)
	);

	function getConversationParticipant(conv: Conversation | null | undefined) {
		if (!conv) return null;
		if (conv.other_member_profile) {
			const profile = conv.other_member_profile;
			return {
				id: profile.user_id,
				name: profile.display_name || profile.username,
				username: profile.username,
				avatar_url: profile.avatar_url ?? null,
				club_id: 'arsenal'
			};
		}
		const otherId = conv.members.find((m) => m !== data.currentUserId) || conv.members[0] || '';
		if (conv.last_message && conv.last_message.sender_id === otherId) {
			return {
				id: otherId,
				name: conv.last_message.sender_name,
				username: null,
				avatar_url: null,
				club_id: conv.last_message.sender_club_id
			};
		}
		return {
			id: otherId,
			name: otherId.startsWith('usr_') ? otherId.replace('usr_', '') : otherId || 'Supporter',
			username: null,
			avatar_url: null,
			club_id: 'arsenal'
		};
	}

	const otherParticipant = $derived(getConversationParticipant(activeConv));

	$effect(() => {
		if (!showStartModal) {
			modalError = null;
		}
	});

	$effect(() => {
		if (!isInitialized && data.conversations) {
			conversations = data.conversations;
			supporterResults = (data.initialSupporters || []).filter(
				(s) => s.user_id !== data.currentUserId
			);
			if (isSignedIn) {
				if (data.initialRecipient) {
					targetUserId = data.initialRecipient.id;
					targetUserName = data.initialRecipient.name;
					targetClubId = data.initialRecipient.club;
					showStartModal = true;
				} else if (
					data.initialConversationId &&
					data.conversations.some((c) => c.id === data.initialConversationId)
				) {
					void selectConversation(data.initialConversationId);
				} else if (data.conversations.length > 0 && !activeConvId) {
					void selectConversation(data.conversations[0].id);
				}
			}
			isInitialized = true;
		}
	});

	$effect(() => {
		const query = supporterQuery;
		const token = data.session?.access_token ?? null;
		if (!isSignedIn || !token) return;

		if (!hasInitializedSearch && query === '') {
			hasInitializedSearch = true;
			return;
		}
		hasInitializedSearch = true;

		let cancelled = false;
		isSearchingSupporters = true;
		supporterSearchError = null;

		const timer = setTimeout(async () => {
			try {
				const found = await searchSupporters(query, 12, token);
				if (!cancelled) {
					supporterResults = found.filter((s) => s.user_id !== data.currentUserId);
				}
			} catch (err) {
				if (!cancelled) {
					supporterSearchError =
						err instanceof ApiError ? err.detail : 'Could not search supporters right now.';
				}
			} finally {
				if (!cancelled) {
					isSearchingSupporters = false;
				}
			}
		}, 250);

		return () => {
			cancelled = true;
			clearTimeout(timer);
		};
	});

	function selectSupporterForDebate(supporter: SupporterSummary) {
		targetUserId = supporter.user_id;
		targetUserName = supporter.display_name || supporter.username;
		targetUsername = supporter.username;
		targetClubId = supporter.favorite_club_id || 'arsenal';
		showStartModal = true;
	}

	async function markThreadRead(convId: string) {
		const token = data.session?.access_token;
		if (!token) return;
		conversations = conversations.map((c) =>
			c.id === convId ? { ...c, unread_count: 0 } : c
		);
		try {
			await markConversationRead(convId, token);
		} catch {
			// Keep UI responsive; unread state will sync on next fetch
		}
	}

	async function selectConversation(convId: string) {
		if (!isSignedIn) return;
		activeConvId = convId;
		isLoadingMessages = true;
		errorBanner = null;

		if (realtimeChannel) {
			data.supabase.removeChannel(realtimeChannel);
			realtimeChannel = null;
		}

		try {
			const msgs = await fetchMessages(convId, data.session?.access_token);
			if (activeConvId !== convId) return;
			messages = msgs;

			await markThreadRead(convId);
			if (activeConvId !== convId) return;

			realtimeChannel = data.supabase
				.channel(`dm:${convId}`)
				.on(
					'postgres_changes',
					{
						event: 'INSERT',
						schema: 'public',
						table: 'direct_messages',
						filter: `conversation_id=eq.${convId}`
					},
					(payload: { new: DirectMessage }) => {
						const incoming = payload.new;
						if (!incoming) return;
						if (!messages.some((m) => m.id === incoming.id)) {
							messages = [...messages, incoming];
						}
						conversations = conversations.map((c) =>
							c.id === convId
								? { ...c, last_message: incoming, updated_at: incoming.created_at, unread_count: 0 }
								: c
						);
						if (incoming.sender_id !== data.currentUserId) {
							void markThreadRead(convId);
						}
					}
				)
				.subscribe();
		} catch (err) {
			messages = [];
			errorBanner =
				err instanceof ApiError
					? err.detail
					: 'Could not load conversation messages. Please try again.';
		} finally {
			isLoadingMessages = false;
		}
	}

	async function handleSendMessage() {
		if (!isSignedIn || !data.currentUserId || !activeConvId || !messageInput.trim() || isSending) return;

		const text = messageInput.trim();
		const prevMessages = messages;
		const prevConversations = conversations.map((c) => ({ ...c }));
		messageInput = '';
		isSending = true;
		errorBanner = null;

		const authorName = data.profile?.display_name || data.user?.email?.split('@')[0] || 'Supporter';
		const authorClub = data.profile?.favorite_club_id || viewingClub.id;

		const optimisticMsg: DirectMessage = {
			id: `msg_opt_${Date.now()}`,
			conversation_id: activeConvId,
			sender_id: data.currentUserId,
			sender_name: authorName,
			sender_club_id: authorClub,
			content: text,
			created_at: new Date().toISOString()
		};

		messages = [...messages, optimisticMsg];

		const targetConv = conversations.find((c) => c.id === activeConvId);
		if (targetConv) {
			const updatedConv: Conversation = {
				...targetConv,
				last_message: optimisticMsg,
				updated_at: optimisticMsg.created_at
			};
			conversations = [
				updatedConv,
				...conversations.filter((c) => c.id !== activeConvId)
			];
		}

		try {
			const sent = await sendMessage(
				activeConvId,
				{
					sender_id: data.currentUserId,
					sender_name: authorName,
					sender_club_id: authorClub,
					content: text
				},
				data.session?.access_token
			);

			if (sent) {
				messages = messages.map((m) => (m.id === optimisticMsg.id ? sent : m));
				conversations = conversations.map((c) =>
					c.id === activeConvId ? { ...c, last_message: sent, updated_at: sent.created_at } : c
				);
			}
		} catch (err) {
			messages = prevMessages;
			conversations = prevConversations;
			messageInput = text;
			errorBanner =
				err instanceof ApiError ? err.detail : 'Failed to send message. Please try again.';
		} finally {
			isSending = false;
		}
	}

	async function handleStartNewDebate() {
		if (!isSignedIn || !data.currentUserId || !targetUserId.trim() || isStartingDebate) return;
		isStartingDebate = true;
		modalError = null;
		errorBanner = null;

		const authorName = data.profile?.display_name || data.user?.email?.split('@')[0] || 'Supporter';
		const authorClub = data.profile?.favorite_club_id || viewingClub.id;

		try {
			const conv = await createConversation(
				{
					initiator_id: data.currentUserId,
					recipient_id: targetUserId.trim(),
					initiator_name: authorName,
					initiator_club_id: authorClub,
					initial_message: initialNote.trim() || undefined
				},
				data.session?.access_token
			);

			if (conv) {
				showStartModal = false;
				targetUserId = '';
				targetUserName = '';
				targetUsername = '';
				initialNote = '';

				if (!conversations.some((c) => c.id === conv.id)) {
					conversations = [conv, ...conversations];
				}
				await selectConversation(conv.id);
			}
		} catch (err) {
			modalError =
				err instanceof ApiError ? err.detail : 'Failed to start debate. Please try again.';
		} finally {
			isStartingDebate = false;
		}
	}

	onDestroy(() => {
		if (realtimeChannel) {
			data.supabase.removeChannel(realtimeChannel);
			realtimeChannel = null;
		}
	});

	function formatTime(isoStr: string): string {
		try {
			const d = new Date(isoStr);
			return d.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' });
		} catch {
			return '';
		}
	}
</script>

<svelte:head>
	<title>The Dressing Room | Direct Debates</title>
</svelte:head>

<div class="container py-12 space-y-8">
	<!-- Header Bar -->
	<div class="border-b-2 border-rule-2 pb-6 flex flex-col sm:flex-row sm:items-end justify-between gap-4">
		<div class="space-y-2">
			<h1>The Dressing Room</h1>
			<p class="lead text-ink-2">
				Direct realtime tactical discussions with fellow Arsenal supporters and analysts.
			</p>
		</div>

		{#if isSignedIn}
			<button
				type="button"
				onclick={() => (showStartModal = true)}
				class="h-10 px-4 rounded-card bg-accent hover:opacity-95 text-accent-ink font-semibold text-xs transition-opacity self-start sm:self-auto"
			>
				Start new debate
			</button>
		{/if}
	</div>

	{#if errorBanner}
		<div role="alert" class="p-3.5 rounded-card bg-paper-2 border border-rule text-error text-xs flex items-center justify-between gap-4">
			<span>{errorBanner}</span>
			<button type="button" onclick={() => (errorBanner = null)} class="text-muted hover:text-ink font-semibold shrink-0">Dismiss</button>
		</div>
	{/if}

	{#if !isSignedIn}
		<section class="border border-rule bg-paper-2 p-8 space-y-5 max-w-xl">
			<div class="space-y-2">
				<h2 class="text-lg font-bold text-ink">Sign in to access direct debates</h2>
				<p class="text-sm text-ink-2 leading-relaxed">
					The Dressing Room hosts private supporter conversations and tactical debates. Sign in with your Gunners account to view active threads or challenge supporters.
				</p>
			</div>
			<div class="flex flex-wrap items-center gap-3">
				<a
					href="/login"
					class="inline-flex items-center h-10 px-5 rounded-card bg-accent hover:opacity-95 text-accent-ink font-semibold text-xs transition-opacity"
				>
					Sign in
				</a>
				<a
					href="/signup"
					class="inline-flex items-center h-10 px-4 rounded-card border border-rule bg-paper hover:bg-paper-3 text-ink font-semibold text-xs transition-colors"
				>
					Create free account
				</a>
			</div>
		</section>
	{:else}
	<!-- Main Chat Layout -->
	<div class="grid grid-cols-1 md:grid-cols-12 h-[640px] border border-rule bg-paper-2">
		<!-- Left Sidebar: Debates List (4 cols) -->
		<div class="md:col-span-4 border-r border-rule flex flex-col bg-paper">
			<div class="p-4 border-b border-rule flex items-center justify-between text-xs">
				<span class="font-bold text-ink">Conversations</span>
				<span class="num font-outlier text-muted">
					{conversations.length}
				</span>
			</div>

			<div class="flex-1 overflow-y-auto divide-y divide-rule">
				{#if conversations.length === 0}
					<div class="p-8 text-muted text-xs space-y-1">
						<p class="font-semibold text-ink-2">No active debates yet.</p>
						<p>Select “Start new debate” or search for a registered supporter.</p>
					</div>
				{:else}
					{#each conversations as c}
						{@const isSelected = c.id === activeConvId}
						{@const participant = getConversationParticipant(c)}
						{@const displayName = participant?.name || 'Supporter'}
						{@const lastSnippet = c.last_message ? c.last_message.content : 'No messages yet'}
						{@const unreadTotal = c.unread_count ?? 0}
						<div class="p-4 transition-colors flex items-start gap-3 {isSelected ? 'bg-paper-2 border-l-2 border-accent-2' : 'hover:bg-paper-2'}">
							{#if participant?.avatar_url}
								<img
									src={participant.avatar_url}
									alt={displayName}
									class="w-9 h-9 rounded-pill object-cover border border-rule shrink-0"
								/>
							{:else}
								<span
									aria-hidden="true"
									class="w-9 h-9 rounded-pill bg-paper-3 border border-rule text-ink-2 text-xs font-bold inline-flex items-center justify-center shrink-0"
								>
									{displayName.slice(0, 1).toUpperCase()}
								</span>
							{/if}

							<div class="min-w-0 flex-1 space-y-1">
								<div class="flex items-center justify-between gap-2">
									<button
										type="button"
										onclick={() => selectConversation(c.id)}
										class="text-xs font-bold text-ink hover:text-accent transition-colors truncate text-left"
									>
										{displayName}
									</button>
									<div class="flex items-center gap-2 shrink-0">
										{#if unreadTotal > 0}
											<span
												aria-label="{unreadTotal} unread messages"
												class="num font-outlier px-1.5 py-0.5 rounded-pill bg-accent text-accent-ink text-xs font-semibold leading-none"
											>
												{unreadTotal > 9 ? '9+' : unreadTotal}
											</span>
										{/if}
										{#if c.last_message}
											<span class="text-xs text-muted num font-outlier">
												{formatTime(c.last_message.created_at)}
											</span>
										{/if}
									</div>
								</div>

								{#if participant?.username}
									<p class="text-xs text-muted truncate">@{participant.username}</p>
								{/if}

								<p class="text-xs text-muted truncate">
									{lastSnippet}
								</p>
							</div>
						</div>
					{/each}
				{/if}
			</div>
		</div>

		<!-- Right Side: Active Chat Window (8 cols) -->
		<div class="md:col-span-8 flex flex-col bg-paper-2">
			{#if !activeConvId}
				<div class="flex-1 flex flex-col justify-center p-8 text-xs text-muted overflow-y-auto space-y-6">
					<div class="space-y-1">
						<h2 class="text-lg font-bold text-ink">Select or start a debate</h2>
						<p class="text-sm text-ink-2">
							Search registered Arsenal supporters below to launch a direct tactical conversation.
						</p>
					</div>

					<div class="w-full max-w-lg space-y-3 border-t border-rule pt-4">
						<label for="supporter-directory-search" class="block text-xs font-semibold text-ink-2">
							Find a registered supporter
						</label>
						<input
							id="supporter-directory-search"
							type="search"
							bind:value={supporterQuery}
							placeholder="Search by display name or @username…"
							class="w-full h-10 bg-paper border border-rule rounded-card px-3 text-xs text-ink placeholder-muted"
						/>

						{#if supporterSearchError}
							<p role="alert" class="text-xs text-error">{supporterSearchError}</p>
						{:else if isSearchingSupporters}
							<p class="text-xs text-muted">Searching supporter directory…</p>
						{:else if filteredSupporters.length === 0}
							<p class="text-xs text-muted">No matching supporters found.</p>
						{:else}
							<div class="divide-y divide-rule border-t border-rule">
								{#each filteredSupporters as supporter}
									{@const sName = supporter.display_name || supporter.username}
									<div class="py-3 flex items-center justify-between gap-4">
										<div class="flex items-center gap-3 min-w-0">
											{#if supporter.avatar_url}
												<img
													src={supporter.avatar_url}
													alt={sName}
													class="w-8 h-8 rounded-pill object-cover border border-rule shrink-0"
												/>
											{:else}
												<span
													aria-hidden="true"
													class="w-8 h-8 rounded-pill bg-paper-3 border border-rule text-ink-2 text-xs font-bold inline-flex items-center justify-center shrink-0"
												>
													{sName.slice(0, 1).toUpperCase()}
												</span>
											{/if}
											<div class="min-w-0">
												<div class="text-xs font-bold text-ink truncate">{sName}</div>
												<p class="text-xs text-muted truncate">@{supporter.username}</p>
											</div>
										</div>
										<button
											type="button"
											onclick={() => selectSupporterForDebate(supporter)}
											class="h-8 px-3 rounded-card bg-paper border border-rule text-accent-2 hover:text-ink font-semibold text-xs transition-colors shrink-0"
										>
											Debate
										</button>
									</div>
								{/each}
							</div>
						{/if}
					</div>
				</div>
			{:else}
				<!-- Chat Header -->
				<div class="p-4 border-b border-rule bg-paper flex items-center justify-between text-xs gap-3">
					<div class="flex items-center gap-3 min-w-0">
						{#if otherParticipant?.avatar_url}
							<img
								src={otherParticipant.avatar_url}
								alt={otherParticipant.name}
								class="w-8 h-8 rounded-pill object-cover border border-rule shrink-0"
							/>
						{:else}
							<span
								aria-hidden="true"
								class="w-8 h-8 rounded-pill bg-paper-3 border border-rule text-ink-2 text-xs font-bold inline-flex items-center justify-center shrink-0"
							>
								{(otherParticipant?.name || 'S').slice(0, 1).toUpperCase()}
							</span>
						{/if}
						<div class="min-w-0">
							<div class="font-bold text-ink flex items-center gap-2 truncate">
								<span class="truncate">{otherParticipant?.name || 'Supporter'}</span>
								{#if otherParticipant?.username}
									<span class="text-muted font-normal">@{otherParticipant.username}</span>
								{/if}
							</div>
							<p class="text-muted">Direct supporter channel</p>
						</div>
					</div>
					<span class="text-success font-semibold shrink-0">Realtime active</span>
				</div>

				<!-- Messages Stream -->
				<div class="flex-1 p-5 overflow-y-auto space-y-4">
					{#if isLoadingMessages}
						<div class="py-12 text-muted text-xs">
							Loading conversation history…
						</div>
					{:else if messages.length === 0}
						<div class="py-12 text-muted text-xs">
							No messages in this debate yet. Start the discussion below.
						</div>
					{:else}
						{#each messages as msg}
							{@const isMe = msg.sender_id === data.currentUserId}
							{@const msgClub = CLUBS[msg.sender_club_id] || CLUBS['arsenal']}
							<div class="flex flex-col {isMe ? 'items-end' : 'items-start'}">
								<div class="flex items-center gap-2 mb-1 text-xs text-muted">
									<span class="font-semibold text-ink-2">{msg.sender_name}</span>
									<span>({msgClub.short_name})</span>
									<span class="num font-outlier">{formatTime(msg.created_at)}</span>
								</div>
								<div
									class="max-w-[75%] px-4 py-2.5 rounded-card text-xs leading-relaxed border {isMe ? 'bg-paper-3 text-ink border-rule-2' : 'bg-paper text-ink-2 border-rule'}"
								>
									{msg.content}
								</div>
							</div>
						{/each}
					{/if}
				</div>

				<!-- Message Input Bar -->
				<form
					onsubmit={(e) => {
						e.preventDefault();
						handleSendMessage();
					}}
					class="p-3 border-t border-rule bg-paper flex items-center gap-2.5"
				>
					<input
						type="text"
						aria-label="Direct message reply"
						bind:value={messageInput}
						placeholder="Send a private reply or debate point…"
						class="flex-1 h-10 bg-paper-2 border border-rule rounded-card px-3 text-xs text-ink placeholder-muted"
					/>
					<button
						type="submit"
						disabled={!messageInput.trim() || isSending}
						class="h-10 px-4 rounded-card bg-accent hover:opacity-95 text-accent-ink font-semibold text-xs transition-opacity"
					>
						{sendBtnLabel}
					</button>
				</form>
			{/if}
		</div>
	</div>
	{/if}
</div>

<!-- Modal: Start New Debate -->
{#if showStartModal}
	<div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-paper/85">
		<div class="w-full max-w-md bg-paper-2 border-t-2 border-rule-2 p-6 space-y-5">
			<div class="flex items-center justify-between border-b border-rule pb-3">
				<div>
					<h2 class="text-base font-bold text-ink">Start new debate</h2>
					<p class="text-xs text-muted">Search and select a registered supporter.</p>
				</div>
				<button
					type="button"
					onclick={() => (showStartModal = false)}
					class="text-muted hover:text-ink text-xs font-semibold"
				>
					Close
				</button>
			</div>

			<div class="space-y-4">
				<div class="space-y-2">
					<label for="modal-supporter-search" class="block text-xs font-semibold text-ink-2">
						Search supporters
					</label>
					<input
						id="modal-supporter-search"
						type="search"
						bind:value={supporterQuery}
						placeholder="Type name or @username…"
						class="w-full h-10 bg-paper border border-rule rounded-card px-3 text-xs text-ink placeholder-muted"
					/>

					{#if isSearchingSupporters}
						<p class="text-xs text-muted">Searching supporters…</p>
					{:else if supporterSearchError}
						<p role="alert" class="text-xs text-error">{supporterSearchError}</p>
					{:else if filteredSupporters.length > 0}
						<div class="max-h-44 overflow-y-auto divide-y divide-rule border-y border-rule bg-paper">
							{#each filteredSupporters as supporter}
								{@const sName = supporter.display_name || supporter.username}
								{@const isChosen = targetUserId === supporter.user_id}
								{@const pickLabel = isChosen ? 'Selected' : 'Select'}
								<div
									class="w-full px-3 py-2 flex items-center justify-between gap-3 transition-colors {isChosen ? 'bg-paper-3' : 'hover:bg-paper-2'}"
								>
									<div class="flex items-center gap-2.5 min-w-0">
										{#if supporter.avatar_url}
											<img
												src={supporter.avatar_url}
												alt={sName}
												class="w-7 h-7 rounded-pill object-cover border border-rule shrink-0"
											/>
										{:else}
											<span
												aria-hidden="true"
												class="w-7 h-7 rounded-pill bg-paper-2 border border-rule text-ink-2 text-xs font-bold inline-flex items-center justify-center shrink-0"
											>
												{sName.slice(0, 1).toUpperCase()}
											</span>
										{/if}
										<div class="min-w-0">
											<div class="text-xs font-bold text-ink truncate">{sName}</div>
											<div class="text-xs text-muted truncate">@{supporter.username}</div>
										</div>
									</div>
									<button
										type="button"
										onclick={() => {
											targetUserId = supporter.user_id;
											targetUserName = sName;
											targetUsername = supporter.username;
											targetClubId = supporter.favorite_club_id || 'arsenal';
										}}
										class="h-7 px-2.5 rounded-card border text-xs font-semibold whitespace-nowrap shrink-0 transition-colors {isChosen ? 'border-accent bg-accent text-accent-ink' : 'border-rule bg-paper-2 text-ink-2 hover:text-ink'}"
									>
										{pickLabel}
									</button>
								</div>
							{/each}
						</div>
					{:else}
						<p class="text-xs text-muted">No matching registered supporters found.</p>
					{/if}
				</div>

				{#if targetUserId}
					<div class="p-3 rounded-card bg-paper border border-rule text-xs flex items-center justify-between gap-2">
						<div>
							<span class="text-muted">Recipient: </span>
							<strong class="text-ink">{targetUserName || targetUserId}</strong>
							{#if targetUsername}
								<span class="text-muted"> (@{targetUsername})</span>
							{/if}
						</div>
						<button
							type="button"
							onclick={() => {
								targetUserId = '';
								targetUserName = '';
								targetUsername = '';
							}}
							class="text-muted hover:text-error font-semibold"
						>
							Clear
						</button>
					</div>
				{/if}

				<div>
					<label for="initial-opening-message" class="block text-xs font-semibold text-ink-2 mb-1">
						Opening argument or note (optional)
					</label>
					<textarea
						id="initial-opening-message"
						bind:value={initialNote}
						rows="3"
						placeholder="What would you like to debate?"
						class="w-full bg-paper border border-rule rounded-card p-3 text-xs text-ink"
					></textarea>
				</div>
			</div>

			<div class="flex items-center justify-end gap-3 pt-3 border-t border-rule">
				{#if modalError}
					<span role="alert" class="mr-auto text-xs text-error">{modalError}</span>
				{/if}
				<button
					type="button"
					onclick={() => (showStartModal = false)}
					class="h-9 px-3 rounded-card text-xs font-semibold text-ink-2 hover:text-ink"
				>
					Cancel
				</button>
				<button
					type="button"
					onclick={handleStartNewDebate}
					disabled={!targetUserId.trim() || isStartingDebate}
					class="h-9 px-4 rounded-card bg-accent hover:opacity-95 text-accent-ink font-semibold text-xs transition-opacity disabled:opacity-50"
				>
					{launchBtnLabel}
				</button>
			</div>
		</div>
	</div>
{/if}

<style>
	/* Hallmark · dropped targetUserId = analyst.name, targetUserId = quick.name, target-supporter-id · replaced hardcoded static supporter personas with live supporter directory */
</style>
