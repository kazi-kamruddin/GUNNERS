<script lang="ts">
	import { markNotificationRead, markAllNotificationsRead } from '$lib/api/football';
	import type { Notification } from '$lib/types/football';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	let notifications = $state<Notification[]>([]);
	let unreadCount = $state(0);
	let isInitialized = false;

	$effect(() => {
		if (!isInitialized && data.notifications) {
			notifications = data.notifications;
			unreadCount = data.unreadCount;
			isInitialized = true;
		}
	});

	async function handleMarkRead(notif: Notification) {
		if (!notif.is_read) {
			notif.is_read = true;
			unreadCount = Math.max(0, unreadCount - 1);
			await markNotificationRead(notif.id);
		}
	}

	async function handleMarkAllRead() {
		for (const n of notifications) {
			n.is_read = true;
		}
		unreadCount = 0;
		await markAllNotificationsRead(data.currentUserId);
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

	function getNotificationIcon(type: string): string {
		switch (type) {
			case 'cheer':
				return '🔥';
			case 'comment':
				return '💬';
			case 'direct_message':
				return '⚡';
			case 'prediction_result':
				return '🎯';
			default:
				return '📢';
		}
	}
</script>

<svelte:head>
	<title>Notifications Hub | GUNNERS Reborn</title>
</svelte:head>

<div class="max-w-3xl mx-auto px-4 py-8 space-y-6">
	<!-- Page Header -->
	<div class="border-b border-[#1e2430] pb-4 flex items-center justify-between">
		<div>
			<div class="inline-flex items-center gap-2 px-2.5 py-0.5 rounded text-[11px] font-semibold uppercase tracking-wider mb-1 bg-amber-500/10 text-amber-400 border border-amber-500/20 font-mono">
				Activity Center
			</div>
			<h1 class="text-2xl font-black text-white uppercase tracking-tight">Notifications</h1>
		</div>

		{#if unreadCount > 0}
			<button
				type="button"
				onclick={handleMarkAllRead}
				class="px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 border border-[#1e2430] text-xs font-semibold text-gray-300 transition"
			>
				Mark All as Read ({unreadCount})
			</button>
		{/if}
	</div>

	<!-- Notifications List -->
	{#if notifications.length === 0}
		<div class="py-16 text-center border border-dashed border-[#1e2430] rounded-xl text-gray-500 text-xs">
			<p>No notifications yet.</p>
			<p class="mt-1 text-gray-600">You'll receive alerts when supporters cheer your insights or reply to your debates.</p>
		</div>
	{:else}
		<div class="divide-y divide-[#1e2430] border border-[#1e2430] rounded-xl overflow-hidden bg-[#12161f]">
			{#each notifications as notif}
				<a
					href={notif.link}
					onclick={() => handleMarkRead(notif)}
					class="p-4 flex items-start gap-3.5 transition group block {notif.is_read ? 'hover:bg-white/[0.02]' : 'bg-white/[0.04] border-l-2 border-amber-400'}"
				>
					<span class="text-xl shrink-0 mt-0.5">{getNotificationIcon(notif.type)}</span>
					<div class="flex-1 min-w-0">
						<div class="flex items-center justify-between gap-2 mb-1">
							<h3 class="text-xs font-bold text-white group-hover:text-amber-400 transition truncate">
								{notif.title}
							</h3>
							<span class="text-[10px] text-gray-500 font-mono shrink-0">
								{formatTimestamp(notif.created_at)}
							</span>
						</div>
						<p class="text-xs text-gray-400 leading-relaxed">
							{notif.message}
						</p>
					</div>
					{#if !notif.is_read}
						<span class="w-2 h-2 rounded-full bg-amber-400 shrink-0 self-center"></span>
					{/if}
				</a>
			{/each}
		</div>
	{/if}
</div>
