<script lang="ts">
	import { page } from '$app/state';

	const status = $derived(page.status || 500);
	const message = $derived(
		page.error?.message ||
			(status === 404
				? 'The page or dispatch you requested could not be found.'
				: 'An unexpected error occurred while loading this page.')
	);
</script>

<svelte:head>
	<title>{status} | GUNNERS</title>
</svelte:head>

<div class="container py-20 max-w-2xl">
	<section class="border-t-2 border-rule-2 pt-8 space-y-6">
		<div class="space-y-2">
			<span class="num font-outlier text-sm font-semibold text-accent">Error {status}</span>
			<h1>
				{status === 404 ? 'Page not found' : 'Request error'}
			</h1>
			<p class="lead text-ink-2">
				{message}
			</p>
		</div>

		<div class="pt-4 border-t border-rule flex flex-wrap items-center gap-3">
			<a
				href="/"
				class="inline-flex items-center h-10 px-5 rounded-card bg-accent hover:opacity-95 text-accent-ink font-semibold text-sm transition-opacity"
			>
				Return home
			</a>
			<a
				href="/matches"
				class="inline-flex items-center h-10 px-4 rounded-card border border-rule bg-paper-2 hover:bg-paper-3 text-ink font-semibold text-sm transition-colors"
			>
				Match ledger
			</a>
			<a
				href="/news"
				class="inline-flex items-center h-10 px-4 rounded-card border border-rule bg-paper-2 hover:bg-paper-3 text-ink font-semibold text-sm transition-colors"
			>
				The Armory news
			</a>
		</div>
	</section>
</div>
