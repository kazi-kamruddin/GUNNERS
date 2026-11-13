<script lang="ts">
	import { invalidateAll } from '$app/navigation';
	import { page } from '$app/state';

	let retrying = $state(false);
	const retryLabel = $derived(retrying ? 'Retrying…' : 'Retry');

	const status = $derived(page.status || 500);
	const heading = $derived(
		status === 404
			? 'Page not found'
			: status === 503
				? 'Service temporarily unavailable'
				: 'Request error'
	);
	const message = $derived(
		page.error?.message ||
			(status === 404
				? 'The page or dispatch you requested could not be found.'
				: status === 503
					? 'The Arsenal data service is waking up or temporarily unavailable. Try again in a few moments.'
					: 'An unexpected error occurred while loading this page.')
	);

	async function handleRetry() {
		retrying = true;
		try {
			await invalidateAll();
		} finally {
			retrying = false;
		}
	}
</script>

<svelte:head>
	<title>{status} | GUNNERS</title>
</svelte:head>

<div class="container py-20 max-w-2xl">
	<section class="border-t-2 border-rule-2 pt-8 space-y-6">
		<div class="space-y-2">
			<span class="num font-outlier text-sm font-semibold text-accent-text">Error {status}</span>
			<h1>{heading}</h1>
			<p class="lead text-ink-2">
				{message}
			</p>
		</div>

		<div class="pt-4 border-t border-rule flex flex-wrap items-center gap-3">
			<button
				type="button"
				onclick={handleRetry}
				disabled={retrying}
				class="inline-flex items-center justify-center min-h-[44px] px-5 rounded-card bg-accent hover:opacity-95 text-accent-ink font-semibold text-sm transition-opacity"
			>
				{retryLabel}
			</button>
			<a
				href="/"
				class="inline-flex items-center justify-center min-h-[44px] px-4 rounded-card border border-rule bg-paper-2 hover:bg-paper-3 text-ink font-semibold text-sm transition-colors"
			>
				Return home
			</a>
			<a
				href="/matches"
				class="inline-flex items-center justify-center min-h-[44px] px-4 rounded-card border border-rule bg-paper-2 hover:bg-paper-3 text-ink font-semibold text-sm transition-colors"
			>
				Match ledger
			</a>
			<a
				href="/news"
				class="inline-flex items-center justify-center min-h-[44px] px-4 rounded-card border border-rule bg-paper-2 hover:bg-paper-3 text-ink font-semibold text-sm transition-colors"
			>
				The Armory news
			</a>
		</div>
	</section>
</div>
