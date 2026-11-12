<script lang="ts">
	import { onMount } from 'svelte';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	let password = $state('');
	let confirmPassword = $state('');
	let hasSession = $state(false);
	let checkingSession = $state(true);
	let submitting = $state(false);
	let errorMessage = $state('');
	let successMessage = $state('');
	const submitLabel = $derived(submitting ? 'Updating password…' : 'Update password');

	onMount(() => {
		let mounted = true;

		async function initRecovery() {
			try {
				const params = new URLSearchParams(window.location.search);
				const code = params.get('code');
				if (code) {
					const { error } = await data.supabase.auth.exchangeCodeForSession(code);
					if (error && mounted) {
						errorMessage = error.message;
					}
				}
				const { data: sessionData } = await data.supabase.auth.getSession();
				if (mounted) {
					hasSession = Boolean(sessionData.session);
				}
			} catch {
				if (mounted) {
					hasSession = Boolean(data.session);
				}
			} finally {
				if (mounted) checkingSession = false;
			}
		}

		initRecovery();

		const { data: authSub } = data.supabase.auth.onAuthStateChange((event, session) => {
			if (event === 'PASSWORD_RECOVERY' || event === 'SIGNED_IN') {
				hasSession = Boolean(session);
			}
		});

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
			<div class="p-3 rounded-card bg-paper-2 border border-rule text-error text-xs">
				{errorMessage}
			</div>
		{/if}

		{#if successMessage}
			<div class="border-t border-rule pt-4 space-y-3">
				<p class="text-sm text-success font-semibold">{successMessage}</p>
				<div class="flex items-center gap-3">
					<a
						href="/profile"
						class="inline-flex items-center h-9 px-4 rounded-card bg-accent text-accent-ink font-semibold text-xs hover:opacity-95 transition-opacity whitespace-nowrap"
					>
						Go to profile
					</a>
					<a href="/login" class="text-xs text-ink-2 hover:text-ink font-semibold whitespace-nowrap">
						Sign in
					</a>
				</div>
			</div>
		{:else if checkingSession}
			<p class="text-sm text-muted">Verifying password recovery session…</p>
		{:else if !hasSession}
			<div class="border-t border-rule pt-4 space-y-3">
				<p class="text-sm text-ink-2">
					Your password reset link is missing or has expired. Request a fresh reset email from the sign-in page.
				</p>
				<a
					href="/login"
					class="inline-flex items-center h-9 px-4 rounded-card bg-accent text-accent-ink font-semibold text-xs hover:opacity-95 transition-opacity whitespace-nowrap"
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
					<input
						id="new-password"
						type="password"
						required
						minlength="6"
						bind:value={password}
						placeholder="Minimum 6 characters"
						class="w-full h-10 bg-paper-2 border border-rule rounded-card px-3 text-sm text-ink placeholder-muted"
					/>
				</div>

				<div>
					<label for="confirm-password" class="block text-xs font-semibold text-ink-2 mb-1">
						Confirm new password
					</label>
					<input
						id="confirm-password"
						type="password"
						required
						minlength="6"
						bind:value={confirmPassword}
						placeholder="Re-enter new password"
						class="w-full h-10 bg-paper-2 border border-rule rounded-card px-3 text-sm text-ink placeholder-muted"
					/>
				</div>

				<button
					type="submit"
					disabled={submitting}
					class="w-full h-10 px-4 bg-accent hover:opacity-95 text-accent-ink font-semibold text-sm rounded-card transition-opacity whitespace-nowrap"
				>
					{submitLabel}
				</button>
			</form>
		{/if}

		<div class="pt-4 border-t border-rule text-xs text-muted">
			<a href="/login" class="text-accent hover:text-ink font-semibold transition-colors">
				Return to sign in
			</a>
		</div>
	</div>
</div>
