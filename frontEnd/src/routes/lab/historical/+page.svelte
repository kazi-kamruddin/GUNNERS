<script lang="ts">
	import { CLUBS } from '$lib/stores/theme.svelte';
	import { fetchHistoricalMatchDetail } from '$lib/api/football';
	import type { HistoricalMatchDetail, ShotEvent, HistoricalMatchSummary } from '$lib/types/football';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	let selectedMatchId = $state<string>('hist_ars_barca_2011');
	let activeDetail = $state<HistoricalMatchDetail | null>(null);
	let viewMode = $state<'shot_map' | 'pass_network'>('shot_map');
	let teamFilter = $state<string>('all');
	let selectedShot = $state<ShotEvent | null>(null);
	let isLoading = $state(false);

	let isInitialized = false;

	$effect(() => {
		if (!isInitialized && data.detail) {
			activeDetail = data.detail;
			selectedMatchId = data.activeMatchId;
			isInitialized = true;
		}
	});

	async function switchMatch(matchId: string) {
		selectedMatchId = matchId;
		isLoading = true;
		selectedShot = null;
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
				return '#10B981'; // emerald-500
			case 'Saved':
				return '#0EA5E9'; // sky-500
			case 'Blocked':
				return '#F59E0B'; // amber-500
			default:
				return '#F43F5E'; // rose-500
		}
	}
</script>

<svelte:head>
	<title>Historical Tactical Analytics (StatsBomb) | Data Lab</title>
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 py-8 space-y-8">
	<!-- Page Header -->
	<div class="border-b border-[#1e2430] pb-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
		<div>
			<div class="inline-flex items-center gap-2 px-2.5 py-0.5 rounded text-[11px] font-semibold uppercase tracking-wider mb-2 bg-rose-500/10 text-rose-400 border border-rose-500/20 font-mono">
				StatsBomb Open Data Telemetry
			</div>
			<h1 class="text-2xl sm:text-3xl font-black text-white uppercase tracking-tight">Deep Tactical Event Visualizations</h1>
			<p class="text-xs sm:text-sm text-gray-400 mt-1">
				Examine coordinate-level shot maps, expected goals (xG), and passing network telemetry from iconic matches.
			</p>
		</div>

		<a
			href="/lab"
			class="px-3.5 py-2 rounded-lg bg-white/5 hover:bg-white/10 border border-[#1e2430] text-xs font-bold text-gray-300 transition self-start md:self-auto"
		>
			← Back to Standard Data Lab
		</a>
	</div>

	<!-- Match Selector & View Mode Toolbar -->
	<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-[#12161f] p-4 rounded-xl border border-[#1e2430]">
		<!-- Match Picker -->
		<div class="flex items-center gap-2 flex-wrap">
			<span class="text-xs uppercase font-bold text-gray-400 mr-1">Match:</span>
			{#each data.matches as m}
				{@const isSelected = selectedMatchId === m.id}
				<button
					type="button"
					onclick={() => switchMatch(m.id)}
					class="px-3 py-1.5 rounded-lg text-xs font-bold transition border {isSelected ? 'bg-red-600 text-white border-red-500' : 'bg-[#0d1017] text-gray-400 border-[#1e2430] hover:text-white'}"
				>
					{m.home_team_name} {m.home_score} - {m.away_score} {m.away_team_name} ({m.season})
				</button>
			{/each}
		</div>

		<!-- Mode Switcher -->
		<div class="flex items-center gap-1.5 bg-[#0d1017] p-1 rounded-lg border border-[#1e2430]">
			<button
				type="button"
				onclick={() => {
					viewMode = 'shot_map';
					selectedShot = null;
				}}
				class="px-3 py-1 rounded text-xs font-bold transition {viewMode === 'shot_map' ? 'bg-amber-400 text-black' : 'text-gray-400 hover:text-white'}"
			>
				Shot Map (xG)
			</button>
			<button
				type="button"
				onclick={() => {
					viewMode = 'pass_network';
					selectedShot = null;
				}}
				class="px-3 py-1 rounded text-xs font-bold transition {viewMode === 'pass_network' ? 'bg-amber-400 text-black' : 'text-gray-400 hover:text-white'}"
			>
				Passing Network
			</button>
		</div>
	</div>

	{#if activeDetail}
		<!-- Match Telemetry Overview Bar -->
		<div class="grid grid-cols-2 sm:grid-cols-4 gap-4 bg-[#12161f] p-4 rounded-xl border border-[#1e2430] text-center text-xs">
			<div>
				<p class="text-[10px] text-gray-500 uppercase font-mono">Home Total xG</p>
				<p class="text-lg font-black text-emerald-400 font-mono">{activeDetail.total_xg_home} xG</p>
				<p class="text-[10px] text-gray-400">({activeDetail.total_shots_home} shots)</p>
			</div>
			<div>
				<p class="text-[10px] text-gray-500 uppercase font-mono">Away Total xG</p>
				<p class="text-lg font-black text-amber-400 font-mono">{activeDetail.total_xg_away} xG</p>
				<p class="text-[10px] text-gray-400">({activeDetail.total_shots_away} shots)</p>
			</div>
			<div>
				<p class="text-[10px] text-gray-500 uppercase font-mono">Competition</p>
				<p class="text-xs font-bold text-white mt-1">{activeDetail.competition}</p>
				<p class="text-[10px] text-gray-400">{activeDetail.season}</p>
			</div>
			<div>
				<p class="text-[10px] text-gray-500 uppercase font-mono">Venue</p>
				<p class="text-xs font-bold text-white mt-1 truncate">{activeDetail.venue}</p>
				<p class="text-[10px] text-gray-400">{activeDetail.match_date}</p>
			</div>
		</div>

		<!-- Interactive Pitch Stage -->
		<div class="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
			<!-- 2D Football Pitch SVG -->
			<div class="lg:col-span-2 p-6 rounded-2xl border border-[#1e2430] bg-[#0c120c] relative shadow-2xl overflow-hidden flex flex-col items-center">
				<div class="w-full flex items-center justify-between mb-4 text-xs font-mono">
					<div class="flex items-center gap-2">
						{#if viewMode === 'shot_map'}
							<span class="text-gray-400 uppercase text-[10px] font-bold">Filter Team:</span>
							<button
								type="button"
								onclick={() => (teamFilter = 'all')}
								class="text-[10px] px-2 py-0.5 rounded transition {teamFilter === 'all' ? 'bg-white text-black font-bold' : 'bg-black/40 text-gray-400'}"
							>
								All
							</button>
							<button
								type="button"
								onclick={() => activeDetail && (teamFilter = activeDetail.home_team_id)}
								class="text-[10px] px-2 py-0.5 rounded transition {activeDetail && teamFilter === activeDetail.home_team_id ? 'bg-emerald-400 text-black font-bold' : 'bg-black/40 text-gray-400'}"
							>
								{activeDetail?.home_team_name}
							</button>
							<button
								type="button"
								onclick={() => activeDetail && (teamFilter = activeDetail.away_team_id)}
								class="text-[10px] px-2 py-0.5 rounded transition {activeDetail && teamFilter === activeDetail.away_team_id ? 'bg-amber-400 text-black font-bold' : 'bg-black/40 text-gray-400'}"
							>
								{activeDetail?.away_team_name}
							</button>
						{:else}
							<span class="text-emerald-400 text-[10px] font-bold uppercase">Pass Volume & Positional Nodes</span>
						{/if}
					</div>

					<div class="flex items-center gap-3 text-[10px] text-gray-400">
						{#if viewMode === 'shot_map'}
							<span class="flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-emerald-400"></span> Goal</span>
							<span class="flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-sky-400"></span> Saved</span>
							<span class="flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-amber-400"></span> Blocked</span>
							<span class="flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-rose-400"></span> Miss</span>
						{/if}
					</div>
				</div>

				<!-- Pitch SVG Container -->
				<svg viewBox="0 0 700 480" class="w-full h-auto border-2 border-emerald-900/40 rounded-xl bg-[#091509]">
					<!-- Pitch Markings -->
					<!-- Boundary -->
					<rect x="15" y="15" width="670" height="450" fill="none" stroke="#166534" stroke-width="2" />
					<!-- Halfway Line -->
					<line x1="350" y1="15" x2="350" y2="465" stroke="#166534" stroke-width="2" />
					<!-- Center Circle -->
					<circle cx="350" cy="240" r="55" fill="none" stroke="#166534" stroke-width="2" />
					<circle cx="350" cy="240" r="3" fill="#166534" />

					<!-- Left Penalty Box -->
					<rect x="15" y="120" width="115" height="240" fill="none" stroke="#166534" stroke-width="2" />
					<rect x="15" y="175" width="40" height="130" fill="none" stroke="#166534" stroke-width="2" />
					<circle cx="85" cy="240" r="2.5" fill="#166534" />

					<!-- Right Penalty Box -->
					<rect x="570" y="120" width="115" height="240" fill="none" stroke="#166534" stroke-width="2" />
					<rect x="645" y="175" width="40" height="130" fill="none" stroke="#166534" stroke-width="2" />
					<circle cx="615" cy="240" r="2.5" fill="#166534" />

					{#if viewMode === 'shot_map'}
						<!-- Render Shots -->
						{#each filteredShots as shot}
							{@const cx = (shot.x / 100) * 670 + 15}
							{@const cy = (shot.y / 100) * 450 + 15}
							{@const radius = Math.max(7, shot.xg * 24)}
							{@const color = getShotColor(shot.outcome)}
							{@const isSelected = selectedShot?.id === shot.id}
							<!-- svelte-ignore a11y_click_events_have_key_events -->
							<!-- svelte-ignore a11y_no_static_element_interactions -->
							<g
								onclick={() => (selectedShot = shot)}
								class="cursor-pointer transition transform hover:scale-125"
							>
								{#if shot.outcome === 'Goal'}
									<circle cx={cx} cy={cy} r={radius + 4} fill="none" stroke="#10B981" stroke-width="2" opacity="0.6" class="animate-ping" />
								{/if}
								<circle
									cx={cx}
									cy={cy}
									r={radius}
									fill={color}
									stroke={isSelected ? '#FFFFFF' : '#000000'}
									stroke-width={isSelected ? '2.5' : '1.5'}
									opacity="0.9"
								/>
							</g>
						{/each}
					{:else}
						<!-- Render Pass Network Links -->
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
									stroke="#F59E0B"
									stroke-width={Math.max(1.5, link.pass_count / 4)}
									stroke-opacity="0.6"
								/>
							{/if}
						{/each}

						<!-- Render Pass Nodes -->
						{#each activeDetail.pass_nodes as node}
							{@const nx = (node.x / 100) * 670 + 15}
							{@const ny = (node.y / 100) * 450 + 15}
							<g class="cursor-pointer">
								<circle cx={nx} cy={ny} r="14" fill="#1e2430" stroke="#F59E0B" stroke-width="2" />
								<text
									x={nx}
									y={ny + 4}
									text-anchor="middle"
									fill="#FFFFFF"
									font-size="10"
									font-weight="bold"
									font-family="monospace"
								>
									{node.jersey_number}
								</text>
								<text
									x={nx}
									y={ny + 24}
									text-anchor="middle"
									fill="#9CA3AF"
									font-size="9"
									font-family="sans-serif"
								>
									{node.player_name}
								</text>
							</g>
						{/each}
					{/if}
				</svg>

				<!-- License Notice directly under pitch -->
				<div class="mt-4 text-[10px] text-gray-500 font-mono text-center">
					⚡ {activeDetail.license_notice}
				</div>
			</div>

			<!-- Right Sidebar: Selected Shot or Telemetry Inspector -->
			<div class="space-y-4">
				{#if viewMode === 'shot_map'}
					<div class="p-5 rounded-2xl border border-[#1e2430] bg-[#12161f] space-y-4">
						<div class="border-b border-[#1e2430] pb-3">
							<h3 class="text-sm font-bold text-white uppercase tracking-wider">Shot Event Inspector</h3>
							<p class="text-[11px] text-gray-400">Click any shot circle on the pitch to examine telemetry</p>
						</div>

						{#if selectedShot}
							<div class="space-y-3 font-mono text-xs">
								<div class="flex items-center justify-between py-1 border-b border-[#1e2430]">
									<span class="text-gray-400">Shooter:</span>
									<span class="font-bold text-white">{selectedShot.player_name}</span>
								</div>
								<div class="flex items-center justify-between py-1 border-b border-[#1e2430]">
									<span class="text-gray-400">Team:</span>
									<span class="text-amber-400">{selectedShot.team_name}</span>
								</div>
								<div class="flex items-center justify-between py-1 border-b border-[#1e2430]">
									<span class="text-gray-400">Minute:</span>
									<span class="text-white">{selectedShot.minute}'{selectedShot.second}"</span>
								</div>
								<div class="flex items-center justify-between py-1 border-b border-[#1e2430]">
									<span class="text-gray-400">Outcome:</span>
									<span class="font-bold {selectedShot.outcome === 'Goal' ? 'text-emerald-400' : 'text-gray-200'}">
										{selectedShot.outcome}
									</span>
								</div>
								<div class="flex items-center justify-between py-1 border-b border-[#1e2430]">
									<span class="text-gray-400">Expected Goals (xG):</span>
									<span class="font-bold text-emerald-400 text-sm">{selectedShot.xg}</span>
								</div>
								<div class="flex items-center justify-between py-1 border-b border-[#1e2430]">
									<span class="text-gray-400">Body Part:</span>
									<span class="text-gray-300">{selectedShot.body_part}</span>
								</div>
								<div class="flex items-center justify-between py-1">
									<span class="text-gray-400">Play Type:</span>
									<span class="text-gray-300">{selectedShot.shot_type}</span>
								</div>
							</div>
						{:else}
							<div class="py-12 text-center text-gray-500 text-xs">
								Select a shot on the pitch to inspect expected goal value (xG) and shooting coordinates.
							</div>
						{/if}
					</div>
				{:else}
					<div class="p-5 rounded-2xl border border-[#1e2430] bg-[#12161f] space-y-4">
						<div class="border-b border-[#1e2430] pb-3">
							<h3 class="text-sm font-bold text-white uppercase tracking-wider">Passing Combinations</h3>
							<p class="text-[11px] text-gray-400">Key passing channels between players</p>
						</div>

						<div class="divide-y divide-[#1e2430] text-xs font-mono">
							{#each activeDetail.pass_links as link}
								<div class="py-2 flex items-center justify-between">
									<span class="text-gray-300">{link.source} ➔ {link.target}</span>
									<span class="font-bold text-amber-400">{link.pass_count} passes</span>
								</div>
							{/each}
						</div>
					</div>
				{/if}

				<!-- Data Lab Export Banner -->
				<div class="p-4 rounded-xl border border-[#1e2430] bg-[#0d1017] text-xs text-gray-400 space-y-2">
					<p class="font-bold text-white">StatsBomb Open Data Architecture</p>
					<p class="text-[11px] leading-relaxed">
						All event coordinates and xG metrics comply with the open-data schema conventions, preserving academic and portfolio integrity.
					</p>
				</div>
			</div>
		</div>
	{/if}
</div>
