import { describe, expect, it } from 'vitest';
import { getSafeRedirectPath } from '$lib/utils/redirect';

describe('getSafeRedirectPath', () => {
	it('preserves safe internal relative paths with query parameters and fragments', () => {
		expect(getSafeRedirectPath('/terrace')).toBe('/terrace');
		expect(getSafeRedirectPath('/lab?tab=trends&venue=home#chart')).toBe('/lab?tab=trends&venue=home#chart');
		expect(getSafeRedirectPath('  /predictions?match=123  ')).toBe('/predictions?match=123');
	});

	it('falls back when raw input is empty or missing', () => {
		expect(getSafeRedirectPath(null)).toBe('/');
		expect(getSafeRedirectPath(undefined)).toBe('/');
		expect(getSafeRedirectPath('')).toBe('/');
		expect(getSafeRedirectPath('   ', '/profile')).toBe('/profile');
	});

	it('blocks protocol-relative, backslash, and external open-redirect payloads', () => {
		expect(getSafeRedirectPath('//evil.com/phish')).toBe('/');
		expect(getSafeRedirectPath('/\\evil.com')).toBe('/');
		expect(getSafeRedirectPath('https://evil.com/login')).toBe('/');
		expect(getSafeRedirectPath('http://localhost:8000/admin')).toBe('/');
		expect(getSafeRedirectPath('javascript:alert(1)')).toBe('/');
		expect(getSafeRedirectPath('terrace')).toBe('/');
	});

	it('blocks control characters and CR/LF header injection attempts', () => {
		expect(getSafeRedirectPath('/terrace\r\nSet-Cookie: a=1')).toBe('/');
		expect(getSafeRedirectPath('/lab\nLocation: //evil.com')).toBe('/');
		expect(getSafeRedirectPath('/board\0')).toBe('/');
	});

	it('prevents auth redirect loops back into login, signup, signout, and callback routes', () => {
		expect(getSafeRedirectPath('/login', '/profile')).toBe('/profile');
		expect(getSafeRedirectPath('/login?next=/terrace', '/profile')).toBe('/profile');
		expect(getSafeRedirectPath('/signup', '/profile')).toBe('/profile');
		expect(getSafeRedirectPath('/auth/signout', '/')).toBe('/');
		expect(getSafeRedirectPath('/auth/callback?code=abc', '/')).toBe('/');
		expect(getSafeRedirectPath('/auth/callback/extra', '/')).toBe('/');
	});
});
