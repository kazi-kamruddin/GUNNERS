<script lang="ts">
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	const player = $derived(data.player);
	const portraitSrc = $derived(player.portrait_url || player.photo_url || '');
	const actionSrc = $derived(player.action_url || '');

	let portraitFailed = $state(false);
	let actionFailed = $state(false);
	let activePhoto = $state<'portrait' | 'action'>('portrait');

	$effect(() => {
		if (player.id) {
			portraitFailed = false;
			actionFailed = false;
			activePhoto = 'portrait';
		}
	});

	const hasPortrait = $derived(Boolean(portraitSrc && !portraitFailed));
	const hasAction = $derived(Boolean(actionSrc && !actionFailed));
	const displayMode = $derived.by(() => {
		if (activePhoto === 'action' && hasAction) return 'action';
		if (hasPortrait) return 'portrait';
		if (hasAction) return 'action';
		return 'fallback';
	});

	const initials = $derived(
		player.name
			.split(/\s+/)
			.map((p) => p[0] || '')
			.join('')
			.slice(0, 2)
			.toUpperCase()
	);

	const computedAge = $derived.by(() => {
		if (!player.date_of_birth) return null;
		const dob = new Date(player.date_of_birth);
		if (Number.isNaN(dob.getTime())) return null;
		const today = new Date();
		let age = today.getFullYear() - dob.getFullYear();
		const m = today.getMonth() - dob.getMonth();
		if (m < 0 || (m === 0 && today.getDate() < dob.getDate())) {
			age -= 1;
		}
		return age > 0 && age < 60 ? age : null;
	});
</script>

<svelte:head>
	<title>#{player.jersey_number} {player.name} | Arsenal Squad | GUNNERS</title>
</svelte:head>

<div class="container py-12 space-y-12 max-w-5xl">
	<!-- Top Navigation -->
	<div class="flex items-center justify-between gap-4 flex-wrap">
		<a
			href="/squad"
			class="inline-flex items-center min-h-[44px] px-3.5 rounded-card border border-rule bg-paper-2 hover:bg-paper-3 text-xs font-semibold text-ink-2 hover:text-ink transition-colors"
		>
			Back to squad
		</a>

		<div class="flex items-center gap-2.5 flex-wrap">
			<a
				href="/squad?compare1={encodeURIComponent(player.id)}"
				class="inline-flex items-center min-h-[44px] px-3.5 rounded-card border border-rule bg-paper-2 hover:bg-paper-3 text-xs font-semibold text-accent-text hover:text-ink transition-colors"
			>
				Compare teammate
			</a>
			<a
				href="/board"
				class="inline-flex items-center min-h-[44px] px-3.5 rounded-card bg-accent text-accent-ink hover:opacity-90 text-xs font-semibold transition-opacity"
			>
				Add to Dugout lineup
			</a>
			<a
				href="/lab"
				class="inline-flex items-center min-h-[44px] px-3.5 rounded-card border border-rule bg-paper-2 hover:bg-paper-3 text-xs font-semibold text-ink transition-colors"
			>
				Open Data Lab
			</a>
		</div>
	</div>

	<!-- Hero Dossier -->
	<section class="border-t-2 border-rule-2 pt-8 grid grid-cols-1 lg:grid-cols-12 gap-10 items-start">
		<!-- Touch/Keyboard Accessible Portrait & Action Switcher -->
		<div class="lg:col-span-5 space-y-3">
			<div class="aspect-[4/5] rounded-card overflow-hidden bg-paper-2 border border-rule flex items-center justify-center">
				{#if displayMode === 'portrait'}
					<img
						src={portraitSrc}
						alt="{player.name} portrait"
						width="500"
						height="625"
						class="w-full h-full object-cover object-top"
						onerror={() => (portraitFailed = true)}
					/>
				{:else if displayMode === 'action'}
					<img
						src={actionSrc}
						alt="{player.name} in match action"
						width="500"
						height="625"
						class="w-full h-full object-cover object-top"
						onerror={() => (actionFailed = true)}
					/>
				{:else}
					<div class="flex flex-col items-center justify-center gap-2 p-6 text-center">
						<span class="num font-display font-bold text-5xl text-accent-text">#{player.jersey_number}</span>
						<span class="font-display font-bold text-xl text-ink">{initials}</span>
						<span class="text-xs text-muted">{player.position}</span>
					</div>
				{/if}
			</div>

			{#if hasPortrait && hasAction}
				<div class="grid grid-cols-2 gap-2" role="group" aria-label="Player photograph view">
					<button
						type="button"
						aria-pressed={displayMode === 'portrait'}
						onclick={() => (activePhoto = 'portrait')}
						class="min-h-[44px] px-3 rounded-card border text-xs font-semibold transition-colors {displayMode === 'portrait' ? 'bg-accent text-accent-ink border-accent' : 'bg-paper-2 text-ink-2 border-rule hover:text-ink'}"
					>
						Portrait
					</button>
					<button
						type="button"
						aria-pressed={displayMode === 'action'}
						onclick={() => (activePhoto = 'action')}
						class="min-h-[44px] px-3 rounded-card border text-xs font-semibold transition-colors {displayMode === 'action' ? 'bg-accent text-accent-ink border-accent' : 'bg-paper-2 text-ink-2 border-rule hover:text-ink'}"
					>
						Match action
					</button>
				</div>
			{/if}
		</div>

		<!-- Identity, Bio & Metadata -->
		<div class="lg:col-span-7 space-y-8 min-w-0">
			<div class="space-y-3 border-b border-rule pb-6">
				<div class="flex items-center gap-3 text-sm">
					<span class="num font-display font-bold text-2xl text-accent-text">#{player.jersey_number}</span>
					<span class="text-muted">{player.position}</span>
				</div>
				<h1 class="text-[length:var(--text-display-s)] leading-[1.08] break-words min-w-0 max-w-none">{player.name}</h1>
				<p class="text-sm text-ink-2">
					Arsenal Football Club, {player.nationality}
				</p>
			</div>

			{#if player.bio}
				<div class="space-y-2">
					<h2 class="text-base font-bold text-ink card-headline">Scouting dossier</h2>
					<p class="text-sm text-ink-2 leading-relaxed">
						{player.bio}
					</p>
				</div>
			{/if}

			<!-- Biographical Ledger -->
			<dl class="grid grid-cols-2 sm:grid-cols-4 gap-4 border-y border-rule py-5 text-xs">
				<div>
					<dt class="text-muted">Date of birth</dt>
					<dd class="text-ink font-semibold num font-outlier mt-1">
						{player.date_of_birth || 'Not listed'}
						{#if computedAge !== null}
							<span class="text-muted font-normal">({computedAge})</span>
						{/if}
					</dd>
				</div>
				<div>
					<dt class="text-muted">Nationality</dt>
					<dd class="text-ink font-semibold mt-1">{player.nationality}</dd>
				</div>
				<div>
					<dt class="text-muted">Height</dt>
					<dd class="text-ink font-semibold num font-outlier mt-1">{player.height || 'Not listed'}</dd>
				</div>
				<div>
					<dt class="text-muted">Joined Arsenal</dt>
					<dd class="text-ink font-semibold num font-outlier mt-1">{player.joined_date || 'Not listed'}</dd>
				</div>
			</dl>

			<!-- Tactical Output -->
			<div class="space-y-4">
				<h2 class="text-base font-bold text-ink card-headline">Season tactical output</h2>
				<div class="grid grid-cols-2 sm:grid-cols-4 gap-4 bg-paper-2 border-t-2 border-rule-2 p-5 text-xs">
					<div>
						<div class="text-muted">Appearances</div>
						<div class="num font-outlier font-bold text-2xl text-ink mt-1">{player.appearances}</div>
					</div>
					<div>
						<div class="text-muted">{player.position === 'Goalkeeper' ? 'Clean sheets' : 'Goals'}</div>
						<div class="num font-outlier font-bold text-2xl text-success mt-1">
							{player.position === 'Goalkeeper' ? player.clean_sheets : player.goals}
						</div>
					</div>
					<div>
						<div class="text-muted">Assists</div>
						<div class="num font-outlier font-bold text-2xl text-accent-2 mt-1">{player.assists}</div>
					</div>
					<div>
						<div class="text-muted">Minutes played</div>
						<div class="num font-outlier font-bold text-2xl text-ink mt-1">{player.minutes_played}</div>
					</div>
					<div>
						<div class="text-muted">Goal contributions</div>
						<div class="num font-outlier font-semibold text-base text-ink mt-1">{player.goal_contributions}</div>
					</div>
					<div>
						<div class="text-muted">Goals per game</div>
						<div class="num font-outlier font-semibold text-base text-ink mt-1">{player.goals_per_game.toFixed(2)}</div>
					</div>
					<div>
						<div class="text-muted">Assists per game</div>
						<div class="num font-outlier font-semibold text-base text-ink mt-1">{player.assists_per_game.toFixed(2)}</div>
					</div>
					<div>
						<div class="text-muted">Discipline (Y / R)</div>
						<div class="num font-outlier font-semibold text-base text-ink mt-1">
							{player.yellow_cards} / {player.red_cards}
						</div>
					</div>
				</div>
			</div>
		</div>
	</section>
</div>
