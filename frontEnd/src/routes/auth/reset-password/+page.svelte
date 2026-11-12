<script lang="ts">
	import { onMount } from 'svelte';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	let password = $state('');
	let confirmPassword = $state('');
	let showPassword = $state(false);
	let showConfirmPassword = $state(false);
	let hasSession = $state(false);
	let checkingSession = $state(true);
	let submitting = $state(false);
	let errorMessage = $state('');
	let successMessage = $state('');
	const submitLabel = $derived(submitting ? 'Updating password…' : 'Update password');
	const passToggleLabel = $derived(showPassword ? 'Hide' : 'Show');
	const confirmPassLabel = $derived(showConfirmPassword ? 'Hide' : 'Show');
	const passwordsMismatch = $derived(
		confirmPassword.length > 0 && password !== confirmPassword
	);

	onMount(() => {
		let mounted = true;
		let authSettled = false;

		const { data: authSub } = data.supabase.auth.onAuthStateChange((event, session) => {
			if (!mounted) return;
			if (event === 'PASSWORD_RECOVERY' || event === 'SIGNED_IN') {
				hasSession = Boolean(session);
				authSettled = true;
				checkingSession = false;
			}
		});

		async function initRecovery() {
			try {
				const queryParams = new URLSearchParams(window.location.search);
				const hashRaw = window.location.hash.startsWith('#')
					? window.location.hash.slice(1)
					: window.location.hash;
				const hashParams = new URLSearchParams(hashRaw);

				const providerError =
					queryParams.get('error_description') ||
					queryParams.get('error') ||
					hashParams.get('error_description') ||
					hashParams.get('error');

				if (providerError && mounted) {
					errorMessage = providerError;
					hasSession = false;
					checkingSession = false;
					return;
				}

				const code = queryParams.get('code');
				if (code) {
					const { error } = await data.supabase.auth.exchangeCodeForSession(code);
					if (error && mounted) {
						errorMessage = error.message;
					}
				}

				const hasHashToken = Boolean(
					hashParams.get('access_token') || hashParams.get('type') === 'recovery'
				);
				if (hasHashToken && !authSettled) {
					await new Promise((resolve) => setTimeout(resolve, 250));
				}

				const { data: userData } = await data.supabase.auth.getUser();
				if (userData.user && mounted) {
					hasSession = true;
				} else if (mounted && !authSettled) {
					const { data: sessionData } = await data.supabase.auth.getSession();
					if (mounted) {
						hasSession = Boolean(sessionData.session);
					}
				}
			} catch {
				if (mounted && !authSettled) {
					hasSession = Boolean(data.user ?? data.session);
				}
			} finally {
				if (mounted) checkingSession = false;
			}
		}

		initRecovery();

		return () => {
			mounted = false;
			authSub.subscription.unsubscribe();
		};
	});

	async function handleUpdatePassword(e: SubmitEvent) {
		e.preventDefault();
		errorMessage = '';
		successMessage = '';

		if (password.length < 6) {
			errorMessage = 'Password must be at least 6 characters long.';
			return;
		}
		if (password !== confirmPassword) {
			errorMessage = 'Passwords do not match.';
			return;
		}

		submitting = true;
		try {
			const { error } = await data.supabase.auth.updateUser({ password });
			if (error) {
				errorMessage = error.message;
				return;
			}
			successMessage = 'Your password has been updated. You can now continue to your supporter profile.';
			password = '';
			confirmPassword = '';
		} catch (err) {
			errorMessage = err instanceof Error ? err.message : 'Failed to update password.';
		} finally {
			submitting = false;
		}
	}
</script>

<svelte:head>
	<title>Reset Password | GUNNERS</title>
</svelte:head>

<div class="container py-16 max-w-md">
	<div class="border-t-2 border-rule-2 pt-8 space-y-6">
		<div class="space-y-2">
			<h1>Set a new password</h1>
			<p class="text-sm text-ink-2">
				Choose a new password for your Arsenal supporter account.
			</p>
		</div>

		{#if errorMessage}
			<div role="alert" class="p-3 rounded-card bg-paper-2 border border-rule text-error text-xs">
				{errorMessage}
			</div>
		{/if}

		{#if successMessage}
			<div role="status" aria-live="polite" class="border-t border-rule pt-4 space-y-3">
				<p class="text-sm text-success font-semibold">{successMessage}</p>
				<div class="flex flex-wrap items-center gap-3">
					<a
						href="/profile"
						class="inline-flex items-center min-h-[44px] px-4 rounded-card bg-accent text-accent-ink font-semibold text-xs hover:opacity-95 transition-opacity whitespace-nowrap"
					>
						Go to profile
					</a>
					<a href="/login" class="inline-flex items-center min-h-[44px] px-2 text-xs text-ink-2 hover:text-ink font-semibold whitespace-nowrap">
						Sign in
					</a>
				</div>
			</div>
		{:else if checkingSession}
			<p role="status" aria-live="polite" class="text-sm text-muted">Verifying password recovery session…</p>
		{:else if !hasSession}
			<div class="border-t border-rule pt-4 space-y-3">
				<p class="text-sm text-ink-2">
					Your password reset link is missing or has expired. Request a fresh reset email from the sign-in page.
				</p>
				<a
					href="/login"
					class="inline-flex items-center min-h-[44px] px-4 rounded-card bg-accent text-accent-ink font-semibold text-xs hover:opacity-95 transition-opacity whitespace-nowrap"
				>
					Back to sign in
				</a>
			</div>
		{:else}
			<form onsubmit={handleUpdatePassword} class="space-y-4">
				<div>
					<label for="new-password" class="block text-xs font-semibold text-ink-2 mb-1">
						New password
					</label>
					<div class="flex items-stretch gap-2">
						<input
							id="new-password"
							type={showPassword ? 'text' : 'password'}
							autocomplete="new-password"
							required
							minlength="6"
							aria-describedby="reset-password-hint"
							bind:value={password}
							placeholder="Enter new password"
							class="flex-1 min-w-0 min-h-[44px] bg-paper-2 border border-rule rounded-card px-3 text-sm text-ink placeholder-muted"
						/>
						<button
							type="button"
							onclick={() => (showPassword = !showPassword)}
							aria-pressed={showPassword}
							aria-controls="new-password"
							aria-label={showPassword ? 'Hide new password' : 'Show new password'}
							class="min-h-[44px] px-3 rounded-card border border-rule bg-paper-2 hover:bg-paper-3 text-xs font-semibold text-ink-2 hover:text-ink transition-colors whitespace-nowrap"
						>
							{passToggleLabel}
						</button>
					</div>
					<span id="reset-password-hint" class="block text-xs text-muted mt-1">
						Minimum 6 characters.
					</span>
				</div>

				<div>
					<label for="confirm-password" class="block text-xs font-semibold text-ink-2 mb-1">
						Confirm new password
					</label>
					<div class="flex items-stretch gap-2">
						<input
							id="confirm-password"
							type={showConfirmPassword ? 'text' : 'password'}
							autocomplete="new-password"
							required
							minlength="6"
							bind:value={confirmPassword}
							placeholder="Re-enter new password"
							class="flex-1 min-w-0 min-h-[44px] bg-paper-2 border border-rule rounded-card px-3 text-sm text-ink placeholder-muted"
						/>
						<button
							type="button"
							onclick={() => (showConfirmPassword = !showConfirmPassword)}
							aria-pressed={showConfirmPassword}
							aria-controls="confirm-password"
							aria-label={showConfirmPassword ? 'Hide confirmation password' : 'Show confirmation password'}
							class="min-h-[44px] px-3 rounded-card border border-rule bg-paper-2 hover:bg-paper-3 text-xs font-semibold text-ink-2 hover:text-ink transition-colors whitespace-nowrap"
						>
							{confirmPassLabel}
						</button>
					</div>
					{#if passwordsMismatch}
						<p role="alert" class="text-xs text-error mt-1">Passwords do not match yet.</p>
					{/if}
				</div>

				<button
					type="submit"
					disabled={submitting}
					class="w-full min-h-[44px] px-4 bg-accent hover:opacity-95 text-accent-ink font-semibold text-sm rounded-card transition-opacity whitespace-nowrap disabled:opacity-60"
				>
					{submitLabel}
				</button>
			</form>
		{/if}

		<div class="pt-4 border-t border-rule text-xs text-muted">
			<a href="/login" class="text-accent-text hover:text-ink font-semibold transition-colors">
				Return to sign in
			</a>
		</div>
	</div>
</div>
