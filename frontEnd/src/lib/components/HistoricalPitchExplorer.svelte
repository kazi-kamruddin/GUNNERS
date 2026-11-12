<script lang="ts">
	import { fetchHistoricalMatchDetail } from '$lib/api/football';
	import type {
		HistoricalMatchDetail,
		HistoricalMatchSummary,
		ShotEvent
	} from '$lib/types/football';

	let {
		matches = [],
		initialDetail = null,
		initialMatchId = '',
		showBackLink = false
	}: {
		matches?: HistoricalMatchSummary[];
		initialDetail?: HistoricalMatchDetail | null;
		initialMatchId?: string;
		showBackLink?: boolean;
	} = $props();

	let selectedMatchId = $state<string>('');
	let activeDetail = $state<HistoricalMatchDetail | null>(null);
	let viewMode = $state<'shot_map' | 'pass_network'>('shot_map');
	let teamFilter = $state<string>('all');
	let selectedShot = $state<ShotEvent | null>(null);
	let isLoading = $state(false);
	let lastSyncedKey = $state<string | null>(null);

	$effect(() => {
		const targetId =
			initialMatchId || initialDetail?.id || matches[0]?.id || 'hist_ars_barca_2011';
		const syncKey = `${targetId}:${initialDetail?.id ?? 'none'}`;
		if (syncKey !== lastSyncedKey) {
			lastSyncedKey = syncKey;
			selectedMatchId = targetId;
			activeDetail = initialDetail;
			selectedShot = null;
			teamFilter = 'all';
		}
	});

	async function switchMatch(matchId: string) {
		selectedMatchId = matchId;
		isLoading = true;
		selectedShot = null;
		teamFilter = 'all';
		try {
			const detail = await fetchHistoricalMatchDetail(matchId);
			activeDetail = detail;
		} finally {
			isLoading = false;
		}
	}

	const filteredShots = $derived.by(() => {
		if (!activeDetail) return [];
		if (teamFilter === 'all') return activeDetail.shots;
		return activeDetail.shots.filter((s) => s.team_id === teamFilter);
	});

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
</script>

<div class="space-y-8">
	<!-- Match Selector & View Mode Toolbar -->
	<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-rule pb-5">
		<div class="flex items-center gap-2 flex-wrap">
			<span class="text-xs font-semibold text-muted mr-1">Match:</span>
			{#each matches as m}
				{@const isSelected = selectedMatchId === m.id}
				{@const matchLabel = `${m.home_team_name} ${m.home_score}–${m.away_score} ${m.away_team_name} (${m.season})`}
				<button
					type="button"
					onclick={() => switchMatch(m.id)}
					aria-pressed={isSelected}
					class="h-9 px-3.5 rounded-card text-xs font-semibold transition-colors border {isSelected ? 'bg-accent text-accent-ink border-accent' : 'bg-paper-2 text-ink-2 border-rule hover:text-ink'}"
				>
					{matchLabel}
				</button>
			{/each}
		</div>

		<div class="flex items-center gap-2 flex-wrap">
			<button
				type="button"
				onclick={() => {
					viewMode = 'shot_map';
					selectedShot = null;
				}}
				aria-pressed={viewMode === 'shot_map'}
				class="h-9 px-3.5 rounded-card text-xs font-semibold transition-colors border {viewMode === 'shot_map' ? 'bg-paper-3 text-accent-2 border-rule-2' : 'bg-paper-2 text-ink-2 border-rule hover:text-ink'}"
			>
				Shot map (xG)
			</button>
			<button
				type="button"
				onclick={() => {
					viewMode = 'pass_network';
					selectedShot = null;
				}}
				aria-pressed={viewMode === 'pass_network'}
				class="h-9 px-3.5 rounded-card text-xs font-semibold transition-colors border {viewMode === 'pass_network' ? 'bg-paper-3 text-accent-2 border-rule-2' : 'bg-paper-2 text-ink-2 border-rule hover:text-ink'}"
			>
				Passing network
			</button>
			{#if showBackLink}
				<a
					href="/lab"
					class="h-9 px-3.5 rounded-card bg-paper-2 hover:bg-paper-3 border border-rule text-xs font-semibold text-ink transition-colors inline-flex items-center"
				>
					Back to Data Lab
				</a>
			{/if}
		</div>
	</div>

	{#if isLoading}
		<div class="py-12 text-sm text-muted">Loading StatsBomb match telemetry…</div>
	{:else if activeDetail}
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
				<p class="text-sm font-bold text-ink mt-1 truncate">{activeDetail.venue}</p>
				<p class="text-muted num font-outlier">{activeDetail.match_date}</p>
			</div>
		</div>

		<!-- Interactive Pitch Stage -->
		<div class="grid grid-cols-1 lg:grid-cols-12 gap-10 items-start">
			<!-- 2D Football Pitch SVG (8 cols) -->
			<div class="lg:col-span-8 space-y-4">
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
								class="h-7 px-2.5 rounded-card transition-colors border {teamFilter === 'all' ? 'bg-paper-3 text-ink border-rule-2 font-semibold' : 'bg-paper-2 text-ink-2 border-rule'}"
							>
								All
							</button>
							<button
								type="button"
								onclick={() => activeDetail && (teamFilter = activeDetail.home_team_id)}
								aria-pressed={Boolean(activeDetail && teamFilter === activeDetail.home_team_id)}
								class="h-7 px-2.5 rounded-card transition-colors border whitespace-nowrap {activeDetail && teamFilter === activeDetail.home_team_id ? 'bg-paper-3 text-success border-rule-2 font-semibold' : 'bg-paper-2 text-ink-2 border-rule'}"
							>
								{homeName}
							</button>
							<button
								type="button"
								onclick={() => activeDetail && (teamFilter = activeDetail.away_team_id)}
								aria-pressed={Boolean(activeDetail && teamFilter === activeDetail.away_team_id)}
								class="h-7 px-2.5 rounded-card transition-colors border whitespace-nowrap {activeDetail && teamFilter === activeDetail.away_team_id ? 'bg-paper-3 text-accent-2 border-rule-2 font-semibold' : 'bg-paper-2 text-ink-2 border-rule'}"
							>
								{awayName}
							</button>
						{:else}
							<span class="text-accent-2 font-semibold">Pass volume & average positional nodes</span>
						{/if}
					</div>

					{#if viewMode === 'shot_map'}
						<div class="flex items-center gap-4 text-xs text-muted">
							<span class="text-success font-semibold">Goal</span>
							<span class="text-ink font-semibold">Saved</span>
							<span class="text-accent-2 font-semibold">Blocked</span>
							<span class="text-error font-semibold">Miss</span>
						</div>
					{/if}
				</div>

				<!-- Pitch SVG Container -->
				<svg
					viewBox="0 0 700 480"
					aria-label="StatsBomb 2D tactical event pitch"
					class="w-full h-auto border border-rule rounded-card bg-pitch"
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
						{#each filteredShots as shot}
							{@const cx = (shot.x / 100) * 670 + 15}
							{@const cy = (shot.y / 100) * 450 + 15}
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
								{#if shot.outcome === 'Goal'}
									<circle cx={cx} cy={cy} r={radius + 4} fill="none" stroke="var(--color-success)" stroke-width="2" opacity="0.6" />
								{/if}
								<circle
									cx={cx}
									cy={cy}
									r={radius}
									fill={color}
									stroke={isSelected ? 'var(--color-ink)' : 'var(--color-paper)'}
									stroke-width={isSelected ? '2.5' : '1.5'}
									opacity="0.9"
								/>
							</g>
						{/each}
					{:else}
						{#each activeDetail.pass_links as link}
							{@const srcNode = activeDetail.pass_nodes.find((n) => n.player_name === link.source)}
							{@const tgtNode = activeDetail.pass_nodes.find((n) => n.player_name === link.target)}
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
									stroke-opacity="0.6"
								/>
							{/if}
						{/each}

						{#each activeDetail.pass_nodes as node}
							{@const nx = (node.x / 100) * 670 + 15}
							{@const ny = (node.y / 100) * 450 + 15}
							<g>
								<circle cx={nx} cy={ny} r="14" fill="var(--color-paper-2)" stroke="var(--color-accent-2)" stroke-width="2" />
								<text
									x={nx}
									y={ny + 4}
									text-anchor="middle"
									fill="var(--color-ink)"
									font-size="10"
									font-weight="bold"
									font-family="var(--font-outlier)"
								>
									{node.jersey_number}
								</text>
								<text
									x={nx}
									y={ny + 24}
									text-anchor="middle"
									fill="var(--color-ink-2)"
									font-size="9"
									font-family="var(--font-body)"
								>
									{node.player_name}
								</text>
							</g>
						{/each}
					{/if}
				</svg>

				<div class="text-xs text-muted">
					{activeDetail.license_notice}
				</div>
			</div>

			<!-- Right Sidebar: Selected Shot or Telemetry Inspector (4 cols) -->
			<aside class="lg:col-span-4 space-y-6">
				{#if viewMode === 'shot_map'}
					<div class="border-t-2 border-rule-2 pt-5 space-y-4">
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
							<p class="text-xs text-muted">High-volume passing channels between Arsenal players.</p>
						</div>

						<div class="divide-y divide-rule text-xs">
							{#each activeDetail.pass_links as link}
								<div class="py-2.5 flex items-center justify-between">
									<span class="text-ink-2">{link.source} to {link.target}</span>
									<span class="font-bold text-accent-2 num font-outlier">{link.pass_count} passes</span>
								</div>
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
