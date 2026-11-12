<script lang="ts">
	import { enhance } from '$app/forms';
	import { page } from '$app/state';
	import { getSafeRedirectPath } from '$lib/utils/redirect';
	import type { PageProps } from './$types';

	let { data, form }: PageProps = $props();

	let emailInput = $state('');
	let showPassword = $state(false);
	let isSubmitting = $state(false);
	let showForgot = $state(false);
	let resetEmail = $state('');
	let resetStatus = $state('');
	let resetError = $state('');
	let isSendingReset = $state(false);
	let isGoogleLoading = $state(false);
	let oauthError = $state('');

	const safeNext = $derived(
		getSafeRedirectPath(form?.next ?? page.url.searchParams.get('next') ?? data.next, '/profile')
	);
	const signupHref = $derived(
		safeNext !== '/profile' ? `/signup?next=${encodeURIComponent(safeNext)}` : '/signup'
	);

	const googleLabel = $derived(isGoogleLoading ? 'Connecting to Google…' : 'Continue with Google');
	const forgotLabel = $derived(showForgot ? 'Close reset' : 'Forgot password?');
	const resetBtnLabel = $derived(isSendingReset ? 'Sending…' : 'Send link');
	const submitLabel = $derived(isSubmitting ? 'Signing in…' : 'Sign in');
	const passToggleLabel = $derived(showPassword ? 'Hide' : 'Show');

	function formatAuthError(raw: string | null | undefined): string {
		if (!raw) return '';
		const code = raw.trim().toLowerCase();
		if (code === 'access_denied') {
			return 'Google sign-in was cancelled. Try again or sign in with email.';
		}
		if (code === 'otp_expired') {
			return 'That sign-in or recovery link has expired. Request a new one below.';
		}
		if (code === 'server_error') {
			return 'Authentication service returned an error. Please try again.';
		}
		return raw;
	}

	const callbackError = $derived(formatAuthError(page.url.searchParams.get('error')));
	const activeError = $derived(form?.error || oauthError || callbackError);

	$effect(() => {
		if (form?.email) {
			emailInput = form.email;
		}
	});

	async function handleGoogleSignIn() {
		oauthError = '';
		isGoogleLoading = true;
		try {
			const callbackUrl = new URL('/auth/callback', window.location.origin);
			if (safeNext !== '/profile') {
				callbackUrl.searchParams.set('next', safeNext);
			}
			const { error } = await data.supabase.auth.signInWithOAuth({
				provider: 'google',
				options: {
					redirectTo: callbackUrl.toString()
				}
			});
			if (error) {
				oauthError = formatAuthError(error.message);
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
			{#if safeNext !== '/profile'}
				<p class="text-xs text-muted">You will be returned to your destination after signing in.</p>
			{/if}
		</div>

		{#if activeError}
			<div role="alert" class="p-3 rounded-card bg-paper-2 border border-rule text-error text-xs">
				{activeError}
			</div>
		{/if}

		<button
			type="button"
			onclick={handleGoogleSignIn}
			disabled={isGoogleLoading}
			class="w-full min-h-[44px] px-4 bg-paper-2 hover:bg-paper-3 border border-rule rounded-card text-sm font-semibold text-ink inline-flex items-center justify-center gap-2.5 transition-colors whitespace-nowrap"
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

		<form
			method="POST"
			use:enhance={() => {
				isSubmitting = true;
				return async ({ update }) => {
					isSubmitting = false;
					await update();
				};
			}}
			class="space-y-4"
		>
			<input type="hidden" name="next" value={safeNext} />

			<div>
				<label for="email" class="block text-xs font-semibold text-ink-2 mb-1">
					Email
				</label>
				<input
					id="email"
					name="email"
					type="email"
					autocomplete="email"
					required
					bind:value={emailInput}
					placeholder="supporter@example.com"
					class="w-full min-h-[44px] bg-paper-2 border border-rule rounded-card px-3 text-sm text-ink placeholder-muted"
				/>
			</div>

			<div>
				<div class="flex items-center justify-between gap-2 mb-1">
					<label for="password" class="block text-xs font-semibold text-ink-2">
						Password
					</label>
					<button
						type="button"
						onclick={toggleForgot}
						aria-expanded={showForgot}
						class="min-h-[36px] px-1 text-xs text-accent-text hover:text-ink font-semibold transition-colors whitespace-nowrap"
					>
						{forgotLabel}
					</button>
				</div>
				<div class="flex items-stretch gap-2">
					<input
						id="password"
						name="password"
						type={showPassword ? 'text' : 'password'}
						autocomplete="current-password"
						required
						placeholder="Enter password"
						class="flex-1 min-w-0 min-h-[44px] bg-paper-2 border border-rule rounded-card px-3 text-sm text-ink placeholder-muted"
					/>
					<button
						type="button"
						onclick={() => (showPassword = !showPassword)}
						aria-pressed={showPassword}
						aria-controls="password"
						aria-label={showPassword ? 'Hide password' : 'Show password'}
						class="min-h-[44px] px-3 rounded-card border border-rule bg-paper-2 hover:bg-paper-3 text-xs font-semibold text-ink-2 hover:text-ink transition-colors whitespace-nowrap"
					>
						{passToggleLabel}
					</button>
				</div>
			</div>

			<button
				type="submit"
				disabled={isSubmitting}
				class="w-full min-h-[44px] px-4 bg-accent hover:opacity-95 text-accent-ink font-semibold text-sm rounded-card transition-opacity mt-2 disabled:opacity-60"
			>
				{submitLabel}
			</button>
		</form>

		{#if showForgot}
			<form onsubmit={handlePasswordReset} class="border-t border-rule pt-4 space-y-3">
				<div class="space-y-1">
					<h2 class="text-sm font-bold text-ink">Reset your password</h2>
					<p class="text-xs text-muted">We will send a recovery link to your registered email address.</p>
				</div>

				{#if resetError}
					<p role="alert" class="text-xs text-error">{resetError}</p>
				{/if}
				{#if resetStatus}
					<p role="status" aria-live="polite" class="text-xs text-success">{resetStatus}</p>
				{/if}

				<div class="flex flex-wrap sm:flex-nowrap gap-2">
					<input
						type="email"
						autocomplete="email"
						aria-label="Recovery email address"
						required
						bind:value={resetEmail}
						placeholder="supporter@example.com"
						class="flex-1 min-w-[180px] min-h-[44px] bg-paper-2 border border-rule rounded-card px-3 text-xs text-ink placeholder-muted"
					/>
					<button
						type="submit"
						disabled={isSendingReset}
						class="min-h-[44px] px-3 rounded-card border border-rule bg-paper-3 hover:bg-paper text-xs font-semibold text-ink whitespace-nowrap transition-colors"
					>
						{resetBtnLabel}
					</button>
				</div>
			</form>
		{/if}

		<div class="pt-4 border-t border-rule text-xs text-muted">
			Don’t have an account yet?
			<a href={signupHref} class="text-accent-text hover:text-ink font-semibold ml-1 transition-colors">Join club</a>
		</div>
	</div>
</div>
