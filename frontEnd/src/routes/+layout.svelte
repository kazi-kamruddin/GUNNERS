<script lang="ts">
	import '../app.css';
	import favicon from '#lib/assets/favicon.svg';
	import { onMount } from 'svelte';
	import { invalidate } from '$app/navigation';
	import { CLUBS, themeState } from '$lib/stores/theme.svelte';
	import { fetchUnreadNotificationsCount } from '$lib/api/football';
	import type { LayoutProps } from './$types';

	let { data, children }: LayoutProps = $props();

	const clubList = Object.values(CLUBS);
	let currentViewingClub = $derived(themeState.currentTheme);
	let unreadCount = $state(0);

	onMount(() => {
		// Initialize theme with profile favorite club if available
		if (data.profile?.favorite_club_id) {
			themeState.setFavoriteClub(data.profile.favorite_club_id);
		} else {
			themeState.applyCssTokens();
		}

		if (data.user?.id) {
			fetchUnreadNotificationsCount(data.user.id).then((count) => {
				unreadCount = count;
			});
		}

		const { data: authListener } = data.supabase.auth.onAuthStateChange((event, newSession) => {
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
	<title>GUNNERS Reborn | Football Analytics & Community</title>
</svelte:head>

<div class="min-h-screen flex flex-col bg-[#0a0c10] text-[#f3f4f6]">
	<header class="border-b border-[#1e2430] bg-[#12161f]/90 backdrop-blur px-6 py-3.5 sticky top-0 z-50">
		<div class="max-w-7xl mx-auto flex items-center justify-between gap-4">
			<div class="flex items-center gap-6">
				<a href="/" class="flex items-center gap-2 group">
					<span class="text-xl font-black tracking-wider uppercase bg-gradient-to-r from-red-500 to-amber-500 bg-clip-text text-transparent group-hover:opacity-90 transition">
						GUNNERS
					</span>
					<span class="text-xs px-2 py-0.5 rounded bg-red-950/70 text-red-400 font-mono border border-red-800/40">
						REBORN
					</span>
				</a>
				<nav class="hidden md:flex items-center gap-4 text-xs font-medium text-gray-400">
					<a href="/" class="hover:text-white transition">Home</a>
					<a href="/lab" class="hover:text-white transition flex items-center gap-1">
						<span>Data Lab</span>
						<span class="text-[9px] bg-amber-500/10 text-amber-400 border border-amber-500/20 px-1 rounded">Analytics</span>
					</a>
					<a href="/board" class="hover:text-white transition">Tactics</a>
					<a href="/squad" class="hover:text-white transition">Squad</a>
					<a href="/predictions" class="hover:text-white transition">Predictions</a>
					<a href="/matches" class="hover:text-white transition">Matches</a>
					<a href="/terrace" class="hover:text-white transition">The Terrace</a>
					<a href="/messages" class="hover:text-white transition">Messages</a>
				</nav>
			</div>

			<div class="flex items-center gap-3">
				<!-- Quick Viewing Club Switcher -->
				<div class="hidden sm:flex items-center gap-1 bg-[#0a0c10] border border-[#1e2430] rounded-lg p-1 text-xs">
					<span class="text-gray-500 text-[10px] uppercase font-semibold px-1.5">Viewing:</span>
					{#each clubList as club}
						<button
							type="button"
							onclick={() => themeState.setViewingClub(club.id)}
							title="View as {club.name}"
							class="px-2 py-0.5 rounded transition text-xs font-semibold flex items-center gap-1 {themeState.viewingClubId === club.id ? 'bg-white/10 text-white' : 'text-gray-400 hover:text-white'}"
						>
							<span class="w-1.5 h-1.5 rounded-full" style="background-color: {club.primary_color}"></span>
							<span>{club.short_name}</span>
						</button>
					{/each}
				</div>

				{#if data.user}
					<div class="flex items-center gap-2">
						<a
							href="/notifications"
							class="relative p-1.5 rounded-lg border border-[#1e2430] bg-[#0a0c10] hover:border-gray-600 text-gray-300 hover:text-white transition"
							title="Activity Notifications"
						>
							<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
							</svg>
							{#if unreadCount > 0}
								<span class="absolute -top-1 -right-1 px-1.5 py-0.2 rounded-full bg-red-600 text-white font-mono text-[9px] font-bold">
									{unreadCount > 9 ? '9+' : unreadCount}
								</span>
							{/if}
						</a>
						<a
							href="/profile"
							class="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-[#1e2430] bg-[#0a0c10] hover:border-gray-600 text-xs text-white transition"
						>
							<span class="w-2 h-2 rounded-full" style="background-color: {currentViewingClub.primary_color}"></span>
							<span class="font-bold">{data.profile?.display_name || data.user.email?.split('@')[0]}</span>
						</a>
						<form method="POST" action="/auth/signout">
							<button
								type="submit"
								class="text-xs px-2.5 py-1.5 rounded text-gray-400 hover:text-white transition"
							>
								Sign Out
							</button>
						</form>
					</div>
				{:else}
					<div class="flex items-center gap-2">
						<a href="/login" class="text-xs px-3 py-1.5 rounded text-gray-300 hover:text-white hover:bg-white/5 transition">
							Sign In
						</a>
						<a href="/signup" class="text-xs px-3.5 py-1.5 rounded bg-red-600 hover:bg-red-500 font-semibold text-white transition shadow-sm">
							Join Club
						</a>
					</div>
				{/if}
			</div>
		</div>
	</header>

	<main class="flex-1">
		{@render children()}
	</main>

	<footer class="border-t border-[#1e2430] bg-[#0d1017] py-8 text-center text-xs text-gray-500">
		<div class="max-w-7xl mx-auto px-4 flex flex-col md:flex-row items-center justify-between gap-4">
			<p>© 2026 GUNNERS Reborn / Touchline. Personalized football analytics & fan-community platform.</p>
			<p class="text-gray-600">Built with SvelteKit 5, FastAPI, and Supabase. $0 Free-Tier Architecture.</p>
		</div>
	</footer>
</div>
