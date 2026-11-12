<script lang="ts">
	import { enhance } from '$app/forms';
	import { page } from '$app/state';
	import { getSafeRedirectPath } from '$lib/utils/redirect';
	import type { PageProps } from './$types';

	let { data, form }: PageProps = $props();

	let showPassword = $state(false);
	let isSubmitting = $state(false);
	let isGoogleLoading = $state(false);
	let oauthError = $state('');
	let isResending = $state(false);
	let resendStatus = $state('');
	let resendError = $state('');

	const safeNext = $derived(
		getSafeRedirectPath(form?.next ?? page.url.searchParams.get('next') ?? data.next, '/profile')
	);
	const formError = $derived(form && 'error' in form ? form.error : '');
	const needsEmailVerification = $derived(
		Boolean(form && 'needsEmailVerification' in form && form.needsEmailVerification)
	);
	const initialUsername = $derived(form && 'username' in form ? (form.username ?? '') : '');
	const initialDisplayName = $derived(
		form && 'displayName' in form ? (form.displayName ?? '') : ''
	);
	const initialEmail = $derived(form?.email ?? '');
	const loginHref = $derived(
		safeNext !== '/profile' ? `/login?next=${encodeURIComponent(safeNext)}` : '/login'
	);

	const googleLabel = $derived(isGoogleLoading ? 'Connecting to Google…' : 'Continue with Google');
	const submitLabel = $derived(isSubmitting ? 'Creating account…' : 'Create account');
	const resendBtnLabel = $derived(isResending ? 'Resending…' : 'Resend verification email');
	const passToggleLabel = $derived(showPassword ? 'Hide' : 'Show');

	function getCallbackUrl(): string {
		const callbackUrl = new URL('/auth/callback', window.location.origin);
		if (safeNext !== '/profile') {
			callbackUrl.searchParams.set('next', safeNext);
		}
		return callbackUrl.toString();
	}

	async function handleGoogleSignUp() {
		oauthError = '';
		isGoogleLoading = true;
		try {
			const { error } = await data.supabase.auth.signInWithOAuth({
				provider: 'google',
				options: {
					redirectTo: getCallbackUrl()
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

	async function handleResendVerification() {
		const email = initialEmail.trim();
		if (!email || isResending) return;
		isResending = true;
		resendStatus = '';
		resendError = '';
		try {
			const { error } = await data.supabase.auth.resend({
				type: 'signup',
				email,
				options: {
					emailRedirectTo: getCallbackUrl()
				}
			});
			if (error) {
				resendError = error.message;
				return;
			}
			resendStatus = `Verification email dispatched to ${email}.`;
		} catch (err) {
			resendError = err instanceof Error ? err.message : 'Unable to resend confirmation email.';
		} finally {
			isResending = false;
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

		{#if formError || oauthError}
			<div role="alert" class="p-3 rounded-card bg-paper-2 border border-rule text-error text-xs">
				{formError || oauthError}
			</div>
		{/if}

		{#if needsEmailVerification}
			<div class="border-t border-rule pt-4 space-y-3">
				<h2 class="text-base font-bold text-success">Check your inbox to verify</h2>
				<p class="text-sm text-ink-2 leading-relaxed">
					We sent a confirmation link to <strong class="text-ink">{initialEmail}</strong>. Open that email to activate your account before signing in.
				</p>
				{#if resendError}
					<p role="alert" class="text-xs text-error">{resendError}</p>
				{/if}
				{#if resendStatus}
					<p role="status" aria-live="polite" class="text-xs text-success">{resendStatus}</p>
				{/if}
				<div class="flex flex-wrap items-center gap-3 pt-1">
					<a
						href={loginHref}
						class="inline-flex items-center min-h-[44px] px-4 rounded-card bg-accent text-accent-ink font-semibold text-xs hover:opacity-95 transition-opacity whitespace-nowrap"
					>
						Proceed to sign in
					</a>
					<button
						type="button"
						onclick={handleResendVerification}
						disabled={isResending}
						class="inline-flex items-center min-h-[44px] px-4 rounded-card border border-rule bg-paper-2 hover:bg-paper-3 text-ink font-semibold text-xs transition-colors whitespace-nowrap disabled:opacity-60"
					>
						{resendBtnLabel}
					</button>
				</div>
			</div>
		{:else}
			<button
				type="button"
				onclick={handleGoogleSignUp}
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
				<span>or register with email</span>
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
					<label for="username" class="block text-xs font-semibold text-ink-2 mb-1">
						Username
					</label>
					<input
						id="username"
						name="username"
						type="text"
						autocomplete="username"
						pattern="[A-Za-z0-9_]+"
						minlength="3"
						required
						aria-describedby="username-hint"
						value={initialUsername}
						placeholder="e.g. gunner_legend"
						class="w-full min-h-[44px] bg-paper-2 border border-rule rounded-card px-3 text-sm text-ink placeholder-muted"
					/>
					<span id="username-hint" class="block text-xs text-muted mt-1">
						Letters, numbers, and underscores only (at least 3 characters); stored lowercase.
					</span>
				</div>

				<div>
					<label for="display_name" class="block text-xs font-semibold text-ink-2 mb-1">
						Display name
					</label>
					<input
						id="display_name"
						name="display_name"
						type="text"
						autocomplete="name"
						value={initialDisplayName}
						placeholder="e.g. Thierry H."
						class="w-full min-h-[44px] bg-paper-2 border border-rule rounded-card px-3 text-sm text-ink placeholder-muted"
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
						autocomplete="email"
						required
						value={initialEmail}
						placeholder="supporter@example.com"
						class="w-full min-h-[44px] bg-paper-2 border border-rule rounded-card px-3 text-sm text-ink placeholder-muted"
					/>
				</div>

				<div>
					<label for="password" class="block text-xs font-semibold text-ink-2 mb-1">
						Password
					</label>
					<div class="flex items-stretch gap-2">
						<input
							id="password"
							name="password"
							type={showPassword ? 'text' : 'password'}
							autocomplete="new-password"
							required
							minlength="6"
							aria-describedby="password-hint"
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
					<span id="password-hint" class="block text-xs text-muted mt-1">
						At least 6 characters.
					</span>
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
					<div id="club-display" class="w-full min-h-[44px] bg-paper-2 border border-rule rounded-card px-3 text-sm text-ink flex items-center">
						<span>Arsenal FC (The Gunners)</span>
					</div>
					<span class="block text-xs text-muted mt-1">Platform membership is exclusively dedicated to Arsenal Football Club supporters.</span>
				</div>

				<button
					type="submit"
					disabled={isSubmitting}
					class="w-full min-h-[44px] px-4 bg-accent hover:opacity-95 text-accent-ink font-semibold text-sm rounded-card transition-opacity mt-2 disabled:opacity-60"
				>
					{submitLabel}
				</button>
			</form>
		{/if}

		<div class="pt-4 border-t border-rule text-xs text-muted">
			Already have an account?
			<a href={loginHref} class="text-accent-text hover:text-ink font-semibold ml-1 transition-colors">Sign in</a>
		</div>
	</div>
</div>
