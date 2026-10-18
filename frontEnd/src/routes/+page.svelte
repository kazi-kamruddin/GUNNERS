<script lang="ts">
	interface Club {
		id: string;
		name: string;
		short_name: string;
		league: string;
		primary_color: string;
		secondary_color: string;
		accent_color: string;
	}

	const clubs: Club[] = [
		{
			id: 'arsenal',
			name: 'Arsenal FC',
			short_name: 'Arsenal',
			league: 'Premier League',
			primary_color: '#EF0107',
			secondary_color: '#FFFFFF',
			accent_color: '#9C824A'
		},
		{
			id: 'real-madrid',
			name: 'Real Madrid CF',
			short_name: 'Real Madrid',
			league: 'La Liga',
			primary_color: '#00529F',
			secondary_color: '#FFFFFF',
			accent_color: '#EEB028'
		},
		{
			id: 'barcelona',
			name: 'FC Barcelona',
			short_name: 'Barcelona',
			league: 'La Liga',
			primary_color: '#A50044',
			secondary_color: '#004D98',
			accent_color: '#EDBB00'
		},
		{
			id: 'milan',
			name: 'AC Milan',
			short_name: 'AC Milan',
			league: 'Serie A',
			primary_color: '#FB090B',
			secondary_color: '#000000',
			accent_color: '#C0C0C0'
		}
	];

	let selectedClub = $state<Club>(clubs[0]);
</script>

<div class="max-w-7xl mx-auto px-6 py-12">
	<!-- Hero Section -->
	<section class="relative rounded-2xl p-8 md:p-12 overflow-hidden border border-[#1e2430] bg-gradient-to-br from-[#12161f] via-[#151a24] to-[#0d1017]">
		<div class="absolute -right-16 -bottom-16 w-96 h-96 rounded-full blur-3xl opacity-20 pointer-events-none transition-all duration-700"
			style="background-color: {selectedClub.primary_color}">
		</div>

		<div class="relative z-10 max-w-2xl">
			<div class="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wider mb-6 bg-white/5 border border-white/10 text-gray-300">
				<span class="w-2 h-2 rounded-full" style="background-color: {selectedClub.primary_color}"></span>
				<span>{selectedClub.name} • {selectedClub.league}</span>
			</div>

			<h1 class="text-4xl md:text-5xl font-black tracking-tight text-white mb-4">
				Football Analytics.<br />
				<span class="bg-gradient-to-r from-red-500 via-amber-400 to-amber-200 bg-clip-text text-transparent">
					Anchored in Evidence.
				</span>
			</h1>

			<p class="text-base text-gray-400 mb-8 leading-relaxed">
				Explore verified metrics, create shareable visual insights in the Data Lab, and debate rivals on The Terrace with real data.
			</p>

			<div class="flex flex-wrap items-center gap-4">
				<a href="/lab" class="px-5 py-2.5 rounded-lg bg-red-600 hover:bg-red-500 font-semibold text-sm text-white transition shadow-md">
					Launch Data Lab →
				</a>
				<a href="/terrace" class="px-5 py-2.5 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 text-sm font-semibold text-gray-200 transition">
					Browse The Terrace
				</a>
			</div>
		</div>
	</section>

	<!-- Club Universe Switcher Preview -->
	<section class="mt-12">
		<div class="flex items-center justify-between mb-6">
			<div>
				<h2 class="text-xl font-bold text-white">Club Universe</h2>
				<p class="text-xs text-gray-400">Select any of the 4 foundation clubs to view themed analytics</p>
			</div>
			<span class="text-xs font-mono text-gray-500">Milestone 1 Preview</span>
		</div>

		<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
			{#each clubs as club}
				<button
					type="button"
					onclick={() => selectedClub = club}
					class="p-5 rounded-xl border text-left transition-all duration-300 relative group overflow-hidden {selectedClub.id === club.id ? 'border-white/30 bg-[#161c28]' : 'border-[#1e2430] bg-[#12161f]/60 hover:border-gray-700'}"
				>
					<div class="w-3 h-3 rounded-full mb-3" style="background-color: {club.primary_color}"></div>
					<h3 class="font-bold text-white group-hover:text-red-400 transition">{club.name}</h3>
					<p class="text-xs text-gray-400 mt-1">{club.league}</p>
					{#if selectedClub.id === club.id}
						<div class="mt-3 text-[11px] font-semibold text-amber-400 flex items-center gap-1">
							<span>Active Viewing Club</span>
						</div>
					{/if}
				</button>
			{/each}
		</div>
	</section>
</div>
