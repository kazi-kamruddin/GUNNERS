<script lang="ts">
	interface Props {
		variant?: 'error' | 'warning' | 'info' | 'empty';
		title: string;
		message: string;
		retryLabel?: string;
		onretry?: () => void;
		busy?: boolean;
		actionHref?: string;
		actionLabel?: string;
		class?: string;
	}

	let {
		variant = 'info',
		title,
		message,
		retryLabel = 'Retry',
		onretry,
		busy = false,
		actionHref,
		actionLabel,
		class: className = ''
	}: Props = $props();

	const topRuleClass = $derived(
		variant === 'error'
			? 'border-t-error'
			: variant === 'warning'
				? 'border-t-accent-2'
				: variant === 'info'
					? 'border-t-rule-2'
					: 'border-t-rule'
	);

	const labelClass = $derived(
		variant === 'error'
			? 'text-error'
			: variant === 'warning'
				? 'text-accent-2'
				: 'text-ink-2'
	);

	const badgeText = $derived(
		variant === 'error'
			? 'Service notice'
			: variant === 'warning'
				? 'Offline preview'
				: variant === 'empty'
					? 'No records'
					: 'Ledger notice'
	);

	const buttonLabel = $derived(busy ? 'Retrying…' : retryLabel);
</script>

<section
	role={variant === 'error' ? 'alert' : 'status'}
	aria-live={variant === 'error' ? 'assertive' : 'polite'}
	class={`border-y border-rule border-t-2 ${topRuleClass} bg-paper-2 p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 ${className}`}
>
	<div class="space-y-1.5 min-w-0">
		<div class="flex flex-wrap items-center gap-2">
			<span class={`font-outlier text-xs font-semibold ${labelClass}`}>{badgeText}</span>
			<span class="text-rule-2" aria-hidden="true">/</span>
			<h2 class="font-display font-bold text-lg text-ink card-headline">{title}</h2>
		</div>
		<p class="text-sm text-ink-2 max-w-2xl">{message}</p>
	</div>

	{#if onretry || (actionHref && actionLabel)}
		<div class="flex flex-wrap items-center gap-2.5 shrink-0">
			{#if onretry}
				<button
					type="button"
					onclick={onretry}
					disabled={busy}
					class="inline-flex items-center justify-center min-h-[44px] px-4 rounded-card border border-rule bg-paper-3 hover:bg-paper text-ink text-sm font-semibold transition-colors whitespace-nowrap"
				>
					{buttonLabel}
				</button>
			{/if}
			{#if actionHref && actionLabel}
				<a
					href={actionHref}
					class="inline-flex items-center justify-center min-h-[44px] px-4 rounded-card bg-accent text-accent-ink hover:opacity-90 text-sm font-semibold transition-opacity whitespace-nowrap"
				>
					{actionLabel}
				</a>
			{/if}
		</div>
	{/if}
</section>
