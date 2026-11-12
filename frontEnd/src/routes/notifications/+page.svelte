<script lang="ts">
	import { ApiError, markNotificationRead, markAllNotificationsRead } from '$lib/api/football';
	import type { Notification } from '$lib/types/football';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	let notifications = $state<Notification[]>([]);
	let unreadCount = $state(0);
	let errorBanner = $state<string | null>(null);
	let isInitialized = false;
	let markAllLabel = $derived(`Mark all read (${unreadCount})`);
	let isSignedIn = $derived(Boolean(data.user && data.session?.access_token && data.currentUserId));

	$effect(() => {
		if (!isInitialized && data.notifications) {
			notifications = data.notifications;
			unreadCount = data.unreadCount;
			isInitialized = true;
		}
	});

	async function handleMarkRead(notif: Notification) {
		if (!isSignedIn || notif.is_read) return;
		errorBanner = null;
		const prevUnread = unreadCount;
		notif.is_read = true;
		const nextUnread = Math.max(0, unreadCount - 1);
		unreadCount = nextUnread;
		try {
			await markNotificationRead(notif.id, data.session?.access_token);
			window.dispatchEvent(
				new CustomEvent('gunners:notifications-updated', { detail: { unreadCount: nextUnread } })
			);
		} catch (err) {
			notif.is_read = false;
			unreadCount = prevUnread;
			errorBanner =
				err instanceof ApiError
					? err.detail
					: 'Could not mark notification as read. Please try again.';
		}
	}

	async function handleMarkAllRead() {
		if (!isSignedIn || !data.currentUserId) return;
		errorBanner = null;
		const prevUnread = unreadCount;
		const prevStates = notifications.map((n) => n.is_read);
		for (const n of notifications) {
			n.is_read = true;
		}
		unreadCount = 0;
		try {
			await markAllNotificationsRead(data.currentUserId, data.session?.access_token);
			window.dispatchEvent(
				new CustomEvent('gunners:notifications-updated', { detail: { unreadCount: 0 } })
			);
		} catch (err) {
			notifications.forEach((n, idx) => {
				n.is_read = prevStates[idx];
			});
			unreadCount = prevUnread;
			errorBanner =
				err instanceof ApiError
					? err.detail
					: 'Could not mark all notifications as read. Please try again.';
		}
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

	function getNotificationLabel(type: string): string {
		switch (type) {
			case 'cheer':
				return 'Cheer';
			case 'comment':
			case 'reply':
				return 'Reply';
			case 'direct_message':
				return 'Debate';
			case 'prediction_result':
				return 'Predictor';
			default:
				return 'Alert';
		}
	}
</script>

<svelte:head>
	<title>Notifications | GUNNERS</title>
</svelte:head>

<div class="container py-12 space-y-10 max-w-3xl">
	<!-- Page Header -->
	<div class="border-b-2 border-rule-2 pb-6 flex items-end justify-between gap-4">
		<div class="space-y-2">
			<h1>Notifications</h1>
			<p class="text-sm text-ink-2">Alerts from Terrace discussions, direct debates, and matchday predictions.</p>
		</div>

		{#if isSignedIn && unreadCount > 0}
			<button
				type="button"
				onclick={handleMarkAllRead}
				class="h-9 px-3.5 rounded-card bg-paper-2 hover:bg-paper-3 border border-rule text-xs font-semibold text-ink transition-colors"
			>
				{markAllLabel}
			</button>
		{/if}
	</div>

	{#if errorBanner}
		<div role="alert" class="p-3.5 rounded-card bg-paper-2 border border-rule text-error text-xs flex items-center justify-between gap-4">
			<span>{errorBanner}</span>
			<button type="button" onclick={() => (errorBanner = null)} class="text-muted hover:text-ink font-semibold shrink-0">Dismiss</button>
		</div>
	{/if}

	<!-- Notifications List -->
	{#if !isSignedIn}
		<div class="py-10 px-6 border border-rule bg-paper-2 space-y-4">
			<div class="space-y-1">
				<p class="text-sm font-bold text-ink">Sign in to view notifications</p>
				<p class="text-xs text-muted">Track cheers on your tactical insights, Terrace replies, and matchday predictor alerts.</p>
			</div>
			<a
				href="/login"
				class="inline-flex items-center h-9 px-4 rounded-card bg-accent hover:opacity-95 text-accent-ink text-xs font-semibold transition-opacity"
			>
				Sign in
			</a>
		</div>
	{:else if notifications.length === 0}
		<div class="py-12 border-t border-rule text-muted text-sm space-y-1">
			<p class="font-semibold text-ink-2">No notifications yet.</p>
			<p>You will receive alerts when supporters cheer your insights or reply to your debates.</p>
		</div>
	{:else}
		<div class="divide-y divide-rule border-y border-rule">
			{#each notifications as notif}
				<a
					href={notif.link}
					onclick={() => handleMarkRead(notif)}
					class="py-4 px-3 flex items-start justify-between gap-4 transition-colors block {notif.is_read ? 'hover:bg-paper-2' : 'bg-paper-2 border-l-2 border-accent-2'}"
				>
					<div class="space-y-1 min-w-0">
						<div class="flex items-center gap-2.5 text-xs">
							<span class="font-semibold text-accent-2">{getNotificationLabel(notif.type)}</span>
							<h2 class="text-sm font-bold text-ink truncate">
								{notif.title}
							</h2>
						</div>
						<p class="text-xs text-ink-2 leading-relaxed">
							{notif.message}
						</p>
					</div>
					<span class="text-xs text-muted num font-outlier shrink-0">
						{formatTimestamp(notif.created_at)}
					</span>
				</a>
			{/each}
		</div>
	{/if}
</div>
