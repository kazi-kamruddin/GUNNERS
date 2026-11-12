<script lang="ts">
	import { invalidateAll } from '$app/navigation';
	import { CLUBS, themeState } from '$lib/stores/theme.svelte';
	import type { PageProps } from './$types';

	let { data, form }: PageProps = $props();

	let currentClub = $derived(CLUBS.arsenal);
	let avatarUrl = $state('');
	let avatarError = $state('');
	let avatarStatus = $state('');
	let isUploadingAvatar = $state(false);
	let avatarLoadFailed = $state(false);

	let newPassword = $state('');
	let confirmPassword = $state('');
	let passwordError = $state('');
	let passwordStatus = $state('');
	let isUpdatingPassword = $state(false);
	const passwordBtnLabel = $derived(isUpdatingPassword ? 'Updating password…' : 'Update password');

	const MAX_AVATAR_BYTES = 3 * 1024 * 1024;
	const ALLOWED_MIME_TYPES = new Set(['image/jpeg', 'image/png', 'image/webp']);

	const initials = $derived.by(() => {
		const label = data.profile?.display_name || data.profile?.username || data.user?.email || 'G';
		return label
			.split(/\s+/)
			.map((p: string) => p[0] || '')
			.join('')
			.slice(0, 2)
			.toUpperCase();
	});

	$effect(() => {
		if (data.profile?.favorite_club_id) {
			themeState.setFavoriteClub(data.profile.favorite_club_id);
		}
		if (data.profile?.avatar_url !== undefined) {
			avatarUrl = data.profile.avatar_url || '';
			avatarLoadFailed = false;
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
							alt="{data.profile?.display_name || 'Supporter'} avatar"
							width="64"
							height="64"
							class="w-full h-full object-cover"
							onerror={() => (avatarLoadFailed = true)}
						/>
					{:else}
						<span class="font-display font-bold text-xl text-accent">{initials}</span>
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
						class="inline-flex items-center h-9 px-3 rounded-card border border-rule bg-paper-2 hover:bg-paper-3 text-xs font-semibold text-ink transition-colors whitespace-nowrap"
					>
						Public dossier
					</a>
				{/if}
			</div>
		</div>

		{#if form?.success}
			<div class="p-3 rounded-card bg-paper-2 border border-rule text-success text-xs">
				Profile updated.
			</div>
		{/if}

		{#if form?.error}
			<div class="p-3 rounded-card bg-paper-2 border border-rule text-error text-xs">
				{form.error}
			</div>
		{/if}

		<dl class="space-y-3 text-xs border-b border-rule pb-6">
			<div class="flex justify-between py-1.5 border-b border-rule">
				<dt class="text-muted">Email</dt>
				<dd class="text-ink num font-outlier">{data.user?.email}</dd>
			</div>
			<div class="flex justify-between py-1.5 border-b border-rule">
				<dt class="text-muted">Username</dt>
				<dd class="text-ink font-semibold">@{data.profile?.username || 'unnamed'}</dd>
			</div>
			<div class="flex justify-between py-1.5">
				<dt class="text-muted">User ID</dt>
				<dd class="text-muted num font-outlier">{data.user?.id}</dd>
			</div>
		</dl>

		<!-- Avatar Upload -->
		<div class="space-y-3 border-b border-rule pb-6">
			<div class="space-y-1">
				<h2 class="text-lg font-bold text-ink">Supporter avatar</h2>
				<p class="text-xs text-muted">Upload a JPEG, PNG, or WebP portrait (max 3 MB).</p>
			</div>

			{#if avatarError}
				<p class="text-xs text-error">{avatarError}</p>
			{/if}
			{#if avatarStatus}
				<p class="text-xs text-success">{avatarStatus}</p>
			{/if}

			<div class="flex items-center gap-4 flex-wrap">
				<label
					for="avatar-upload"
					class="inline-flex items-center h-9 px-4 rounded-card border border-rule bg-paper-2 hover:bg-paper-3 text-xs font-semibold text-ink cursor-pointer transition-colors"
				>
					{isUploadingAvatar ? 'Uploading portrait…' : 'Choose portrait image'}
				</label>
				<input
					id="avatar-upload"
					type="file"
					accept="image/jpeg,image/png,image/webp"
					disabled={isUploadingAvatar}
					onchange={handleAvatarSelect}
					class="visually-hidden"
				/>
				<span class="text-xs text-muted">Stored in verified Arsenal supporter bucket.</span>
			</div>
		</div>

		<div class="space-y-5">
			<h2 class="text-lg font-bold text-ink">Edit profile</h2>

			<form method="POST" action="?/updateProfile" class="space-y-4">
				<input type="hidden" name="avatar_url" value={avatarUrl} />

				<div>
					<label for="display_name" class="block text-xs font-semibold text-ink-2 mb-1">
						Display name
					</label>
					<input
						id="display_name"
						name="display_name"
						type="text"
						required
						value={data.profile?.display_name || ''}
						class="w-full h-10 bg-paper-2 border border-rule rounded-card px-3 text-sm text-ink"
					/>
				</div>

				<div>
					<label for="bio" class="block text-xs font-semibold text-ink-2 mb-1">
						Bio & tactical focus
					</label>
					<textarea
						id="bio"
						name="bio"
						rows="3"
						placeholder="Share your favorite Arsenal era, tactical focus, or matchday routine…"
						class="w-full bg-paper-2 border border-rule rounded-card p-3 text-sm text-ink placeholder-muted"
					>{data.profile?.bio || ''}</textarea>
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
					<div class="w-full h-10 bg-paper-2 border border-rule rounded-card px-3 text-sm text-ink flex items-center">
						<span>Arsenal FC, Emirates Stadium</span>
					</div>
				</div>

				<div class="pt-2">
					<button
						type="submit"
						class="h-10 px-5 bg-accent hover:opacity-95 text-accent-ink font-semibold text-sm rounded-card transition-opacity"
					>
						Save changes
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
			<p class="text-xs text-error">{passwordError}</p>
		{/if}
		{#if passwordStatus}
			<p class="text-xs text-success">{passwordStatus}</p>
		{/if}

		<form onsubmit={handlePasswordUpdate} class="grid grid-cols-1 sm:grid-cols-2 gap-3">
			<div>
				<label for="profile-new-password" class="block text-xs font-semibold text-ink-2 mb-1">
					New password
				</label>
				<input
					id="profile-new-password"
					type="password"
					minlength="6"
					required
					bind:value={newPassword}
					placeholder="Minimum 6 characters"
					class="w-full h-9 bg-paper-2 border border-rule rounded-card px-3 text-sm text-ink placeholder-muted"
				/>
			</div>

			<div>
				<label for="profile-confirm-password" class="block text-xs font-semibold text-ink-2 mb-1">
					Confirm password
				</label>
				<input
					id="profile-confirm-password"
					type="password"
					minlength="6"
					required
					bind:value={confirmPassword}
					placeholder="Re-enter password"
					class="w-full h-9 bg-paper-2 border border-rule rounded-card px-3 text-sm text-ink placeholder-muted"
				/>
			</div>

			<div class="sm:col-span-2 pt-1">
				<button
					type="submit"
					disabled={isUpdatingPassword}
					class="h-9 px-4 rounded-card border border-rule bg-paper-2 hover:bg-paper-3 text-xs font-semibold text-ink transition-colors whitespace-nowrap"
				>
					{passwordBtnLabel}
				</button>
			</div>
		</form>
	</section>

	<div class="border-t border-rule pt-6 flex items-center justify-between gap-4">
		<div class="space-y-0.5">
			<h2 class="text-base font-bold text-ink">Sign out</h2>
			<p class="text-xs text-muted">End your current session on this device.</p>
		</div>
		<form method="POST" action="/auth/signout">
			<button
				type="submit"
				class="h-9 px-4 rounded-card bg-paper-2 hover:bg-paper-3 text-ink-2 hover:text-ink border border-rule text-xs font-semibold transition-colors"
			>
				Sign out
			</button>
		</form>
	</div>
</div>
