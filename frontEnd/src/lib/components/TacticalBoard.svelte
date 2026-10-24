<script lang="ts">
	import type { TacticalPlayerToken, TacticalAnnotation, Player } from '$lib/types/football';

	interface Props {
		lineup: TacticalPlayerToken[];
		annotations?: TacticalAnnotation[];
		squadPlayers?: Player[];
		readonly?: boolean;
		showGuides?: boolean;
		onchange?: () => void;
	}

	let {
		lineup = $bindable([]),
		annotations = $bindable([]),
		squadPlayers = [],
		readonly = false,
		showGuides = $bindable(true),
		onchange
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

	// Player editor modal state
	let editingPlayer = $state<TacticalPlayerToken | null>(null);
	let selectedRosterId = $state('');

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
					selectedRosterId = '';
				}
			}
		} else if (isDrawingVector && vectorStart && vectorCurrent) {
			// Add annotation if distance is noticeable
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

	function removeAnnotation(id: string) {
		annotations = annotations.filter((a) => a.id !== id);
		onchange?.();
	}

	function clearAllAnnotations() {
		annotations = [];
		onchange?.();
	}

	function handleSavePlayerModal() {
		if (!editingPlayer) return;
		const idx = lineup.findIndex((p) => p.id === editingPlayer?.id);
		if (idx !== -1) {
			lineup[idx] = { ...editingPlayer };
			onchange?.();
		}
		editingPlayer = null;
	}

	function handleRosterSelect(player: Player) {
		if (!editingPlayer) return;
		editingPlayer.name = player.name;
		editingPlayer.number = player.jersey_number;
		editingPlayer.role = player.position;
	}
</script>

<div class="space-y-3 select-none">
	{#if !readonly}
		<!-- Pitch Toolbar -->
		<div class="flex items-center justify-between gap-2 p-2 rounded-lg bg-[#0d1017] border border-[#1e2430] flex-wrap text-xs">
			<div class="flex items-center gap-1">
				<span class="text-gray-500 text-[10px] uppercase font-mono font-bold mr-1">Tool:</span>
				<button
					type="button"
					onclick={() => (activeTool = 'select')}
					class="px-2.5 py-1 rounded font-medium transition {activeTool === 'select' ? 'bg-white/20 text-white font-bold' : 'text-gray-400 hover:text-white'}"
				>
					✋ Move
				</button>
				<button
					type="button"
					onclick={() => (activeTool = 'run')}
					class="px-2.5 py-1 rounded font-medium transition {activeTool === 'run' ? 'bg-amber-500/20 text-amber-300 font-bold border border-amber-500/40' : 'text-gray-400 hover:text-white'}"
				>
					↗ Attacking Run
				</button>
				<button
					type="button"
					onclick={() => (activeTool = 'pass')}
					class="px-2.5 py-1 rounded font-medium transition {activeTool === 'pass' ? 'bg-emerald-500/20 text-emerald-300 font-bold border border-emerald-500/40' : 'text-gray-400 hover:text-white'}"
				>
					⤏ Pass
				</button>
				<button
					type="button"
					onclick={() => (activeTool = 'press')}
					class="px-2.5 py-1 rounded font-medium transition {activeTool === 'press' ? 'bg-rose-500/20 text-rose-300 font-bold border border-rose-500/40' : 'text-gray-400 hover:text-white'}"
				>
					⚡ Press
				</button>
			</div>

			<div class="flex items-center gap-2">
				<button
					type="button"
					onclick={() => (showGuides = !showGuides)}
					class="text-[11px] px-2 py-1 rounded text-gray-400 hover:text-white transition {showGuides ? 'text-amber-400' : ''}"
				>
					{showGuides ? 'Hide Zones' : 'Show Zones'}
				</button>
				{#if annotations.length > 0}
					<button
						type="button"
						onclick={clearAllAnnotations}
						class="text-[11px] px-2 py-1 rounded text-rose-400 hover:text-rose-300 hover:bg-rose-950/40 transition"
					>
						Clear Arrows ({annotations.length})
					</button>
				{/if}
			</div>
		</div>
	{/if}

	<!-- Pitch SVG Container -->
	<div class="relative w-full rounded-xl border-2 border-emerald-950 bg-[#061207] shadow-xl overflow-hidden touch-none">
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
				<!-- Arrow Marker: Run (Amber) -->
				<marker id="arrow-run" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">
					<path d="M 0 1.5 L 9 5 L 0 8.5 z" fill="#f59e0b" />
				</marker>
				<!-- Arrow Marker: Pass (Emerald) -->
				<marker id="arrow-pass" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">
					<path d="M 0 1.5 L 9 5 L 0 8.5 z" fill="#10b981" />
				</marker>
				<!-- Arrow Marker: Press (Rose) -->
				<marker id="arrow-press" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">
					<path d="M 0 1.5 L 9 5 L 0 8.5 z" fill="#f43f5e" />
				</marker>

				<!-- Field grass stripes -->
				<pattern id="stripes" width="100" height="680" patternUnits="userSpaceOnUse">
					<rect width="50" height="680" fill="#071708" />
					<rect x="50" width="50" height="680" fill="#061307" />
				</pattern>
			</defs>

			<!-- Grass background -->
			<rect width="1000" height="680" fill="url(#stripes)" />

			<!-- Pitch Markings (White with subtle opacity) -->
			<!-- Outer Boundary -->
			<rect x="30" y="30" width="940" height="620" fill="none" stroke="#22c55e" stroke-width="2.5" stroke-opacity="0.35" />

			<!-- Halfway Line -->
			<line x1="500" y1="30" x2="500" y2="650" stroke="#22c55e" stroke-width="2.5" stroke-opacity="0.35" />

			<!-- Center Circle & Spot -->
			<circle cx="500" cy="340" r="85" fill="none" stroke="#22c55e" stroke-width="2.5" stroke-opacity="0.35" />
			<circle cx="500" cy="340" r="4" fill="#22c55e" fill-opacity="0.5" />

			<!-- Left Penalty Box -->
			<rect x="30" y="165" width="165" height="350" fill="none" stroke="#22c55e" stroke-width="2.5" stroke-opacity="0.35" />
			<!-- Left 6-Yard Box -->
			<rect x="30" y="245" width="55" height="190" fill="none" stroke="#22c55e" stroke-width="2.5" stroke-opacity="0.35" />
			<!-- Left Penalty Spot & Arc -->
			<circle cx="140" cy="340" r="3.5" fill="#22c55e" fill-opacity="0.5" />
			<path d="M 195 290 A 85 85 0 0 1 195 390" fill="none" stroke="#22c55e" stroke-width="2.5" stroke-opacity="0.35" />

			<!-- Right Penalty Box -->
			<rect x="805" y="165" width="165" height="350" fill="none" stroke="#22c55e" stroke-width="2.5" stroke-opacity="0.35" />
			<!-- Right 6-Yard Box -->
			<rect x="915" y="245" width="55" height="190" fill="none" stroke="#22c55e" stroke-width="2.5" stroke-opacity="0.35" />
			<!-- Right Penalty Spot & Arc -->
			<circle cx="860" cy="340" r="3.5" fill="#22c55e" fill-opacity="0.5" />
			<path d="M 805 290 A 85 85 0 0 0 805 390" fill="none" stroke="#22c55e" stroke-width="2.5" stroke-opacity="0.35" />

			<!-- Tactical Guide Overlays (Half-spaces and thirds) -->
			{#if showGuides}
				<!-- Half-space channels -->
				<line x1="30" y1="204" x2="970" y2="204" stroke="#eab308" stroke-dasharray="4 6" stroke-width="1.5" stroke-opacity="0.25" />
				<line x1="30" y1="476" x2="970" y2="476" stroke="#eab308" stroke-dasharray="4 6" stroke-width="1.5" stroke-opacity="0.25" />

				<!-- Vertical Thirds (Defensive third, middle third, final third) -->
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
					<!-- Attacking Run: Solid Amber Arrow -->
					<line
						x1={x1}
						y1={y1}
						x2={x2}
						y2={y2}
						stroke="#f59e0b"
						stroke-width="3.5"
						stroke-linecap="round"
						marker-end="url(#arrow-run)"
					/>
				{:else if ann.type === 'pass'}
					<!-- Passing Channel: Dashed Emerald Arrow -->
					<line
						x1={x1}
						y1={y1}
						x2={x2}
						y2={y2}
						stroke="#10b981"
						stroke-width="3"
						stroke-dasharray="6 4"
						stroke-linecap="round"
						marker-end="url(#arrow-pass)"
					/>
				{:else if ann.type === 'press'}
					<!-- High Press: Rose Wavy / Distinct Arrow -->
					<line
						x1={x1}
						y1={y1}
						x2={x2}
						y2={y2}
						stroke="#f43f5e"
						stroke-width="3.5"
						stroke-dasharray="8 3"
						marker-end="url(#arrow-press)"
					/>
				{/if}
			{/each}

			<!-- Live Drawing Vector Preview -->
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
					stroke={activeTool === 'run' ? '#f59e0b' : activeTool === 'pass' ? '#10b981' : '#f43f5e'}
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
					class="transition-transform duration-75 {readonly ? '' : 'cursor-grab active:cursor-grabbing focus:outline-none'}"
					role="button"
					tabindex={readonly ? -1 : 0}
					aria-label="{player.name} #{player.number} {player.role}"
					onkeydown={(e) => {
						if (!readonly && (e.key === 'Enter' || e.key === ' ')) {
							editingPlayer = { ...player };
							selectedRosterId = '';
						}
					}}
					onpointerdown={(e) => {
						e.stopPropagation();
						handlePointerDown(e, player.id);
					}}
				>
					<!-- Glow ring when active -->
					{#if isDragging}
						<circle r="30" fill="none" stroke="#f59e0b" stroke-width="3" opacity="0.6" />
					{/if}

					<!-- Outer Token Circle -->
					<circle
						r="20"
						fill="#111827"
						stroke="#ef4444"
						stroke-width="3"
						class="filter drop-shadow-md"
					/>

					<!-- Player Jersey Number -->
					<text
						text-anchor="middle"
						dy="6"
						fill="#ffffff"
						font-size="14"
						font-weight="bold"
						font-family="monospace"
					>
						{player.number}
					</text>

					<!-- Player Name & Role Tag -->
					<g transform="translate(0, 32)">
						<rect
							x="-45"
							y="-10"
							width="90"
							height="18"
							rx="4"
							fill="#030712"
							fill-opacity="0.85"
							stroke="#1e2430"
						/>
						<text
							text-anchor="middle"
							dy="3"
							fill="#f3f4f6"
							font-size="10"
							font-weight="600"
							font-family="sans-serif"
						>
							{player.name} ({player.role})
						</text>
					</g>
				</g>
			{/each}
		</svg>
	</div>

	<!-- Quick Player Edit Modal (Opens on token tap/click) -->
	{#if editingPlayer}
		<div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
			<div class="bg-[#12161f] border border-[#1e2430] rounded-xl p-5 w-full max-w-sm space-y-4 shadow-2xl">
				<div class="flex items-center justify-between border-b border-[#1e2430] pb-2">
					<h3 class="text-sm font-bold text-white flex items-center gap-2">
						<span class="w-2.5 h-2.5 rounded-full bg-red-500"></span>
						Edit Player Token #{editingPlayer.number}
					</h3>
					<button
						type="button"
						onclick={() => (editingPlayer = null)}
						class="text-gray-400 hover:text-white text-xs"
					>
						✕
					</button>
				</div>

				{#if squadPlayers && squadPlayers.length > 0}
					<!-- Option 1: Select directly from live squad roster -->
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
							<option value="">-- Choose Club Player --</option>
							{#each squadPlayers as sp}
								<option value={sp.id}>
									#{sp.jersey_number} {sp.name} ({sp.position})
								</option>
							{/each}
						</select>
					</div>
					<div class="text-[10px] text-gray-500 font-mono text-center">or edit manually:</div>
				{/if}

				<!-- Option 2: Edit custom name / number / role directly -->
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
								<option value="LWB">LWB (Left Wingback)</option>
								<option value="RWB">RWB (Right Wingback)</option>
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
					<button
						type="button"
						onclick={() => (editingPlayer = null)}
						class="px-3 py-1.5 rounded text-xs text-gray-400 hover:text-white"
					>
						Cancel
					</button>
					<button
						type="button"
						onclick={handleSavePlayerModal}
						class="px-4 py-1.5 rounded-lg bg-red-600 hover:bg-red-500 text-xs font-bold text-white transition shadow-sm"
					>
						Save Player
					</button>
				</div>
			</div>
		</div>
	{/if}
</div>
