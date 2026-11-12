<script lang="ts">
	import TacticalBoardComponent from '$lib/components/TacticalBoard.svelte';
	import { ApiError, saveTacticalBoard } from '$lib/api/football';
	import { CLUBS, themeState } from '$lib/stores/theme.svelte';
	import type { PageProps } from './$types';
	import type { TacticalPlayerToken, TacticalAnnotation, TacticalBoard } from '$lib/types/football';

	let { data }: PageProps = $props();

	let title = $state('High Press & Overload Masterclass');
	let selectedFormationId = $state('4-3-3');
	let tacticalNotes = $state('Invert fullbacks to secure the center while wingers isolate wide defenders in 1v1 situations.');
	let currentLineup = $state<TacticalPlayerToken[]>([]);
	let currentAnnotations = $state<TacticalAnnotation[]>([]);
	let communityBoards = $state<TacticalBoard[]>([]);

	let isSaving = $state(false);
	let toastMessage = $state<string | null>(null);
	let toastKind = $state<'success' | 'error'>('success');
	let toastNeedsLogin = $state(false);
	let toastTimer: ReturnType<typeof setTimeout> | null = null;
	let savedBoardId = $state<string | null>(null);
	let publishLabel = $derived(isSaving ? 'Publishing…' : 'Publish blueprint');

	$effect(() => {
		communityBoards = data.communityBoards || [];
		if (data.presets && data.presets.length > 0 && currentLineup.length === 0) {
			const initialPreset = data.presets.find((p) => p.id === '4-3-3') || data.presets[0];
			currentLineup = JSON.parse(JSON.stringify(initialPreset.players));
			selectedFormationId = initialPreset.id;
		}
	});

	function handleFormationSelect(presetId: string) {
		selectedFormationId = presetId;
		const preset = data.presets.find((p) => p.id === presetId);
		if (preset) {
			currentLineup = JSON.parse(JSON.stringify(preset.players));
			currentAnnotations = [];
			showToast(`Applied preset: ${preset.name}`);
		}
	}

	function loadCommunityBoard(board: TacticalBoard) {
		title = board.title;
		selectedFormationId = board.formation;
		tacticalNotes = board.tactical_notes || '';
		currentLineup = JSON.parse(JSON.stringify(board.lineup));
		currentAnnotations = JSON.parse(JSON.stringify(board.annotations || []));
		savedBoardId = board.id;
		showToast(`Loaded blueprint: “${board.title}”`);
		window.scrollTo({ top: 0, behavior: 'smooth' });
	}

	async function handleSaveBoard() {
		if (!title.trim() || currentLineup.length === 0) return;
		if (!data.user || !data.session?.access_token) {
			showToast('Please sign in to publish tactical blueprints.', 'error', true);
			return;
		}
		isSaving = true;
		try {
			const authorName = data.profile?.display_name || data.user?.email?.split('@')[0] || 'Supporter';
			const authorClub = data.profile?.favorite_club_id || themeState.viewingClubId;

			const created = await saveTacticalBoard(
				{
					title: title.trim(),
					formation: selectedFormationId,
					lineup: currentLineup,
					annotations: currentAnnotations,
					tactical_notes: tacticalNotes.trim(),
					author_name: authorName,
					author_club_id: authorClub,
					user_id: data.user?.id
				},
				data.session?.access_token
			);

			if (created) {
				savedBoardId = created.id;
				communityBoards = [created, ...communityBoards];
				showToast('Tactical blueprint published to the community archive.', 'success', false);
			}
		} catch (err) {
			const isAuth = err instanceof ApiError && err.status === 401;
			showToast(
				isAuth
					? 'Please sign in to publish tactical blueprints.'
					: err instanceof ApiError
						? err.detail
						: 'Could not publish tactical blueprint. Please try again.',
				'error',
				isAuth
			);
		} finally {
			isSaving = false;
		}
	}

	function showToast(msg: string, kind: 'success' | 'error' = 'success', needsLogin: boolean = false) {
		if (toastTimer) clearTimeout(toastTimer);
		toastMessage = msg;
		toastKind = kind;
		toastNeedsLogin = needsLogin;
		toastTimer = setTimeout(() => {
			toastMessage = null;
			toastNeedsLogin = false;
		}, 5000);
	}
</script>

<svelte:head>
	<title>Tactical Pitch Studio | GUNNERS</title>
</svelte:head>

<div class="container py-12 space-y-12">
	<!-- Toast Notification -->
	{#if toastMessage}
		<div
			role={toastKind === 'error' ? 'alert' : 'status'}
			class="fixed bottom-6 right-6 z-50 bg-paper-2 border border-rule-2 px-4 py-3 rounded-card text-xs flex items-center gap-3 {toastKind === 'error' ? 'text-error' : 'text-success'}"
		>
			<span>{toastMessage}</span>
			{#if toastNeedsLogin}
				<a
					href="/login"
					class="underline text-ink font-semibold hover:text-accent"
				>
					Sign in
				</a>
			{:else if toastKind === 'success' && savedBoardId}
				<a
					href="/terrace"
					class="underline text-ink font-semibold hover:text-accent"
				>
					Post to Terrace
				</a>
			{/if}
		</div>
	{/if}

	<!-- Header -->
	<div class="flex flex-col md:flex-row md:items-end justify-between gap-6 border-b-2 border-rule-2 pb-8">
		<div class="space-y-3">
			<h1>Matchday lineup & tactical studio</h1>
			<p class="lead text-ink-2">
				Build your starting eleven, swap bench substitutes, draw pressing channels, and export high-resolution lineup graphics.
			</p>
		</div>

		<div class="flex items-center gap-3 flex-wrap">
			<button
				type="button"
				onclick={handleSaveBoard}
				disabled={isSaving || !title.trim()}
				class="h-10 px-5 rounded-card bg-accent hover:opacity-95 text-sm text-accent-ink font-semibold transition-opacity"
			>
				{publishLabel}
			</button>
		</div>
	</div>

	<!-- Main Workspace Grid: Controls & Pitch Board -->
	<div class="grid grid-cols-1 lg:grid-cols-12 gap-10 items-start">
		<!-- Left: Pitch Canvas (8 cols) -->
		<div class="lg:col-span-8 space-y-6">
			<!-- Preset & Quick Actions Bar -->
			<div class="pb-4 border-b border-rule flex items-center justify-between gap-4 flex-wrap text-xs">
				<div class="flex items-center gap-3">
					<label for="formation-select" class="text-ink-2 font-semibold">Formation preset</label>
					<select
						id="formation-select"
						value={selectedFormationId}
						onchange={(e) => handleFormationSelect((e.target as HTMLSelectElement).value)}
						class="h-9 bg-paper-2 border border-rule text-ink text-xs rounded-card px-3 font-semibold"
					>
						{#each data.presets as p}
							<option value={p.id}>{p.name}</option>
						{/each}
					</select>
				</div>

				<p class="text-xs text-muted">
					Select a bench player to swap into the starting eleven, or drag tokens across the turf.
				</p>
			</div>

			<!-- Interactive Tactical Pitch Component -->
			<div>
				<TacticalBoardComponent
					bind:lineup={currentLineup}
					bind:annotations={currentAnnotations}
					squadPlayers={data.squad}
					formationName={data.presets.find((p) => p.id === selectedFormationId)?.name || '4-3-3 Attacking'}
					readonly={false}
					onshare={() => {
						window.location.href = '/terrace';
					}}
				/>
			</div>
		</div>

		<!-- Right: Blueprint Info & Tactical Instructions (4 cols) -->
		<aside class="lg:col-span-4 border-t-2 border-rule-2 pt-5 space-y-5">
			<h2 class="text-lg font-bold text-ink">Blueprint notes</h2>

			<div class="space-y-2">
				<label for="blueprint-title" class="block text-xs text-ink-2 font-semibold">Tactic title</label>
				<input
					id="blueprint-title"
					type="text"
					bind:value={title}
					placeholder="e.g. Arteta 4-3-3 asymmetrical build-up"
					class="w-full h-10 bg-paper-2 border border-rule rounded-card px-3 text-xs text-ink placeholder-muted"
				/>
			</div>

			<div class="space-y-2">
				<label for="tactical-notes" class="block text-xs text-ink-2 font-semibold">Tactical instructions & debrief</label>
				<textarea
					id="tactical-notes"
					bind:value={tacticalNotes}
					rows="6"
					placeholder="Explain passing channels, pressing triggers, defensive rest-defense shape, or matchup notes…"
					class="w-full bg-paper-2 border border-rule rounded-card p-3 text-xs text-ink placeholder-muted resize-none"
				></textarea>
			</div>

			<dl class="pt-4 border-t border-rule space-y-2.5 text-xs">
				<div class="flex items-center justify-between">
					<dt class="text-muted">Players on pitch</dt>
					<dd class="num font-outlier font-semibold text-ink">{currentLineup.length}</dd>
				</div>
				<div class="flex items-center justify-between">
					<dt class="text-muted">Tactical vectors</dt>
					<dd class="num font-outlier font-semibold text-accent-2">{currentAnnotations.length}</dd>
				</div>
				<div class="flex items-center justify-between">
					<dt class="text-muted">Club affiliation</dt>
					<dd class="font-semibold text-ink">{themeState.currentTheme.name}</dd>
				</div>
			</dl>
		</aside>
	</div>

	<!-- Community Tactical Blueprints Section -->
	<section class="border-t-2 border-rule-2 pt-8 space-y-6">
		<div class="space-y-1">
			<h2 class="text-xl font-bold text-ink">Community tactical blueprints</h2>
			<p class="text-sm text-muted">Explore matchday setups and pressing plans designed by fellow Gooners.</p>
		</div>

		{#if communityBoards.length === 0}
			<div class="py-10 border-t border-rule text-sm text-muted">
				No community tactics published yet. Publish your first blueprint above.
			</div>
		{:else}
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
				{#each communityBoards as b}
					{@const _authorClub = CLUBS[b.author_club_id] || CLUBS['arsenal']}
					<article class="border-t border-rule pt-4 flex flex-col justify-between space-y-4">
						<div class="space-y-2">
							<div class="flex items-center justify-between text-xs">
								<span class="font-semibold text-ink-2">{b.author_name}</span>
								<span class="num font-outlier font-semibold text-accent">
									{b.formation}
								</span>
							</div>

							<h3 class="text-base font-bold text-ink">{b.title}</h3>
							{#if b.tactical_notes}
								<p class="text-sm text-ink-2 line-clamp-2 leading-relaxed">{b.tactical_notes}</p>
							{/if}
						</div>

						<div class="pt-3 border-t border-rule flex items-center justify-between text-xs">
							<span class="num font-outlier text-muted">
								{b.annotations.length} vectors
							</span>
							<button
								type="button"
								onclick={() => loadCommunityBoard(b)}
								class="font-semibold text-accent-2 hover:text-ink transition-colors"
							>
								Load to pitch
							</button>
						</div>
					</article>
				{/each}
			</div>
		{/if}
	</section>
</div>
