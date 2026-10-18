<script lang="ts">
	import type { ActionData } from './$types';

	let { form }: { form: ActionData } = $props();
</script>

<svelte:head>
	<title>Sign In | GUNNERS Reborn</title>
</svelte:head>

<div class="max-w-md mx-auto px-6 py-12">
	<div class="bg-[#12161f] border border-[#1e2430] rounded-xl p-8 shadow-sm">
		<h1 class="text-2xl font-bold text-white mb-2">Welcome Back</h1>
		<p class="text-xs text-gray-400 mb-6">Enter your email and password to access your fan account.</p>

		{#if form?.error}
			<div class="mb-4 p-3 rounded bg-red-950/60 border border-red-800/60 text-red-300 text-xs">
				{form.error}
			</div>
		{/if}

		<form method="POST" class="space-y-4">
			<div>
				<label for="email" class="block text-xs font-semibold text-gray-300 uppercase tracking-wider mb-1">
					Email
				</label>
				<input
					id="email"
					name="email"
					type="email"
					required
					value={form?.email ?? ''}
					placeholder="fan@example.com"
					class="w-full bg-[#0a0c10] border border-[#1e2430] rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-red-500"
				/>
			</div>

			<div>
				<label for="password" class="block text-xs font-semibold text-gray-300 uppercase tracking-wider mb-1">
					Password
				</label>
				<input
					id="password"
					name="password"
					type="password"
					required
					placeholder="••••••••"
					class="w-full bg-[#0a0c10] border border-[#1e2430] rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-red-500"
				/>
			</div>

			<button
				type="submit"
				class="w-full py-2.5 px-4 bg-red-600 hover:bg-red-500 text-white font-semibold text-sm rounded-lg transition mt-4"
			>
				Sign In
			</button>
		</form>

		<div class="mt-6 text-center text-xs text-gray-400">
			Don't have an account yet?
			<a href="/signup" class="text-red-400 hover:underline font-semibold ml-1">Join Club</a>
		</div>
	</div>
</div>
