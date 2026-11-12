<script lang="ts">
	import { enhance } from '$app/forms';
	import { invalidateAll } from '$app/navigation';
	import { CLUBS, themeState } from '$lib/stores/theme.svelte';
	import type { PageProps } from './$types';

	let { data, form }: PageProps = $props();

	let currentClub = $derived(CLUBS.arsenal);
	let avatarUrl = $state('');
	let avatarError = $state('');
	let avatarStatus = $state('');
	let isUploadingAvatar = $state(false);
	let isRemovingAvatar = $state(false);
	let avatarLoadFailed = $state(false);

	let displayNameInput = $state('');
	let bioInput = $state('');
	let hasInitializedDrafts = $state(false);
	let isDisplayNameDirty = $state(false);
	let isBioDirty = $state(false);
	let isSavingProfile = $state(false);

	let newPassword = $state('');
	let confirmPassword = $state('');
	let showNewPassword = $state(false);
	let showConfirmPassword = $state(false);
	let passwordError = $state('');
	let passwordStatus = $state('');
	let isUpdatingPassword = $state(false);
	const passwordBtnLabel = $derived(isUpdatingPassword ? 'Updating password…' : 'Update password');
	const removeAvatarLabel = $derived(isRemovingAvatar ? 'Removing…' : 'Remove portrait');
	const saveProfileLabel = $derived(isSavingProfile ? 'Saving changes…' : 'Save changes');
	const newPassToggleLabel = $derived(showNewPassword ? 'Hide' : 'Show');
	const confirmToggleLabel = $derived(showConfirmPassword ? 'Hide' : 'Show');
	const passwordsMismatch = $derived(
		confirmPassword.length > 0 && newPassword !== confirmPassword
	);
	const formSuccess = $derived(Boolean(form && 'success' in form && form.success));
	const formAvatarRemoved = $derived(
		Boolean(form && 'avatarRemoved' in form && form.avatarRemoved)
	);
	const formError = $derived(form && 'error' in form ? form.error : '');

	const MAX_AVATAR_BYTES = 3 * 1024 * 1024;
	const ALLOWED_MIME_TYPES = new Set(['image/jpeg', 'image/png', 'image/webp']);

	const initials = $derived.by(() => {
		const label =
			displayNameInput || data.profile?.display_name || data.profile?.username || data.user?.email || 'G';
		return label
			.split(/\s+/)
			.map((p: string) => p[0] || '')
			.join('')
			.slice(0, 2)
			.toUpperCase();
	});

	function extractOwnedAvatarPath(url: string | null | undefined, userId: string): string | null {
		if (!url) return null;
		const marker = '/storage/v1/object/public/avatars/';
		const idx = url.indexOf(marker);
		if (idx === -1) return null;
		const path = decodeURIComponent(url.slice(idx + marker.length).split('?')[0]);
		return path.startsWith(`${userId}/`) ? path : null;
	}

	$effect(() => {
		if (data.profile?.favorite_club_id) {
			themeState.setFavoriteClub(data.profile.favorite_club_id);
		}
		if (data.profile?.avatar_url !== undefined) {
			avatarUrl = data.profile.avatar_url || '';
			avatarLoadFailed = false;
		}
		if (!hasInitializedDrafts && data.profile) {
			displayNameInput = data.profile.display_name || '';
			bioInput = data.profile.bio || '';
			hasInitializedDrafts = true;
		} else if (data.profile) {
			if (!isDisplayNameDirty) displayNameInput = data.profile.display_name || '';
			if (!isBioDirty) bioInput = data.profile.bio || '';
		}
	});

	async function handleAvatarSelect(e: Event) {
		const input = e.currentTarget as HTMLInputElement;
		const file = input.files?.[0];
		if (!file || !data.user) return;

		avatarError = '';
		avatarStatus = '';

		if (!ALLOWED_MIME_TYPES.has(file.type)) {
			avatarError = 'Please choose a JPEG, PNG, or WebP image.';
			input.value = '';
			return;
		}
		if (file.size > MAX_AVATAR_BYTES) {
			avatarError = 'Image must be 3 MB or smaller.';
			input.value = '';
			return;
		}

		isUploadingAvatar = true;
		const previousAvatarUrl = avatarUrl;
		try {
			const safeFilename = file.name.replace(/[^a-zA-Z0-9._-]/g, '_');
			const objectPath = `${data.user.id}/${Date.now()}-${safeFilename}`;

			const { error: uploadErr } = await data.supabase.storage
				.from('avatars')
				.upload(objectPath, file, {
					cacheControl: '3600',
					upsert: true,
					contentType: file.type
				});

			if (uploadErr) {
				avatarError = uploadErr.message;
				return;
			}

			const { data: pub } = data.supabase.storage.from('avatars').getPublicUrl(objectPath);
			const publicUrl = pub.publicUrl;

			const { error: updateErr } = await data.supabase
				.from('profiles')
				.update({
					avatar_url: publicUrl,
					updated_at: new Date().toISOString()
				})
				.eq('id', data.user.id);

			if (updateErr) {
				avatarError = updateErr.message;
				return;
			}

			const oldPath = extractOwnedAvatarPath(previousAvatarUrl, data.user.id);
			if (oldPath && oldPath !== objectPath) {
				await data.supabase.storage.from('avatars').remove([oldPath]).catch(() => {});
			}

			avatarUrl = publicUrl;
			avatarLoadFailed = false;
			avatarStatus = 'Avatar uploaded and saved.';
			await invalidateAll();
		} catch (err) {
			avatarError = err instanceof Error ? err.message : 'Unable to upload avatar.';
		} finally {
			isUploadingAvatar = false;
			input.value = '';
		}
	}

	async function handlePasswordUpdate(e: SubmitEvent) {
		e.preventDefault();
		passwordError = '';
		passwordStatus = '';

		if (newPassword.length < 6) {
			passwordError = 'New password must be at least 6 characters long.';
			return;
		}
		if (newPassword !== confirmPassword) {
			passwordError = 'Passwords do not match.';
			return;
		}

		isUpdatingPassword = true;
		try {
			const { error } = await data.supabase.auth.updateUser({ password: newPassword });
			if (error) {
				passwordError = error.message;
				return;
			}
			newPassword = '';
			confirmPassword = '';
			passwordStatus = 'Account password updated.';
		} catch (err) {
			passwordError = err instanceof Error ? err.message : 'Failed to update password.';
		} finally {
			isUpdatingPassword = false;
		}
	}
</script>

<svelte:head>
	<title>Supporter Profile | GUNNERS</title>
</svelte:head>

<div class="container py-12 max-w-2xl space-y-10">
	<div class="border-t-2 border-rule-2 pt-8 space-y-8">
		<div class="flex items-end justify-between pb-6 border-b border-rule gap-4 flex-wrap">
			<div class="flex items-center gap-4 min-w-0">
				<div class="w-16 h-16 rounded-card border border-rule bg-paper-2 overflow-hidden shrink-0 flex items-center justify-center">
					{#if avatarUrl && !avatarLoadFailed}
						<img
							src={avatarUrl}
							alt="{displayNameInput || data.profile?.display_name || 'Supporter'} avatar"
							width="64"
							height="64"
							class="w-full h-full object-cover"
							onerror={() => (avatarLoadFailed = true)}
						/>
					{:else}
						<span class="font-display font-bold text-xl text-accent-text">{initials}</span>
					{/if}
				</div>
				<div class="space-y-1 min-w-0">
					<h1>Supporter profile</h1>
					<p class="text-sm text-ink-2">Manage your identity, avatar, and account security.</p>
				</div>
			</div>

			<div class="flex items-center gap-3 flex-wrap">
				<span class="text-xs font-bold text-accent-2">
					{currentClub.name}
				</span>
				{#if data.profile?.username}
					<a
						href="/supporters/{encodeURIComponent(data.profile.username)}"
						class="inline-flex items-center min-h-[44px] px-3 rounded-card border border-rule bg-paper-2 hover:bg-paper-3 text-xs font-semibold text-ink transition-colors whitespace-nowrap"
					>
						Public dossier
					</a>
				{/if}
			</div>
		</div>

		{#if formSuccess}
			<div role="status" aria-live="polite" class="p-3 rounded-card bg-paper-2 border border-rule text-success text-xs">
				Profile updated.
			</div>
		{/if}

		{#if formAvatarRemoved}
			<div role="status" aria-live="polite" class="p-3 rounded-card bg-paper-2 border border-rule text-success text-xs">
				Portrait image removed.
			</div>
		{/if}

		{#if formError}
			<div role="alert" class="p-3 rounded-card bg-paper-2 border border-rule text-error text-xs">
				{formError}
			</div>
		{/if}

		<dl class="space-y-3 text-xs border-b border-rule pb-6">
			<div class="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1 py-1.5 border-b border-rule">
				<dt class="text-muted shrink-0">Email</dt>
				<dd class="text-ink num font-outlier break-all">{data.user?.email}</dd>
			</div>
			<div class="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1 py-1.5 border-b border-rule">
				<dt class="text-muted shrink-0">Username</dt>
				<dd class="text-ink font-semibold break-all">@{data.profile?.username || 'unnamed'}</dd>
			</div>
			<div class="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1 py-1.5">
				<dt class="text-muted shrink-0">User ID</dt>
				<dd class="text-muted num font-outlier break-all">{data.user?.id}</dd>
			</div>
		</dl>

		<!-- Avatar Upload -->
		<div class="space-y-3 border-b border-rule pb-6">
			<div class="space-y-1">
				<h2 class="text-lg font-bold text-ink">Supporter avatar</h2>
				<p class="text-xs text-muted">Upload a JPEG, PNG, or WebP portrait (max 3 MB).</p>
			</div>

			{#if avatarError}
				<p role="alert" class="text-xs text-error">{avatarError}</p>
			{/if}
			{#if avatarLoadFailed && avatarUrl}
				<p role="alert" class="text-xs text-error">
					Saved avatar image could not be loaded. Choose a new portrait or remove the broken link.
				</p>
			{/if}
			{#if avatarStatus}
				<p role="status" aria-live="polite" class="text-xs text-success">{avatarStatus}</p>
			{/if}

			<div class="flex items-center gap-3 flex-wrap">
				<label
					for="avatar-upload"
					class="inline-flex items-center min-h-[44px] px-4 rounded-card border border-rule bg-paper-2 hover:bg-paper-3 text-xs font-semibold text-ink cursor-pointer transition-colors focus-within:outline-2 focus-within:outline-[var(--color-focus)] focus-within:outline-offset-2"
				>
					<span>{isUploadingAvatar ? 'Uploading portrait…' : 'Choose portrait image'}</span>
					<input
						id="avatar-upload"
						type="file"
						accept="image/jpeg,image/png,image/webp"
						disabled={isUploadingAvatar || isRemovingAvatar}
						onchange={handleAvatarSelect}
						class="visually-hidden"
					/>
				</label>

				{#if avatarUrl}
					<form
						method="POST"
						action="?/removeAvatar"
						use:enhance={() => {
							isRemovingAvatar = true;
							avatarError = '';
							avatarStatus = '';
							return async ({ update }) => {
								isRemovingAvatar = false;
								await update();
							};
						}}
					>
						<button
							type="submit"
							disabled={isRemovingAvatar || isUploadingAvatar}
							class="inline-flex items-center min-h-[44px] px-4 rounded-card border border-rule bg-paper-2 hover:bg-paper-3 text-xs font-semibold text-error transition-colors whitespace-nowrap disabled:opacity-60"
						>
							{removeAvatarLabel}
						</button>
					</form>
				{/if}

				<span class="text-xs text-muted">Stored in verified Arsenal supporter bucket.</span>
			</div>
		</div>

		<div class="space-y-5">
			<h2 class="text-lg font-bold text-ink">Edit profile</h2>

			<form
				method="POST"
				action="?/updateProfile"
				use:enhance={() => {
					isSavingProfile = true;
					return async ({ result, update }) => {
						isSavingProfile = false;
						if (result.type === 'success') {
							isDisplayNameDirty = false;
							isBioDirty = false;
						}
						await update({ reset: false });
					};
				}}
				class="space-y-4"
			>
				<input type="hidden" name="avatar_url" value={avatarUrl} />

				<div>
					<label for="display_name" class="block text-xs font-semibold text-ink-2 mb-1">
						Display name
					</label>
					<input
						id="display_name"
						name="display_name"
						type="text"
						autocomplete="name"
						required
						bind:value={displayNameInput}
						oninput={() => (isDisplayNameDirty = true)}
						class="w-full min-h-[44px] bg-paper-2 border border-rule rounded-card px-3 text-sm text-ink"
					/>
				</div>

				<div>
					<label for="bio" class="block text-xs font-semibold text-ink-2 mb-1">
						Bio &amp; tactical focus
					</label>
					<textarea
						id="bio"
						name="bio"
						rows="3"
						bind:value={bioInput}
						oninput={() => (isBioDirty = true)}
						placeholder="Share your favorite Arsenal era, tactical focus, or matchday routine…"
						class="w-full bg-paper-2 border border-rule rounded-card p-3 text-sm text-ink placeholder-muted"
					></textarea>
				</div>

				<div>
					<span class="block text-xs font-semibold text-ink-2 mb-1">
						Supporter affiliation
					</span>
					<input
						type="hidden"
						name="favorite_club_id"
						value="arsenal"
					/>
					<div class="w-full min-h-[44px] bg-paper-2 border border-rule rounded-card px-3 text-sm text-ink flex items-center">
						<span>Arsenal FC, Emirates Stadium</span>
					</div>
				</div>

				<div class="pt-2">
					<button
						type="submit"
						disabled={isSavingProfile}
						class="min-h-[44px] px-5 bg-accent hover:opacity-95 text-accent-ink font-semibold text-sm rounded-card transition-opacity whitespace-nowrap disabled:opacity-60"
					>
						{saveProfileLabel}
					</button>
				</div>
			</form>
		</div>
	</div>

	<!-- Password Update Section -->
	<section class="border-t border-rule pt-6 space-y-4">
		<div class="space-y-1">
			<h2 class="text-base font-bold text-ink">Update password</h2>
			<p class="text-xs text-muted">Set a new password for your signed-in session.</p>
		</div>

		{#if passwordError}
			<p role="alert" class="text-xs text-error">{passwordError}</p>
		{/if}
		{#if passwordStatus}
			<p role="status" aria-live="polite" class="text-xs text-success">{passwordStatus}</p>
		{/if}

		<form onsubmit={handlePasswordUpdate} class="grid grid-cols-1 sm:grid-cols-2 gap-3">
			<div>
				<label for="profile-new-password" class="block text-xs font-semibold text-ink-2 mb-1">
					New password
				</label>
				<div class="flex items-stretch gap-2">
					<input
						id="profile-new-password"
						type={showNewPassword ? 'text' : 'password'}
						autocomplete="new-password"
						minlength="6"
						required
						bind:value={newPassword}
						placeholder="Enter new password"
						class="flex-1 min-w-0 min-h-[44px] bg-paper-2 border border-rule rounded-card px-3 text-sm text-ink placeholder-muted"
					/>
					<button
						type="button"
						onclick={() => (showNewPassword = !showNewPassword)}
						aria-pressed={showNewPassword}
						aria-controls="profile-new-password"
						aria-label={showNewPassword ? 'Hide new password' : 'Show new password'}
						class="min-h-[44px] px-3 rounded-card border border-rule bg-paper-2 hover:bg-paper-3 text-xs font-semibold text-ink-2 hover:text-ink transition-colors whitespace-nowrap"
					>
						{newPassToggleLabel}
					</button>
				</div>
				<span class="block text-xs text-muted mt-1">Minimum 6 characters.</span>
			</div>

			<div>
				<label for="profile-confirm-password" class="block text-xs font-semibold text-ink-2 mb-1">
					Confirm password
				</label>
				<div class="flex items-stretch gap-2">
					<input
						id="profile-confirm-password"
						type={showConfirmPassword ? 'text' : 'password'}
						autocomplete="new-password"
						minlength="6"
						required
						bind:value={confirmPassword}
						placeholder="Re-enter password"
						class="flex-1 min-w-0 min-h-[44px] bg-paper-2 border border-rule rounded-card px-3 text-sm text-ink placeholder-muted"
					/>
					<button
						type="button"
						onclick={() => (showConfirmPassword = !showConfirmPassword)}
						aria-pressed={showConfirmPassword}
						aria-controls="profile-confirm-password"
						aria-label={showConfirmPassword ? 'Hide confirm password' : 'Show confirm password'}
						class="min-h-[44px] px-3 rounded-card border border-rule bg-paper-2 hover:bg-paper-3 text-xs font-semibold text-ink-2 hover:text-ink transition-colors whitespace-nowrap"
					>
						{confirmToggleLabel}
					</button>
				</div>
				{#if passwordsMismatch}
					<p role="alert" class="text-xs text-error mt-1">Passwords do not match yet.</p>
				{/if}
			</div>

			<div class="sm:col-span-2 pt-1">
				<button
					type="submit"
					disabled={isUpdatingPassword}
					class="min-h-[44px] px-4 rounded-card border border-rule bg-paper-2 hover:bg-paper-3 text-xs font-semibold text-ink transition-colors whitespace-nowrap disabled:opacity-60"
				>
					{passwordBtnLabel}
				</button>
			</div>
		</form>
	</section>

	<div class="border-t border-rule pt-6 flex flex-wrap items-center justify-between gap-4">
		<div class="space-y-0.5">
			<h2 class="text-base font-bold text-ink">Sign out</h2>
			<p class="text-xs text-muted">End your current session on this device.</p>
		</div>
		<form method="POST" action="/auth/signout">
			<button
				type="submit"
				class="min-h-[44px] px-4 rounded-card bg-paper-2 hover:bg-paper-3 text-ink-2 hover:text-ink border border-rule text-xs font-semibold transition-colors"
			>
				Sign out
			</button>
		</form>
	</div>
</div>
