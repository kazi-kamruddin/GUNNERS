<script lang="ts">
	import { CLUBS, themeState } from '$lib/stores/theme.svelte';
	import type { ActionData, PageData } from './$types';

	let { data, form }: { data: PageData; form: ActionData } = $props();

	let currentClub = $derived(CLUBS.arsenal);

	$effect(() => {
		if (data.profile?.favorite_club_id) {
			themeState.setFavoriteClub(data.profile.favorite_club_id);
		}
	});
</script>

<svelte:head>
	<title>Supporter Profile | GUNNERS</title>
</svelte:head>

<div class="container py-12 max-w-2xl space-y-10">
	<div class="border-t-2 border-rule-2 pt-8 space-y-8">
		<div class="flex items-end justify-between pb-6 border-b border-rule gap-4 flex-wrap">
			<div class="space-y-2">
				<h1>Supporter profile</h1>
				<p class="text-sm text-ink-2">Manage your identity, club affiliation, and bio.</p>
			</div>
			<span class="text-xs font-bold text-accent-2">
				{currentClub.name}
			</span>
		</div>

		{#if form?.success}
			<div class="p-3 rounded-card bg-paper-2 border border-rule text-success text-xs">
				Profile updated.
			</div>
		{/if}

		{#if form?.error}
			<div class="p-3 rounded-card bg-paper-2 border border-rule text-error text-xs">
				{form.error}
			</div>
		{/if}

		<dl class="space-y-3 text-xs border-b border-rule pb-6">
			<div class="flex justify-between py-1.5 border-b border-rule">
				<dt class="text-muted">Email</dt>
				<dd class="text-ink num font-outlier">{data.user?.email}</dd>
			</div>
			<div class="flex justify-between py-1.5 border-b border-rule">
				<dt class="text-muted">Username</dt>
				<dd class="text-ink font-semibold">@{data.profile?.username || 'unnamed'}</dd>
			</div>
			<div class="flex justify-between py-1.5">
				<dt class="text-muted">User ID</dt>
				<dd class="text-muted num font-outlier">{data.user?.id}</dd>
			</div>
		</dl>

		<div class="space-y-5">
			<h2 class="text-lg font-bold text-ink">Edit profile</h2>

			<form method="POST" action="?/updateProfile" class="space-y-4">
				<div>
					<label for="display_name" class="block text-xs font-semibold text-ink-2 mb-1">
						Display name
					</label>
					<input
						id="display_name"
						name="display_name"
						type="text"
						required
						value={data.profile?.display_name || ''}
						class="w-full h-10 bg-paper-2 border border-rule rounded-card px-3 text-sm text-ink"
					/>
				</div>

				<div>
					<label for="bio" class="block text-xs font-semibold text-ink-2 mb-1">
						Bio & tactical focus
					</label>
					<textarea
						id="bio"
						name="bio"
						rows="3"
						placeholder="Share your favorite Arsenal era, tactical focus, or matchday routine…"
						class="w-full bg-paper-2 border border-rule rounded-card p-3 text-sm text-ink placeholder-muted"
					>{data.profile?.bio || ''}</textarea>
				</div>

				<div>
					<span class="block text-xs font-semibold text-ink-2 mb-1">
						Supporter affiliation
					</span>
					<input
						type="hidden"
						name="favorite_club_id"
						value="arsenal"
					/>
					<div class="w-full h-10 bg-paper-2 border border-rule rounded-card px-3 text-sm text-ink flex items-center">
						<span>Arsenal FC, Emirates Stadium</span>
					</div>
				</div>

				<div class="pt-2">
					<button
						type="submit"
						class="h-10 px-5 bg-accent hover:opacity-95 text-accent-ink font-semibold text-sm rounded-card transition-opacity"
					>
						Save changes
					</button>
				</div>
			</form>
		</div>
	</div>

	<div class="border-t border-rule pt-6 flex items-center justify-between gap-4">
		<div class="space-y-0.5">
			<h2 class="text-base font-bold text-ink">Sign out</h2>
			<p class="text-xs text-muted">End your current session on this device.</p>
		</div>
		<form method="POST" action="/auth/signout">
			<button
				type="submit"
				class="h-9 px-4 rounded-card bg-paper-2 hover:bg-paper-3 text-ink-2 hover:text-ink border border-rule text-xs font-semibold transition-colors"
			>
				Sign out
			</button>
		</form>
	</div>
</div>
