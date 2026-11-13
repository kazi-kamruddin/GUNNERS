<script lang="ts">
	import { untrack } from 'svelte';
	import { goto } from '$app/navigation';
	import TacticalBoardComponent from '$lib/components/TacticalBoard.svelte';
	import StateBanner from '$lib/components/StateBanner.svelte';
	import {
		ApiError,
		saveTacticalBoard,
		deleteTacticalBoard,
		fetchTacticalBoardsResult
	} from '$lib/api/football';
	import { themeState } from '$lib/stores/theme.svelte';
	import type { PageProps } from './$types';
	import type { TacticalPlayerToken, TacticalAnnotation, TacticalBoard } from '$lib/types/football';

	let { data }: PageProps = $props();

	const initialPreset = untrack(
		() => data.presets.find((p) => p.id === '4-3-3') || data.presets[0]
	);

	let title = $state('High Press & Overload Masterclass');
	let selectedFormationId = $state(initialPreset?.id || '4-3-3');
	let tacticalNotes = $state(
		'Invert fullbacks to secure the center while wingers isolate wide defenders in 1v1 situations.'
	);
	let currentLineup = $state<TacticalPlayerToken[]>(
		initialPreset ? JSON.parse(JSON.stringify(initialPreset.players)) : []
	);
	let currentAnnotations = $state<TacticalAnnotation[]>([]);
	let communityBoards = $state<TacticalBoard[]>(untrack(() => data.communityBoards || []));
	let boardsError = $state<string | null>(untrack(() => data.boardsError ?? null));
	let isRetryingBoards = $state(false);
	let isSaving = $state(false);
	let confirmDeleteBoardId = $state<string | null>(null);
	let deletingBoardId = $state<string | null>(null);

	let toastMessage = $state<string | null>(null);
	let toastKind = $state<'success' | 'error'>('success');
	let toastNeedsLogin = $state(false);
	let toastTimer: ReturnType<typeof setTimeout> | null = null;
	let savedBoardId = $state<string | null>(null);
	let lastSyncedClub = $state(untrack(() => data.viewingClub));

	let trimmedTitleLength = $derived(title.trim().length);
	let isTitleValid = $derived(trimmedTitleLength >= 2 && trimmedTitleLength <= 150);
	let publishLabel = $derived(isSaving ? 'Publishing…' : 'Publish blueprint');

	$effect(() => {
		if (data.viewingClub !== lastSyncedClub) {
			lastSyncedClub = data.viewingClub;
			communityBoards = data.communityBoards || [];
			boardsError = data.boardsError ?? null;
		}
	});

	function handleFormationSelect(presetId: string) {
		selectedFormationId = presetId;
		savedBoardId = null;
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

	async function retryLoadBoards() {
		isRetryingBoards = true;
		try {
			const res = await fetchTacticalBoardsResult(
				data.viewingClub,
				data.session?.access_token ?? null
			);
			boardsError = res.error;
			if (!res.error) {
				communityBoards = res.data;
			}
		} finally {
			isRetryingBoards = false;
		}
	}

	async function handleSaveBoard() {
		if (!isTitleValid || currentLineup.length === 0) {
			showToast('Tactic title must be between 2 and 150 characters.', 'error', false);
			return;
		}
		if (!data.user || !data.session?.access_token) {
			showToast('Please sign in to publish tactical blueprints.', 'error', true);
			return;
		}
		isSaving = true;
		try {
			const authorName =
				data.profile?.display_name || data.user?.email?.split('@')[0] || 'Supporter';
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
				boardsError = null;
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

	async function handleDeleteBoard(board: TacticalBoard) {
		if (!data.session?.access_token) {
			showToast('Please sign in to manage your blueprints.', 'error', true);
			return;
		}
		deletingBoardId = board.id;
		try {
			await deleteTacticalBoard(board.id, data.session.access_token);
			communityBoards = communityBoards.filter((b) => b.id !== board.id);
			if (savedBoardId === board.id) {
				savedBoardId = null;
			}
			confirmDeleteBoardId = null;
			showToast(`Deleted blueprint “${board.title}”.`, 'success', false);
		} catch (err) {
			const isAuth = err instanceof ApiError && err.status === 401;
			showToast(
				isAuth
					? 'Please sign in to delete this blueprint.'
					: err instanceof ApiError
						? err.detail
						: 'Could not delete blueprint. Please try again.',
				'error',
				isAuth
			);
		} finally {
			deletingBoardId = null;
		}
	}

	function handleShareToTerrace() {
		if (savedBoardId) {
			goto(`/terrace?tactic=${encodeURIComponent(savedBoardId)}`);
		} else {
			goto('/terrace');
		}
	}

	function showToast(
		msg: string,
		kind: 'success' | 'error' = 'success',
		needsLogin: boolean = false
	) {
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
			class="fixed bottom-6 right-6 left-6 sm:left-auto max-w-md z-[var(--z-toast)] bg-paper-2 border border-rule-2 px-4 py-3 rounded-card text-xs flex items-center justify-between gap-3 {toastKind === 'error' ? 'text-error' : 'text-success'}"
		>
			<div class="flex items-center gap-3 flex-wrap min-w-0">
				<span>{toastMessage}</span>
				{#if toastNeedsLogin}
					<a href="/login?next=/board" class="underline text-ink font-semibold hover:text-accent-text">
						Sign in
					</a>
				{:else if toastKind === 'success' && savedBoardId}
					<a
						href="/terrace?tactic={encodeURIComponent(savedBoardId)}"
						class="underline text-ink font-semibold hover:text-accent-text"
					>
						Post to Terrace
					</a>
				{/if}
			</div>
			<button
				type="button"
				onclick={() => (toastMessage = null)}
				class="min-h-[44px] px-2 text-muted hover:text-ink font-semibold shrink-0"
			>
				Close
			</button>
		</div>
	{/if}

	<!-- Compact Top Control Bar -->
	<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-rule pb-4">
		<div class="flex items-center gap-3 flex-wrap">
			<label for="formation-select" class="text-xs text-ink-2 font-semibold">Formation preset</label>
			<select
				id="formation-select"
				value={selectedFormationId}
				onchange={(e) => handleFormationSelect((e.target as HTMLSelectElement).value)}
				class="min-h-[44px] bg-paper-2 border border-rule text-ink text-xs rounded-card px-3 font-semibold"
			>
				{#each data.presets as p (p.id)}
					<option value={p.id}>{p.name}</option>
				{/each}
			</select>
			<p class="text-xs text-muted">
				Click or press Enter on any pitch token to edit or swap; drag or use Arrow keys to adjust positioning.
			</p>
		</div>

		<button
			type="button"
			onclick={handleSaveBoard}
			disabled={isSaving || !isTitleValid || currentLineup.length === 0}
			class="min-h-[44px] px-5 rounded-card bg-accent hover:opacity-95 disabled:opacity-50 text-sm text-accent-ink font-semibold transition-opacity shrink-0 self-start sm:self-auto"
		>
			{publishLabel}
		</button>
	</div>

	<!-- Interactive Tactical Pitch (70% vertical pitch + 30% substitutes, tools below) -->
	<div>
		<TacticalBoardComponent
			bind:lineup={currentLineup}
			bind:annotations={currentAnnotations}
			squadPlayers={data.squad}
			formationName={data.presets.find((p) => p.id === selectedFormationId)?.name || '4-3-3 Attacking'}
			readonly={false}
			onchange={() => {
				savedBoardId = null;
			}}
			onshare={handleShareToTerrace}
		/>
	</div>

	<!-- Blueprint Info & Tactical Instructions (below pitch & tools) -->
	<section class="border-t-2 border-rule-2 pt-6 space-y-5">
		<div class="flex items-center justify-between flex-wrap gap-3">
			<h2 class="text-lg font-bold text-ink">Blueprint notes</h2>
			<div class="flex items-center gap-6 text-xs">
				<span><span class="text-muted">Players on pitch:</span> <strong class="num font-outlier text-ink">{currentLineup.length}</strong></span>
				<span><span class="text-muted">Tactical vectors:</span> <strong class="num font-outlier text-accent-2">{currentAnnotations.length}</strong></span>
				<span><span class="text-muted">Club:</span> <strong class="text-ink">{themeState.currentTheme.name}</strong></span>
			</div>
		</div>

		<div class="grid grid-cols-1 md:grid-cols-12 gap-6">
			<div class="md:col-span-5 space-y-2">
				<div class="flex items-center justify-between text-xs">
					<label for="blueprint-title" class="text-ink-2 font-semibold">Tactic title</label>
					<span class="num font-outlier text-muted">{trimmedTitleLength}/150</span>
				</div>
				<input
					id="blueprint-title"
					type="text"
					minlength={2}
					maxlength={150}
					bind:value={title}
					oninput={() => {
						savedBoardId = null;
					}}
					placeholder="e.g. Arteta 4-3-3 asymmetrical build-up"
					class="w-full min-h-[44px] bg-paper-2 border border-rule rounded-card px-3 text-xs text-ink placeholder-muted"
				/>
				{#if trimmedTitleLength < 2}
					<p class="text-xs text-error">Title must be at least 2 characters.</p>
				{/if}
			</div>

			<div class="md:col-span-7 space-y-2">
				<div class="flex items-center justify-between text-xs">
					<label for="tactical-notes" class="text-ink-2 font-semibold">Tactical instructions &amp; debrief</label>
					<span class="num font-outlier text-muted">{tacticalNotes.length}/3000</span>
				</div>
				<textarea
					id="tactical-notes"
					maxlength={3000}
					bind:value={tacticalNotes}
					oninput={() => {
						savedBoardId = null;
					}}
					rows="3"
					placeholder="Explain passing channels, pressing triggers, defensive rest-defense shape, or matchup notes…"
					class="w-full bg-paper-2 border border-rule rounded-card p-3 text-xs text-ink placeholder-muted resize-none"
				></textarea>
			</div>
		</div>
	</section>

	<!-- Community Tactical Blueprints Section -->
	<section class="border-t-2 border-rule-2 pt-8 space-y-6">
		<div class="space-y-1">
			<h2 class="text-xl font-bold text-ink">Community tactical blueprints</h2>
			<p class="text-sm text-muted">Explore matchday setups and pressing plans designed by fellow Gooners.</p>
		</div>

		{#if boardsError && communityBoards.length === 0}
			<StateBanner
				variant="error"
				title="Unable to load community blueprints"
				message={boardsError}
				onretry={retryLoadBoards}
				busy={isRetryingBoards}
			/>
		{:else if communityBoards.length === 0}
			<div class="py-10 border-t border-rule text-sm text-muted">
				No community tactics published yet. Publish your first blueprint above.
			</div>
		{:else}
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
				{#each communityBoards as b (b.id)}
					{@const isOwner = Boolean(data.user?.id && b.user_id && data.user.id === b.user_id)}
					<article class="border-t border-rule pt-4 flex flex-col justify-between space-y-4">
						<div class="space-y-2">
							<div class="flex items-center justify-between text-xs gap-2">
								<span class="font-semibold text-ink-2 truncate">{b.author_name}</span>
								<span class="num font-outlier font-semibold text-accent-text shrink-0">
									{b.formation}
								</span>
							</div>

							<h3 class="text-base font-bold text-ink card-headline">{b.title}</h3>
							{#if b.tactical_notes}
								<p class="text-sm text-ink-2 line-clamp-2 leading-relaxed">{b.tactical_notes}</p>
							{/if}
						</div>

						<div class="pt-3 border-t border-rule flex items-center justify-between gap-2 text-xs flex-wrap">
							<span class="num font-outlier text-muted">
								{b.annotations.length} vectors
							</span>
							<div class="flex items-center gap-2">
								{#if isOwner}
									{#if confirmDeleteBoardId === b.id}
										{@const delBtnLabel = deletingBoardId === b.id ? 'Deleting…' : 'Confirm'}
										<button
											type="button"
											disabled={deletingBoardId === b.id}
											onclick={() => handleDeleteBoard(b)}
											class="min-h-[44px] px-2.5 font-semibold text-error hover:text-ink transition-colors whitespace-nowrap"
										>
											{delBtnLabel}
										</button>
										<button
											type="button"
											onclick={() => (confirmDeleteBoardId = null)}
											class="min-h-[44px] px-2 text-muted hover:text-ink transition-colors"
										>
											Cancel
										</button>
									{:else}
										<button
											type="button"
											onclick={() => (confirmDeleteBoardId = b.id)}
											aria-label="Delete {b.title}"
											class="min-h-[44px] px-2 font-semibold text-muted hover:text-error transition-colors"
										>
											Delete
										</button>
									{/if}
								{/if}

								<button
									type="button"
									onclick={() => loadCommunityBoard(b)}
									class="min-h-[44px] px-2 font-semibold text-accent-2 hover:text-ink transition-colors"
								>
									Load to pitch
								</button>
							</div>
						</div>
					</article>
				{/each}
			</div>
		{/if}
	</section>
</div>
