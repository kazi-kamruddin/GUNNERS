<script lang="ts">
	import '../app.css';
	import favicon from '#lib/assets/favicon.svg';
	import type { LayoutProps } from './$types';

	let { children }: LayoutProps = $props();
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
	<title>GUNNERS Reborn | Football Analytics & Community</title>
</svelte:head>

<div class="min-h-screen flex flex-col bg-[#0a0c10] text-[#f3f4f6]">
	<header class="border-b border-[#1e2430] bg-[#12161f]/80 backdrop-blur px-6 py-4 sticky top-0 z-50">
		<div class="max-w-7xl mx-auto flex items-center justify-between">
			<div class="flex items-center gap-6">
				<a href="/" class="flex items-center gap-2 group">
					<span class="text-xl font-black tracking-wider uppercase bg-gradient-to-r from-red-500 to-amber-500 bg-clip-text text-transparent group-hover:opacity-90 transition">
						GUNNERS
					</span>
					<span class="text-xs px-2 py-0.5 rounded bg-red-950/70 text-red-400 font-mono border border-red-800/40">
						REBORN
					</span>
				</a>
				<nav class="hidden md:flex items-center gap-5 text-sm font-medium text-gray-400">
					<a href="/" class="hover:text-white transition">Home</a>
					<a href="/lab" class="hover:text-white transition flex items-center gap-1.5">
						<span>Data Lab</span>
						<span class="text-[10px] bg-amber-500/10 text-amber-400 border border-amber-500/20 px-1 rounded">Analytics</span>
					</a>
					<a href="/terrace" class="hover:text-white transition">The Terrace</a>
					<a href="/matches" class="hover:text-white transition">Matches</a>
				</nav>
			</div>

			<div class="flex items-center gap-3">
				<a href="/login" class="text-xs px-3 py-1.5 rounded text-gray-300 hover:text-white hover:bg-white/5 transition">
					Sign In
				</a>
				<a href="/signup" class="text-xs px-3.5 py-1.5 rounded bg-red-600 hover:bg-red-500 font-semibold text-white transition shadow-sm">
					Join Club
				</a>
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
