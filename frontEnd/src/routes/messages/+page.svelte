<script lang="ts">
	import { onDestroy } from 'svelte';
	import { CLUBS, themeState } from '$lib/stores/theme.svelte';
	import {
		ApiError,
		fetchMessages,
		sendMessage,
		createConversation
	} from '$lib/api/football';
	import type { DirectMessage, Conversation } from '$lib/types/football';
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
	let targetClubId = $state('arsenal');
	let initialNote = $state('');
	let isStartingDebate = $state(false);
	let modalError = $state<string | null>(null);

	let isInitialized = false;
	let realtimeChannel: any = null;

	let sendBtnLabel = $derived(isSending ? 'Sending…' : 'Send');
	let launchBtnLabel = $derived(isStartingDebate ? 'Connecting…' : 'Launch debate');
	let isSignedIn = $derived(Boolean(data.user && data.session?.access_token && data.currentUserId));

	const viewingClub = $derived(themeState.currentTheme);
	const activeConv = $derived(
		activeConvId ? conversations.find((c) => c.id === activeConvId) : null
	);

	const otherParticipant = $derived.by(() => {
		if (!activeConv) return null;
		const otherId = activeConv.members.find((m) => m !== data.currentUserId) || activeConv.members[0];
		if (activeConv.last_message && activeConv.last_message.sender_id === otherId) {
			return {
				id: otherId,
				name: activeConv.last_message.sender_name,
				club_id: activeConv.last_message.sender_club_id
			};
		}
		return {
			id: otherId,
			name: otherId.startsWith('usr_') ? otherId.replace('usr_', '') : otherId,
			club_id: 'arsenal'
		};
	});

	$effect(() => {
		if (!showStartModal) {
			modalError = null;
		}
	});

	$effect(() => {
		if (!isInitialized && data.conversations) {
			conversations = data.conversations;
			if (isSignedIn) {
				if (data.initialRecipient) {
					targetUserId = data.initialRecipient.id;
					targetUserName = data.initialRecipient.name;
					targetClubId = data.initialRecipient.club;
					showStartModal = true;
				} else if (data.conversations.length > 0 && !activeConvId) {
					selectConversation(data.conversations[0].id);
				}
			}
			isInitialized = true;
		}
	});

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
			messages = msgs;

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
						if (payload.new && !messages.some((m) => m.id === payload.new.id)) {
							messages = [...messages, payload.new];
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
					The Dressing Room hosts private supporter conversations and tactical debates. Sign in with your Gunners account to view active threads or challenge analysts.
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
						<p>Select “Start new debate” or challenge someone from The Terrace.</p>
					</div>
				{:else}
					{#each conversations as c}
						{@const isSelected = c.id === activeConvId}
						{@const other = c.members.find((m) => m !== data.currentUserId) || c.members[0] || ''}
						{@const displayOther = other.startsWith('usr_') ? other.replace('usr_', '') : other}
						{@const lastSnippet = c.last_message ? c.last_message.content : 'No messages yet'}
						<div class="p-4 transition-colors flex flex-col gap-1 {isSelected ? 'bg-paper-2 border-l-2 border-accent-2' : 'hover:bg-paper-2'}">
							<div class="flex items-center justify-between gap-2">
								<button
									type="button"
									onclick={() => selectConversation(c.id)}
									class="text-xs font-bold text-ink hover:text-accent transition-colors truncate text-left"
								>
									{displayOther}
								</button>
								{#if c.last_message}
									<span class="text-xs text-muted num font-outlier shrink-0">
										{formatTime(c.last_message.created_at)}
									</span>
								{/if}
							</div>
							<p class="text-xs text-muted truncate">
								{lastSnippet}
							</p>
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
							Connect directly with community analysts for one-on-one tactical debriefs.
						</p>
					</div>

					<div class="w-full max-w-lg space-y-3 border-t border-rule pt-4">
						<p class="text-xs font-semibold text-ink-2">
							Featured community analysts
						</p>
						<div class="divide-y divide-rule">
							{#each [
								{ name: 'GoonerAlex', club: 'arsenal', desc: 'Emirates high press & overload specialist' },
								{ name: 'ClockEndTactician', club: 'arsenal', desc: '3-2-4-1 inverted low-block breaker & pivot analyst' },
								{ name: 'NorthBankFan', club: 'arsenal', desc: 'Set-piece conversion & defensive wall tracker' },
								{ name: 'AshburtonAnalyst', club: 'arsenal', desc: 'Statistical modeling, xG, and duel success analyst' }
							] as analyst}
								{@const clb = CLUBS[analyst.club] || CLUBS.arsenal}
								<div class="py-3 flex items-center justify-between gap-4">
									<div>
										<div class="text-xs font-bold text-ink flex items-center gap-2">
											<span>{analyst.name}</span>
											<span class="text-muted font-normal">{clb.short_name}</span>
										</div>
										<p class="text-xs text-muted mt-0.5">{analyst.desc}</p>
									</div>
									<button
										type="button"
										onclick={() => {
											targetUserId = analyst.name;
											targetUserName = analyst.name;
											targetClubId = analyst.club;
											showStartModal = true;
										}}
										class="h-8 px-3 rounded-card bg-paper border border-rule text-accent-2 hover:text-ink font-semibold text-xs transition-colors"
									>
										Debate
									</button>
								</div>
							{/each}
						</div>
					</div>
				</div>
			{:else}
				<!-- Chat Header -->
				<div class="p-4 border-b border-rule bg-paper flex items-center justify-between text-xs">
					<div>
						<div class="font-bold text-ink flex items-center gap-2">
							<span>{otherParticipant?.name || 'Supporter'}</span>
							<span class="text-muted font-normal">
								{CLUBS[otherParticipant?.club_id || 'arsenal']?.short_name || 'ARS'}
							</span>
						</div>
						<p class="text-muted">Direct supporter channel</p>
					</div>
					<span class="text-success font-semibold">Realtime active</span>
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
					<p class="text-xs text-muted">Open a direct channel with another supporter.</p>
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
				<div>
					<label for="target-supporter-id" class="block text-xs font-semibold text-ink-2 mb-1">
						Target supporter ID or username
					</label>
					<input
						id="target-supporter-id"
						type="text"
						bind:value={targetUserId}
						placeholder="e.g. GoonerAlex, ClockEndTactician…"
						class="w-full h-10 bg-paper border border-rule rounded-card px-3 text-xs text-ink"
					/>
					<div class="flex items-center gap-2 flex-wrap pt-2">
						{#each [
							{ name: 'GoonerAlex', club: 'arsenal' },
							{ name: 'ClockEndTactician', club: 'arsenal' },
							{ name: 'NorthBankFan', club: 'arsenal' },
							{ name: 'AshburtonAnalyst', club: 'arsenal' }
						] as quick}
							<button
								type="button"
								onclick={() => {
									targetUserId = quick.name;
									targetUserName = quick.name;
									targetClubId = quick.club;
								}}
								class="h-7 px-2.5 rounded-card text-xs border transition-colors {targetUserId === quick.name ? 'border-accent-2 bg-paper-3 text-accent-2 font-semibold' : 'border-rule bg-paper text-ink-2 hover:text-ink'}"
							>
								@{quick.name}
							</button>
						{/each}
					</div>
				</div>

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
					class="h-9 px-4 rounded-card bg-accent hover:opacity-95 text-accent-ink font-semibold text-xs transition-opacity"
				>
					{launchBtnLabel}
				</button>
			</div>
		</div>
	</div>
{/if}
