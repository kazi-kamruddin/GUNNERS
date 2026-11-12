<script lang="ts">
	import type { TacticalPlayerToken, TacticalAnnotation, Player } from '$lib/types/football';

	interface Props {
		lineup: TacticalPlayerToken[];
		bench?: TacticalPlayerToken[];
		annotations?: TacticalAnnotation[];
		squadPlayers?: Player[];
		readonly?: boolean;
		showGuides?: boolean;
		fluidMode?: boolean;
		formationName?: string;
		onchange?: () => void;
		onshare?: () => void;
	}

	let {
		lineup = $bindable([]),
		bench = $bindable([]),
		annotations = $bindable([]),
		squadPlayers = [],
		readonly = false,
		showGuides = $bindable(true),
		fluidMode = $bindable(false),
		formationName = '4-3-3 Attacking',
		onchange,
		onshare
	}: Props = $props();

	let activeTool = $state<'select' | 'run' | 'pass' | 'press'>('select');
	let svgRef = $state<SVGSVGElement | null>(null);
	let draggingPlayerId = $state<string | null>(null);
	let hasDragged = $state(false);
	let isDrawingVector = $state(false);
	let vectorStart = $state<{ x: number; y: number } | null>(null);
	let vectorCurrent = $state<{ x: number; y: number } | null>(null);
	let selectedBenchPlayerId = $state<string | null>(null);
	let editingPlayer = $state<TacticalPlayerToken | null>(null);
	let isEditingBench = $state(false);
	let selectedRosterId = $state('');
	let exportSuccessMessage = $state<string | null>(null);

	let fluidModeLabel = $derived(fluidMode ? 'Fluid free-roam' : 'Preset grid');
	let benchInstruction = $derived(
		selectedBenchPlayerId
			? 'Select a starting player on the pitch to complete the swap'
			: 'Select a bench player to swap into the starting eleven'
	);

	$effect(() => {
		if (bench.length === 0) {
			bench = [
				{ id: 'b1', name: 'Neto', number: 32, role: 'GK', x: 0, y: 0 },
				{ id: 'b2', name: 'Timber', number: 12, role: 'DF', x: 0, y: 0 },
				{ id: 'b3', name: 'Calafiori', number: 33, role: 'DF', x: 0, y: 0 },
				{ id: 'b4', name: 'Merino', number: 23, role: 'MF', x: 0, y: 0 },
				{ id: 'b5', name: 'Jorginho', number: 20, role: 'MF', x: 0, y: 0 },
				{ id: 'b6', name: 'Trossard', number: 19, role: 'FW', x: 0, y: 0 },
				{ id: 'b7', name: 'Sterling', number: 30, role: 'FW', x: 0, y: 0 },
				{ id: 'b8', name: 'G. Jesus', number: 9, role: 'FW', x: 0, y: 0 }
			];
		}
	});

	function getPitchCoords(e: PointerEvent): { x: number; y: number } | null {
		if (!svgRef) return null;
		const rect = svgRef.getBoundingClientRect();
		const x = Math.max(2, Math.min(98, ((e.clientX - rect.left) / rect.width) * 100));
		const y = Math.max(2, Math.min(98, ((e.clientY - rect.top) / rect.height) * 100));
		return {
			x: Math.round(x * 10) / 10,
			y: Math.round(y * 10) / 10
		};
	}

	function handlePointerDown(e: PointerEvent, playerId?: string) {
		if (readonly) return;

		if (selectedBenchPlayerId && playerId) {
			swapBenchWithStarting(selectedBenchPlayerId, playerId);
			return;
		}

		if (activeTool === 'select' && playerId) {
			draggingPlayerId = playerId;
			hasDragged = false;
			(e.target as Element).setPointerCapture(e.pointerId);
		} else if (activeTool !== 'select') {
			const pt = getPitchCoords(e);
			if (pt) {
				isDrawingVector = true;
				vectorStart = pt;
				vectorCurrent = pt;
			}
		}
	}

	function handlePointerMove(e: PointerEvent) {
		if (readonly) return;

		if (draggingPlayerId) {
			hasDragged = true;
			const pt = getPitchCoords(e);
			if (pt) {
				const idx = lineup.findIndex((p) => p.id === draggingPlayerId);
				if (idx !== -1) {
					lineup[idx].x = pt.x;
					lineup[idx].y = pt.y;
					onchange?.();
				}
			}
		} else if (isDrawingVector && vectorStart) {
			const pt = getPitchCoords(e);
			if (pt) {
				vectorCurrent = pt;
			}
		}
	}

	function handlePointerUp() {
		if (readonly) return;

		if (draggingPlayerId) {
			const pid = draggingPlayerId;
			draggingPlayerId = null;
			if (!hasDragged) {
				const player = lineup.find((p) => p.id === pid);
				if (player) {
					editingPlayer = { ...player };
					isEditingBench = false;
					selectedRosterId = '';
				}
			}
		} else if (isDrawingVector && vectorStart && vectorCurrent) {
			const dist = Math.hypot(vectorCurrent.x - vectorStart.x, vectorCurrent.y - vectorStart.y);
			if (dist > 3) {
				const newAnnotation: TacticalAnnotation = {
					id: `ann_${Date.now()}_${Math.random().toString(36).substring(2, 6)}`,
					type: activeTool,
					from_x: vectorStart.x,
					from_y: vectorStart.y,
					to_x: vectorCurrent.x,
					to_y: vectorCurrent.y
				};
				annotations = [...annotations, newAnnotation];
				onchange?.();
			}
			isDrawingVector = false;
			vectorStart = null;
			vectorCurrent = null;
		}
	}

	function swapBenchWithStarting(benchId: string, startingId: string) {
		const bIdx = bench.findIndex((p) => p.id === benchId);
		const sIdx = lineup.findIndex((p) => p.id === startingId);
		if (bIdx !== -1 && sIdx !== -1) {
			const benchPlayer = bench[bIdx];
			const startingPlayer = lineup[sIdx];

			const tempName = startingPlayer.name;
			const tempNumber = startingPlayer.number;
			const tempRole = startingPlayer.role;

			startingPlayer.name = benchPlayer.name;
			startingPlayer.number = benchPlayer.number;
			startingPlayer.role = benchPlayer.role;

			benchPlayer.name = tempName;
			benchPlayer.number = tempNumber;
			benchPlayer.role = tempRole;

			selectedBenchPlayerId = null;
			onchange?.();
		}
	}

	function clearAllAnnotations() {
		annotations = [];
		onchange?.();
	}

	function handleSavePlayerModal() {
		if (!editingPlayer) return;
		if (isEditingBench) {
			const idx = bench.findIndex((p) => p.id === editingPlayer?.id);
			if (idx !== -1) {
				bench[idx] = { ...editingPlayer };
				onchange?.();
			}
		} else {
			const idx = lineup.findIndex((p) => p.id === editingPlayer?.id);
			if (idx !== -1) {
				lineup[idx] = { ...editingPlayer };
				onchange?.();
			}
		}
		editingPlayer = null;
	}

	function handleRosterSelect(player: Player) {
		if (!editingPlayer) return;
		editingPlayer.name = player.name;
		editingPlayer.number = player.jersey_number;
		editingPlayer.role = player.position;
	}

	function exportLineupAsImage() {
		try {
			const canvas = document.createElement('canvas');
			canvas.width = 1200;
			canvas.height = 850;
			const ctx = canvas.getContext('2d');
			if (!ctx) return;

			ctx.fillStyle = 'rgb(6, 26, 9)';
			ctx.fillRect(0, 0, 1200, 850);

			ctx.fillStyle = 'rgb(8, 33, 12)';
			for (let x = 0; x < 1200; x += 100) {
				if ((x / 100) % 2 === 0) {
					ctx.fillRect(x, 0, 50, 850);
				}
			}

			ctx.strokeStyle = 'rgb(34, 197, 94)';
			ctx.lineWidth = 3;
			ctx.strokeRect(50, 60, 1100, 680);

			ctx.beginPath();
			ctx.moveTo(600, 60);
			ctx.lineTo(600, 740);
			ctx.stroke();

			ctx.beginPath();
			ctx.arc(600, 400, 85, 0, Math.PI * 2);
			ctx.stroke();

			ctx.strokeRect(50, 220, 180, 360);
			ctx.strokeRect(970, 220, 180, 360);

			ctx.fillStyle = 'rgb(239, 1, 7)';
			ctx.fillRect(50, 10, 1100, 35);
			ctx.fillStyle = 'rgb(255, 255, 255)';
			ctx.font = 'bold 16px sans-serif';
			ctx.fillText('GUNNERS REBORN : ARSENAL MATCHDAY TACTICAL LINEUP', 70, 33);
			ctx.fillStyle = 'rgb(254, 240, 138)';
			ctx.font = 'bold 14px monospace';
			ctx.fillText(`FORMATION: ${formationName.toUpperCase()}`, 960, 33);

			for (const p of lineup) {
				const px = 50 + (p.x / 100) * 1100;
				const py = 60 + (p.y / 100) * 680;

				ctx.beginPath();
				ctx.arc(px, py, 24, 0, Math.PI * 2);
				ctx.fillStyle = 'rgb(239, 1, 7)';
				ctx.fill();
				ctx.lineWidth = 3;
				ctx.strokeStyle = 'rgb(255, 255, 255)';
				ctx.stroke();

				ctx.fillStyle = 'rgb(255, 255, 255)';
				ctx.font = 'bold 16px monospace';
				ctx.textAlign = 'center';
				ctx.fillText(String(p.number), px, py + 6);

				ctx.fillStyle = 'rgb(10, 12, 16)';
				ctx.fillRect(px - 55, py + 30, 110, 20);
				ctx.strokeStyle = 'rgb(156, 130, 74)';
				ctx.lineWidth = 1;
				ctx.strokeRect(px - 55, py + 30, 110, 20);

				ctx.fillStyle = 'rgb(255, 255, 255)';
				ctx.font = 'bold 11px sans-serif';
				ctx.fillText(`${p.name} (${p.role})`, px, py + 44);
			}

			ctx.fillStyle = 'rgb(13, 16, 23)';
			ctx.fillRect(50, 760, 1100, 75);
			ctx.strokeStyle = 'rgb(30, 36, 48)';
			ctx.strokeRect(50, 760, 1100, 75);

			ctx.fillStyle = 'rgb(156, 130, 74)';
			ctx.font = 'bold 12px monospace';
			ctx.textAlign = 'left';
			ctx.fillText('BENCH:', 70, 802);

			let bx = 140;
			for (const bp of bench.slice(0, 8)) {
				ctx.fillStyle = 'rgb(255, 255, 255)';
				ctx.font = '11px sans-serif';
				ctx.fillText(`#${bp.number} ${bp.name}`, bx, 802);
				bx += 115;
			}

			const dataUrl = canvas.toDataURL('image/png');
			const link = document.createElement('a');
			link.download = `Arsenal_Tactical_Lineup_${Date.now()}.png`;
			link.href = dataUrl;
			link.click();

			exportSuccessMessage = 'Lineup exported as high-resolution PNG image.';
			setTimeout(() => {
				exportSuccessMessage = null;
			}, 4000);
		} catch (err) {
			console.error('Export failed:', err);
		}
	}
</script>

<div class="space-y-6 select-none">
	{#if exportSuccessMessage}
		<div class="p-3 rounded-card bg-paper-2 text-success border border-rule text-xs flex items-center justify-between">
			<span>{exportSuccessMessage}</span>
			<button type="button" onclick={() => (exportSuccessMessage = null)} class="text-muted hover:text-ink transition-colors">Close</button>
		</div>
	{/if}

	{#if !readonly}
		<!-- Pitch Toolbar -->
		<div class="flex items-center justify-between gap-3 pb-4 border-b border-rule flex-wrap text-xs">
			<!-- Drawing & Moving Tools -->
			<div class="flex items-center gap-2 flex-wrap">
				<span class="text-muted font-semibold mr-1">Tools:</span>
				<button
					type="button"
					onclick={() => (activeTool = 'select')}
					class="h-8 px-3 rounded-card font-semibold transition-colors border {activeTool === 'select' ? 'bg-paper-3 text-ink border-rule-2' : 'bg-paper-2 text-ink-2 border-rule hover:text-ink'}"
				>
					Move tokens
				</button>
				<button
					type="button"
					onclick={() => (activeTool = 'run')}
					class="h-8 px-3 rounded-card font-semibold transition-colors border {activeTool === 'run' ? 'bg-paper-3 text-accent-2 border-rule-2' : 'bg-paper-2 text-ink-2 border-rule hover:text-ink'}"
				>
					Run vector
				</button>
				<button
					type="button"
					onclick={() => (activeTool = 'pass')}
					class="h-8 px-3 rounded-card font-semibold transition-colors border {activeTool === 'pass' ? 'bg-paper-3 text-success border-rule-2' : 'bg-paper-2 text-ink-2 border-rule hover:text-ink'}"
				>
					Pass channel
				</button>
				<button
					type="button"
					onclick={() => (activeTool = 'press')}
					class="h-8 px-3 rounded-card font-semibold transition-colors border {activeTool === 'press' ? 'bg-paper-3 text-error border-rule-2' : 'bg-paper-2 text-ink-2 border-rule hover:text-ink'}"
				>
					High press
				</button>

				<button
					type="button"
					onclick={() => (fluidMode = !fluidMode)}
					class="h-8 px-3 rounded-card font-semibold transition-colors border ml-1 {fluidMode ? 'bg-accent-2 text-paper border-accent-2' : 'bg-paper-2 text-ink-2 border-rule hover:text-ink'}"
					title="Fluid movement allows unconstrained dragging anywhere on pitch"
				>
					{fluidModeLabel}
				</button>
			</div>

			<!-- Actions: Export PNG, Clear, Share -->
			<div class="flex items-center gap-2">
				<button
					type="button"
					onclick={exportLineupAsImage}
					class="h-8 px-3.5 rounded-card bg-accent hover:opacity-95 text-accent-ink font-semibold text-xs transition-opacity"
					title="Download high-resolution lineup graphic"
				>
					Export PNG
				</button>

				{#if onshare}
					<button
						type="button"
						onclick={onshare}
						class="h-8 px-3.5 rounded-card bg-paper-2 hover:bg-paper-3 text-accent-2 font-semibold text-xs transition-colors border border-rule"
					>
						Share to Terrace
					</button>
				{/if}

				{#if annotations.length > 0}
					<button
						type="button"
						onclick={clearAllAnnotations}
						class="h-8 px-2.5 rounded-card text-error hover:text-ink transition-colors"
					>
						Clear arrows
					</button>
				{/if}
			</div>
		</div>
	{/if}

	<!-- Pitch SVG Container -->
	<div class="relative w-full rounded-card border border-rule bg-pitch overflow-hidden touch-none">
		<svg
			bind:this={svgRef}
			viewBox="0 0 1000 680"
			class="w-full h-auto cursor-crosshair"
			role="application"
			aria-label="Football tactical pitch diagram"
			onpointerdown={(e) => handlePointerDown(e)}
			onpointermove={handlePointerMove}
			onpointerup={handlePointerUp}
		>
			<defs>
				<marker id="arrow-run" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">
					<path d="M 0 1.5 L 9 5 L 0 8.5 z" fill="var(--color-accent-2)" />
				</marker>
				<marker id="arrow-pass" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">
					<path d="M 0 1.5 L 9 5 L 0 8.5 z" fill="var(--color-success)" />
				</marker>
				<marker id="arrow-press" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">
					<path d="M 0 1.5 L 9 5 L 0 8.5 z" fill="var(--color-error)" />
				</marker>

				<pattern id="stripes" width="100" height="680" patternUnits="userSpaceOnUse">
					<rect width="50" height="680" fill="var(--color-pitch)" />
					<rect x="50" width="50" height="680" fill="var(--color-pitch-2)" />
				</pattern>
			</defs>

			<!-- Grass background -->
			<rect width="1000" height="680" fill="url(#stripes)" />

			<!-- Pitch Markings -->
			<rect x="30" y="30" width="940" height="620" fill="none" stroke="var(--color-success)" stroke-width="2.5" stroke-opacity="0.35" />
			<line x1="500" y1="30" x2="500" y2="650" stroke="var(--color-success)" stroke-width="2.5" stroke-opacity="0.35" />
			<circle cx="500" cy="340" r="85" fill="none" stroke="var(--color-success)" stroke-width="2.5" stroke-opacity="0.35" />
			<circle cx="500" cy="340" r="4" fill="var(--color-success)" fill-opacity="0.5" />

			<rect x="30" y="165" width="165" height="350" fill="none" stroke="var(--color-success)" stroke-width="2.5" stroke-opacity="0.35" />
			<rect x="30" y="245" width="55" height="190" fill="none" stroke="var(--color-success)" stroke-width="2.5" stroke-opacity="0.35" />
			<circle cx="140" cy="340" r="3.5" fill="var(--color-success)" fill-opacity="0.5" />
			<path d="M 195 290 A 85 85 0 0 1 195 390" fill="none" stroke="var(--color-success)" stroke-width="2.5" stroke-opacity="0.35" />

			<rect x="805" y="165" width="165" height="350" fill="none" stroke="var(--color-success)" stroke-width="2.5" stroke-opacity="0.35" />
			<rect x="915" y="245" width="55" height="190" fill="none" stroke="var(--color-success)" stroke-width="2.5" stroke-opacity="0.35" />
			<circle cx="860" cy="340" r="3.5" fill="var(--color-success)" fill-opacity="0.5" />
			<path d="M 805 290 A 85 85 0 0 0 805 390" fill="none" stroke="var(--color-success)" stroke-width="2.5" stroke-opacity="0.35" />

			{#if showGuides}
				<line x1="30" y1="204" x2="970" y2="204" stroke="var(--color-accent-2)" stroke-dasharray="4 6" stroke-width="1.5" stroke-opacity="0.25" />
				<line x1="30" y1="476" x2="970" y2="476" stroke="var(--color-accent-2)" stroke-dasharray="4 6" stroke-width="1.5" stroke-opacity="0.25" />
				<line x1="343" y1="30" x2="343" y2="650" stroke="var(--color-ink-2)" stroke-dasharray="4 6" stroke-width="1.5" stroke-opacity="0.2" />
				<line x1="657" y1="30" x2="657" y2="650" stroke="var(--color-ink-2)" stroke-dasharray="4 6" stroke-width="1.5" stroke-opacity="0.2" />
			{/if}

			<!-- Vector Annotations Layer -->
			{#each annotations as ann (ann.id)}
				{@const x1 = (ann.from_x / 100) * 1000}
				{@const y1 = (ann.from_y / 100) * 680}
				{@const x2 = (ann.to_x / 100) * 1000}
				{@const y2 = (ann.to_y / 100) * 680}
				{#if ann.type === 'run'}
					<line x1={x1} y1={y1} x2={x2} y2={y2} stroke="var(--color-accent-2)" stroke-width="3.5" stroke-linecap="round" marker-end="url(#arrow-run)" />
				{:else if ann.type === 'pass'}
					<line x1={x1} y1={y1} x2={x2} y2={y2} stroke="var(--color-success)" stroke-width="3" stroke-dasharray="6 4" stroke-linecap="round" marker-end="url(#arrow-pass)" />
				{:else if ann.type === 'press'}
					<line x1={x1} y1={y1} x2={x2} y2={y2} stroke="var(--color-error)" stroke-width="3.5" stroke-dasharray="8 3" marker-end="url(#arrow-press)" />
				{/if}
			{/each}

			{#if isDrawingVector && vectorStart && vectorCurrent}
				{@const sx = (vectorStart.x / 100) * 1000}
				{@const sy = (vectorStart.y / 100) * 680}
				{@const cx = (vectorCurrent.x / 100) * 1000}
				{@const cy = (vectorCurrent.y / 100) * 680}
				<line
					x1={sx}
					y1={sy}
					x2={cx}
					y2={cy}
					stroke={activeTool === 'run' ? 'var(--color-accent-2)' : activeTool === 'pass' ? 'var(--color-success)' : 'var(--color-error)'}
					stroke-width="3"
					stroke-dasharray="4 4"
					opacity="0.8"
				/>
			{/if}

			<!-- Player Tokens Layer -->
			{#each lineup as player (player.id)}
				{@const px = (player.x / 100) * 1000}
				{@const py = (player.y / 100) * 680}
				{@const isDragging = draggingPlayerId === player.id}
				<g
					transform="translate({px}, {py})"
					class={readonly ? '' : 'cursor-grab active:cursor-grabbing focus:outline-none'}
					role="button"
					tabindex={readonly ? -1 : 0}
					aria-label="{player.name} #{player.number} {player.role}"
					onkeydown={(e) => {
						if (!readonly && (e.key === 'Enter' || e.key === ' ')) {
							editingPlayer = { ...player };
							isEditingBench = false;
							selectedRosterId = '';
						}
					}}
					onpointerdown={(e) => {
						e.stopPropagation();
						handlePointerDown(e, player.id);
					}}
				>
					{#if isDragging || (selectedBenchPlayerId && !readonly)}
						<circle
							r="30"
							fill="none"
							stroke={selectedBenchPlayerId ? 'var(--color-success)' : 'var(--color-accent-2)'}
							stroke-width="3"
							opacity="0.7"
							stroke-dasharray={selectedBenchPlayerId ? '4 2' : 'none'}
						/>
					{/if}

					<circle r="22" fill="var(--color-accent)" stroke="var(--color-ink)" stroke-width="3" />

					<text text-anchor="middle" dy="5" fill="var(--color-ink)" font-size="14" font-weight="bold" font-family="var(--font-outlier)">
						{player.number}
					</text>

					<g transform="translate(0, 32)">
						<rect x="-48" y="-10" width="96" height="20" rx="4" fill="var(--color-paper)" fill-opacity="0.95" stroke="var(--color-accent-2)" stroke-width="1" />
						<text text-anchor="middle" dy="4" fill="var(--color-ink)" font-size="10" font-weight="bold" font-family="var(--font-body)">
							{player.name} ({player.role})
						</text>
					</g>
				</g>
			{/each}
		</svg>
	</div>

	<!-- Substitutes Bench Pool (The Dugout) -->
	{#if bench && bench.length > 0}
		<div class="border-t border-rule pt-5 space-y-3">
			<div class="flex items-center justify-between flex-wrap gap-2">
				<span class="text-sm font-bold text-ink">
					Substitutes bench (<span class="num font-outlier">{bench.length}</span> players)
				</span>
				<span class="text-xs text-muted">
					{benchInstruction}
				</span>
			</div>

			<div class="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-8 gap-2.5">
				{#each bench as bPlayer}
					{@const isSelected = selectedBenchPlayerId === bPlayer.id}
					{@const bTag = `#${bPlayer.number} ${bPlayer.name}`}
					<button
						type="button"
						onclick={() => {
							if (readonly) return;
							selectedBenchPlayerId = isSelected ? null : bPlayer.id;
						}}
						class="p-2.5 rounded-card border transition-colors text-center flex flex-col items-center justify-center gap-1 whitespace-nowrap {isSelected ? 'bg-paper-3 border-accent-2 text-accent-2' : 'bg-paper-2 border-rule text-ink-2 hover:text-ink'}"
					>
						<span class="text-xs font-semibold text-ink truncate max-w-[85px]">{bTag}</span>
					</button>
				{/each}
			</div>
		</div>
	{/if}

	<!-- Quick Player Edit Modal -->
	{#if editingPlayer}
		<div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-paper/85">
			<div class="bg-paper-2 border-t-2 border-rule-2 p-6 w-full max-w-sm space-y-5">
				<div class="flex items-center justify-between border-b border-rule pb-3">
					<h3 class="text-base font-bold text-ink">
						Edit <span class="num font-outlier text-accent">#{editingPlayer.number}</span> {editingPlayer.name}
					</h3>
					<button type="button" onclick={() => (editingPlayer = null)} class="text-muted hover:text-ink text-xs font-semibold">Close</button>
				</div>

				{#if squadPlayers && squadPlayers.length > 0}
					<div class="space-y-1.5">
						<label for="roster-select" class="block text-xs font-semibold text-ink-2">
							Select from Arsenal squad roster
						</label>
						<select
							id="roster-select"
							bind:value={selectedRosterId}
							onchange={() => {
								const selected = squadPlayers.find((p) => p.id === selectedRosterId);
								if (selected) handleRosterSelect(selected);
							}}
							class="w-full h-10 bg-paper border border-rule rounded-card px-3 text-xs text-ink"
						>
							<option value="">Choose Arsenal player…</option>
							{#each squadPlayers as sp}
								<option value={sp.id}>
									#{sp.jersey_number} {sp.name} ({sp.position})
								</option>
							{/each}
						</select>
					</div>
				{/if}

				<div class="space-y-3">
					<div>
						<label for="player-name" class="block text-xs font-semibold text-ink-2">Player name</label>
						<input
							id="player-name"
							type="text"
							bind:value={editingPlayer.name}
							class="w-full h-10 bg-paper border border-rule rounded-card px-3 text-xs text-ink mt-1"
						/>
					</div>

					<div class="grid grid-cols-2 gap-3">
						<div>
							<label for="player-number" class="block text-xs font-semibold text-ink-2">Jersey number</label>
							<input
								id="player-number"
								type="number"
								min="1"
								max="99"
								bind:value={editingPlayer.number}
								class="w-full h-10 bg-paper border border-rule rounded-card px-3 text-xs text-ink num font-outlier mt-1"
							/>
						</div>
						<div>
							<label for="player-role" class="block text-xs font-semibold text-ink-2">Tactical role</label>
							<select
								id="player-role"
								bind:value={editingPlayer.role}
								class="w-full h-10 bg-paper border border-rule rounded-card px-3 text-xs text-ink mt-1"
							>
								<option value="GK">GK (Goalkeeper)</option>
								<option value="CB">CB (Center Back)</option>
								<option value="LB">LB (Left Back)</option>
								<option value="RB">RB (Right Back)</option>
								<option value="DM">DM (Defensive Mid)</option>
								<option value="CM">CM (Central Mid)</option>
								<option value="AM">AM (Attacking Mid)</option>
								<option value="LW">LW (Left Wing)</option>
								<option value="RW">RW (Right Wing)</option>
								<option value="ST">ST (Striker)</option>
							</select>
						</div>
					</div>
				</div>

				<div class="flex items-center justify-end gap-3 pt-3 border-t border-rule">
					<button type="button" onclick={() => (editingPlayer = null)} class="h-9 px-3 rounded-card text-xs font-semibold text-ink-2 hover:text-ink">Cancel</button>
					<button type="button" onclick={handleSavePlayerModal} class="h-9 px-4 rounded-card bg-accent hover:opacity-95 text-xs font-semibold text-accent-ink transition-opacity">
						Save player
					</button>
				</div>
			</div>
		</div>
	{/if}
</div>
