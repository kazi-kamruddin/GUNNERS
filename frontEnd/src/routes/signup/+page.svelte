<script lang="ts">
	import type { PageProps } from './$types';

	let { data, form }: PageProps = $props();

	let isGoogleLoading = $state(false);
	let oauthError = $state('');
	const googleLabel = $derived(isGoogleLoading ? 'Connecting to Google…' : 'Continue with Google');

	async function handleGoogleSignUp() {
		oauthError = '';
		isGoogleLoading = true;
		try {
			const { error } = await data.supabase.auth.signInWithOAuth({
				provider: 'google',
				options: {
					redirectTo: `${window.location.origin}/auth/callback`
				}
			});
			if (error) {
				oauthError = error.message;
				isGoogleLoading = false;
			}
		} catch (err) {
			oauthError = err instanceof Error ? err.message : 'Unable to start Google sign-up.';
			isGoogleLoading = false;
		}
	}
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

		{#if form?.error || oauthError}
			<div class="p-3 rounded-card bg-paper-2 border border-rule text-error text-xs">
				{form?.error || oauthError}
			</div>
		{/if}

		{#if form?.needsEmailVerification}
			<div class="border-t border-rule pt-4 space-y-3">
				<h2 class="text-base font-bold text-success">Check your inbox to verify</h2>
				<p class="text-sm text-ink-2 leading-relaxed">
					We sent a confirmation link to <strong class="text-ink">{form.email}</strong>. Open that email to activate your account before signing in.
				</p>
				<a
					href="/login"
					class="inline-flex items-center h-9 px-4 rounded-card bg-accent text-accent-ink font-semibold text-xs hover:opacity-95 transition-opacity whitespace-nowrap"
				>
					Proceed to sign in
				</a>
			</div>
		{:else}
			<button
				type="button"
				onclick={handleGoogleSignUp}
				disabled={isGoogleLoading}
				class="w-full h-10 px-4 bg-paper-2 hover:bg-paper-3 border border-rule rounded-card text-sm font-semibold text-ink inline-flex items-center justify-center gap-2.5 transition-colors whitespace-nowrap"
			>
				<svg class="w-4 h-4 shrink-0" viewBox="0 0 24 24" aria-hidden="true">
					<path
						fill="currentColor"
						d="M21.805 10.023H12.2v3.955h5.523c-.238 1.271-.955 2.348-2.036 3.07v2.55h3.296c1.928-1.775 3.04-4.388 3.04-7.49 0-.7-.063-1.39-.218-2.085z"
					/>
					<path
						fill="currentColor"
						d="M12.2 22c2.755 0 5.065-.913 6.753-2.472l-3.296-2.55c-.913.612-2.082.974-3.457.974-2.658 0-4.909-1.795-5.713-4.208H3.08v2.634C4.756 19.708 8.21 22 12.2 22z"
					/>
					<path
						fill="currentColor"
						d="M6.487 13.744A5.95 5.95 0 016.174 12c0-.606.112-1.193.313-1.744V7.622H3.08A9.978 9.978 0 002 12c0 1.613.387 3.139 1.08 4.378l3.407-2.634z"
					/>
					<path
						fill="currentColor"
						d="M12.2 6.048c1.498 0 2.843.515 3.9 1.525l2.926-2.926C17.26 2.996 14.95 2 12.2 2 8.21 2 4.756 4.292 3.08 7.622l3.407 2.634c.804-2.413 3.055-4.208 5.713-4.208z"
					/>
				</svg>
				<span>{googleLabel}</span>
			</button>

			<div class="flex items-center gap-3 text-xs text-muted">
				<span class="flex-1 h-px bg-rule"></span>
				<span>or register with email</span>
				<span class="flex-1 h-px bg-rule"></span>
			</div>

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
		{/if}

		<div class="pt-4 border-t border-rule text-xs text-muted">
			Already have an account?
			<a href="/login" class="text-accent hover:text-ink font-semibold ml-1 transition-colors">Sign in</a>
		</div>
	</div>
</div>
