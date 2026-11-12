<script lang="ts">
	import '../app.css';
	import favicon from '$lib/assets/favicon.svg';
	import { onMount } from 'svelte';
	import { invalidate } from '$app/navigation';
	import { themeState } from '$lib/stores/theme.svelte';
	import {
		fetchNotifications,
		fetchUnreadNotificationsCount,
		setApiAccessToken
	} from '$lib/api/football';
	import type { LayoutProps } from './$types';

	let { data, children }: LayoutProps = $props();

	let unreadCount = $state(0);

	$effect(() => {
		const token = data.session?.access_token ?? null;
		setApiAccessToken(token);
		if (!data.user || !token) {
			unreadCount = 0;
		}
	});

	$effect(() => {
		const userId = data.user?.id;
		const supabase = data.supabase;
		const token = data.session?.access_token ?? null;
		if (!userId || !supabase) return;

		let cancelled = false;

		const refreshFromApi = async () => {
			if (!token) return;
			const items = await fetchNotifications(userId, token);
			if (!cancelled) {
				unreadCount = items.filter((item) => !item.is_read).length;
			}
		};

		if (token) {
			fetchUnreadNotificationsCount(userId, token).then((count) => {
				if (!cancelled) {
					unreadCount = count;
				}
			});
		}

		const channel = supabase
			.channel(`notifications:${userId}`)
			.on(
				'postgres_changes',
				{
					event: '*',
					schema: 'public',
					table: 'notifications',
					filter: `user_id=eq.${userId}`
				},
				() => {
					void refreshFromApi();
				}
			)
			.subscribe();

		const handleNotificationsUpdated = (event: Event) => {
			const customEvent = event as CustomEvent<{ unreadCount?: unknown }>;
			const nextCount = customEvent.detail?.unreadCount;
			if (typeof nextCount === 'number' && Number.isFinite(nextCount)) {
				unreadCount = Math.max(0, nextCount);
			} else {
				void refreshFromApi();
			}
		};

		window.addEventListener('gunners:notifications-updated', handleNotificationsUpdated);

		return () => {
			cancelled = true;
			supabase.removeChannel(channel);
			window.removeEventListener('gunners:notifications-updated', handleNotificationsUpdated);
		};
	});

	onMount(() => {
		themeState.applyCssTokens();

		const { data: authListener } = data.supabase.auth.onAuthStateChange((_event, newSession) => {
			setApiAccessToken(newSession?.access_token ?? null);
			if (newSession?.expires_at !== data.session?.expires_at) {
				invalidate('supabase:auth');
			}
		});

		return () => {
			authListener.subscription.unsubscribe();
		};
	});
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
	<title>GUNNERS | Arsenal FC Tactical Intelligence & Supporter Ledger</title>
</svelte:head>

<div class="min-h-dvh flex flex-col bg-paper text-ink">
	<header class="border-b border-rule bg-paper sticky top-0 z-50">
		<div class="container flex items-center justify-between gap-6 h-16">
			<div class="flex items-center gap-8 min-w-0">
				<a href="/" aria-label="GUNNERS Home" class="flex items-baseline gap-2.5 text-ink hover:text-accent transition-colors shrink-0">
					<span class="font-display font-bold text-xl">Gunners</span>
					<span class="text-xs text-muted">North London</span>
				</a>
				<nav aria-label="Primary navigation" class="hidden md:flex items-center gap-6 text-sm text-muted overflow-x-auto">
					<a href="/" class="hover:text-ink transition-colors whitespace-nowrap">Home</a>
					<a href="/news" class="hover:text-ink transition-colors whitespace-nowrap">The Armory</a>
					<a href="/board" class="hover:text-ink transition-colors whitespace-nowrap">The Dugout</a>
					<a href="/squad" class="hover:text-ink transition-colors whitespace-nowrap">Squad</a>
					<a href="/terrace" class="hover:text-ink transition-colors whitespace-nowrap">The Terrace</a>
					<a href="/lab" class="hover:text-ink transition-colors whitespace-nowrap">Data Lab</a>
					<a href="/matches" class="hover:text-ink transition-colors whitespace-nowrap">Matches</a>
					<a href="/messages" class="hover:text-ink transition-colors whitespace-nowrap">Debates</a>
				</nav>
			</div>

			<div class="flex items-center gap-3 shrink-0">
				{#if data.user}
					<div class="flex items-center gap-3">
						<a
							href="/notifications"
							aria-label="Activity notifications"
							class="relative inline-flex items-center justify-center w-9 h-9 rounded-card border border-rule bg-paper-2 hover:bg-paper-3 text-ink-2 hover:text-ink transition-colors"
							title="Activity notifications"
						>
							<svg class="w-4 h-4 shrink-0" aria-hidden="true" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
							</svg>
							{#if unreadCount > 0}
								<span role="status" class="num absolute -top-1.5 -right-1.5 px-1.5 py-0.5 rounded-pill bg-accent text-accent-ink text-xs font-semibold leading-none">
									{unreadCount > 9 ? '9+' : unreadCount}
								</span>
							{/if}
						</a>
						<a
							href="/profile"
							class="inline-flex items-center h-9 px-3 rounded-card border border-rule bg-paper-2 hover:bg-paper-3 text-sm font-semibold text-ink transition-colors whitespace-nowrap"
						>
							{data.profile?.display_name || data.user.email?.split('@')[0]}
						</a>
						<form method="POST" action="/auth/signout">
							<button
								type="submit"
								class="inline-flex items-center h-9 px-3 rounded-card text-sm text-muted hover:text-ink transition-colors whitespace-nowrap"
							>
								Sign out
							</button>
						</form>
					</div>
				{:else}
					<div class="flex items-center gap-3">
						<a href="/login" class="inline-flex items-center h-9 px-3 rounded-card text-sm text-ink-2 hover:text-ink transition-colors whitespace-nowrap">
							Sign in
						</a>
						<a href="/signup" class="inline-flex items-center h-9 px-4 rounded-card bg-accent text-accent-ink hover:opacity-90 text-sm font-semibold transition-opacity whitespace-nowrap">
							Join club
						</a>
					</div>
				{/if}
			</div>
		</div>
	</header>

	<main class="flex-1">
		{@render children()}
	</main>

	<footer class="border-t border-rule bg-paper py-10 text-sm text-muted">
		<div class="container flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
			<div class="flex flex-wrap items-baseline gap-4">
				<span class="font-display font-bold text-ink">Gunners</span>
				<span>Arsenal FC Tactical Intelligence and Supporter Ledger.</span>
			</div>
			<p class="text-muted">Victoria Concordia Crescit. Built with SvelteKit, FastAPI, and Supabase.</p>
		</div>
	</footer>
</div>
