<script lang="ts">
	import { onDestroy, untrack } from 'svelte';
	import { afterNavigate, replaceState } from '$app/navigation';
	import { page } from '$app/state';
	import { focusTrap } from '$lib/actions/focusTrap';
	import StateBanner from '$lib/components/StateBanner.svelte';
	import { CLUBS, themeState } from '$lib/stores/theme.svelte';
	import {
		ApiError,
		fetchConversationsResult,
		fetchMessages,
		sendMessage,
		createConversation
	} from '$lib/api/football';
	import { searchSupporters, markConversationRead } from '$lib/api/community';
	import type { DirectMessage, Conversation, SupporterSummary } from '$lib/types/football';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	let conversations = $state<Conversation[]>([]);
	let conversationsError = $state<string | null>(null);
	let isRetryingInbox = $state(false);
	let activeConvId = $state<string | null>(null);
	let mobileView = $state<'list' | 'thread'>('list');
	let messages = $state<DirectMessage[]>([]);
	let isLoadingMessages = $state(false);
	let isSending = $state(false);
	let messageInput = $state('');
	let errorBanner = $state<string | null>(null);
	let invalidConvNotice = $state<string | null>(null);

	let realtimeStatus = $state<'connecting' | 'live' | 'reconnecting' | 'offline'>('connecting');
	let messagesContainer = $state<HTMLDivElement | null>(null);

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

	let hasInitializedSearch = false;
	let lastHandledRecipientKey = '';
	let lastHandledMissingConvId = '';
	let realtimeChannel: ReturnType<typeof data.supabase.channel> | null = null;

	let sendBtnLabel = $derived(isSending ? 'Sending…' : 'Send');
	let launchBtnLabel = $derived(isStartingDebate ? 'Connecting…' : 'Launch debate');
	let isSignedIn = $derived(Boolean(data.user && data.session?.access_token && data.currentUserId));
	let authNext = $derived(encodeURIComponent(page.url.pathname + page.url.search));

	const viewingClub = $derived(themeState.currentTheme);
	const activeConv = $derived(
		activeConvId ? conversations.find((c) => c.id === activeConvId) : null
	);

	const filteredSupporters = $derived(
		supporterResults.filter((s) => s.user_id !== data.currentUserId)
	);

	const realtimeLabel = $derived(
		realtimeStatus === 'live'
			? 'Realtime live'
			: realtimeStatus === 'reconnecting'
				? 'Reconnecting…'
				: realtimeStatus === 'offline'
					? 'Realtime offline'
					: 'Connecting…'
	);

	const realtimeStatusClass = $derived(
		realtimeStatus === 'live'
			? 'text-success'
			: realtimeStatus === 'offline'
				? 'text-error'
				: 'text-accent-2'
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
		if (!isSignedIn) {
			conversations = [];
			conversationsError = null;
			supporterResults = [];
			activeConvId = null;
			mobileView = 'list';
			messages = [];
			showStartModal = false;
			lastHandledRecipientKey = '';
			lastHandledMissingConvId = '';
			if (realtimeChannel) {
				data.supabase.removeChannel(realtimeChannel);
				realtimeChannel = null;
			}
			return;
		}

		const loadedConvs = data.conversations || [];
		conversations = loadedConvs;
		conversationsError = data.conversationsError ?? null;

		if (!untrack(() => supporterQuery).trim()) {
			supporterResults = (data.initialSupporters || []).filter(
				(s) => s.user_id !== data.currentUserId
			);
		}

		if (data.initialRecipient) {
			const recipientKey = `${data.initialRecipient.id}:${data.initialRecipient.name}:${data.initialRecipient.club}`;
			if (recipientKey !== lastHandledRecipientKey) {
				lastHandledRecipientKey = recipientKey;
				if (data.initialRecipient.id === data.currentUserId) {
					errorBanner = 'You cannot start a direct debate with yourself.';
				} else {
					const existingConv = loadedConvs.find((c) =>
						c.members.includes(data.initialRecipient!.id)
					);
					if (existingConv) {
						void selectConversation(existingConv.id, false);
					} else {
						targetUserId = data.initialRecipient.id;
						targetUserName = data.initialRecipient.name;
						targetClubId = data.initialRecipient.club;
						showStartModal = true;
					}
				}
			}
		} else {
			lastHandledRecipientKey = '';
			const requestedConvId = data.initialConversationId;
			if (requestedConvId) {
				if (loadedConvs.some((c) => c.id === requestedConvId)) {
					invalidConvNotice = null;
					if (untrack(() => activeConvId) !== requestedConvId) {
						void selectConversation(requestedConvId, false);
					}
				} else if (!data.conversationsError && requestedConvId !== lastHandledMissingConvId) {
					lastHandledMissingConvId = requestedConvId;
					invalidConvNotice =
						'Requested conversation could not be loaded or you are not a member.';
					if (loadedConvs.length > 0 && !untrack(() => activeConvId)) {
						void selectConversation(loadedConvs[0].id, false);
					}
				}
			} else if (loadedConvs.length > 0 && !untrack(() => activeConvId)) {
				void selectConversation(loadedConvs[0].id, false);
			}
		}
	});

	$effect(() => {
		const _convId = activeConvId;
		const _count = messages.length;
		const loading = isLoadingMessages;
		if (!loading && _convId && _count > 0 && messagesContainer) {
			queueMicrotask(() => {
				if (messagesContainer) {
					messagesContainer.scrollTop = messagesContainer.scrollHeight;
				}
			});
		}
	});

	afterNavigate(({ to }) => {
		if (!isSignedIn) return;
		const requestedConvId = to?.url.searchParams.get('c');
		if (
			requestedConvId &&
			conversations.some((c) => c.id === requestedConvId) &&
			activeConvId !== requestedConvId
		) {
			invalidConvNotice = null;
			void selectConversation(requestedConvId, false);
		}
	});

	$effect(() => {
		const userId = data.currentUserId;
		const token = data.session?.access_token ?? null;
		const supabase = data.supabase;
		if (!isSignedIn || !userId || !token || !supabase) return;

		let cancelled = false;
		const notifChannel = supabase
			.channel(`messages-inbox-notifs:${userId}`)
			.on(
				'postgres_changes',
				{
					event: 'INSERT',
					schema: 'public',
					table: 'notifications',
					filter: `user_id=eq.${userId}`
				},
				(payload: { new?: { type?: string; link?: string } }) => {
					if (cancelled) return;
					if (payload.new?.type !== 'direct_message') return;

					void fetchConversationsResult(userId, token).then((res) => {
						if (cancelled || res.error) return;
						const currentActive = untrack(() => activeConvId);
						conversations = res.data.map((conv) =>
							currentActive && conv.id === currentActive
								? { ...conv, unread_count: 0 }
								: conv
						);
					});
				}
			)
			.subscribe();

		return () => {
			cancelled = true;
			supabase.removeChannel(notifChannel);
		};
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

	async function retryLoadInbox() {
		if (!isSignedIn || !data.currentUserId || isRetryingInbox) return;
		isRetryingInbox = true;
		conversationsError = null;
		try {
			const res = await fetchConversationsResult(
				data.currentUserId,
				data.session?.access_token
			);
			if (res.error) {
				conversationsError = res.error;
				return;
			}
			conversations = res.data;
			if (res.data.length > 0 && !activeConvId) {
				await selectConversation(res.data[0].id, false);
			}
		} finally {
			isRetryingInbox = false;
		}
	}

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

	async function selectConversation(convId: string, syncUrl = true) {
		if (!isSignedIn) return;
		activeConvId = convId;
		mobileView = 'thread';
		isLoadingMessages = true;
		errorBanner = null;
		realtimeStatus = 'connecting';

		if (syncUrl && typeof window !== 'undefined' && page.url.searchParams.get('c') !== convId) {
			replaceState(`/messages?c=${encodeURIComponent(convId)}`, page.state);
		}

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
							const optIdx =
								incoming.sender_id === data.currentUserId
									? messages.findIndex(
											(m) =>
												m.id.startsWith('msg_opt_') &&
												m.content === incoming.content
										)
									: -1;

							if (optIdx !== -1) {
								messages = messages.map((m, idx) =>
									idx === optIdx ? incoming : m
								);
							} else {
								messages = [...messages, incoming];
							}
						}

						conversations = conversations.map((c) =>
							c.id === convId
								? {
										...c,
										last_message: incoming,
										updated_at: incoming.created_at,
										unread_count: 0
									}
								: c
						);
						if (incoming.sender_id !== data.currentUserId) {
							void markThreadRead(convId);
						}
					}
				)
				.subscribe((status) => {
					if (activeConvId !== convId) return;
					if (status === 'SUBSCRIBED') {
						realtimeStatus = 'live';
					} else if (status === 'CHANNEL_ERROR' || status === 'TIMED_OUT') {
						realtimeStatus = 'reconnecting';
					} else if (status === 'CLOSED') {
						realtimeStatus = 'offline';
					}
				});
		} catch (err) {
			messages = [];
			realtimeStatus = 'offline';
			errorBanner =
				err instanceof ApiError
					? err.detail
					: 'Could not load conversation messages. Please try again.';
		} finally {
			isLoadingMessages = false;
		}
	}

	function openDirectoryView() {
		activeConvId = null;
		mobileView = 'thread';
		if (realtimeChannel) {
			data.supabase.removeChannel(realtimeChannel);
			realtimeChannel = null;
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
				if (messages.some((m) => m.id === sent.id)) {
					messages = messages.filter((m) => m.id !== optimisticMsg.id);
				} else {
					messages = messages.map((m) => (m.id === optimisticMsg.id ? sent : m));
				}
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
				await selectConversation(conv.id, true);
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

	function getDayKey(isoStr: string): string {
		const d = new Date(isoStr);
		if (Number.isNaN(d.getTime())) return isoStr;
		return `${d.getFullYear()}-${d.getMonth()}-${d.getDate()}`;
	}

	function formatDayDivider(isoStr: string): string {
		const d = new Date(isoStr);
		if (Number.isNaN(d.getTime())) return '';
		const today = new Date();
		const yesterday = new Date();
		yesterday.setDate(today.getDate() - 1);

		if (d.toDateString() === today.toDateString()) return 'Today';
		if (d.toDateString() === yesterday.toDateString()) return 'Yesterday';
		return d.toLocaleDateString(undefined, {
			month: 'short',
			day: 'numeric',
			year: 'numeric'
		});
	}
</script>

<svelte:head>
	<title>The Dressing Room | Direct Debates</title>
</svelte:head>

<div class="container py-8 space-y-6">
	<!-- Compact Header Bar -->
	<div class="border-b border-rule pb-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
		<p class="text-sm text-ink-2">
			Direct realtime tactical discussions with fellow Arsenal supporters and analysts.
		</p>

		{#if isSignedIn}
			<button
				type="button"
				onclick={() => (showStartModal = true)}
				class="min-h-[40px] px-4 rounded-card bg-accent hover:opacity-95 text-accent-ink font-semibold text-xs transition-opacity self-start sm:self-auto whitespace-nowrap"
			>
				Start new debate
			</button>
		{/if}
	</div>

	{#if invalidConvNotice}
		<div role="status" class="p-3.5 bg-paper-2 border border-rule border-l-2 border-l-accent-2 text-ink-2 text-xs flex items-center justify-between gap-4">
			<span>{invalidConvNotice}</span>
			<button type="button" onclick={() => (invalidConvNotice = null)} class="min-h-[44px] px-2 text-muted hover:text-ink font-semibold shrink-0">Dismiss</button>
		</div>
	{/if}

	{#if errorBanner}
		<div role="alert" class="p-3.5 rounded-card bg-paper-2 border border-rule text-error text-xs flex items-center justify-between gap-4">
			<span>{errorBanner}</span>
			<button type="button" onclick={() => (errorBanner = null)} class="min-h-[44px] px-2 text-muted hover:text-ink font-semibold shrink-0">Dismiss</button>
		</div>
	{/if}

	{#if !isSignedIn}
		<section class="border-t-2 border-rule-2 border-b border-rule bg-paper-2 p-8 space-y-5 max-w-xl">
			<div class="space-y-2">
				<h2 class="text-lg font-bold text-ink">Sign in to access direct debates</h2>
				<p class="text-sm text-ink-2 leading-relaxed">
					The Dressing Room hosts private supporter conversations and tactical debates. Sign in with your Gunners account to view active threads or challenge supporters.
				</p>
			</div>
			<div class="flex flex-wrap items-center gap-3">
				<a
					href="/login?next={authNext}"
					class="inline-flex items-center min-h-[44px] px-5 rounded-card bg-accent hover:opacity-95 text-accent-ink font-semibold text-xs transition-opacity"
				>
					Sign in
				</a>
				<a
					href="/signup?next={authNext}"
					class="inline-flex items-center min-h-[44px] px-4 rounded-card border border-rule bg-paper hover:bg-paper-3 text-ink font-semibold text-xs transition-colors"
				>
					Create free account
				</a>
			</div>
		</section>
	{:else if conversationsError && conversations.length === 0}
		<StateBanner
			variant="error"
			title="Debates inbox unavailable"
			message={conversationsError}
			onretry={retryLoadInbox}
			busy={isRetryingInbox}
		/>
	{:else}
		{#if conversationsError}
			<StateBanner
				variant="warning"
				title="Inbox refresh issue"
				message={conversationsError}
				onretry={retryLoadInbox}
				busy={isRetryingInbox}
			/>
		{/if}

		<!-- Main Chat Layout -->
		<div class="grid grid-cols-1 md:grid-cols-12 h-[min(74dvh,640px)] min-h-[420px] border border-rule bg-paper-2 overflow-hidden">
			<!-- Left Sidebar: Debates List (4 cols) -->
			<div
				class="md:col-span-4 border-b md:border-b-0 md:border-r border-rule flex-col min-h-0 overflow-hidden bg-paper {mobileView === 'list' ? 'flex' : 'hidden md:flex'}"
			>
				<div class="p-4 border-b border-rule flex items-center justify-between gap-2 text-xs">
					<div class="flex items-center gap-2">
						<span class="font-bold text-ink">Conversations</span>
						<span class="num font-outlier text-muted">
							{conversations.length}
						</span>
					</div>
					{#if activeConvId}
						<button
							type="button"
							onclick={openDirectoryView}
							class="min-h-[36px] px-2 text-xs font-semibold text-accent-text hover:text-ink transition-colors whitespace-nowrap"
						>
							Find supporter
						</button>
					{/if}
				</div>

				<div class="flex-1 min-h-0 overflow-y-auto divide-y divide-rule">
					{#if conversations.length === 0}
						<div class="p-8 text-muted text-xs space-y-1">
							<p class="font-semibold text-ink-2">No active debates yet.</p>
							<p>Select “Start new debate” or search for a registered supporter.</p>
						</div>
					{:else}
						{#each conversations as c (c.id)}
							{@const isSelected = c.id === activeConvId}
							{@const participant = getConversationParticipant(c)}
							{@const displayName = participant?.name || 'Supporter'}
							{@const lastSnippet = c.last_message ? c.last_message.content : 'No messages yet'}
							{@const unreadTotal = c.unread_count ?? 0}
							<button
								type="button"
								onclick={() => selectConversation(c.id)}
								aria-current={isSelected ? 'true' : undefined}
								class="debate-row-btn w-full text-left p-4 transition-colors flex items-start gap-3 {isSelected ? 'bg-paper-2 border-l-2 border-l-accent-2' : 'hover:bg-paper-2'}"
							>
								{#if participant?.avatar_url}
									<img
										src={participant.avatar_url}
										alt=""
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

								<div class="min-w-0 flex-1 space-y-1 whitespace-normal">
									<div class="flex items-center justify-between gap-2">
										<span class="text-xs font-bold text-ink truncate">
											{displayName}
										</span>
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
							</button>
						{/each}
					{/if}
				</div>
			</div>

			<!-- Right Side: Active Chat Window (8 cols) -->
			<div
				class="md:col-span-8 flex-col min-h-0 overflow-hidden bg-paper-2 {mobileView === 'thread' ? 'flex' : 'hidden md:flex'}"
			>
				{#if !activeConvId}
					<div class="flex-1 min-h-0 flex flex-col justify-start p-6 sm:p-8 text-xs text-muted overflow-y-auto space-y-6">
						<div class="flex items-center justify-between gap-3">
							<div class="space-y-1">
								<h2 class="text-lg font-bold text-ink">Select or start a debate</h2>
								<p class="text-sm text-ink-2">
									Search registered Arsenal supporters below to launch a direct tactical conversation.
								</p>
							</div>
							{#if conversations.length > 0}
								<button
									type="button"
									onclick={() => (mobileView = 'list')}
									class="md:hidden min-h-[44px] px-3 rounded-card border border-rule bg-paper text-ink text-xs font-semibold shrink-0"
								>
									Conversations
								</button>
							{/if}
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
								class="w-full min-h-[44px] bg-paper border border-rule rounded-card px-3 text-xs text-ink placeholder-muted"
							/>

							{#if supporterSearchError}
								<p role="alert" class="text-xs text-error">{supporterSearchError}</p>
							{:else if isSearchingSupporters}
								<p role="status" class="text-xs text-muted">Searching supporter directory…</p>
							{:else if filteredSupporters.length === 0}
								<p class="text-xs text-muted">No matching supporters found.</p>
							{:else}
								<div class="divide-y divide-rule border-t border-rule">
									{#each filteredSupporters as supporter (supporter.user_id)}
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
												class="min-h-[44px] px-3 rounded-card bg-paper border border-rule text-accent-2 hover:text-ink font-semibold text-xs transition-colors shrink-0"
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
					<div class="p-3 sm:p-4 border-b border-rule bg-paper flex items-center justify-between text-xs gap-3 shrink-0">
						<div class="flex items-center gap-2.5 min-w-0">
							<button
								type="button"
								onclick={() => (mobileView = 'list')}
								aria-label="Back to conversations"
								class="md:hidden min-h-[44px] px-2.5 rounded-card border border-rule bg-paper-2 hover:bg-paper-3 text-ink text-xs font-semibold shrink-0 whitespace-nowrap"
							>
								← Debates
							</button>

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
										<span class="text-muted font-normal truncate">@{otherParticipant.username}</span>
									{/if}
								</div>
								<p class="text-muted truncate">Direct supporter channel</p>
							</div>
						</div>
						<span role="status" aria-live="polite" class="{realtimeStatusClass} font-semibold shrink-0 whitespace-nowrap">
							{realtimeLabel}
						</span>
					</div>

					<!-- Messages Stream -->
					<div bind:this={messagesContainer} class="flex-1 min-h-0 p-4 sm:p-5 overflow-y-auto space-y-4">
						{#if isLoadingMessages}
							<div role="status" class="py-12 text-muted text-xs">
								Loading conversation history…
							</div>
						{:else if messages.length === 0}
							<div class="py-12 text-muted text-xs">
								No messages in this debate yet. Start the discussion below.
							</div>
						{:else}
							{#each messages as msg, idx (msg.id)}
								{@const isMe = msg.sender_id === data.currentUserId}
								{@const msgClub = CLUBS[msg.sender_club_id] || CLUBS['arsenal']}
								{@const showDayDivider = idx === 0 || getDayKey(messages[idx - 1].created_at) !== getDayKey(msg.created_at)}
								{#if showDayDivider}
									<div class="flex items-center gap-3 my-2 text-xs text-muted">
										<span class="flex-1 h-px bg-rule"></span>
										<span>{formatDayDivider(msg.created_at)}</span>
										<span class="flex-1 h-px bg-rule"></span>
									</div>
								{/if}
								<div class="flex flex-col {isMe ? 'items-end' : 'items-start'}">
									<div class="flex items-center gap-2 mb-1 text-xs text-muted flex-wrap">
										<span class="font-semibold text-ink-2">{msg.sender_name}</span>
										{#if msg.sender_club_id !== 'arsenal'}
											<span>({msgClub.short_name})</span>
										{/if}
										<span class="num font-outlier">{formatTime(msg.created_at)}</span>
									</div>
									<div
										class="max-w-[80%] sm:max-w-[75%] px-4 py-2.5 rounded-card text-xs leading-relaxed border break-words [overflow-wrap:anywhere] {isMe ? 'bg-paper-3 text-ink border-rule-2' : 'bg-paper text-ink-2 border-rule'}"
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
						class="p-3 border-t border-rule bg-paper flex items-center gap-2.5 shrink-0"
					>
						<input
							type="text"
							aria-label="Direct message reply"
							bind:value={messageInput}
							placeholder="Send a private reply or debate point…"
							class="flex-1 min-w-0 min-h-[44px] bg-paper-2 border border-rule rounded-card px-3 text-xs text-ink placeholder-muted"
						/>
						<button
							type="submit"
							disabled={!messageInput.trim() || isSending}
							class="min-h-[44px] px-4 rounded-card bg-accent hover:opacity-95 text-accent-ink font-semibold text-xs transition-opacity shrink-0 disabled:opacity-50"
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
	<div
		class="fixed inset-0 z-[var(--z-modal)] flex items-center justify-center p-4 bg-paper/85"
		role="presentation"
		onclick={(e) => {
			if (e.target === e.currentTarget) showStartModal = false;
		}}
	>
		<div
			role="dialog"
			aria-modal="true"
			aria-labelledby="start-debate-title"
			use:focusTrap={{
				active: showStartModal,
				onEscape: () => (showStartModal = false),
				initialFocusSelector: '#modal-supporter-search'
			}}
			class="w-full max-w-md bg-paper-2 border-t-2 border-rule-2 p-6 space-y-5 max-h-[90dvh] overflow-y-auto"
		>
			<div class="flex items-center justify-between border-b border-rule pb-3 gap-3">
				<div>
					<h2 id="start-debate-title" class="text-base font-bold text-ink">Start new debate</h2>
					<p class="text-xs text-muted">Search and select a registered supporter.</p>
				</div>
				<button
					type="button"
					onclick={() => (showStartModal = false)}
					class="min-h-[44px] px-2.5 text-muted hover:text-ink text-xs font-semibold shrink-0"
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
						class="w-full min-h-[44px] bg-paper border border-rule rounded-card px-3 text-xs text-ink placeholder-muted"
					/>

					{#if isSearchingSupporters}
						<p role="status" class="text-xs text-muted">Searching supporters…</p>
					{:else if supporterSearchError}
						<p role="alert" class="text-xs text-error">{supporterSearchError}</p>
					{:else if filteredSupporters.length > 0}
						<div class="max-h-48 overflow-y-auto divide-y divide-rule border-y border-rule bg-paper" aria-label="Registered supporters">
							{#each filteredSupporters as supporter (supporter.user_id)}
								{@const sName = supporter.display_name || supporter.username}
								{@const isChosen = targetUserId === supporter.user_id}
								{@const pickLabel = isChosen ? 'Selected' : 'Select'}
								<button
									type="button"
									aria-pressed={isChosen}
									onclick={() => {
										targetUserId = supporter.user_id;
										targetUserName = sName;
										targetUsername = supporter.username;
										targetClubId = supporter.favorite_club_id || 'arsenal';
									}}
									class="debate-row-btn w-full text-left px-3 py-2.5 min-h-[44px] flex items-center justify-between gap-3 transition-colors {isChosen ? 'bg-paper-3' : 'hover:bg-paper-2'}"
								>
									<div class="flex items-center gap-2.5 min-w-0 whitespace-normal">
										{#if supporter.avatar_url}
											<img
												src={supporter.avatar_url}
												alt=""
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
									<span
										class="px-2.5 py-1 rounded-card border text-xs font-semibold whitespace-nowrap shrink-0 transition-colors {isChosen ? 'border-accent bg-accent text-accent-ink' : 'border-rule bg-paper-2 text-ink-2'}"
									>
										{pickLabel}
									</span>
								</button>
							{/each}
						</div>
					{:else}
						<p class="text-xs text-muted">No matching registered supporters found.</p>
					{/if}
				</div>

				{#if targetUserId}
					<div class="p-3 rounded-card bg-paper border border-rule text-xs flex items-center justify-between gap-2">
						<div class="min-w-0">
							<span class="text-muted">Recipient: </span>
							<strong class="text-ink break-words">{targetUserName || targetUserId}</strong>
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
							class="min-h-[36px] px-2 text-muted hover:text-error font-semibold shrink-0"
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

			<div class="flex flex-wrap items-center justify-end gap-3 pt-3 border-t border-rule">
				{#if modalError}
					<span role="alert" class="mr-auto text-xs text-error">{modalError}</span>
				{/if}
				<button
					type="button"
					onclick={() => (showStartModal = false)}
					class="min-h-[44px] px-3 rounded-card text-xs font-semibold text-ink-2 hover:text-ink"
				>
					Cancel
				</button>
				<button
					type="button"
					onclick={handleStartNewDebate}
					disabled={!targetUserId.trim() || isStartingDebate}
					class="min-h-[44px] px-4 rounded-card bg-accent hover:opacity-95 text-accent-ink font-semibold text-xs transition-opacity disabled:opacity-50"
				>
					{launchBtnLabel}
				</button>
			</div>
		</div>
	</div>
{/if}

<style>
	/* Hallmark · dropped targetUserId = analyst.name, targetUserId = quick.name, target-supporter-id · replaced hardcoded static supporter personas with live supporter directory */
	.debate-row-btn {
		white-space: nowrap;
	}
</style>
