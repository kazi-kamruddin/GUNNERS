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

	// Interaction modes: 'select' (drag players) | 'run' | 'pass' | 'press'
	let activeTool = $state<'select' | 'run' | 'pass' | 'press'>('select');

	// SVG element reference
	let svgRef = $state<SVGSVGElement | null>(null);

	// Dragging player state
	let draggingPlayerId = $state<string | null>(null);
	let hasDragged = $state(false);

	// Drawing vector arrow state
	let isDrawingVector = $state(false);
	let vectorStart = $state<{ x: number; y: number } | null>(null);
	let vectorCurrent = $state<{ x: number; y: number } | null>(null);

	// Bench swap state
	let selectedBenchPlayerId = $state<string | null>(null);

	// Player editor modal state
	let editingPlayer = $state<TacticalPlayerToken | null>(null);
	let isEditingBench = $state(false);
	let selectedRosterId = $state('');
	let exportSuccessMessage = $state<string | null>(null);

	// Fallback baseline bench if empty
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

		// If a bench player is selected, clicking a starting XI player swaps them!
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

	function handlePointerUp(e: PointerEvent) {
		if (readonly) return;

		if (draggingPlayerId) {
			const pid = draggingPlayerId;
			draggingPlayerId = null;
			// If not dragged (just clicked), open player edit modal
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

			// Swap identities while preserving coordinates and pitch slot
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

	// Client-side Lineup Graphic Export via HTML5 Canvas
	function exportLineupAsImage() {
		try {
			const canvas = document.createElement('canvas');
			canvas.width = 1200;
			canvas.height = 850;
			const ctx = canvas.getContext('2d');
			if (!ctx) return;

			// 1. Pitch Grass Background
			ctx.fillStyle = '#061a09';
			ctx.fillRect(0, 0, 1200, 850);

			// Alternating turf stripes
			ctx.fillStyle = '#08210c';
			for (let x = 0; x < 1200; x += 100) {
				if ((x / 100) % 2 === 0) {
					ctx.fillRect(x, 0, 50, 850);
				}
			}

			// 2. White Pitch Boundary Markings
			ctx.strokeStyle = '#22c55e';
			ctx.lineWidth = 3;
			ctx.strokeRect(50, 60, 1100, 680);

			// Halfway Line
			ctx.beginPath();
			ctx.moveTo(600, 60);
			ctx.lineTo(600, 740);
			ctx.stroke();

			// Center Circle
			ctx.beginPath();
			ctx.arc(600, 400, 85, 0, Math.PI * 2);
			ctx.stroke();

			// Penalty Boxes
			ctx.strokeRect(50, 220, 180, 360);
			ctx.strokeRect(970, 220, 180, 360);

			// 3. Header Branding
			ctx.fillStyle = '#EF0107';
			ctx.fillRect(50, 10, 1100, 35);
			ctx.fillStyle = '#ffffff';
			ctx.font = 'bold 16px sans-serif';
			ctx.fillText('GUNNERS REBORN  •  ARSENAL MATCHDAY TACTICAL LINEUP', 70, 33);
			ctx.fillStyle = '#fef08a';
			ctx.font = 'bold 14px monospace';
			ctx.fillText(`FORMATION: ${formationName.toUpperCase()}`, 960, 33);

			// 4. Starting XI Player Tokens
			for (const p of lineup) {
				const px = 50 + (p.x / 100) * 1100;
				const py = 60 + (p.y / 100) * 680;

				// Token Circle (Arsenal Red & White)
				ctx.beginPath();
				ctx.arc(px, py, 24, 0, Math.PI * 2);
				ctx.fillStyle = '#EF0107';
				ctx.fill();
				ctx.lineWidth = 3;
				ctx.strokeStyle = '#ffffff';
				ctx.stroke();

				// Jersey Number
				ctx.fillStyle = '#ffffff';
				ctx.font = 'bold 16px monospace';
				ctx.textAlign = 'center';
				ctx.fillText(String(p.number), px, py + 6);

				// Player Name Tag
				ctx.fillStyle = '#0a0c10';
				ctx.fillRect(px - 55, py + 30, 110, 20);
				ctx.strokeStyle = '#9C824A';
				ctx.lineWidth = 1;
				ctx.strokeRect(px - 55, py + 30, 110, 20);

				ctx.fillStyle = '#ffffff';
				ctx.font = 'bold 11px sans-serif';
				ctx.fillText(`${p.name} (${p.role})`, px, py + 44);
			}

			// 5. Substitutes Bench Footer
			ctx.fillStyle = '#0d1017';
			ctx.fillRect(50, 760, 1100, 75);
			ctx.strokeStyle = '#1e2430';
			ctx.strokeRect(50, 760, 1100, 75);

			ctx.fillStyle = '#9C824A';
			ctx.font = 'bold 12px monospace';
			ctx.textAlign = 'left';
			ctx.fillText('BENCH:', 70, 802);

			let bx = 140;
			for (const bp of bench.slice(0, 8)) {
				ctx.fillStyle = '#ffffff';
				ctx.font = '11px sans-serif';
				ctx.fillText(`#${bp.number} ${bp.name}`, bx, 802);
				bx += 115;
			}

			// Trigger download
			const dataUrl = canvas.toDataURL('image/png');
			const link = document.createElement('a');
			link.download = `Arsenal_Tactical_Lineup_${Date.now()}.png`;
			link.href = dataUrl;
			link.click();

			exportSuccessMessage = 'Lineup exported as high-resolution PNG image!';
			setTimeout(() => {
				exportSuccessMessage = null;
			}, 4000);
		} catch (err) {
			console.error('Export failed:', err);
		}
	}
</script>

<div class="space-y-4 select-none">
	{#if exportSuccessMessage}
		<div class="p-3 rounded-lg bg-emerald-950/70 text-emerald-300 border border-emerald-800/40 text-xs font-mono flex items-center justify-between">
			<span>✓ {exportSuccessMessage}</span>
			<button type="button" onclick={() => (exportSuccessMessage = null)} class="text-emerald-400 hover:text-white">✕</button>
		</div>
	{/if}

	{#if !readonly}
		<!-- Pitch Toolbar -->
		<div class="flex items-center justify-between gap-3 p-3 rounded-xl bg-[#0d1017] border border-[#1e2430] flex-wrap text-xs">
			<!-- Drawing & Moving Tools -->
			<div class="flex items-center gap-1.5 flex-wrap">
				<span class="text-gray-500 text-[10px] uppercase font-mono font-bold mr-1">Controls:</span>
				<button
					type="button"
					onclick={() => (activeTool = 'select')}
					class="px-2.5 py-1 rounded font-medium transition {activeTool === 'select' ? 'bg-white/20 text-white font-bold' : 'text-gray-400 hover:text-white'}"
				>
					✋ Move Tokens
				</button>
				<button
					type="button"
					onclick={() => (activeTool = 'run')}
					class="px-2.5 py-1 rounded font-medium transition {activeTool === 'run' ? 'bg-amber-500/20 text-amber-300 font-bold border border-amber-500/40' : 'text-gray-400 hover:text-white'}"
				>
					↗ Run Vector
				</button>
				<button
					type="button"
					onclick={() => (activeTool = 'pass')}
					class="px-2.5 py-1 rounded font-medium transition {activeTool === 'pass' ? 'bg-emerald-500/20 text-emerald-300 font-bold border border-emerald-500/40' : 'text-gray-400 hover:text-white'}"
				>
					⤏ Pass Channel
				</button>
				<button
					type="button"
					onclick={() => (activeTool = 'press')}
					class="px-2.5 py-1 rounded font-medium transition {activeTool === 'press' ? 'bg-rose-500/20 text-rose-300 font-bold border border-rose-500/40' : 'text-gray-400 hover:text-white'}"
				>
					⚡ High Press
				</button>

				<!-- Fluid Movement Toggle -->
				<button
					type="button"
					onclick={() => (fluidMode = !fluidMode)}
					class="px-2.5 py-1 rounded font-mono text-[11px] transition border ml-2 {fluidMode ? 'bg-amber-500 text-black font-bold border-amber-400' : 'bg-[#12161f] text-gray-400 border-[#1e2430] hover:text-white'}"
					title="Fluid movement allows unconstrained dragging anywhere on pitch"
				>
					{fluidMode ? '✓ Fluid Free-Roam' : 'Preset Grid'}
				</button>
			</div>

			<!-- Actions: Export PNG, Clear, Share -->
			<div class="flex items-center gap-2">
				<button
					type="button"
					onclick={exportLineupAsImage}
					class="px-3 py-1.5 rounded-lg bg-red-600 hover:bg-red-500 text-white font-bold text-xs transition flex items-center gap-1.5 shadow-sm"
					title="Download high-resolution lineup graphic"
				>
					<span>📷</span>
					<span>Export Image (PNG)</span>
				</button>

				{#if onshare}
					<button
						type="button"
						onclick={onshare}
						class="px-3 py-1.5 rounded-lg bg-amber-500/20 hover:bg-amber-500 text-amber-300 hover:text-black font-semibold text-xs transition border border-amber-500/30"
					>
						Share to Terrace
					</button>
				{/if}

				{#if annotations.length > 0}
					<button
						type="button"
						onclick={clearAllAnnotations}
						class="text-[11px] px-2 py-1 rounded text-rose-400 hover:text-rose-300 transition"
					>
						Clear Arrows
					</button>
				{/if}
			</div>
		</div>
	{/if}

	<!-- Pitch SVG Container -->
	<div class="relative w-full rounded-2xl border-2 border-emerald-950 bg-[#061207] shadow-2xl overflow-hidden touch-none">
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
					<path d="M 0 1.5 L 9 5 L 0 8.5 z" fill="#f59e0b" />
				</marker>
				<marker id="arrow-pass" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">
					<path d="M 0 1.5 L 9 5 L 0 8.5 z" fill="#10b981" />
				</marker>
				<marker id="arrow-press" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">
					<path d="M 0 1.5 L 9 5 L 0 8.5 z" fill="#f43f5e" />
				</marker>

				<pattern id="stripes" width="100" height="680" patternUnits="userSpaceOnUse">
					<rect width="50" height="680" fill="#071708" />
					<rect x="50" width="50" height="680" fill="#061307" />
				</pattern>
			</defs>

			<!-- Grass background -->
			<rect width="1000" height="680" fill="url(#stripes)" />

			<!-- Pitch Markings -->
			<rect x="30" y="30" width="940" height="620" fill="none" stroke="#22c55e" stroke-width="2.5" stroke-opacity="0.35" />
			<line x1="500" y1="30" x2="500" y2="650" stroke="#22c55e" stroke-width="2.5" stroke-opacity="0.35" />
			<circle cx="500" cy="340" r="85" fill="none" stroke="#22c55e" stroke-width="2.5" stroke-opacity="0.35" />
			<circle cx="500" cy="340" r="4" fill="#22c55e" fill-opacity="0.5" />

			<rect x="30" y="165" width="165" height="350" fill="none" stroke="#22c55e" stroke-width="2.5" stroke-opacity="0.35" />
			<rect x="30" y="245" width="55" height="190" fill="none" stroke="#22c55e" stroke-width="2.5" stroke-opacity="0.35" />
			<circle cx="140" cy="340" r="3.5" fill="#22c55e" fill-opacity="0.5" />
			<path d="M 195 290 A 85 85 0 0 1 195 390" fill="none" stroke="#22c55e" stroke-width="2.5" stroke-opacity="0.35" />

			<rect x="805" y="165" width="165" height="350" fill="none" stroke="#22c55e" stroke-width="2.5" stroke-opacity="0.35" />
			<rect x="915" y="245" width="55" height="190" fill="none" stroke="#22c55e" stroke-width="2.5" stroke-opacity="0.35" />
			<circle cx="860" cy="340" r="3.5" fill="#22c55e" fill-opacity="0.5" />
			<path d="M 805 290 A 85 85 0 0 0 805 390" fill="none" stroke="#22c55e" stroke-width="2.5" stroke-opacity="0.35" />

			{#if showGuides}
				<line x1="30" y1="204" x2="970" y2="204" stroke="#eab308" stroke-dasharray="4 6" stroke-width="1.5" stroke-opacity="0.25" />
				<line x1="30" y1="476" x2="970" y2="476" stroke="#eab308" stroke-dasharray="4 6" stroke-width="1.5" stroke-opacity="0.25" />
				<line x1="343" y1="30" x2="343" y2="650" stroke="#38bdf8" stroke-dasharray="4 6" stroke-width="1.5" stroke-opacity="0.2" />
				<line x1="657" y1="30" x2="657" y2="650" stroke="#38bdf8" stroke-dasharray="4 6" stroke-width="1.5" stroke-opacity="0.2" />
			{/if}

			<!-- Vector Annotations Layer -->
			{#each annotations as ann (ann.id)}
				{@const x1 = (ann.from_x / 100) * 1000}
				{@const y1 = (ann.from_y / 100) * 680}
				{@const x2 = (ann.to_x / 100) * 1000}
				{@const y2 = (ann.to_y / 100) * 680}
				{#if ann.type === 'run'}
					<line x1={x1} y1={y1} x2={x2} y2={y2} stroke="#f59e0b" stroke-width="3.5" stroke-linecap="round" marker-end="url(#arrow-run)" />
				{:else if ann.type === 'pass'}
					<line x1={x1} y1={y1} x2={x2} y2={y2} stroke="#10b981" stroke-width="3" stroke-dasharray="6 4" stroke-linecap="round" marker-end="url(#arrow-pass)" />
				{:else if ann.type === 'press'}
					<line x1={x1} y1={y1} x2={x2} y2={y2} stroke="#f43f5e" stroke-width="3.5" stroke-dasharray="8 3" marker-end="url(#arrow-press)" />
				{/if}
			{/each}

			{#if isDrawingVector && vectorStart && vectorCurrent}
				{@const sx = (vectorStart.x / 100) * 1000}
				{@const sy = (vectorStart.y / 100) * 680}
				{@const cx = (vectorCurrent.x / 100) * 1000}
				{@const cy = (vectorCurrent.y / 100) * 680}
				<line x1={sx} y1={sy} x2={cx} y2={cy} stroke={activeTool === 'run' ? '#f59e0b' : activeTool === 'pass' ? '#10b981' : '#f43f5e'} stroke-width="3" stroke-dasharray="4 4" opacity="0.8" />
			{/if}

			<!-- Player Tokens Layer -->
			{#each lineup as player (player.id)}
				{@const px = (player.x / 100) * 1000}
				{@const py = (player.y / 100) * 680}
				{@const isDragging = draggingPlayerId === player.id}
				<g
					transform="translate({px}, {py})"
					class="transition-transform duration-75 {readonly ? '' : 'cursor-grab active:cursor-grabbing focus:outline-none'}"
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
						<circle r="30" fill="none" stroke={selectedBenchPlayerId ? '#10b981' : '#f59e0b'} stroke-width="3" opacity="0.7" stroke-dasharray={selectedBenchPlayerId ? '4 2' : 'none'} />
					{/if}

					<!-- Outer Arsenal Crest/Jersey Circle -->
					<circle r="22" fill="#EF0107" stroke="#ffffff" stroke-width="3" class="filter drop-shadow-md" />

					<!-- Jersey Number -->
					<text text-anchor="middle" dy="6" fill="#ffffff" font-size="14" font-weight="bold" font-family="monospace">
						{player.number}
					</text>

					<!-- Player Name & Role Tag -->
					<g transform="translate(0, 32)">
						<rect x="-48" y="-10" width="96" height="20" rx="4" fill="#030712" fill-opacity="0.9" stroke="#9C824A" stroke-width="1" />
						<text text-anchor="middle" dy="4" fill="#f3f4f6" font-size="10" font-weight="bold" font-family="sans-serif">
							{player.name} ({player.role})
						</text>
					</g>
				</g>
			{/each}
		</svg>
	</div>

	<!-- Substitutes Bench Pool (The Dugout) -->
	{#if bench && bench.length > 0}
		<div class="p-4 rounded-xl border border-[#1e2430] bg-[#0d1017] space-y-2.5">
			<div class="flex items-center justify-between">
				<div class="flex items-center gap-2">
					<span class="w-2 h-2 rounded-full bg-amber-400"></span>
					<span class="text-xs font-bold text-white uppercase tracking-wider font-mono">
						Substitutes Bench ({bench.length} players)
					</span>
				</div>
				<span class="text-[11px] text-gray-500 font-mono">
					{selectedBenchPlayerId ? '👉 Click any starting player on the pitch to swap!' : 'Click a bench player to swap into Starting XI'}
				</span>
			</div>

			<div class="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-8 gap-2">
				{#each bench as bPlayer}
					{@const isSelected = selectedBenchPlayerId === bPlayer.id}
					<button
						type="button"
						onclick={() => {
							if (readonly) return;
							selectedBenchPlayerId = isSelected ? null : bPlayer.id;
						}}
						class="p-2 rounded-lg border transition text-center flex flex-col items-center justify-center gap-1 {isSelected ? 'bg-amber-500/20 border-amber-400 text-amber-300' : 'bg-[#12161f] border-[#1e2430] text-gray-300 hover:border-gray-500'}"
					>
						<span class="w-6 h-6 rounded-full bg-red-950 text-red-400 border border-red-800 font-mono text-xs font-bold flex items-center justify-center">
							{bPlayer.number}
						</span>
						<span class="text-xs font-bold truncate max-w-[80px]">{bPlayer.name}</span>
						<span class="text-[9px] text-gray-500 font-mono uppercase">{bPlayer.role}</span>
					</button>
				{/each}
			</div>
		</div>
	{/if}

	<!-- Quick Player Edit Modal -->
	{#if editingPlayer}
		<div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
			<div class="bg-[#12161f] border border-[#1e2430] rounded-xl p-5 w-full max-w-sm space-y-4 shadow-2xl">
				<div class="flex items-center justify-between border-b border-[#1e2430] pb-2">
					<h3 class="text-sm font-bold text-white flex items-center gap-2">
						<span class="w-2.5 h-2.5 rounded-full bg-red-500"></span>
						Edit #{editingPlayer.number} {editingPlayer.name}
					</h3>
					<button type="button" onclick={() => (editingPlayer = null)} class="text-gray-400 hover:text-white text-xs">✕</button>
				</div>

				{#if squadPlayers && squadPlayers.length > 0}
					<div class="space-y-1">
						<label for="roster-select" class="text-[11px] font-mono text-gray-400 uppercase font-semibold">
							Select From Squad Roster:
						</label>
						<select
							id="roster-select"
							bind:value={selectedRosterId}
							onchange={() => {
								const selected = squadPlayers.find((p) => p.id === selectedRosterId);
								if (selected) handleRosterSelect(selected);
							}}
							class="w-full bg-[#0a0c10] border border-[#1e2430] rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-red-500"
						>
							<option value="">-- Choose Arsenal Player --</option>
							{#each squadPlayers as sp}
								<option value={sp.id}>
									#{sp.jersey_number} {sp.name} ({sp.position})
								</option>
							{/each}
						</select>
					</div>
					<div class="text-[10px] text-gray-500 font-mono text-center">or customize:</div>
				{/if}

				<div class="space-y-3">
					<div>
						<label for="player-name" class="text-[11px] font-mono text-gray-400 uppercase font-semibold">Name</label>
						<input
							id="player-name"
							type="text"
							bind:value={editingPlayer.name}
							class="w-full bg-[#0a0c10] border border-[#1e2430] rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-red-500 mt-1"
						/>
					</div>

					<div class="grid grid-cols-2 gap-2">
						<div>
							<label for="player-number" class="text-[11px] font-mono text-gray-400 uppercase font-semibold">Jersey #</label>
							<input
								id="player-number"
								type="number"
								min="1"
								max="99"
								bind:value={editingPlayer.number}
								class="w-full bg-[#0a0c10] border border-[#1e2430] rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-red-500 mt-1"
							/>
						</div>
						<div>
							<label for="player-role" class="text-[11px] font-mono text-gray-400 uppercase font-semibold">Role</label>
							<select
								id="player-role"
								bind:value={editingPlayer.role}
								class="w-full bg-[#0a0c10] border border-[#1e2430] rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-red-500 mt-1"
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

				<div class="flex items-center justify-end gap-2 pt-2 border-t border-[#1e2430]">
					<button type="button" onclick={() => (editingPlayer = null)} class="px-3 py-1.5 rounded text-xs text-gray-400 hover:text-white">Cancel</button>
					<button type="button" onclick={handleSavePlayerModal} class="px-4 py-1.5 rounded-lg bg-red-600 hover:bg-red-500 text-xs font-bold text-white transition shadow-sm">
						Save Player
					</button>
				</div>
			</div>
		</div>
	{/if}
</div>
