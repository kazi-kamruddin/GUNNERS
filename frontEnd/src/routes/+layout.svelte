<script lang="ts">
	import '../app.css';
	import favicon from '$lib/assets/favicon.svg';
	import { onMount } from 'svelte';
	import { afterNavigate, invalidate } from '$app/navigation';
	import { navigating, page } from '$app/state';
	import { focusTrap } from '$lib/actions/focusTrap';
	import { themeState } from '$lib/stores/theme.svelte';
	import {
		fetchNotifications,
		fetchUnreadNotificationsCount,
		setApiAccessToken
	} from '$lib/api/football';
	import type { LayoutProps } from './$types';

	let { data, children }: LayoutProps = $props();

	const NAV_LINKS = [
		{ href: '/', label: 'Home' },
		{ href: '/news', label: 'The Armory' },
		{ href: '/board', label: 'The Dugout' },
		{ href: '/squad', label: 'Squad' },
		{ href: '/terrace', label: 'The Terrace' },
		{ href: '/lab', label: 'Data Lab' },
		{ href: '/matches', label: 'Matches' },
		{ href: '/predictions', label: 'Predictor' },
		{ href: '/messages', label: 'Debates' }
	] as const;

	let unreadCount = $state(0);
	let mobileMenuOpen = $state(false);
	let shouldRestoreMenuFocus = $state(true);
	let slowNavigation = $state(false);

	const pathname = $derived(page.url.pathname);
	const displayName = $derived(
		data.profile?.display_name || data.user?.email?.split('@')[0] || 'Supporter'
	);
	const bellAriaLabel = $derived(
		unreadCount > 0
			? `Activity notifications (${unreadCount} unread)`
			: 'Activity notifications'
	);

	function isNavActive(href: string): boolean {
		if (href === '/') return pathname === '/';
		return pathname === href || pathname.startsWith(`${href}/`);
	}

	function navLinkClass(href: string): string {
		return isNavActive(href)
			? 'inline-flex items-center min-h-[44px] whitespace-nowrap transition-colors text-ink font-semibold underline decoration-accent-text decoration-2 underline-offset-8'
			: 'inline-flex items-center min-h-[44px] whitespace-nowrap transition-colors text-muted hover:text-ink';
	}

	function toggleMobileMenu() {
		shouldRestoreMenuFocus = true;
		mobileMenuOpen = !mobileMenuOpen;
	}

	function closeMobileMenuByEscape() {
		shouldRestoreMenuFocus = true;
		mobileMenuOpen = false;
	}

	function closeMobileMenuOnLink() {
		shouldRestoreMenuFocus = false;
		mobileMenuOpen = false;
	}

	afterNavigate(() => {
		shouldRestoreMenuFocus = false;
		mobileMenuOpen = false;
	});

	$effect(() => {
		if (!navigating.to) {
			slowNavigation = false;
			return;
		}
		const timer = setTimeout(() => {
			slowNavigation = true;
		}, 2500);
		return () => clearTimeout(timer);
	});

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

<a href="#main-content" class="skip-link">Skip to main content</a>

{#if navigating.to}
	<div
		class="fixed top-0 inset-x-0 h-[2px] bg-accent z-[var(--z-tooltip)] pointer-events-none"
		aria-hidden="true"
	></div>
{/if}

<div class="min-h-dvh flex flex-col bg-paper text-ink">
	<header class="border-b border-rule bg-paper sticky top-0 z-[var(--z-sticky-nav)]">
		<div class="container flex items-center justify-between gap-2 sm:gap-4 h-16">
			<div class="flex items-center gap-2 sm:gap-6 min-w-0">
				<button
					type="button"
					onclick={toggleMobileMenu}
					aria-expanded={mobileMenuOpen}
					aria-controls="mobile-primary-nav"
					aria-label={mobileMenuOpen ? 'Close navigation menu' : 'Open navigation menu'}
					class="lg:hidden inline-flex items-center justify-center min-w-[44px] min-h-[44px] rounded-card border border-rule bg-paper-2 hover:bg-paper-3 text-ink transition-colors shrink-0"
				>
					<svg class="w-5 h-5" aria-hidden="true" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d={mobileMenuOpen ? 'M6 18L18 6M6 6l12 12' : 'M4 6h16M4 12h16M4 18h16'}
						/>
					</svg>
				</button>

				<a
					href="/"
					aria-label="GUNNERS Home"
					class="inline-flex items-center gap-2.5 min-h-[44px] py-2 text-ink hover:text-accent-text transition-colors shrink-0"
				>
					<img src={favicon} alt="" class="w-6 h-6 rounded-[4px] shrink-0" aria-hidden="true" />
					<span class="font-display font-bold text-lg sm:text-xl">Gunners</span>
				</a>

				<nav aria-label="Primary navigation" class="hidden lg:flex items-center gap-4 xl:gap-5 text-sm">
					<a href="/" aria-current={isNavActive('/') ? 'page' : undefined} class={navLinkClass('/')}>Home</a>
					<a href="/news" aria-current={isNavActive('/news') ? 'page' : undefined} class={navLinkClass('/news')}>The Armory</a>
					<a href="/board" aria-current={isNavActive('/board') ? 'page' : undefined} class={navLinkClass('/board')}>The Dugout</a>
					<a href="/squad" aria-current={isNavActive('/squad') ? 'page' : undefined} class={navLinkClass('/squad')}>Squad</a>
					<a href="/terrace" aria-current={isNavActive('/terrace') ? 'page' : undefined} class={navLinkClass('/terrace')}>The Terrace</a>
					<a href="/lab" aria-current={isNavActive('/lab') ? 'page' : undefined} class={navLinkClass('/lab')}>Data Lab</a>
					<a href="/matches" aria-current={isNavActive('/matches') ? 'page' : undefined} class={navLinkClass('/matches')}>Matches</a>
					<a href="/predictions" aria-current={isNavActive('/predictions') ? 'page' : undefined} class={navLinkClass('/predictions')}>Predictor</a>
					<a href="/messages" aria-current={isNavActive('/messages') ? 'page' : undefined} class={navLinkClass('/messages')}>Debates</a>
				</nav>
			</div>

			<div class="flex items-center gap-1.5 sm:gap-2.5 shrink-0">
				{#if data.user}
					<div class="flex items-center gap-1.5 sm:gap-2.5">
						<a
							href="/notifications"
							aria-label={bellAriaLabel}
							class="relative inline-flex items-center justify-center min-w-[44px] min-h-[44px] rounded-card border border-rule bg-paper-2 hover:bg-paper-3 text-ink-2 hover:text-ink transition-colors shrink-0"
							title={bellAriaLabel}
						>
							<svg class="w-4 h-4 shrink-0" aria-hidden="true" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
							</svg>
							{#if unreadCount > 0}
								<span role="status" class="num absolute -top-1 -right-1 px-1.5 py-0.5 rounded-pill bg-accent text-accent-ink text-xs font-semibold leading-none">
									{unreadCount > 9 ? '9+' : unreadCount}
								</span>
							{/if}
						</a>
						<a
							href="/profile"
							aria-label={`Supporter profile (${displayName})`}
							class="inline-flex items-center justify-center min-w-[44px] min-h-[44px] px-2.5 sm:px-3 rounded-card border border-rule bg-paper-2 hover:bg-paper-3 text-sm font-semibold text-ink transition-colors max-w-[44px] min-[400px]:max-w-[7.5rem] sm:max-w-[10rem]"
						>
							<svg class="w-4 h-4 min-[400px]:hidden shrink-0" aria-hidden="true" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
							</svg>
							<span class="hidden min-[400px]:inline truncate">{displayName}</span>
						</a>
						<form method="POST" action="/auth/signout">
							<button
								type="submit"
								class="inline-flex items-center justify-center min-h-[44px] px-2 sm:px-3 rounded-card text-xs sm:text-sm text-muted hover:text-ink transition-colors whitespace-nowrap"
							>
								Sign out
							</button>
						</form>
					</div>
				{:else}
					<div class="flex items-center gap-1.5 sm:gap-2.5">
						<a
							href="/login"
							class="inline-flex items-center justify-center min-h-[44px] px-2.5 sm:px-3 rounded-card text-xs sm:text-sm text-ink-2 hover:text-ink transition-colors whitespace-nowrap"
						>
							Sign in
						</a>
						<a
							href="/signup"
							class="inline-flex items-center justify-center min-h-[44px] px-3 sm:px-4 rounded-card bg-accent text-accent-ink hover:opacity-90 text-xs sm:text-sm font-semibold transition-opacity whitespace-nowrap"
						>
							Join club
						</a>
					</div>
				{/if}
			</div>
		</div>

		{#if mobileMenuOpen}
			<div
				id="mobile-primary-nav"
				class="lg:hidden border-t border-rule bg-paper"
				use:focusTrap={{
					active: mobileMenuOpen,
					onEscape: closeMobileMenuByEscape,
					restoreFocus: shouldRestoreMenuFocus
				}}
			>
				<nav aria-label="Mobile primary navigation" class="container py-3 flex flex-col gap-1">
					{#each NAV_LINKS as item (item.href)}
						{@const active = isNavActive(item.href)}
						<a
							href={item.href}
							onclick={closeMobileMenuOnLink}
							aria-current={active ? 'page' : undefined}
							class={`flex items-center justify-between min-h-[44px] px-3 rounded-card text-sm transition-colors ${
								active
									? 'bg-paper-2 border border-rule text-ink font-semibold'
									: 'text-ink-2 hover:bg-paper-2 hover:text-ink'
							}`}
						>
							<span>{item.label}</span>
							{#if active}
								<span class="font-outlier text-xs text-accent-text">Active</span>
							{/if}
						</a>
					{/each}
				</nav>
			</div>
		{/if}
	</header>

	{#if slowNavigation}
		<div role="status" aria-live="polite" class="border-b border-rule bg-paper-2 text-ink-2 text-xs">
			<div class="container py-2.5 flex items-center gap-2">
				<span class="w-2 h-2 rounded-pill bg-accent shrink-0" aria-hidden="true"></span>
				<span>Waking Arsenal data service: initial cold start can take up to 50s.</span>
			</div>
		</div>
	{/if}

	<main id="main-content" tabindex="-1" class="flex-1 outline-none">
		{@render children()}
	</main>

	<footer class="border-t border-rule bg-paper py-10 text-sm text-muted">
		<div class="container flex flex-col gap-6">
			<div class="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
				<div class="flex flex-wrap items-baseline gap-4">
					<span class="font-display font-bold text-ink">Gunners</span>
					<span>Arsenal FC Tactical Intelligence and Supporter Ledger.</span>
				</div>
				<nav aria-label="Footer navigation" class="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs sm:text-sm">
					<a href="/news" class="inline-flex items-center min-h-[44px] text-ink-2 hover:text-ink transition-colors">The Armory</a>
					<a href="/matches" class="inline-flex items-center min-h-[44px] text-ink-2 hover:text-ink transition-colors">Matches</a>
					<a href="/squad" class="inline-flex items-center min-h-[44px] text-ink-2 hover:text-ink transition-colors">Squad</a>
					<a href="/lab" class="inline-flex items-center min-h-[44px] text-ink-2 hover:text-ink transition-colors">Data Lab</a>
					<a href="/predictions" class="inline-flex items-center min-h-[44px] text-ink-2 hover:text-ink transition-colors">Predictor</a>
					<a href="/terrace" class="inline-flex items-center min-h-[44px] text-ink-2 hover:text-ink transition-colors">The Terrace</a>
				</nav>
			</div>
			<p class="text-muted text-xs sm:text-sm">North London Forever. Built with SvelteKit, FastAPI, and Supabase.</p>
		</div>
	</footer>
</div>
