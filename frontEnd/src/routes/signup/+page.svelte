<script lang="ts">
	import type { ActionData } from './$types';

	let { form }: { form: ActionData } = $props();
</script>

<svelte:head>
	<title>Join Club | GUNNERS Reborn</title>
</svelte:head>

<div class="max-w-md mx-auto px-6 py-12">
	<div class="bg-[#12161f] border border-[#1e2430] rounded-xl p-8 shadow-sm">
		<h1 class="text-2xl font-bold text-white mb-2">Create Fan Account</h1>
		<p class="text-xs text-gray-400 mb-6">Choose your club affiliation and enter your credentials.</p>

		{#if form?.error}
			<div class="mb-4 p-3 rounded bg-red-950/60 border border-red-800/60 text-red-300 text-xs">
				{form.error}
			</div>
		{/if}

		<form method="POST" class="space-y-4">
			<div>
				<label for="username" class="block text-xs font-semibold text-gray-300 uppercase tracking-wider mb-1">
					Username
				</label>
				<input
					id="username"
					name="username"
					type="text"
					required
					value={form?.username ?? ''}
					placeholder="e.g. gunner_legend"
					class="w-full bg-[#0a0c10] border border-[#1e2430] rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-red-500"
				/>
			</div>

			<div>
				<label for="display_name" class="block text-xs font-semibold text-gray-300 uppercase tracking-wider mb-1">
					Display Name
				</label>
				<input
					id="display_name"
					name="display_name"
					type="text"
					value={form?.displayName ?? ''}
					placeholder="e.g. Thierry H."
					class="w-full bg-[#0a0c10] border border-[#1e2430] rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-red-500"
				/>
			</div>

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
					minlength="6"
					placeholder="••••••••"
					class="w-full bg-[#0a0c10] border border-[#1e2430] rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-red-500"
				/>
			</div>

			<div>
				<label for="club-display" class="block text-xs font-semibold text-gray-300 uppercase tracking-wider mb-1">
					Supporter Affiliation
				</label>
				<input
					type="hidden"
					name="favorite_club_id"
					value="arsenal"
				/>
				<div id="club-display" class="w-full bg-[#0a0c10] border border-[#1e2430] rounded-lg px-3 py-2 text-sm text-white flex items-center gap-2">
					<span class="w-2.5 h-2.5 rounded-full bg-red-600"></span>
					<span>Arsenal FC (The Gunners)</span>
				</div>
				<span class="block text-[11px] text-gray-500 mt-1">Platform membership is exclusively dedicated to Arsenal Football Club supporters.</span>
			</div>

			<button
				type="submit"
				class="w-full py-2.5 px-4 bg-red-600 hover:bg-red-500 text-white font-semibold text-sm rounded-lg transition mt-4"
			>
				Create Account
			</button>
		</form>

		<div class="mt-6 text-center text-xs text-gray-400">
			Already have an account?
			<a href="/login" class="text-red-400 hover:underline font-semibold ml-1">Sign In</a>
		</div>
	</div>
</div>
