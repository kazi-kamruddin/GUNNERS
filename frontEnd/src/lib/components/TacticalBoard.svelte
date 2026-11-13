<script lang="ts">
	import { untrack } from 'svelte';
	import { focusTrap } from '$lib/actions/focusTrap';
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

	const DEFAULT_BENCH_POOL: TacticalPlayerToken[] = [
		{ id: 'b1', name: 'Kepa', number: 13, role: 'GK', x: 0, y: 0 },
		{ id: 'b2', name: 'Meslier', number: 30, role: 'GK', x: 0, y: 0 },
		{ id: 'b3', name: 'White', number: 4, role: 'RB', x: 0, y: 0 },
		{ id: 'b4', name: 'Mosquera', number: 3, role: 'CB', x: 0, y: 0 },
		{ id: 'b5', name: 'Hincapié', number: 5, role: 'CB', x: 0, y: 0 },
		{ id: 'b6', name: 'Konsa', number: 15, role: 'CB', x: 0, y: 0 },
		{ id: 'b7', name: 'Merino', number: 23, role: 'CM', x: 0, y: 0 },
		{ id: 'b8', name: 'Bruno G.', number: 39, role: 'CM', x: 0, y: 0 },
		{ id: 'b9', name: 'Madueke', number: 20, role: 'RW', x: 0, y: 0 },
		{ id: 'b10', name: 'Havertz', number: 29, role: 'ST', x: 0, y: 0 },
		{ id: 'b11', name: 'Lewis-Skelly', number: 49, role: 'CM', x: 0, y: 0 },
		{ id: 'b12', name: 'Dowman', number: 56, role: 'AM', x: 0, y: 0 }
	];

	function mapPositionToRole(position: string, existingRole?: string): string {
		if (position === 'Goalkeeper') return 'GK';
		if (position === 'Defender') {
			return existingRole && ['CB', 'LB', 'RB', 'LWB', 'RWB'].includes(existingRole) ? existingRole : 'CB';
		}
		if (position === 'Midfielder') {
			return existingRole && ['DM', 'CM', 'AM', 'LM', 'RM'].includes(existingRole) ? existingRole : 'CM';
		}
		if (position === 'Attacker') {
			return existingRole && ['LW', 'RW', 'ST', 'CF'].includes(existingRole) ? existingRole : 'ST';
		}
		return existingRole || 'CM';
	}

	function shortSquadName(fullName: string): string {
		const parts = fullName.trim().split(/\s+/);
		return parts.length > 1 ? parts[parts.length - 1] : fullName;
	}

	function buildInitialBench(currentLineup: TacticalPlayerToken[], roster: Player[]): TacticalPlayerToken[] {
		const starterNames = new Set(currentLineup.map((p) => p.name.trim().toLowerCase()));
		const starterNums = new Set(currentLineup.map((p) => p.number));

		if (roster && roster.length > 0) {
			const derived: TacticalPlayerToken[] = [];
			for (const p of roster) {
				const last = shortSquadName(p.name).toLowerCase();
				const full = p.name.trim().toLowerCase();
				if (starterNames.has(last) || starterNames.has(full) || starterNums.has(p.jersey_number)) {
					continue;
				}
				derived.push({
					id: `b_${p.id}`,
					name: shortSquadName(p.name),
					number: p.jersey_number,
					role: mapPositionToRole(p.position),
					x: 0,
					y: 0
				});
				if (derived.length >= 8) break;
			}
			if (derived.length >= 4) return derived;
		}

		const filtered = DEFAULT_BENCH_POOL.filter(
			(bp) => !starterNames.has(bp.name.toLowerCase()) && !starterNums.has(bp.number)
		);
		return (filtered.length >= 8 ? filtered : DEFAULT_BENCH_POOL).slice(0, 8);
	}

	let activeTool = $state<'select' | 'run' | 'pass' | 'press'>('select');
	let svgRef = $state<SVGSVGElement | null>(null);
	let draggingPlayerId = $state<string | null>(null);
	let dragStartCoords = $state<{ x: number; y: number } | null>(null);
	let hasDragged = $state(false);
	let isDrawingVector = $state(false);
	let vectorStart = $state<{ x: number; y: number } | null>(null);
	let vectorCurrent = $state<{ x: number; y: number } | null>(null);
	let selectedBenchPlayerId = $state<string | null>(null);
	let editingPlayer = $state<TacticalPlayerToken | null>(null);
	let isEditingBench = $state(false);
	let selectedRosterId = $state('');
	let exportSuccessMessage = $state<string | null>(null);
	let modalErrorMessage = $state<string | null>(null);

	let fluidModeLabel = $derived(fluidMode ? 'Fluid free-roam' : 'Preset grid');
	let benchInstruction = $derived(
		selectedBenchPlayerId
			? 'Click or press Enter on a starting player to complete the swap (Escape to cancel)'
			: 'Select a bench player to swap into the starting eleven'
	);

	// Seed default bench synchronously for SSR when interactive & empty
	if (untrack(() => !readonly && bench.length === 0)) {
		bench = untrack(() => buildInitialBench(lineup, squadPlayers));
	}

	$effect(() => {
		if (!readonly && bench.length === 0) {
			bench = buildInitialBench(lineup, squadPlayers);
		}
	});

	function getPitchCoords(e: PointerEvent): { x: number; y: number } | null {
		if (!svgRef) return null;
		const rect = svgRef.getBoundingClientRect();
		if (rect.width <= 0 || rect.height <= 0) return null;
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
			dragStartCoords = getPitchCoords(e);
			const targetEl = e.currentTarget as Element | null;
			targetEl?.setPointerCapture?.(e.pointerId);
		} else if (activeTool !== 'select') {
			const pt = getPitchCoords(e);
			if (pt) {
				isDrawingVector = true;
				vectorStart = pt;
				vectorCurrent = pt;
				const svgTarget = e.currentTarget as Element | null;
				svgTarget?.setPointerCapture?.(e.pointerId);
			}
		}
	}

	function handlePointerMove(e: PointerEvent) {
		if (readonly) return;

		if (draggingPlayerId) {
			const pt = getPitchCoords(e);
			if (!pt) return;
			if (!hasDragged && dragStartCoords) {
				const delta = Math.hypot(pt.x - dragStartCoords.x, pt.y - dragStartCoords.y);
				if (delta < 0.8) {
					return;
				}
			}
			hasDragged = true;
			const idx = lineup.findIndex((p) => p.id === draggingPlayerId);
			if (idx !== -1) {
				lineup[idx].x = pt.x;
				lineup[idx].y = pt.y;
				onchange?.();
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
			const didDrag = hasDragged;
			draggingPlayerId = null;
			dragStartCoords = null;
			hasDragged = false;
			if (!didDrag) {
				const player = lineup.find((p) => p.id === pid);
				if (player) {
					editingPlayer = { ...player };
					isEditingBench = false;
					selectedRosterId = '';
					modalErrorMessage = null;
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

	function handlePointerCancel() {
		draggingPlayerId = null;
		dragStartCoords = null;
		hasDragged = false;
		isDrawingVector = false;
		vectorStart = null;
		vectorCurrent = null;
	}

	function handleTokenKeydown(e: KeyboardEvent, player: TacticalPlayerToken) {
		if (readonly) return;

		if (e.key === 'Escape' && selectedBenchPlayerId) {
			e.preventDefault();
			selectedBenchPlayerId = null;
			return;
		}

		if (e.key === 'Enter' || e.key === ' ') {
			e.preventDefault();
			if (selectedBenchPlayerId) {
				swapBenchWithStarting(selectedBenchPlayerId, player.id);
				return;
			}
			editingPlayer = { ...player };
			isEditingBench = false;
			selectedRosterId = '';
			modalErrorMessage = null;
			return;
		}

		const step = e.shiftKey ? 5 : 2;
		let dx = 0;
		let dy = 0;
		if (e.key === 'ArrowLeft') dx = -step;
		else if (e.key === 'ArrowRight') dx = step;
		else if (e.key === 'ArrowUp') dy = -step;
		else if (e.key === 'ArrowDown') dy = step;

		if (dx !== 0 || dy !== 0) {
			e.preventDefault();
			const idx = lineup.findIndex((p) => p.id === player.id);
			if (idx !== -1) {
				lineup[idx].x = Math.max(2, Math.min(98, Math.round((lineup[idx].x + dx) * 10) / 10));
				lineup[idx].y = Math.max(2, Math.min(98, Math.round((lineup[idx].y + dy) * 10) / 10));
				onchange?.();
			}
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

	function undoLastAnnotation() {
		if (annotations.length === 0) return;
		annotations = annotations.slice(0, -1);
		onchange?.();
	}

	function clearAllAnnotations() {
		annotations = [];
		onchange?.();
	}

	function handleSavePlayerModal() {
		if (!editingPlayer) return;
		const cleanName = editingPlayer.name.trim();
		if (!cleanName) {
			modalErrorMessage = 'Player name cannot be empty.';
			return;
		}
		const clampedNumber = Math.max(1, Math.min(99, Math.round(Number(editingPlayer.number) || 1)));
		const updated: TacticalPlayerToken = {
			...editingPlayer,
			name: cleanName,
			number: clampedNumber
		};

		if (isEditingBench) {
			const idx = bench.findIndex((p) => p.id === updated.id);
			if (idx !== -1) {
				bench[idx] = updated;
				onchange?.();
			}
		} else {
			const idx = lineup.findIndex((p) => p.id === updated.id);
			if (idx !== -1) {
				lineup[idx] = updated;
				onchange?.();
			}
		}
		modalErrorMessage = null;
		editingPlayer = null;
	}

	function handleRosterSelect(player: Player) {
		if (!editingPlayer) return;
		editingPlayer.name = shortSquadName(player.name);
		editingPlayer.number = player.jersey_number;
		editingPlayer.role = mapPositionToRole(player.position, editingPlayer.role);
		modalErrorMessage = null;
	}

	function drawArrowOnCanvas(
		ctx: CanvasRenderingContext2D,
		x1: number,
		y1: number,
		x2: number,
		y2: number,
		color: string,
		dash: number[],
		lineWidth: number
	) {
		ctx.save();
		ctx.strokeStyle = color;
		ctx.fillStyle = color;
		ctx.lineWidth = lineWidth;
		ctx.lineCap = 'round';
		ctx.setLineDash(dash);

		ctx.beginPath();
		ctx.moveTo(x1, y1);
		ctx.lineTo(x2, y2);
		ctx.stroke();

		const angle = Math.atan2(y2 - y1, x2 - x1);
		const headLen = 14;
		ctx.setLineDash([]);
		ctx.beginPath();
		ctx.moveTo(x2, y2);
		ctx.lineTo(x2 - headLen * Math.cos(angle - Math.PI / 6), y2 - headLen * Math.sin(angle - Math.PI / 6));
		ctx.lineTo(x2 - headLen * Math.cos(angle + Math.PI / 6), y2 - headLen * Math.sin(angle + Math.PI / 6));
		ctx.closePath();
		ctx.fill();
		ctx.restore();
	}

	function exportLineupAsImage() {
		try {
			const canvas = document.createElement('canvas');
			canvas.width = 680;
			canvas.height = 1120;
			const ctx = canvas.getContext('2d');
			if (!ctx) return;

			const styles = getComputedStyle(document.documentElement);
			const paperColor = styles.getPropertyValue('--color-paper').trim() || '#140f0e';
			const paper2Color = styles.getPropertyValue('--color-paper-2').trim() || '#1d1614';
			const ruleColor = styles.getPropertyValue('--color-rule-2').trim() || '#443532';
			const inkColor = styles.getPropertyValue('--color-ink').trim() || '#f3eee8';
			const accentColor = styles.getPropertyValue('--color-accent').trim() || '#c72a25';
			const goldColor = styles.getPropertyValue('--color-accent-2').trim() || '#d5b263';
			const successColor = styles.getPropertyValue('--color-success').trim() || '#3fb970';
			const errorColor = styles.getPropertyValue('--color-error').trim() || '#e45c50';
			const pitchColor = styles.getPropertyValue('--color-pitch').trim() || '#173822';
			const pitch2Color = styles.getPropertyValue('--color-pitch-2').trim() || '#14321e';

			ctx.fillStyle = paperColor;
			ctx.fillRect(0, 0, 680, 1120);

			ctx.fillStyle = pitchColor;
			ctx.fillRect(30, 60, 620, 900);

			ctx.fillStyle = pitch2Color;
			for (let y = 60; y < 960; y += 90) {
				ctx.fillRect(30, y, 620, 45);
			}

			ctx.strokeStyle = successColor;
			ctx.globalAlpha = 0.45;
			ctx.lineWidth = 3;
			ctx.strokeRect(30, 60, 620, 900);

			ctx.beginPath();
			ctx.moveTo(30, 510);
			ctx.lineTo(650, 510);
			ctx.stroke();

			ctx.beginPath();
			ctx.arc(340, 510, 80, 0, Math.PI * 2);
			ctx.stroke();

			// Top (Opponent) & Bottom (Arsenal) penalty boxes
			ctx.strokeRect(165, 60, 350, 155);
			ctx.strokeRect(165, 805, 350, 155);
			ctx.globalAlpha = 1;

			// Top Banner
			ctx.fillStyle = accentColor;
			ctx.fillRect(30, 12, 620, 38);
			ctx.fillStyle = inkColor;
			ctx.font = 'bold 14px sans-serif';
			ctx.textAlign = 'left';
			ctx.fillText('GUNNERS : ARSENAL LINEUP', 46, 36);

			ctx.fillStyle = goldColor;
			ctx.font = 'bold 12px monospace';
			ctx.textAlign = 'right';
			ctx.fillText(formationName.toUpperCase(), 634, 35, 260);

			// Tactical Vector Annotations
			for (const ann of annotations) {
				const x1 = 30 + (ann.from_x / 100) * 620;
				const y1 = 60 + (ann.from_y / 100) * 900;
				const x2 = 30 + (ann.to_x / 100) * 620;
				const y2 = 60 + (ann.to_y / 100) * 900;
				if (ann.type === 'run') {
					drawArrowOnCanvas(ctx, x1, y1, x2, y2, goldColor, [], 4);
				} else if (ann.type === 'pass') {
					drawArrowOnCanvas(ctx, x1, y1, x2, y2, successColor, [10, 6], 3.5);
				} else if (ann.type === 'press') {
					drawArrowOnCanvas(ctx, x1, y1, x2, y2, errorColor, [12, 5], 4);
				}
			}

			// Player Tokens
			for (const p of lineup) {
				const px = 30 + (p.x / 100) * 620;
				const py = 60 + (p.y / 100) * 900;

				ctx.beginPath();
				ctx.arc(px, py, 22, 0, Math.PI * 2);
				ctx.fillStyle = accentColor;
				ctx.fill();
				ctx.lineWidth = 3;
				ctx.strokeStyle = inkColor;
				ctx.stroke();

				ctx.fillStyle = inkColor;
				ctx.font = 'bold 15px monospace';
				ctx.textAlign = 'center';
				ctx.fillText(String(p.number), px, py + 5);

				ctx.fillStyle = paperColor;
				ctx.fillRect(px - 58, py + 28, 116, 20);
				ctx.strokeStyle = goldColor;
				ctx.lineWidth = 1;
				ctx.strokeRect(px - 58, py + 28, 116, 20);

				ctx.fillStyle = inkColor;
				ctx.font = 'bold 10px sans-serif';
				ctx.fillText(`${p.name} (${p.role})`, px, py + 42, 110);
			}

			// Substitutes Bench Bar
			ctx.fillStyle = paper2Color;
			ctx.fillRect(30, 976, 620, 128);
			ctx.strokeStyle = ruleColor;
			ctx.lineWidth = 1.5;
			ctx.strokeRect(30, 976, 620, 128);

			ctx.fillStyle = goldColor;
			ctx.font = 'bold 11px monospace';
			ctx.textAlign = 'left';
			ctx.fillText('SUBSTITUTES:', 46, 1002);

			const benchSlice = bench.slice(0, 8);
			benchSlice.forEach((bp, idx) => {
				const col = idx % 2;
				const row = Math.floor(idx / 2);
				const bx = 46 + col * 300;
				const by = 1026 + row * 22;
				ctx.fillStyle = inkColor;
				ctx.font = '12px sans-serif';
				ctx.fillText(`#${bp.number} ${bp.name} (${bp.role})`, bx, by, 285);
			});

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

	function displayTokenLabel(p: TacticalPlayerToken): string {
		const raw = `${p.name} (${p.role})`;
		return raw.length > 18 ? `${p.name.slice(0, 11)}… (${p.role})` : raw;
	}
</script>

<div class="space-y-6 select-none">
	{#if exportSuccessMessage}
		<div
			role="status"
			class="p-3 rounded-card bg-paper-2 text-success border border-rule text-xs flex items-center justify-between gap-3"
		>
			<span>{exportSuccessMessage}</span>
			<button
				type="button"
				onclick={() => (exportSuccessMessage = null)}
				class="min-h-[44px] px-2 text-muted hover:text-ink transition-colors font-semibold"
			>
				Close
			</button>
		</div>
	{/if}

	<!-- Main Pitch (70% left, vertical) + Substitutes (30% right) -->
	<div class="grid grid-cols-1 lg:grid-cols-10 gap-6 items-start">
		<!-- Left: Vertical Pitch SVG Container (70% width) -->
		<div
			class="{!readonly && bench && bench.length > 0 ? 'lg:col-span-7' : 'lg:col-span-10'} relative w-full rounded-card border border-rule bg-pitch overflow-hidden {!readonly && (activeTool !== 'select' || draggingPlayerId !== null) ? 'touch-none' : 'touch-pan-y'}"
		>
			<svg
				bind:this={svgRef}
				viewBox="0 0 680 960"
				class="w-full max-w-[470px] aspect-[680/960] mx-auto block {readonly ? '' : activeTool === 'select' ? 'cursor-default' : 'cursor-crosshair'}"
				role={readonly ? 'img' : 'group'}
				aria-label="Arsenal vertical tactical pitch diagram (opponent goal at top, Arsenal goal at bottom)"
				onpointerdown={(e) => handlePointerDown(e)}
				onpointermove={handlePointerMove}
				onpointerup={handlePointerUp}
				onpointercancel={handlePointerCancel}
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

					<pattern id="stripes" width="680" height="96" patternUnits="userSpaceOnUse">
						<rect width="680" height="48" fill="var(--color-pitch)" />
						<rect y="48" width="680" height="48" fill="var(--color-pitch-2)" />
					</pattern>
				</defs>

				<!-- Grass background -->
				<rect width="680" height="960" fill="url(#stripes)" />

				<!-- Vertical Pitch Markings (Opponent goal at top, Arsenal goal at bottom) -->
				<rect x="30" y="30" width="620" height="900" fill="none" stroke="var(--color-success)" stroke-width="2.5" stroke-opacity="0.35" />
				<line x1="30" y1="480" x2="650" y2="480" stroke="var(--color-success)" stroke-width="2.5" stroke-opacity="0.35" />
				<circle cx="340" cy="480" r="80" fill="none" stroke="var(--color-success)" stroke-width="2.5" stroke-opacity="0.35" />
				<circle cx="340" cy="480" r="4" fill="var(--color-success)" fill-opacity="0.5" />

				<!-- Top (Opponent) Goal & Penalty Area -->
				<rect x="285" y="14" width="110" height="16" fill="none" stroke="var(--color-ink-2)" stroke-width="2" stroke-opacity="0.45" />
				<rect x="165" y="30" width="350" height="160" fill="none" stroke="var(--color-success)" stroke-width="2.5" stroke-opacity="0.35" />
				<rect x="245" y="30" width="190" height="55" fill="none" stroke="var(--color-success)" stroke-width="2.5" stroke-opacity="0.35" />
				<circle cx="340" cy="138" r="3.5" fill="var(--color-success)" fill-opacity="0.5" />
				<path d="M 285 190 A 80 80 0 0 0 395 190" fill="none" stroke="var(--color-success)" stroke-width="2.5" stroke-opacity="0.35" />

				<!-- Bottom (Arsenal) Goal & Penalty Area -->
				<rect x="285" y="930" width="110" height="16" fill="none" stroke="var(--color-accent-2)" stroke-width="2.5" stroke-opacity="0.7" />
				<rect x="165" y="770" width="350" height="160" fill="none" stroke="var(--color-success)" stroke-width="2.5" stroke-opacity="0.35" />
				<rect x="245" y="875" width="190" height="55" fill="none" stroke="var(--color-success)" stroke-width="2.5" stroke-opacity="0.35" />
				<circle cx="340" cy="822" r="3.5" fill="var(--color-success)" fill-opacity="0.5" />
				<path d="M 285 770 A 80 80 0 0 1 395 770" fill="none" stroke="var(--color-success)" stroke-width="2.5" stroke-opacity="0.35" />

				{#if showGuides}
					<line x1="30" y1="330" x2="650" y2="330" stroke="var(--color-accent-2)" stroke-dasharray="4 6" stroke-width="1.5" stroke-opacity="0.25" />
					<line x1="30" y1="630" x2="650" y2="630" stroke="var(--color-accent-2)" stroke-dasharray="4 6" stroke-width="1.5" stroke-opacity="0.25" />
					<line x1="236" y1="30" x2="236" y2="930" stroke="var(--color-ink-2)" stroke-dasharray="4 6" stroke-width="1.5" stroke-opacity="0.2" />
					<line x1="444" y1="30" x2="444" y2="930" stroke="var(--color-ink-2)" stroke-dasharray="4 6" stroke-width="1.5" stroke-opacity="0.2" />
				{/if}

				<!-- Vector Annotations Layer -->
				{#each annotations as ann (ann.id)}
					{@const x1 = (ann.from_x / 100) * 680}
					{@const y1 = (ann.from_y / 100) * 960}
					{@const x2 = (ann.to_x / 100) * 680}
					{@const y2 = (ann.to_y / 100) * 960}
					{#if ann.type === 'run'}
						<line x1={x1} y1={y1} x2={x2} y2={y2} stroke="var(--color-accent-2)" stroke-width="3.5" stroke-linecap="round" marker-end="url(#arrow-run)" />
					{:else if ann.type === 'pass'}
						<line x1={x1} y1={y1} x2={x2} y2={y2} stroke="var(--color-success)" stroke-width="3" stroke-dasharray="6 4" stroke-linecap="round" marker-end="url(#arrow-pass)" />
					{:else if ann.type === 'press'}
						<line x1={x1} y1={y1} x2={x2} y2={y2} stroke="var(--color-error)" stroke-width="3.5" stroke-dasharray="8 3" marker-end="url(#arrow-press)" />
					{/if}
				{/each}

				{#if isDrawingVector && vectorStart && vectorCurrent}
					{@const sx = (vectorStart.x / 100) * 680}
					{@const sy = (vectorStart.y / 100) * 960}
					{@const cx = (vectorCurrent.x / 100) * 680}
					{@const cy = (vectorCurrent.y / 100) * 960}
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
					{@const px = (player.x / 100) * 680}
					{@const py = (player.y / 100) * 960}
					{@const isDragging = draggingPlayerId === player.id}
					{#if readonly}
						<g transform="translate({px}, {py})">
							<circle r="22" fill="var(--color-accent)" stroke="var(--color-ink)" stroke-width="3" />
							<text text-anchor="middle" dy="5" fill="var(--color-ink)" font-size="14" font-weight="bold" font-family="var(--font-outlier)">
								{player.number}
							</text>
							<g transform="translate(0, 32)">
								<rect x="-56" y="-11" width="112" height="22" rx="4" fill="var(--color-paper)" fill-opacity="0.95" stroke="var(--color-accent-2)" stroke-width="1" />
								<text text-anchor="middle" dy="4" fill="var(--color-ink)" font-size="11" font-weight="bold" font-family="var(--font-body)">
									{displayTokenLabel(player)}
								</text>
							</g>
						</g>
					{:else}
						<g
							transform="translate({px}, {py})"
							class="cursor-grab active:cursor-grabbing pitch-token"
							role="button"
							tabindex="0"
							aria-label={`${player.name} #${player.number} ${player.role}. Press Enter to edit or swap, Arrow keys to move.`}
							onkeydown={(e) => handleTokenKeydown(e, player)}
							onpointerdown={(e) => {
								if (activeTool === 'select') {
									e.stopPropagation();
									handlePointerDown(e, player.id);
								}
							}}
						>
							{#if isDragging || selectedBenchPlayerId}
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
								<rect x="-56" y="-11" width="112" height="22" rx="4" fill="var(--color-paper)" fill-opacity="0.95" stroke="var(--color-accent-2)" stroke-width="1" />
								<text text-anchor="middle" dy="4" fill="var(--color-ink)" font-size="11" font-weight="bold" font-family="var(--font-body)">
									{displayTokenLabel(player)}
								</text>
							</g>
						</g>
					{/if}
				{/each}
			</svg>
		</div>

		<!-- Right: Substitutes Bench Pool (30% width) -->
		{#if !readonly && bench && bench.length > 0}
			<aside class="lg:col-span-3 rounded-card border border-rule bg-paper-2 p-4 space-y-3">
				<div class="border-b border-rule pb-3 space-y-1">
					<div class="flex items-center justify-between gap-2">
						<span class="text-sm font-bold text-ink">Substitutes</span>
						<span class="num font-outlier text-xs text-muted">{bench.length} players</span>
					</div>
					<p class="text-xs text-muted" aria-live="polite">
						{benchInstruction}
					</p>
				</div>

				<div class="flex flex-col gap-2">
					{#each bench as bPlayer (bPlayer.id)}
						{@const isSelected = selectedBenchPlayerId === bPlayer.id}
						{@const bTag = `#${bPlayer.number} ${bPlayer.name}`}
						<button
							type="button"
							aria-pressed={isSelected}
							onclick={() => { if (readonly) return; selectedBenchPlayerId = isSelected ? null : bPlayer.id; }}
							class="min-h-[44px] w-full px-3 py-2 rounded-card border transition-colors text-left flex items-center justify-between gap-2 {isSelected ? 'bg-paper-3 border-accent-2 text-accent-2' : 'bg-paper border-rule text-ink-2 hover:text-ink hover:bg-paper-3/60'}"
						>
							<span class="text-xs font-semibold text-ink truncate">{bTag}</span>
							<span class="text-xs font-outlier text-muted shrink-0">{bPlayer.role}</span>
						</button>
					{/each}
				</div>
			</aside>
		{/if}
	</div>

	{#if !readonly}
		<!-- Below Pitch & Substitutes: Tools, Export PNG, Share to Terrace -->
		<div class="flex items-center justify-between gap-3 pt-4 border-t border-rule flex-wrap text-xs">
			<!-- Drawing & Moving Tools -->
			<div class="flex items-center gap-2 flex-wrap">
				<span class="text-muted font-semibold mr-1">Tools:</span>
				<button
					type="button"
					onclick={() => (activeTool = 'select')}
					aria-pressed={activeTool === 'select'}
					class="min-h-[44px] px-3 rounded-card font-semibold transition-colors border {activeTool === 'select' ? 'bg-paper-3 text-ink border-rule-2' : 'bg-paper-2 text-ink-2 border-rule hover:text-ink'}"
				>
					Move tokens
				</button>
				<button
					type="button"
					onclick={() => (activeTool = 'run')}
					aria-pressed={activeTool === 'run'}
					class="min-h-[44px] px-3 rounded-card font-semibold transition-colors border {activeTool === 'run' ? 'bg-paper-3 text-accent-2 border-rule-2' : 'bg-paper-2 text-ink-2 border-rule hover:text-ink'}"
				>
					Run vector
				</button>
				<button
					type="button"
					onclick={() => (activeTool = 'pass')}
					aria-pressed={activeTool === 'pass'}
					class="min-h-[44px] px-3 rounded-card font-semibold transition-colors border {activeTool === 'pass' ? 'bg-paper-3 text-success border-rule-2' : 'bg-paper-2 text-ink-2 border-rule hover:text-ink'}"
				>
					Pass channel
				</button>
				<button
					type="button"
					onclick={() => (activeTool = 'press')}
					aria-pressed={activeTool === 'press'}
					class="min-h-[44px] px-3 rounded-card font-semibold transition-colors border {activeTool === 'press' ? 'bg-paper-3 text-error border-rule-2' : 'bg-paper-2 text-ink-2 border-rule hover:text-ink'}"
				>
					High press
				</button>

				<button
					type="button"
					onclick={() => (fluidMode = !fluidMode)}
					aria-pressed={fluidMode}
					class="min-h-[44px] px-3 rounded-card font-semibold transition-colors border sm:ml-1 {fluidMode ? 'bg-accent-2 text-paper border-accent-2' : 'bg-paper-2 text-ink-2 border-rule hover:text-ink'}"
					title="Fluid movement allows unconstrained dragging anywhere on pitch"
				>
					{fluidModeLabel}
				</button>
			</div>

			<!-- Actions: Export PNG, Undo, Clear, Share -->
			<div class="flex items-center gap-2 flex-wrap">
				<button
					type="button"
					onclick={exportLineupAsImage}
					class="min-h-[44px] px-3.5 rounded-card bg-accent hover:opacity-95 text-accent-ink font-semibold text-xs transition-opacity"
					title="Download high-resolution lineup graphic"
				>
					Export PNG
				</button>

				{#if onshare}
					<button
						type="button"
						onclick={onshare}
						class="min-h-[44px] px-3.5 rounded-card bg-paper-2 hover:bg-paper-3 text-accent-2 font-semibold text-xs transition-colors border border-rule"
					>
						Share to Terrace
					</button>
				{/if}

				{#if annotations.length > 0}
					<button
						type="button"
						onclick={undoLastAnnotation}
						class="min-h-[44px] px-3 rounded-card bg-paper-2 border border-rule text-ink-2 hover:text-ink font-semibold transition-colors"
					>
						Undo arrow
					</button>
					<button
						type="button"
						onclick={clearAllAnnotations}
						class="min-h-[44px] px-2.5 rounded-card text-error hover:text-ink transition-colors font-semibold"
					>
						Clear arrows
					</button>
				{/if}
			</div>
		</div>
	{/if}

	<!-- Quick Player Edit Modal -->
	{#if editingPlayer}
		<div class="fixed inset-0 z-[var(--z-modal)] flex items-center justify-center p-4">
			<button
				type="button"
				tabindex="-1"
				aria-label="Close player editor"
				onclick={() => (editingPlayer = null)}
				class="fixed inset-0 w-full h-full bg-paper/85 cursor-default"
			></button>
			<div
				role="dialog"
				aria-modal="true"
				aria-labelledby="edit-player-modal-title"
				use:focusTrap={{
					active: Boolean(editingPlayer),
					onEscape: () => (editingPlayer = null),
					initialFocusSelector: '#roster-select, #player-name'
				}}
				class="relative z-10 bg-paper-2 border-t-2 border-rule-2 p-6 w-full max-w-sm space-y-5"
			>
				<div class="flex items-center justify-between border-b border-rule pb-3">
					<h3 id="edit-player-modal-title" class="text-base font-bold text-ink">
						Edit <span class="num font-outlier text-accent-text">#{editingPlayer.number}</span> {editingPlayer.name}
					</h3>
					<button
						type="button"
						onclick={() => (editingPlayer = null)}
						class="min-h-[44px] px-2 text-muted hover:text-ink text-xs font-semibold"
					>
						Close
					</button>
				</div>

				{#if squadPlayers && squadPlayers.length > 0}
					<div class="space-y-1.5">
						<label for="roster-select" class="block text-xs font-semibold text-ink-2">
							Select from Arsenal squad roster
						</label>
						<select
							id="roster-select"
							bind:value={selectedRosterId}
							onchange={() => { const selected = squadPlayers.find((p) => p.id === selectedRosterId); if (selected) handleRosterSelect(selected); }}
							class="w-full min-h-[44px] bg-paper border border-rule rounded-card px-3 text-xs text-ink"
						>
							<option value="">Choose Arsenal player…</option>
							{#each squadPlayers as sp (sp.id)}
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
							maxlength={40}
							bind:value={editingPlayer.name}
							class="w-full min-h-[44px] bg-paper border border-rule rounded-card px-3 text-xs text-ink mt-1"
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
								class="w-full min-h-[44px] bg-paper border border-rule rounded-card px-3 text-xs text-ink num font-outlier mt-1"
							/>
						</div>
						<div>
							<label for="player-role" class="block text-xs font-semibold text-ink-2">Tactical role</label>
							<select
								id="player-role"
								bind:value={editingPlayer.role}
								class="w-full min-h-[44px] bg-paper border border-rule rounded-card px-3 text-xs text-ink mt-1"
							>
								<option value="GK">GK (Goalkeeper)</option>
								<option value="CB">CB (Center Back)</option>
								<option value="LB">LB (Left Back)</option>
								<option value="RB">RB (Right Back)</option>
								<option value="LWB">LWB (Left Wingback)</option>
								<option value="RWB">RWB (Right Wingback)</option>
								<option value="DM">DM (Defensive Mid)</option>
								<option value="CM">CM (Central Mid)</option>
								<option value="LM">LM (Left Mid)</option>
								<option value="RM">RM (Right Mid)</option>
								<option value="AM">AM (Attacking Mid)</option>
								<option value="LW">LW (Left Wing)</option>
								<option value="RW">RW (Right Wing)</option>
								<option value="CF">CF (Center Forward)</option>
								<option value="ST">ST (Striker)</option>
							</select>
						</div>
					</div>
				</div>

				{#if modalErrorMessage}
					<p role="alert" class="text-xs text-error font-semibold">{modalErrorMessage}</p>
				{/if}

				<div class="flex items-center justify-end gap-3 pt-3 border-t border-rule">
					<button
						type="button"
						onclick={() => (editingPlayer = null)}
						class="min-h-[44px] px-3 rounded-card text-xs font-semibold text-ink-2 hover:text-ink"
					>
						Cancel
					</button>
					<button
						type="button"
						onclick={handleSavePlayerModal}
						disabled={!editingPlayer.name.trim()}
						class="min-h-[44px] px-4 rounded-card bg-accent hover:opacity-95 disabled:opacity-50 text-xs font-semibold text-accent-ink transition-opacity"
					>
						Save player
					</button>
				</div>
			</div>
		</div>
	{/if}
</div>

<style>
	.pitch-token:focus-visible {
		outline: 2px solid var(--color-focus);
		outline-offset: 4px;
	}
</style>
