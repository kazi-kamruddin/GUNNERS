<script lang="ts">
	import type { ActionData } from './$types';

	let { form }: { form: ActionData } = $props();
</script>

<svelte:head>
	<title>Sign In | GUNNERS</title>
</svelte:head>

<div class="container py-16 max-w-md">
	<div class="border-t-2 border-rule-2 pt-8 space-y-6">
		<div class="space-y-2">
			<h1>Welcome back</h1>
			<p class="text-sm text-ink-2">Enter your email and password to access your Arsenal supporter account.</p>
		</div>

		{#if form?.error}
			<div class="p-3 rounded-card bg-paper-2 border border-rule text-error text-xs">
				{form.error}
			</div>
		{/if}

		<form method="POST" class="space-y-4">
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
					placeholder="Enter password"
					class="w-full h-10 bg-paper-2 border border-rule rounded-card px-3 text-sm text-ink placeholder-muted"
				/>
			</div>

			<button
				type="submit"
				class="w-full h-10 px-4 bg-accent hover:opacity-95 text-accent-ink font-semibold text-sm rounded-card transition-opacity mt-2"
			>
				Sign in
			</button>
		</form>

		<div class="pt-4 border-t border-rule text-xs text-muted">
			Don’t have an account yet?
			<a href="/signup" class="text-accent hover:text-ink font-semibold ml-1 transition-colors">Join club</a>
		</div>
	</div>
</div>
