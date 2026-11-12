<script lang="ts">
	import HistoricalPitchExplorer from '$lib/components/HistoricalPitchExplorer.svelte';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
</script>

<svelte:head>
	<title>Historical Tactical Analytics (StatsBomb) | GUNNERS</title>
</svelte:head>

<div class="container py-12 space-y-10">
	<div class="border-b-2 border-rule-2 pb-8 space-y-3">
		<h1>Deep tactical event visualizations</h1>
		<p class="lead text-ink-2">
			Examine coordinate-level shot maps, expected goals (xG), and passing network telemetry from landmark Arsenal fixtures.
		</p>
	</div>

	<HistoricalPitchExplorer
		matches={data.matches}
		initialDetail={data.detail}
		initialMatchId={data.activeMatchId}
		showBackLink={true}
	/>
</div>
