<script lang="ts">
	import { onDestroy } from 'svelte';
	import { CLUBS, themeState } from '$lib/stores/theme.svelte';
	import {
		fetchMessages,
		sendMessage,
		createConversation,
		fetchConversations
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

	// Start debate modal
	let showStartModal = $state(false);
	let targetUserId = $state('');
	let targetUserName = $state('');
	let targetClubId = $state('arsenal');
	let initialNote = $state('');
	let isStartingDebate = $state(false);

	let isInitialized = false;
	let realtimeChannel: any = null;

	const viewingClub = $derived(themeState.currentTheme);
	const activeConv = $derived(
		activeConvId ? conversations.find((c) => c.id === activeConvId) : null
	);

	const otherParticipant = $derived.by(() => {
		if (!activeConv) return null;
		const otherId = activeConv.members.find((m) => m !== data.currentUserId) || activeConv.members[0];
		// If last message was from the other person, get their name and club
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
		if (!isInitialized && data.conversations) {
			conversations = data.conversations;
			if (data.initialRecipient) {
				targetUserId = data.initialRecipient.id;
				targetUserName = data.initialRecipient.name;
				targetClubId = data.initialRecipient.club;
				showStartModal = true;
			} else if (data.conversations.length > 0 && !activeConvId) {
				selectConversation(data.conversations[0].id);
			}
			isInitialized = true;
		}
	});

	async function selectConversation(convId: string) {
		activeConvId = convId;
		isLoadingMessages = true;

		// Clean up existing realtime channel if any
		if (realtimeChannel) {
			data.supabase.removeChannel(realtimeChannel);
			realtimeChannel = null;
		}

		try {
			const msgs = await fetchMessages(convId);
			messages = msgs;

			// Subscribe to Supabase Realtime channel for live incoming messages
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
		} finally {
			isLoadingMessages = false;
		}
	}

	async function handleSendMessage() {
		if (!activeConvId || !messageInput.trim() || isSending) return;

		const text = messageInput.trim();
		messageInput = '';
		isSending = true;

		const authorName = data.profile?.display_name || data.user?.email?.split('@')[0] || 'Supporter';
		const authorClub = data.profile?.favorite_club_id || viewingClub.id;

		// Optimistic message
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

		// Update conversation in list
		const targetConv = conversations.find((c) => c.id === activeConvId);
		if (targetConv) {
			targetConv.last_message = optimisticMsg;
			targetConv.updated_at = optimisticMsg.created_at;
			conversations = [
				targetConv,
				...conversations.filter((c) => c.id !== activeConvId)
			];
		}

		try {
			const sent = await sendMessage(activeConvId, {
				sender_id: data.currentUserId,
				sender_name: authorName,
				sender_club_id: authorClub,
				content: text
			});

			if (sent) {
				// Replace optimistic msg with real one
				messages = messages.map((m) => (m.id === optimisticMsg.id ? sent : m));
				if (targetConv) targetConv.last_message = sent;
			}
		} finally {
			isSending = false;
		}
	}

	async function handleStartNewDebate() {
		if (!targetUserId.trim() || isStartingDebate) return;
		isStartingDebate = true;

		const authorName = data.profile?.display_name || data.user?.email?.split('@')[0] || 'Supporter';
		const authorClub = data.profile?.favorite_club_id || viewingClub.id;

		try {
			const conv = await createConversation({
				initiator_id: data.currentUserId,
				recipient_id: targetUserId.trim(),
				initiator_name: authorName,
				initiator_club_id: authorClub,
				initial_message: initialNote.trim() || undefined
			});

			if (conv) {
				showStartModal = false;
				targetUserId = '';
				targetUserName = '';
				initialNote = '';

				// Add or update in list
				if (!conversations.some((c) => c.id === conv.id)) {
					conversations = [conv, ...conversations];
				}
				await selectConversation(conv.id);
			}
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

<div class="max-w-6xl mx-auto px-4 py-6">
	<!-- Header Bar -->
	<div class="border-b border-[#1e2430] pb-4 mb-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
		<div>
			<div class="inline-flex items-center gap-2 px-2.5 py-0.5 rounded text-[11px] font-semibold uppercase tracking-wider mb-1 bg-amber-500/10 text-amber-400 border border-amber-500/20 font-mono">
				Private Debates
			</div>
			<h1 class="text-2xl font-black text-white uppercase tracking-tight">The Dressing Room</h1>
			<p class="text-xs text-gray-400 mt-0.5">
				1-on-1 realtime tactical discussions with rival and fellow supporters.
			</p>
		</div>

		<button
			type="button"
			onclick={() => (showStartModal = true)}
			class="px-3.5 py-2 rounded-lg bg-amber-500 hover:bg-amber-400 text-black font-bold text-xs transition shadow-sm flex items-center justify-center gap-1.5 self-start sm:self-auto"
		>
			<span>+</span>
			<span>Start New Debate</span>
		</button>
	</div>

	<!-- Main Chat Layout -->
	<div class="grid grid-cols-1 md:grid-cols-3 gap-6 h-[650px] border border-[#1e2430] rounded-xl overflow-hidden bg-[#12161f]">
		<!-- Left Sidebar: Debates List -->
		<div class="md:col-span-1 border-r border-[#1e2430] flex flex-col bg-[#0d1017]">
			<div class="p-3 border-b border-[#1e2430] flex items-center justify-between">
				<span class="text-xs font-bold text-gray-400 uppercase tracking-wider">Conversations</span>
				<span class="text-[10px] font-mono px-2 py-0.5 rounded bg-black/40 text-gray-400 border border-[#1e2430]">
					{conversations.length}
				</span>
			</div>

			<div class="flex-1 overflow-y-auto divide-y divide-[#1e2430]">
				{#if conversations.length === 0}
					<div class="p-8 text-center text-gray-500 text-xs">
						<p>No active debates yet.</p>
						<p class="mt-1 text-gray-600">Click "Start New Debate" or challenge someone from The Terrace!</p>
					</div>
				{:else}
					{#each conversations as c}
						{@const isSelected = c.id === activeConvId}
						{@const other = c.members.find((m) => m !== data.currentUserId) || c.members[0]}
						<button
							type="button"
							onclick={() => selectConversation(c.id)}
							class="w-full text-left p-3.5 transition flex flex-col gap-1 {isSelected ? 'bg-white/5 border-l-2 border-amber-400' : 'hover:bg-white/[0.02]'}"
						>
							<div class="flex items-center justify-between">
								<span class="text-xs font-bold text-white truncate">
									{other.startsWith('usr_') ? other.replace('usr_', '') : other}
								</span>
								{#if c.last_message}
									<span class="text-[10px] text-gray-500 font-mono">
										{formatTime(c.last_message.created_at)}
									</span>
								{/if}
							</div>
							<p class="text-xs text-gray-400 truncate">
								{c.last_message ? c.last_message.content : 'No messages yet'}
							</p>
						</button>
					{/each}
				{/if}
			</div>
		</div>

		<!-- Right Side: Active Chat Window -->
		<div class="md:col-span-2 flex flex-col bg-[#12161f]">
			{#if !activeConvId}
				<div class="flex-1 flex flex-col items-center justify-center p-8 text-center text-gray-500">
					<span class="text-3xl mb-2">💬</span>
					<p class="text-sm font-semibold text-gray-300">Select a conversation</p>
					<p class="text-xs text-gray-500 mt-1 max-w-sm">
						Choose a debate from the list on the left, or challenge an analyst from The Terrace to start a 1-on-1 debate.
					</p>
				</div>
			{:else}
				<!-- Chat Header -->
				<div class="p-3.5 border-b border-[#1e2430] bg-[#0d1017] flex items-center justify-between">
					<div class="flex items-center gap-2.5">
						<span class="w-2.5 h-2.5 rounded-full" style="background-color: {CLUBS[otherParticipant?.club_id || 'arsenal']?.primary_color || '#EF0107'}"></span>
						<div>
							<div class="text-xs font-bold text-white flex items-center gap-2">
								<span>{otherParticipant?.name || 'Supporter'}</span>
								<span class="text-[10px] font-mono px-1.5 py-0.2 rounded bg-black/40 text-gray-400 border border-[#1e2430]">
									{CLUBS[otherParticipant?.club_id || 'arsenal']?.short_name || 'Supporter'}
								</span>
							</div>
							<p class="text-[10px] text-gray-500">Encrypted 1-on-1 Supporter Channel</p>
						</div>
					</div>
					<span class="text-[10px] font-mono text-emerald-400 flex items-center gap-1">
						<span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
						<span>Realtime Active</span>
					</span>
				</div>

				<!-- Messages Stream -->
				<div class="flex-1 p-4 overflow-y-auto space-y-3">
					{#if isLoadingMessages}
						<div class="py-12 text-center text-gray-500 text-xs">
							Loading conversation history...
						</div>
					{:else if messages.length === 0}
						<div class="py-12 text-center text-gray-500 text-xs">
							No messages in this debate yet. Break the ice below!
						</div>
					{:else}
						{#each messages as msg}
							{@const isMe = msg.sender_id === data.currentUserId}
							{@const msgClub = CLUBS[msg.sender_club_id] || CLUBS['arsenal']}
							<div class="flex flex-col {isMe ? 'items-end' : 'items-start'}">
								<div class="flex items-center gap-1.5 mb-1 text-[10px] text-gray-500">
									<span class="font-bold text-gray-400">{msg.sender_name}</span>
									<span class="font-mono">({msgClub.short_name})</span>
									<span>•</span>
									<span class="font-mono">{formatTime(msg.created_at)}</span>
								</div>
								<div
									class="max-w-[75%] px-3.5 py-2 rounded-xl text-xs leading-relaxed {isMe ? 'bg-amber-500/20 text-amber-100 border border-amber-500/30' : 'bg-[#1e2430] text-gray-200 border border-gray-700/50'}"
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
					class="p-3 border-t border-[#1e2430] bg-[#0d1017] flex items-center gap-2"
				>
					<input
						type="text"
						bind:value={messageInput}
						placeholder="Send a private reply or debate point..."
						class="flex-1 bg-[#12161f] border border-[#1e2430] rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-amber-400 transition"
					/>
					<button
						type="submit"
						disabled={!messageInput.trim() || isSending}
						class="px-4 py-2 rounded-lg bg-amber-500 hover:bg-amber-400 text-black font-bold text-xs transition disabled:opacity-50"
					>
						{isSending ? 'Sending...' : 'Send'}
					</button>
				</form>
			{/if}
		</div>
	</div>
</div>

<!-- Modal: Start New Debate -->
{#if showStartModal}
	<div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
		<div class="w-full max-w-md bg-[#12161f] border border-[#1e2430] rounded-xl p-6 space-y-4">
			<div class="flex items-center justify-between border-b border-[#1e2430] pb-3">
				<div>
					<h3 class="text-sm font-bold text-white uppercase tracking-wider">Start New Debate</h3>
					<p class="text-[11px] text-gray-400">Open a direct channel with another supporter.</p>
				</div>
				<button
					type="button"
					onclick={() => (showStartModal = false)}
					class="text-gray-400 hover:text-white text-xs font-mono"
				>
					✕
				</button>
			</div>

			<div class="space-y-3">
				<div>
					<label for="target-supporter-id" class="block text-[11px] font-semibold text-gray-300 uppercase mb-1">
						Target Supporter ID or Username
					</label>
					<input
						id="target-supporter-id"
						type="text"
						bind:value={targetUserId}
						placeholder="e.g. MadridistaAnalytics, CuleFan, etc."
						class="w-full bg-[#0a0c10] border border-[#1e2430] rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-amber-400 transition"
					/>
				</div>

				<div>
					<label for="initial-opening-message" class="block text-[11px] font-semibold text-gray-300 uppercase mb-1">
						Opening Argument / Note (Optional)
					</label>
					<textarea
						id="initial-opening-message"
						bind:value={initialNote}
						rows="3"
						placeholder="What would you like to debate?"
						class="w-full bg-[#0a0c10] border border-[#1e2430] rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-amber-400 transition"
					></textarea>
				</div>
			</div>

			<div class="flex items-center justify-end gap-2 pt-2 border-t border-[#1e2430]">
				<button
					type="button"
					onclick={() => (showStartModal = false)}
					class="px-3 py-1.5 rounded-lg border border-[#1e2430] text-xs text-gray-400 hover:text-white transition"
				>
					Cancel
				</button>
				<button
					type="button"
					onclick={handleStartNewDebate}
					disabled={!targetUserId.trim() || isStartingDebate}
					class="px-4 py-1.5 rounded-lg bg-amber-500 hover:bg-amber-400 text-black font-bold text-xs transition disabled:opacity-50"
				>
					{isStartingDebate ? 'Connecting...' : 'Launch Debate'}
				</button>
			</div>
		</div>
	</div>
{/if}
