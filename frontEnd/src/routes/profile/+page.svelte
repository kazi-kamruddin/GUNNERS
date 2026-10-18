<script lang="ts">
	import { CLUBS, themeState } from '$lib/stores/theme.svelte';
	import type { ActionData, PageData } from './$types';

	let { data, form }: { data: PageData; form: ActionData } = $props();

	const clubList = Object.values(CLUBS);
	let currentClub = $derived(CLUBS[data.profile?.favorite_club_id || 'arsenal'] || CLUBS.arsenal);

	// Sync themeState favorite club on load
	$effect(() => {
		if (data.profile?.favorite_club_id) {
			themeState.setFavoriteClub(data.profile.favorite_club_id);
		}
	});
</script>

<svelte:head>
	<title>Fan Profile | GUNNERS Reborn</title>
</svelte:head>

<div class="max-w-2xl mx-auto px-6 py-12">
	<div class="bg-[#12161f] border border-[#1e2430] rounded-xl p-8 mb-6">
		<div class="flex items-center justify-between pb-6 border-b border-[#1e2430] mb-6">
			<div>
				<h1 class="text-2xl font-bold text-white">Supporter Profile</h1>
				<p class="text-xs text-gray-400">Manage your identity, club affiliation, and settings.</p>
			</div>
			<div class="flex items-center gap-2 px-3 py-1.5 rounded-full border border-white/10 bg-white/5 text-xs">
				<span class="w-2.5 h-2.5 rounded-full" style="background-color: {currentClub.primary_color}"></span>
				<span class="font-bold text-white">{currentClub.name}</span>
			</div>
		</div>

		{#if form?.success}
			<div class="mb-4 p-3 rounded bg-green-950/60 border border-green-800/60 text-green-300 text-xs">
				Profile updated successfully!
			</div>
		{/if}

		{#if form?.error}
			<div class="mb-4 p-3 rounded bg-red-950/60 border border-red-800/60 text-red-300 text-xs">
				{form.error}
			</div>
		{/if}

		<div class="space-y-4 mb-8 text-sm">
			<div class="flex justify-between py-2 border-b border-[#1e2430]">
				<span class="text-gray-400">Email:</span>
				<span class="text-white font-mono">{data.user?.email}</span>
			</div>
			<div class="flex justify-between py-2 border-b border-[#1e2430]">
				<span class="text-gray-400">Username:</span>
				<span class="text-white font-semibold">@{data.profile?.username || 'unnamed'}</span>
			</div>
			<div class="flex justify-between py-2 border-b border-[#1e2430]">
				<span class="text-gray-400">User ID:</span>
				<span class="text-gray-400 font-mono text-xs">{data.user?.id}</span>
			</div>
		</div>

		<h2 class="text-lg font-bold text-white mb-4">Edit Profile</h2>

		<form method="POST" action="?/updateProfile" class="space-y-4">
			<div>
				<label for="display_name" class="block text-xs font-semibold text-gray-300 uppercase tracking-wider mb-1">
					Display Name
				</label>
				<input
					id="display_name"
					name="display_name"
					type="text"
					required
					value={data.profile?.display_name || ''}
					class="w-full bg-[#0a0c10] border border-[#1e2430] rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-red-500"
				/>
			</div>

			<div>
				<label for="bio" class="block text-xs font-semibold text-gray-300 uppercase tracking-wider mb-1">
					Bio / About
				</label>
				<textarea
					id="bio"
					name="bio"
					rows="3"
					placeholder="A few words about your football passion..."
					class="w-full bg-[#0a0c10] border border-[#1e2430] rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-red-500"
				>{data.profile?.bio || ''}</textarea>
			</div>

			<div>
				<label for="favorite_club_id" class="block text-xs font-semibold text-gray-300 uppercase tracking-wider mb-1">
					Permanent Favorite Club
				</label>
				<select
					id="favorite_club_id"
					name="favorite_club_id"
					class="w-full bg-[#0a0c10] border border-[#1e2430] rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-red-500"
				>
					{#each clubList as club}
						<option value={club.id} selected={data.profile?.favorite_club_id === club.id}>
							{club.name} ({club.league})
						</option>
					{/each}
				</select>
			</div>

			<div class="flex items-center gap-4 pt-2">
				<button
					type="submit"
					class="py-2.5 px-5 bg-red-600 hover:bg-red-500 text-white font-semibold text-sm rounded-lg transition"
				>
					Save Changes
				</button>
			</div>
		</form>
	</div>

	<div class="p-6 rounded-xl border border-[#1e2430] bg-[#12161f] flex items-center justify-between">
		<div>
			<h3 class="text-sm font-bold text-white">Sign Out</h3>
			<p class="text-xs text-gray-400">End your current session on this device.</p>
		</div>
		<form method="POST" action="/auth/signout">
			<button
				type="submit"
				class="py-2 px-4 rounded bg-white/5 hover:bg-white/10 text-gray-300 hover:text-white border border-white/10 text-xs font-semibold transition"
			>
				Sign Out
			</button>
		</form>
	</div>
</div>
