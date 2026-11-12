<script lang="ts">
	import type { ActionData } from './$types';

	let { form }: { form: ActionData } = $props();
</script>

<svelte:head>
	<title>Join Club | GUNNERS</title>
</svelte:head>

<div class="container py-16 max-w-md">
	<div class="border-t-2 border-rule-2 pt-8 space-y-6">
		<div class="space-y-2">
			<h1>Create supporter account</h1>
			<p class="text-sm text-ink-2">Register your Arsenal supporter identity to publish tactics, insights, and Terrace debriefs.</p>
		</div>

		{#if form?.error}
			<div class="p-3 rounded-card bg-paper-2 border border-rule text-error text-xs">
				{form.error}
			</div>
		{/if}

		<form method="POST" class="space-y-4">
			<div>
				<label for="username" class="block text-xs font-semibold text-ink-2 mb-1">
					Username
				</label>
				<input
					id="username"
					name="username"
					type="text"
					required
					value={form?.username ?? ''}
					placeholder="e.g. gunner_legend"
					class="w-full h-10 bg-paper-2 border border-rule rounded-card px-3 text-sm text-ink placeholder-muted"
				/>
			</div>

			<div>
				<label for="display_name" class="block text-xs font-semibold text-ink-2 mb-1">
					Display name
				</label>
				<input
					id="display_name"
					name="display_name"
					type="text"
					value={form?.displayName ?? ''}
					placeholder="e.g. Thierry H."
					class="w-full h-10 bg-paper-2 border border-rule rounded-card px-3 text-sm text-ink placeholder-muted"
				/>
			</div>

			<div>
				<label for="email" class="block text-xs font-semibold text-ink-2 mb-1">
					Email
				</label>
				<input
					id="email"
					name="email"
					type="email"
					required
					value={form?.email ?? ''}
					placeholder="supporter@example.com"
					class="w-full h-10 bg-paper-2 border border-rule rounded-card px-3 text-sm text-ink placeholder-muted"
				/>
			</div>

			<div>
				<label for="password" class="block text-xs font-semibold text-ink-2 mb-1">
					Password
				</label>
				<input
					id="password"
					name="password"
					type="password"
					required
					minlength="6"
					placeholder="Minimum 6 characters"
					class="w-full h-10 bg-paper-2 border border-rule rounded-card px-3 text-sm text-ink placeholder-muted"
				/>
			</div>

			<div>
				<label for="club-display" class="block text-xs font-semibold text-ink-2 mb-1">
					Supporter affiliation
				</label>
				<input
					type="hidden"
					name="favorite_club_id"
					value="arsenal"
				/>
				<div id="club-display" class="w-full h-10 bg-paper-2 border border-rule rounded-card px-3 text-sm text-ink flex items-center">
					<span>Arsenal FC (The Gunners)</span>
				</div>
				<span class="block text-xs text-muted mt-1">Platform membership is exclusively dedicated to Arsenal Football Club supporters.</span>
			</div>

			<button
				type="submit"
				class="w-full h-10 px-4 bg-accent hover:opacity-95 text-accent-ink font-semibold text-sm rounded-card transition-opacity mt-2"
			>
				Create account
			</button>
		</form>

		<div class="pt-4 border-t border-rule text-xs text-muted">
			Already have an account?
			<a href="/login" class="text-accent hover:text-ink font-semibold ml-1 transition-colors">Sign in</a>
		</div>
	</div>
</div>
