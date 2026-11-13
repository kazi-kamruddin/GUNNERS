<script lang="ts">
	import { untrack } from 'svelte';
	import StateBanner from '$lib/components/StateBanner.svelte';
	import { ApiError, fetchHistoricalMatchDetailStrict } from '$lib/api/football';
	import type {
		HistoricalMatchDetail,
		HistoricalMatchSummary,
		ShotEvent
	} from '$lib/types/football';

	let {
		matches = [],
		initialDetail = null,
		initialMatchId = '',
		initialMatchesError = null,
		initialDetailError = null,
		showBackLink = false
	}: {
		matches?: HistoricalMatchSummary[];
		initialDetail?: HistoricalMatchDetail | null;
		initialMatchId?: string;
		initialMatchesError?: string | null;
		initialDetailError?: string | null;
		showBackLink?: boolean;
	} = $props();

	const initialTargetId = untrack(
		() => initialMatchId || initialDetail?.id || matches[0]?.id || 'hist_ars_barca_2011'
	);

	let selectedMatchId = $state<string>(initialTargetId);
	let activeDetail = $state<HistoricalMatchDetail | null>(untrack(() => initialDetail));
	let viewMode = $state<'shot_map' | 'pass_network'>('shot_map');
	let teamFilter = $state<string>('all');
	let selectedShot = $state<ShotEvent | null>(null);
	let selectedPassPlayer = $state<string | null>(null);
	let isLoading = $state(false);
	let detailError = $state<string | null>(untrack(() => initialDetailError ?? null));
	let lastSyncedKey = $state<string>(
		`${initialTargetId}:${untrack(() => initialDetail?.id ?? 'none')}:${untrack(() => initialDetailError ?? 'ok')}`
	);
	let matchRequestSeq = 0;

	$effect(() => {
		const targetId =
			initialMatchId || initialDetail?.id || matches[0]?.id || 'hist_ars_barca_2011';
		const syncKey = `${targetId}:${initialDetail?.id ?? 'none'}:${initialDetailError ?? 'ok'}`;
		if (syncKey !== lastSyncedKey) {
			lastSyncedKey = syncKey;
			selectedMatchId = targetId;
			activeDetail = initialDetail;
			detailError = initialDetailError ?? null;
			selectedShot = null;
			selectedPassPlayer = null;
			teamFilter = 'all';
		}
	});

	function syncMatchUrlParam(matchId: string) {
		if (typeof window === 'undefined') return;
		const url = new URL(window.location.href);
		url.searchParams.set('match', matchId);
		window.history.replaceState({}, '', url.toString());
	}

	async function switchMatch(matchId: string) {
		selectedMatchId = matchId;
		isLoading = true;
		detailError = null;
		selectedShot = null;
		selectedPassPlayer = null;
		teamFilter = 'all';
		syncMatchUrlParam(matchId);
		const reqId = ++matchRequestSeq;
		try {
			const detail = await fetchHistoricalMatchDetailStrict(matchId);
			if (reqId !== matchRequestSeq) return;
			if (!detail) {
				detailError = 'Historical match telemetry was not found.';
			} else {
				activeDetail = detail;
			}
		} catch (err) {
			if (reqId !== matchRequestSeq) return;
			detailError =
				err instanceof ApiError
					? err.detail
					: 'Unable to load StatsBomb match telemetry right now.';
		} finally {
			if (reqId === matchRequestSeq) {
				isLoading = false;
			}
		}
	}

	const filteredShots = $derived.by(() => {
		if (!activeDetail) return [];
		if (teamFilter === 'all') return activeDetail.shots;
		return activeDetail.shots.filter((s) => s.team_id === teamFilter);
	});

	// Deterministic visual de-confliction so shared coordinates (e.g. two penalties at 88.5, 50.0) remain clickable
	const positionedShots = $derived.by(() => {
		const groups: ShotEvent[][] = [];
		for (const shot of filteredShots) {
			const existing = groups.find((g) => Math.hypot(g[0].x - shot.x, g[0].y - shot.y) < 0.6);
			if (existing) existing.push(shot);
			else groups.push([shot]);
		}
		const coords = new Map<string, { x: number; y: number }>();
		for (const group of groups) {
			if (group.length === 1) {
				coords.set(group[0].id, { x: group[0].x, y: group[0].y });
			} else {
				group.forEach((shot, i) => {
					const angle = (i / group.length) * Math.PI * 2;
					const offset = 1.1;
					coords.set(shot.id, {
						x: Math.max(2, Math.min(98, shot.x + Math.cos(angle) * offset)),
						y: Math.max(2, Math.min(98, shot.y + Math.sin(angle) * offset))
					});
				});
			}
		}
		return filteredShots.map((shot) => ({
			shot,
			pos: coords.get(shot.id) || { x: shot.x, y: shot.y }
		}));
	});

	const selectedShotIndex = $derived(
		selectedShot ? filteredShots.findIndex((s) => s.id === selectedShot?.id) : -1
	);

	function stepShot(delta: number) {
		if (filteredShots.length === 0) return;
		if (selectedShotIndex === -1) {
			selectedShot = delta > 0 ? filteredShots[0] : filteredShots[filteredShots.length - 1];
			return;
		}
		const nextIdx = (selectedShotIndex + delta + filteredShots.length) % filteredShots.length;
		selectedShot = filteredShots[nextIdx];
	}

	function getShotColor(outcome: string): string {
		switch (outcome) {
			case 'Goal':
				return 'var(--color-success)';
			case 'Saved':
				return 'var(--color-ink)';
			case 'Blocked':
				return 'var(--color-accent-2)';
			default:
				return 'var(--color-error)';
		}
	}

	function handleShotKeydown(event: KeyboardEvent, shot: ShotEvent) {
		if (event.key === 'Enter' || event.key === ' ') {
			event.preventDefault();
			selectedShot = shot;
		}
	}

	function handleNodeKeydown(event: KeyboardEvent, playerName: string) {
		if (event.key === 'Enter' || event.key === ' ') {
			event.preventDefault();
			selectedPassPlayer = selectedPassPlayer === playerName ? null : playerName;
		}
	}
</script>

<div class="space-y-8">
	<!-- Match Selector & View Mode Toolbar -->
	<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-rule pb-5">
		<div class="flex items-center gap-2 flex-wrap">
			<span class="text-xs font-semibold text-muted mr-1">Match:</span>
			{#each matches as m (m.id)}
				{@const isSelected = selectedMatchId === m.id}
				{@const matchLabel = `${m.home_team_name} ${m.home_score}–${m.away_score} ${m.away_team_name} (${m.season})`}
				<button
					type="button"
					onclick={() => switchMatch(m.id)}
					aria-pressed={isSelected}
					class="min-h-[44px] px-3.5 rounded-card text-xs font-semibold transition-colors border {isSelected ? 'bg-accent text-accent-ink border-accent' : 'bg-paper-2 text-ink-2 border-rule hover:text-ink'}"
				>
					{matchLabel}
				</button>
			{/each}
		</div>

		<div class="flex items-center gap-2 flex-wrap">
			<button
				type="button"
				onclick={() => { viewMode = 'shot_map'; selectedShot = null; }}
				aria-pressed={viewMode === 'shot_map'}
				class="min-h-[44px] px-3.5 rounded-card text-xs font-semibold transition-colors border {viewMode === 'shot_map' ? 'bg-paper-3 text-accent-2 border-rule-2' : 'bg-paper-2 text-ink-2 border-rule hover:text-ink'}"
			>
				Shot map (xG)
			</button>
			<button
				type="button"
				onclick={() => { viewMode = 'pass_network'; selectedShot = null; }}
				aria-pressed={viewMode === 'pass_network'}
				class="min-h-[44px] px-3.5 rounded-card text-xs font-semibold transition-colors border {viewMode === 'pass_network' ? 'bg-paper-3 text-accent-2 border-rule-2' : 'bg-paper-2 text-ink-2 border-rule hover:text-ink'}"
			>
				Passing network
			</button>
			{#if showBackLink}
				<a
					href="/lab"
					class="min-h-[44px] px-3.5 rounded-card bg-paper-2 hover:bg-paper-3 border border-rule text-xs font-semibold text-ink transition-colors inline-flex items-center"
				>
					Back to Data Lab
				</a>
			{/if}
		</div>
	</div>

	{#if initialMatchesError && matches.length === 0}
		<StateBanner
			variant="error"
			title="Unable to load classic fixtures"
			message={initialMatchesError}
			onretry={() => switchMatch(selectedMatchId)}
			busy={isLoading}
		/>
	{:else if isLoading}
		<div class="py-12 text-sm text-muted" role="status" aria-live="polite">
			Loading StatsBomb match telemetry…
		</div>
	{:else if detailError && !activeDetail}
		<StateBanner
			variant="error"
			title="Unable to load match telemetry"
			message={detailError}
			onretry={() => switchMatch(selectedMatchId)}
			busy={isLoading}
		/>
	{:else if activeDetail}
		{#if detailError}
			<StateBanner
				variant="error"
				title="Could not switch match telemetry"
				message={detailError}
				onretry={() => switchMatch(selectedMatchId)}
				busy={isLoading}
			/>
		{/if}

		<!-- Match Telemetry Overview Bar -->
		<div class="grid grid-cols-2 sm:grid-cols-4 gap-6 border-b border-rule pb-6 text-xs">
			<div>
				<p class="text-muted">Home total xG</p>
				<p class="text-2xl font-bold text-success num font-outlier mt-1">{activeDetail.total_xg_home} xG</p>
				<p class="text-muted num font-outlier">({activeDetail.total_shots_home} shots)</p>
			</div>
			<div>
				<p class="text-muted">Away total xG</p>
				<p class="text-2xl font-bold text-accent-2 num font-outlier mt-1">{activeDetail.total_xg_away} xG</p>
				<p class="text-muted num font-outlier">({activeDetail.total_shots_away} shots)</p>
			</div>
			<div>
				<p class="text-muted">Competition</p>
				<p class="text-sm font-bold text-ink mt-1">{activeDetail.competition}</p>
				<p class="text-muted num font-outlier">{activeDetail.season}</p>
			</div>
			<div>
				<p class="text-muted">Venue</p>
				<p class="text-sm font-bold text-ink mt-1 truncate" title={activeDetail.venue}>{activeDetail.venue}</p>
				<p class="text-muted num font-outlier">{activeDetail.match_date}</p>
			</div>
		</div>

		<!-- Interactive Pitch Stage -->
		<div class="grid grid-cols-1 lg:grid-cols-12 gap-10 items-start">
			<!-- 2D Football Pitch SVG (8 cols) -->
			<div class="lg:col-span-8 space-y-4 min-w-0">
				<div class="w-full flex items-center justify-between flex-wrap gap-3 text-xs">
					<div class="flex items-center gap-2 flex-wrap">
						{#if viewMode === 'shot_map'}
							{@const homeName = activeDetail?.home_team_name || 'Home'}
							{@const awayName = activeDetail?.away_team_name || 'Away'}
							<span class="text-muted font-semibold">Filter team:</span>
							<button
								type="button"
								onclick={() => (teamFilter = 'all')}
								aria-pressed={teamFilter === 'all'}
								class="min-h-[44px] px-3 rounded-card transition-colors border {teamFilter === 'all' ? 'bg-paper-3 text-ink border-rule-2 font-semibold' : 'bg-paper-2 text-ink-2 border-rule'}"
							>
								All
							</button>
							<button
								type="button"
								onclick={() => activeDetail && (teamFilter = activeDetail.home_team_id)}
								aria-pressed={Boolean(activeDetail && teamFilter === activeDetail.home_team_id)}
								class="min-h-[44px] px-3 rounded-card transition-colors border whitespace-nowrap {activeDetail && teamFilter === activeDetail.home_team_id ? 'bg-paper-3 text-success border-rule-2 font-semibold' : 'bg-paper-2 text-ink-2 border-rule'}"
							>
								{homeName}
							</button>
							<button
								type="button"
								onclick={() => activeDetail && (teamFilter = activeDetail.away_team_id)}
								aria-pressed={Boolean(activeDetail && teamFilter === activeDetail.away_team_id)}
								class="min-h-[44px] px-3 rounded-card transition-colors border whitespace-nowrap {activeDetail && teamFilter === activeDetail.away_team_id ? 'bg-paper-3 text-accent-2 border-rule-2 font-semibold' : 'bg-paper-2 text-ink-2 border-rule'}"
							>
								{awayName}
							</button>
						{:else}
							<span class="text-accent-2 font-semibold">
								{activeDetail.home_team_name} passing network · Circle = avg position, stroke width = pass volume
							</span>
							{#if selectedPassPlayer}
								<button
									type="button"
									onclick={() => (selectedPassPlayer = null)}
									class="min-h-[44px] px-2.5 text-ink-2 hover:text-ink underline font-semibold"
								>
									Clear highlight
								</button>
							{/if}
						{/if}
					</div>

					{#if viewMode === 'shot_map'}
						<div class="flex items-center gap-4 text-xs text-muted flex-wrap">
							<span class="inline-flex items-center gap-1.5 text-success font-semibold">
								<span class="w-3 h-3 rounded-full bg-success ring-2 ring-success/40 inline-block" aria-hidden="true"></span>
								Goal
							</span>
							<span class="inline-flex items-center gap-1.5 text-ink font-semibold">
								<span class="w-2.5 h-2.5 rounded-full bg-ink inline-block" aria-hidden="true"></span>
								Saved
							</span>
							<span class="inline-flex items-center gap-1.5 text-accent-2 font-semibold">
								<span class="w-2.5 h-2.5 rounded-full bg-accent-2 inline-block" aria-hidden="true"></span>
								Blocked
							</span>
							<span class="inline-flex items-center gap-1.5 text-error font-semibold">
								<span class="w-2.5 h-2.5 rounded-full bg-error inline-block" aria-hidden="true"></span>
								Miss
							</span>
						</div>
					{/if}
				</div>

				<!-- Pitch SVG Container (scrollable on very narrow phones for >=10px legibility) -->
				<div class="overflow-x-auto border border-rule rounded-card bg-pitch">
					<div class="min-w-[540px]">
						<svg
							viewBox="0 0 700 480"
							role="img"
							aria-label="StatsBomb 2D tactical event pitch"
							class="w-full h-auto block"
						>
							<rect x="15" y="15" width="670" height="450" fill="none" stroke="var(--color-success)" stroke-width="2" stroke-opacity="0.35" />
							<line x1="350" y1="15" x2="350" y2="465" stroke="var(--color-success)" stroke-width="2" stroke-opacity="0.35" />
							<circle cx="350" cy="240" r="55" fill="none" stroke="var(--color-success)" stroke-width="2" stroke-opacity="0.35" />
							<circle cx="350" cy="240" r="3" fill="var(--color-success)" fill-opacity="0.5" />

							<rect x="15" y="120" width="115" height="240" fill="none" stroke="var(--color-success)" stroke-width="2" stroke-opacity="0.35" />
							<rect x="15" y="175" width="40" height="130" fill="none" stroke="var(--color-success)" stroke-width="2" stroke-opacity="0.35" />
							<circle cx="85" cy="240" r="2.5" fill="var(--color-success)" fill-opacity="0.5" />

							<rect x="570" y="120" width="115" height="240" fill="none" stroke="var(--color-success)" stroke-width="2" stroke-opacity="0.35" />
							<rect x="645" y="175" width="40" height="130" fill="none" stroke="var(--color-success)" stroke-width="2" stroke-opacity="0.35" />
							<circle cx="615" cy="240" r="2.5" fill="var(--color-success)" fill-opacity="0.5" />

							{#if viewMode === 'shot_map'}
								{#each positionedShots as item (item.shot.id)}
									{@const shot = item.shot}
									{@const cx = (item.pos.x / 100) * 670 + 15}
									{@const cy = (item.pos.y / 100) * 450 + 15}
									{@const radius = Math.max(7, shot.xg * 24)}
									{@const color = getShotColor(shot.outcome)}
									{@const isSelected = selectedShot?.id === shot.id}
									<g
										role="button"
										tabindex="0"
										aria-label={`${shot.player_name} (${shot.team_name}), ${shot.minute}m ${shot.second}s, ${shot.outcome}, xG ${shot.xg}`}
										aria-pressed={isSelected}
										onclick={() => (selectedShot = shot)}
										onkeydown={(e) => handleShotKeydown(e, shot)}
										class="cursor-pointer shot-marker"
									>
										<circle cx={cx} cy={cy} r={Math.max(18, radius + 6)} fill="transparent" />
										{#if shot.outcome === 'Goal'}
											<circle cx={cx} cy={cy} r={radius + 4} fill="none" stroke="var(--color-success)" stroke-width="2" opacity="0.65" />
										{/if}
										<circle
											cx={cx}
											cy={cy}
											r={radius}
											fill={color}
											stroke={isSelected ? 'var(--color-ink)' : 'var(--color-paper)'}
											stroke-width={isSelected ? '2.5' : '1.5'}
											opacity="0.92"
										/>
									</g>
								{/each}
							{:else}
								{#each activeDetail.pass_links as link (`${link.source}->${link.target}`)}
									{@const srcNode = activeDetail.pass_nodes.find((n) => n.player_name === link.source)}
									{@const tgtNode = activeDetail.pass_nodes.find((n) => n.player_name === link.target)}
									{@const isLinked = !selectedPassPlayer || link.source === selectedPassPlayer || link.target === selectedPassPlayer}
									{#if srcNode && tgtNode}
										{@const x1 = (srcNode.x / 100) * 670 + 15}
										{@const y1 = (srcNode.y / 100) * 450 + 15}
										{@const x2 = (tgtNode.x / 100) * 670 + 15}
										{@const y2 = (tgtNode.y / 100) * 450 + 15}
										<line
											x1={x1}
											y1={y1}
											x2={x2}
											y2={y2}
											stroke="var(--color-accent-2)"
											stroke-width={Math.max(1.5, link.pass_count / 4)}
											stroke-opacity={isLinked ? (selectedPassPlayer ? 0.95 : 0.6) : 0.14}
										/>
									{/if}
								{/each}

								{#each activeDetail.pass_nodes as node (node.player_name)}
									{@const nx = (node.x / 100) * 670 + 15}
									{@const ny = (node.y / 100) * 450 + 15}
									{@const isNodeActive = selectedPassPlayer === node.player_name}
									<g
										role="button"
										tabindex="0"
										aria-pressed={isNodeActive}
										aria-label={`${node.player_name} #${node.jersey_number}, ${node.passes_completed} passes completed. Activate to highlight passing links.`}
										onclick={() => (selectedPassPlayer = isNodeActive ? null : node.player_name)}
										onkeydown={(e) => handleNodeKeydown(e, node.player_name)}
										class="cursor-pointer shot-marker"
									>
										<circle cx={nx} cy={ny} r="20" fill="transparent" />
										<circle
											cx={nx}
											cy={ny}
											r="15"
											fill={isNodeActive ? 'var(--color-paper-3)' : 'var(--color-paper-2)'}
											stroke={isNodeActive ? 'var(--color-ink)' : 'var(--color-accent-2)'}
											stroke-width={isNodeActive ? '2.5' : '2'}
										/>
										<text
											x={nx}
											y={ny + 4}
											text-anchor="middle"
											fill="var(--color-ink)"
											font-size="11"
											font-weight="bold"
											font-family="var(--font-outlier)"
										>
											{node.jersey_number}
										</text>
										<text
											x={nx}
											y={ny + 26}
											text-anchor="middle"
											fill="var(--color-ink)"
											font-size="10"
											font-weight="600"
											font-family="var(--font-body)"
										>
											{node.player_name}
										</text>
									</g>
								{/each}
							{/if}
						</svg>
					</div>
				</div>

				<!-- Mobile & Keyboard Shot Stepper + Inline Summary -->
				{#if viewMode === 'shot_map' && filteredShots.length > 0}
					<div class="flex items-center justify-between gap-3 flex-wrap border-y border-rule bg-paper-2 px-4 py-2.5 text-xs">
						<div class="flex flex-wrap items-center gap-x-2.5 gap-y-1 min-w-0">
							{#if selectedShot}
								<span class="font-bold text-ink">{selectedShot.player_name}</span>
								<span class="text-muted num font-outlier">{selectedShot.minute}m</span>
								<span class="font-semibold {selectedShot.outcome === 'Goal' ? 'text-success' : 'text-ink-2'}">{selectedShot.outcome}</span>
								<span class="text-success font-outlier font-bold">({selectedShot.xg} xG)</span>
							{:else}
								<span class="text-muted">{filteredShots.length} shots plotted. Step through or tap a shot marker.</span>
							{/if}
						</div>
						<div class="flex items-center gap-2 shrink-0">
							<button
								type="button"
								onclick={() => stepShot(-1)}
								class="min-h-[44px] px-3 rounded-card border border-rule bg-paper hover:bg-paper-3 text-ink-2 hover:text-ink font-semibold"
							>
								Prev shot
							</button>
							<button
								type="button"
								onclick={() => stepShot(1)}
								class="min-h-[44px] px-3 rounded-card border border-rule bg-paper hover:bg-paper-3 text-ink-2 hover:text-ink font-semibold"
							>
								Next shot
							</button>
						</div>
					</div>
				{/if}

				<div class="text-xs text-muted space-y-1">
					<p>{activeDetail.license_notice}</p>
					<p class="flex items-center gap-3 flex-wrap">
						<span>
							Data source:
							<a
								href="https://github.com/statsbomb/open-data"
								target="_blank"
								rel="noopener noreferrer"
								class="underline text-ink-2 hover:text-accent-text font-semibold"
							>
								StatsBomb Open Data
							</a>
						</span>
						<span aria-hidden="true">·</span>
						<span>
							License:
							<a
								href="https://opendatacommons.org/licenses/odbl/1.0/"
								target="_blank"
								rel="noopener noreferrer"
								class="underline text-ink-2 hover:text-accent-text font-semibold"
							>
								ODbL v1.0
							</a>
						</span>
					</p>
				</div>
			</div>

			<!-- Right Sidebar: Selected Shot or Telemetry Inspector (4 cols) -->
			<aside class="lg:col-span-4 space-y-6">
				{#if viewMode === 'shot_map'}
					<div class="border-t-2 border-rule-2 pt-5 space-y-4" aria-live="polite">
						<div class="border-b border-rule pb-3">
							<h2 class="text-lg font-bold text-ink">Shot event inspector</h2>
							<p class="text-xs text-muted">Select or focus any shot circle on the pitch to examine telemetry.</p>
						</div>

						{#if selectedShot}
							<dl class="space-y-3 text-xs">
								<div class="flex items-center justify-between py-1.5 border-b border-rule">
									<dt class="text-muted">Shooter</dt>
									<dd class="font-bold text-ink">{selectedShot.player_name}</dd>
								</div>
								<div class="flex items-center justify-between py-1.5 border-b border-rule">
									<dt class="text-muted">Team</dt>
									<dd class="text-accent-2 font-semibold">{selectedShot.team_name}</dd>
								</div>
								<div class="flex items-center justify-between py-1.5 border-b border-rule">
									<dt class="text-muted">Timestamp</dt>
									<dd class="text-ink num font-outlier">{selectedShot.minute}m {selectedShot.second}s</dd>
								</div>
								<div class="flex items-center justify-between py-1.5 border-b border-rule">
									<dt class="text-muted">Outcome</dt>
									<dd class="font-bold {selectedShot.outcome === 'Goal' ? 'text-success' : 'text-ink'}">
										{selectedShot.outcome}
									</dd>
								</div>
								<div class="flex items-center justify-between py-1.5 border-b border-rule">
									<dt class="text-muted">Expected goals (xG)</dt>
									<dd class="font-bold text-success text-sm num font-outlier">{selectedShot.xg}</dd>
								</div>
								<div class="flex items-center justify-between py-1.5 border-b border-rule">
									<dt class="text-muted">Body part</dt>
									<dd class="text-ink-2">{selectedShot.body_part}</dd>
								</div>
								<div class="flex items-center justify-between py-1.5">
									<dt class="text-muted">Play pattern</dt>
									<dd class="text-ink-2">{selectedShot.shot_type}</dd>
								</div>
							</dl>
						{:else}
							<div class="py-10 text-muted text-xs">
								Select a shot on the pitch to inspect expected goal value (xG) and shooting coordinates.
							</div>
						{/if}
					</div>
				{:else}
					<div class="border-t-2 border-rule-2 pt-5 space-y-4">
						<div class="border-b border-rule pb-3">
							<h2 class="text-lg font-bold text-ink">Passing combinations</h2>
							<p class="text-xs text-muted">Activate a player node or channel below to highlight connections.</p>
						</div>

						<div class="divide-y divide-rule text-xs">
							{#each activeDetail.pass_links as link (`${link.source}->${link.target}`)}
								{@const isChannelActive = selectedPassPlayer === link.source || selectedPassPlayer === link.target}
								{@const linkPair = `${link.source} to ${link.target}`}
								{@const linkN = `${link.pass_count} passes`}
								<button
									type="button"
									onclick={() => (selectedPassPlayer = selectedPassPlayer === link.source ? null : link.source)}
									aria-pressed={isChannelActive}
									class="w-full min-h-[44px] py-2 px-2 flex items-center justify-between text-left transition-colors {isChannelActive ? 'bg-paper-2 text-ink' : 'hover:bg-paper-2'}"
								>
									<span class="text-ink-2">{linkPair}</span>
									<span class="font-bold text-accent-2 num font-outlier">{linkN}</span>
								</button>
							{/each}
						</div>
					</div>
				{/if}

				<div class="border-t border-rule pt-4 text-xs text-muted space-y-1.5">
					<p class="font-bold text-ink-2">StatsBomb open data architecture</p>
					<p class="leading-relaxed">
						All event coordinates and xG metrics follow the open-data 120x80 yard pitch schema, normalized for browser rendering.
					</p>
				</div>
			</aside>
		</div>
	{:else}
		<div class="py-12 border-t border-rule text-sm text-muted">
			No historical StatsBomb match telemetry available right now.
		</div>
	{/if}
</div>

<style>
	.shot-marker:focus-visible {
		outline: 2px solid var(--color-focus);
		outline-offset: 3px;
	}
</style>
