<script lang="ts">
	import TacticalBoardComponent from '$lib/components/TacticalBoard.svelte';
	import { saveTacticalBoard, fetchTacticalBoards } from '$lib/api/football';
	import { CLUBS, themeState } from '$lib/stores/theme.svelte';
	import type { PageProps } from './$types';
	import type { TacticalPlayerToken, TacticalAnnotation, TacticalBoard } from '$lib/types/football';

	let { data }: PageProps = $props();

	// Active tactical board state
	let title = $state('High Press & Overload Masterclass');
	let selectedFormationId = $state('4-3-3');
	let tacticalNotes = $state('Invert fullbacks to secure the center while wingers isolate wide defenders in 1v1 situations.');
	let currentLineup = $state<TacticalPlayerToken[]>([]);
	let currentAnnotations = $state<TacticalAnnotation[]>([]);
	let communityBoards = $state<TacticalBoard[]>([]);

	// Actions state
	let isSaving = $state(false);
	let toastMessage = $state<string | null>(null);
	let savedBoardId = $state<string | null>(null);

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
		showToast(`Loaded blueprint: "${board.title}"`);
		window.scrollTo({ top: 0, behavior: 'smooth' });
	}

	async function handleSaveBoard() {
		if (!title.trim() || currentLineup.length === 0) return;
		isSaving = true;
		try {
			const authorName = data.profile?.display_name || data.user?.email?.split('@')[0] || 'Supporter';
			const authorClub = data.profile?.favorite_club_id || themeState.viewingClubId;

			const created = await saveTacticalBoard({
				title: title.trim(),
				formation: selectedFormationId,
				lineup: currentLineup,
				annotations: currentAnnotations,
				tactical_notes: tacticalNotes.trim(),
				author_name: authorName,
				author_club_id: authorClub,
				user_id: data.user?.id
			});

			if (created) {
				savedBoardId = created.id;
				communityBoards = [created, ...communityBoards];
				showToast('Tactical blueprint published successfully!');
			}
		} finally {
			isSaving = false;
		}
	}

	function showToast(msg: string) {
		toastMessage = msg;
		setTimeout(() => {
			toastMessage = null;
		}, 4000);
	}
</script>

<svelte:head>
	<title>Tactical Pitch Studio | GUNNERS Reborn</title>
</svelte:head>

<div class="max-w-7xl mx-auto px-4 py-8 space-y-8">
	<!-- Toast Notification -->
	{#if toastMessage}
		<div class="fixed bottom-6 right-6 z-50 bg-[#12161f] border border-emerald-500/40 text-emerald-300 px-4 py-3 rounded-lg shadow-xl text-xs flex items-center gap-2">
			<span class="w-2 h-2 rounded-full bg-emerald-400"></span>
			<span>{toastMessage}</span>
			{#if savedBoardId}
				<a
					href="/terrace"
					class="ml-2 underline text-white font-bold hover:text-emerald-200"
				>
					Post to Terrace →
				</a>
			{/if}
		</div>
	{/if}

	<!-- Header -->
	<div class="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[#1e2430] pb-6">
		<div>
			<div class="inline-flex items-center gap-2 px-2.5 py-0.5 rounded text-[11px] font-semibold uppercase tracking-wider mb-2 bg-red-950/70 text-red-400 border border-red-800/40 font-mono">
				Interactive Tactical Studio
			</div>
			<h1 class="text-2xl font-black text-white uppercase tracking-tight">Formation & Pitch Board</h1>
			<p class="text-sm text-gray-400 mt-1">
				Diagram starting line-ups, draw tactical runs and pressing triggers, then attach your setup to Terrace debates.
			</p>
		</div>

		<!-- Action buttons -->
		<div class="flex items-center gap-2 flex-wrap">
			<button
				type="button"
				onclick={handleSaveBoard}
				disabled={isSaving || !title.trim()}
				class="px-4 py-2 rounded-lg bg-red-600 hover:bg-red-500 text-xs text-white font-bold transition disabled:opacity-50 shadow-sm"
			>
				{isSaving ? 'Publishing...' : 'Publish Tactical Blueprint'}
			</button>
		</div>
	</div>

	<!-- Main Workspace Grid: Controls & Pitch Board -->
	<div class="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
		<!-- Left: Pitch Canvas (Span 2) -->
		<div class="lg:col-span-2 space-y-4">
			<!-- Preset & Quick Actions Bar -->
			<div class="p-3.5 rounded-lg border border-[#1e2430] bg-[#12161f] flex items-center justify-between gap-3 flex-wrap text-xs">
				<div class="flex items-center gap-2">
					<label for="formation-select" class="text-gray-400 font-mono font-bold uppercase text-[11px]">Formation:</label>
					<select
						id="formation-select"
						value={selectedFormationId}
						onchange={(e) => handleFormationSelect((e.target as HTMLSelectElement).value)}
						class="bg-[#0a0c10] border border-[#1e2430] text-gray-200 text-xs rounded px-2.5 py-1.5 focus:outline-none focus:border-red-500 font-bold"
					>
						{#each data.presets as p}
							<option value={p.id}>{p.name}</option>
						{/each}
					</select>
				</div>

				<div class="flex items-center gap-2 text-gray-400 text-xs">
					<span class="text-[11px]">💡 Click any player token to edit name, number, or pick from live squad roster</span>
				</div>
			</div>

			<!-- Interactive Tactical Pitch Component -->
			<div class="p-4 rounded-xl border border-[#1e2430] bg-[#0c120c]">
				<TacticalBoardComponent
					bind:lineup={currentLineup}
					bind:annotations={currentAnnotations}
					squadPlayers={data.squad}
					readonly={false}
				/>
			</div>
		</div>

		<!-- Right: Blueprint Info & Tactical Instructions (Span 1) -->
		<div class="space-y-4">
			<div class="p-5 rounded-xl border border-[#1e2430] bg-[#12161f] space-y-4">
				<h3 class="text-xs font-mono font-bold uppercase text-gray-400">Blueprint Details</h3>

				<div class="space-y-2">
					<label for="blueprint-title" class="text-xs text-gray-300 font-medium">Tactic Title</label>
					<input
						id="blueprint-title"
						type="text"
						bind:value={title}
						placeholder="e.g. Arteta 4-3-3 Asymmetrical Build-Up"
						class="w-full bg-[#0a0c10] border border-[#1e2430] rounded-lg p-2.5 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-red-500"
					/>
				</div>

				<div class="space-y-2">
					<label for="tactical-notes" class="text-xs text-gray-300 font-medium">Tactical Instructions & Debrief</label>
					<textarea
						id="tactical-notes"
						bind:value={tacticalNotes}
						rows="6"
						placeholder="Explain passing channels, pressing intensity, defensive shape, or matchup instructions..."
						class="w-full bg-[#0a0c10] border border-[#1e2430] rounded-lg p-2.5 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-red-500 resize-none"
					></textarea>
				</div>

				<div class="pt-2 border-t border-[#1e2430] space-y-2 text-xs text-gray-400">
					<div class="flex items-center justify-between">
						<span>Total Players on Pitch:</span>
						<span class="font-mono font-bold text-white">{currentLineup.length}</span>
					</div>
					<div class="flex items-center justify-between">
						<span>Tactical Arrows / Marks:</span>
						<span class="font-mono font-bold text-amber-400">{currentAnnotations.length}</span>
					</div>
					<div class="flex items-center justify-between">
						<span>Author Affiliation:</span>
						<span class="font-mono font-bold text-white capitalize">{themeState.currentTheme.name}</span>
					</div>
				</div>
			</div>
		</div>
	</div>

	<!-- Community Tactical Blueprints Section -->
	<div class="border-t border-[#1e2430] pt-8 space-y-4">
		<div class="flex items-center justify-between">
			<div>
				<h2 class="text-lg font-black text-white uppercase tracking-tight">Community Tactical Blueprints</h2>
				<p class="text-xs text-gray-400">Explore setups and game plans designed by fellow supporters.</p>
			</div>
		</div>

		{#if communityBoards.length === 0}
			<div class="py-12 text-center border border-dashed border-[#1e2430] rounded-xl text-xs text-gray-500">
				No community tactics published yet. Be the first to publish one above!
			</div>
		{:else}
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
				{#each communityBoards as b}
					{@const authorClub = CLUBS[b.author_club_id] || CLUBS['arsenal']}
					<div class="p-4 rounded-xl border border-[#1e2430] bg-[#12161f] space-y-3 flex flex-col justify-between hover:border-gray-600 transition">
						<div class="space-y-2">
							<div class="flex items-center justify-between text-[11px]">
								<div class="flex items-center gap-1.5">
									<span class="w-2 h-2 rounded-full" style="background-color: {authorClub.primary_color}"></span>
									<span class="font-bold text-white">{b.author_name}</span>
								</div>
								<span class="px-2 py-0.5 rounded font-mono font-bold text-[10px] bg-red-950/70 text-red-300 border border-red-800/40">
									{b.formation}
								</span>
							</div>

							<h4 class="text-xs font-bold text-gray-100">{b.title}</h4>
							{#if b.tactical_notes}
								<p class="text-[11px] text-gray-400 line-clamp-2 leading-relaxed">{b.tactical_notes}</p>
							{/if}
						</div>

						<div class="pt-2 border-t border-[#1e2430] flex items-center justify-between text-xs">
							<span class="text-[10px] text-gray-500 font-mono">
								{b.annotations.length} vectors
							</span>
							<button
								type="button"
								onclick={() => loadCommunityBoard(b)}
								class="text-[11px] font-bold text-amber-400 hover:text-amber-300 transition"
							>
								Load to Pitch →
							</button>
						</div>
					</div>
				{/each}
			</div>
		{/if}
	</div>
</div>
