<script lang="ts">
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import {
		ApiError,
		fetchNotificationsResult,
		fetchUnreadNotificationsCount,
		markNotificationRead,
		markAllNotificationsRead
	} from '$lib/api/football';
	import StateBanner from '$lib/components/StateBanner.svelte';
	import type { Notification } from '$lib/types/football';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	let notifications = $state<Notification[]>([]);
	let unreadCount = $state(0);
	let errorBanner = $state<string | null>(null);
	let loadError = $state<string | null>(null);
	let isRetrying = $state(false);
	let isMarkingAll = $state(false);
	let markingIds = $state<Record<string, boolean>>({});
	let statusAnnouncement = $state('');

	let markAllLabel = $derived(isMarkingAll ? 'Marking all read…' : `Mark all read (${unreadCount})`);
	let isSignedIn = $derived(Boolean(data.user && data.session?.access_token && data.currentUserId));
	let signInHref = $derived(`/login?next=${encodeURIComponent(page.url.pathname + page.url.search)}`);

	$effect(() => {
		if (!isSignedIn) {
			notifications = [];
			unreadCount = 0;
			loadError = null;
			return;
		}
		notifications = data.notifications ? data.notifications.map((n) => ({ ...n })) : [];
		unreadCount = data.unreadCount ?? 0;
		loadError = data.notificationsError ?? null;
	});

	$effect(() => {
		const userId = data.currentUserId;
		const token = data.session?.access_token ?? null;
		const supabase = data.supabase;
		if (!isSignedIn || !userId || !token || !supabase) return;

		let cancelled = false;
		const channel = supabase
			.channel(`notifications-page:${userId}`)
			.on(
				'postgres_changes',
				{
					event: 'INSERT',
					schema: 'public',
					table: 'notifications',
					filter: `user_id=eq.${userId}`
				},
				(payload) => {
					void Promise.all([
						fetchNotificationsResult(userId, token),
						fetchUnreadNotificationsCount(userId, token)
					]).then(([result, count]) => {
						if (cancelled) return;
						if (result.error) {
							loadError = result.error;
							return;
						}
						loadError = null;
						notifications = result.data;
						unreadCount = count;
						const newTitle = (payload.new as { title?: string } | undefined)?.title;
						statusAnnouncement = newTitle
							? `New notification: ${newTitle}`
							: 'New notification received.';
					});
				}
			)
			.subscribe();

		return () => {
			cancelled = true;
			supabase.removeChannel(channel);
		};
	});

	async function retryLoadNotifications() {
		if (!isSignedIn || !data.currentUserId || isRetrying) return;
		isRetrying = true;
		loadError = null;
		try {
			const [result, count] = await Promise.all([
				fetchNotificationsResult(data.currentUserId, data.session?.access_token),
				fetchUnreadNotificationsCount(data.currentUserId, data.session?.access_token)
			]);
			if (result.error) {
				loadError = result.error;
				return;
			}
			notifications = result.data;
			unreadCount = count;
			statusAnnouncement = `Loaded ${result.data.length} notifications.`;
		} finally {
			isRetrying = false;
		}
	}

	async function handleMarkRead(notif: Notification): Promise<boolean> {
		if (!isSignedIn || notif.is_read || markingIds[notif.id] || isMarkingAll) return true;
		errorBanner = null;
		markingIds = { ...markingIds, [notif.id]: true };
		const prevUnread = unreadCount;
		notif.is_read = true;
		const nextUnread = Math.max(0, unreadCount - 1);
		unreadCount = nextUnread;
		window.dispatchEvent(
			new CustomEvent('gunners:notifications-updated', { detail: { unreadCount: nextUnread } })
		);
		try {
			await markNotificationRead(notif.id, data.session?.access_token);
			statusAnnouncement = `Marked "${notif.title}" as read.`;
			return true;
		} catch (err) {
			notif.is_read = false;
			unreadCount = prevUnread;
			window.dispatchEvent(
				new CustomEvent('gunners:notifications-updated', { detail: { unreadCount: prevUnread } })
			);
			errorBanner =
				err instanceof ApiError
					? err.detail
					: 'Could not mark notification as read. Please try again.';
			return false;
		} finally {
			const nextMap = { ...markingIds };
			delete nextMap[notif.id];
			markingIds = nextMap;
		}
	}

	async function handleNotificationClick(e: MouseEvent, notif: Notification) {
		if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || e.button !== 0) return;
		if (!notif.is_read) {
			e.preventDefault();
			const ok = await handleMarkRead(notif);
			if (!ok) return;
			if (notif.link.startsWith('/')) {
				await goto(notif.link);
			} else {
				window.location.assign(notif.link);
			}
		}
	}

	async function handleMarkAllRead() {
		if (!isSignedIn || !data.currentUserId || isMarkingAll) return;
		errorBanner = null;
		isMarkingAll = true;
		const prevUnread = unreadCount;
		const prevStates = notifications.map((n) => n.is_read);
		for (const n of notifications) {
			n.is_read = true;
		}
		unreadCount = 0;
		window.dispatchEvent(
			new CustomEvent('gunners:notifications-updated', { detail: { unreadCount: 0 } })
		);
		try {
			await markAllNotificationsRead(data.currentUserId, data.session?.access_token);
			statusAnnouncement = 'All notifications marked as read.';
		} catch (err) {
			notifications.forEach((n, idx) => {
				n.is_read = prevStates[idx];
			});
			unreadCount = prevUnread;
			window.dispatchEvent(
				new CustomEvent('gunners:notifications-updated', { detail: { unreadCount: prevUnread } })
			);
			errorBanner =
				err instanceof ApiError
					? err.detail
					: 'Could not mark all notifications as read. Please try again.';
		} finally {
			isMarkingAll = false;
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
	<p aria-live="polite" class="visually-hidden">{statusAnnouncement}</p>

	<!-- Page Header -->
	<div class="border-b-2 border-rule-2 pb-6 flex flex-wrap items-end justify-between gap-4">
		<div class="space-y-2">
			<h1>Notifications</h1>
			<p class="text-sm text-ink-2">Alerts from Terrace discussions, direct debates, and matchday predictions.</p>
		</div>

		{#if isSignedIn && unreadCount > 0}
			<button
				type="button"
				onclick={handleMarkAllRead}
				disabled={isMarkingAll}
				class="min-h-[44px] px-3.5 rounded-card bg-paper-2 hover:bg-paper-3 border border-rule text-xs font-semibold text-ink transition-colors disabled:opacity-60 whitespace-nowrap"
			>
				{markAllLabel}
			</button>
		{/if}
	</div>

	{#if errorBanner}
		<div role="alert" class="p-3.5 rounded-card bg-paper-2 border border-rule text-error text-xs flex items-center justify-between gap-4">
			<span>{errorBanner}</span>
			<button type="button" onclick={() => (errorBanner = null)} class="min-h-[44px] px-2 text-muted hover:text-ink font-semibold shrink-0">Dismiss</button>
		</div>
	{/if}

	<!-- Notifications List -->
	{#if !isSignedIn}
		<div class="py-8 px-6 border-t-2 border-rule-2 border-b border-rule bg-paper-2 space-y-4">
			<div class="space-y-1">
				<p class="text-sm font-bold text-ink">Sign in to view notifications</p>
				<p class="text-xs text-muted">Track cheers on your tactical insights, Terrace replies, and matchday predictor alerts.</p>
			</div>
			<a
				href={signInHref}
				class="inline-flex items-center min-h-[44px] px-4 rounded-card bg-accent hover:opacity-95 text-accent-ink text-xs font-semibold transition-opacity"
			>
				Sign in
			</a>
		</div>
	{:else if loadError && notifications.length === 0}
		<StateBanner
			variant="error"
			title="Notifications service unavailable"
			message={loadError}
			onretry={retryLoadNotifications}
			busy={isRetrying}
		/>
	{:else if notifications.length === 0}
		<div class="py-12 border-t border-rule text-muted text-sm space-y-1">
			<p class="font-semibold text-ink-2">No notifications yet.</p>
			<p>You will receive alerts when supporters cheer your insights or reply to your debates.</p>
		</div>
	{:else}
		{#if loadError}
			<StateBanner
				variant="warning"
				title="Live refresh issue"
				message={loadError}
				onretry={retryLoadNotifications}
				busy={isRetrying}
			/>
		{/if}

		<ul aria-label="Activity notifications" class="divide-y divide-rule border-y border-rule">
			{#each notifications as notif (notif.id)}
				{@const markBtnLabel = markingIds[notif.id] ? 'Saving…' : 'Mark read'}
				<li
					class="flex items-start justify-between gap-4 py-4 px-3 transition-colors {notif.is_read ? 'hover:bg-paper-2 opacity-85' : 'bg-paper-2 border-l-2 border-l-accent-2'}"
				>
					<a
						href={notif.link}
						onclick={(e) => handleNotificationClick(e, notif)}
						class="flex-1 min-w-0 space-y-1"
					>
						<div class="flex items-center gap-2.5 text-xs flex-wrap">
							<span class="font-semibold text-accent-2">{getNotificationLabel(notif.type)}</span>
							{#if !notif.is_read}
								<span class="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-card bg-paper-3 border border-rule text-xs font-bold text-ink">
									<svg class="w-3 h-3 text-accent-2 shrink-0" viewBox="0 0 16 16" fill="currentColor" aria-hidden="true">
										<circle cx="8" cy="8" r="4" />
									</svg>
									Unread
								</span>
							{:else}
								<span class="inline-flex items-center gap-1 text-xs text-muted">
									<svg class="w-3 h-3 shrink-0" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.75" aria-hidden="true">
										<path d="M3.5 8.5l3 3 6-6" />
									</svg>
									Read
								</span>
							{/if}
							<h2 class="text-sm font-bold text-ink truncate">
								{notif.title}
							</h2>
						</div>
						<p class="text-xs text-ink-2 leading-relaxed">
							{notif.message}
						</p>
					</a>
					<div class="flex flex-col items-end gap-2 shrink-0">
						<span class="text-xs text-muted num font-outlier">
							{formatTimestamp(notif.created_at)}
						</span>
						{#if !notif.is_read}
							<button
								type="button"
								onclick={() => handleMarkRead(notif)}
								disabled={Boolean(markingIds[notif.id]) || isMarkingAll}
								aria-label="Mark notification '{notif.title}' as read"
								class="min-h-[44px] px-3 rounded-card border border-rule bg-paper hover:bg-paper-3 text-ink-2 hover:text-ink text-xs font-semibold transition-colors disabled:opacity-60 whitespace-nowrap"
							>
								{markBtnLabel}
							</button>
						{/if}
					</div>
				</li>
			{/each}
		</ul>

		{#if notifications.length >= 20}
			<p class="text-xs text-muted">Showing your 20 most recent notifications.</p>
		{/if}
	{/if}
</div>
