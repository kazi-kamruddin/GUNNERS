const AUTH_BLOCKED_PREFIXES = ['/login', '/signup', '/auth/signout', '/auth/callback'];

export function getSafeRedirectPath(raw: string | null | undefined, fallback = '/'): string {
	if (!raw) return fallback;
	const trimmed = raw.trim();
	if (!trimmed.startsWith('/') || trimmed.startsWith('//') || trimmed.startsWith('/\\')) {
		return fallback;
	}
	if (/[\r\n\0]/.test(trimmed)) {
		return fallback;
	}
	try {
		const parsed = new URL(trimmed, 'https://gunners.local');
		if (parsed.origin !== 'https://gunners.local') return fallback;
		const normalized = `${parsed.pathname}${parsed.search}${parsed.hash}`;
		if (AUTH_BLOCKED_PREFIXES.some((prefix) => parsed.pathname === prefix || parsed.pathname.startsWith(`${prefix}/`))) {
			return fallback;
		}
		return normalized || fallback;
	} catch {
		return fallback;
	}
}
