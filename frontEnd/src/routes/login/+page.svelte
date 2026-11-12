<script lang="ts">
	import { page } from '$app/state';
	import type { PageProps } from './$types';

	let { data, form }: PageProps = $props();

	let emailInput = $state('');
	let showForgot = $state(false);
	let resetEmail = $state('');
	let resetStatus = $state('');
	let resetError = $state('');
	let isSendingReset = $state(false);
	let isGoogleLoading = $state(false);
	let oauthError = $state('');

	const googleLabel = $derived(isGoogleLoading ? 'Connecting to Google…' : 'Continue with Google');
	const forgotLabel = $derived(showForgot ? 'Close reset' : 'Forgot password?');
	const resetBtnLabel = $derived(isSendingReset ? 'Sending…' : 'Send link');
	const callbackError = $derived(page.url.searchParams.get('error'));

	$effect(() => {
		if (form?.email) {
			emailInput = form.email;
		}
	});

	async function handleGoogleSignIn() {
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
			oauthError = err instanceof Error ? err.message : 'Unable to start Google sign-in.';
			isGoogleLoading = false;
		}
	}

	function toggleForgot() {
		showForgot = !showForgot;
		resetStatus = '';
		resetError = '';
		if (showForgot && !resetEmail && emailInput) {
			resetEmail = emailInput;
		}
	}

	async function handlePasswordReset(e: SubmitEvent) {
		e.preventDefault();
		resetStatus = '';
		resetError = '';
		const target = resetEmail.trim();
		if (!target) {
			resetError = 'Please enter your account email address.';
			return;
		}

		isSendingReset = true;
		try {
			const { error } = await data.supabase.auth.resetPasswordForEmail(target, {
				redirectTo: `${window.location.origin}/auth/reset-password`
			});
			if (error) {
				resetError = error.message;
				return;
			}
			resetStatus = `Check ${target} for your password recovery link.`;
		} catch (err) {
			resetError = err instanceof Error ? err.message : 'Failed to send reset link.';
		} finally {
			isSendingReset = false;
		}
	}
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

		{#if form?.error || callbackError || oauthError}
			<div class="p-3 rounded-card bg-paper-2 border border-rule text-error text-xs">
				{form?.error || oauthError || callbackError}
			</div>
		{/if}

		<button
			type="button"
			onclick={handleGoogleSignIn}
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
			<span>or sign in with email</span>
			<span class="flex-1 h-px bg-rule"></span>
		</div>

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
					bind:value={emailInput}
					placeholder="supporter@example.com"
					class="w-full h-10 bg-paper-2 border border-rule rounded-card px-3 text-sm text-ink placeholder-muted"
				/>
			</div>

			<div>
				<div class="flex items-center justify-between mb-1">
					<label for="password" class="block text-xs font-semibold text-ink-2">
						Password
					</label>
					<button
						type="button"
						onclick={toggleForgot}
						class="text-xs text-accent hover:text-ink font-semibold transition-colors whitespace-nowrap"
					>
						{forgotLabel}
					</button>
				</div>
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

		{#if showForgot}
			<form onsubmit={handlePasswordReset} class="border-t border-rule pt-4 space-y-3">
				<div class="space-y-1">
					<h2 class="text-sm font-bold text-ink">Reset your password</h2>
					<p class="text-xs text-muted">We will send a recovery link to your registered email address.</p>
				</div>

				{#if resetError}
					<p class="text-xs text-error">{resetError}</p>
				{/if}
				{#if resetStatus}
					<p class="text-xs text-success">{resetStatus}</p>
				{/if}

				<div class="flex gap-2">
					<input
						type="email"
						aria-label="Recovery email address"
						required
						bind:value={resetEmail}
						placeholder="supporter@example.com"
						class="flex-1 min-w-0 h-9 bg-paper-2 border border-rule rounded-card px-3 text-xs text-ink placeholder-muted"
					/>
					<button
						type="submit"
						disabled={isSendingReset}
						class="h-9 px-3 rounded-card border border-rule bg-paper-3 hover:bg-paper text-xs font-semibold text-ink whitespace-nowrap transition-colors"
					>
						{resetBtnLabel}
					</button>
				</div>
			</form>
		{/if}

		<div class="pt-4 border-t border-rule text-xs text-muted">
			Don’t have an account yet?
			<a href="/signup" class="text-accent hover:text-ink font-semibold ml-1 transition-colors">Join club</a>
		</div>
	</div>
</div>
