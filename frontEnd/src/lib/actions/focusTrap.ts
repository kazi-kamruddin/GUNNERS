import type { Action } from 'svelte/action';

export interface FocusTrapOptions {
	active: boolean;
	onEscape?: () => void;
	initialFocusSelector?: string;
	restoreFocus?: boolean;
}

type FocusableDomElement = HTMLElement | SVGElement;

const FOCUSABLE_SELECTOR = [
	'a[href]',
	'button:not(:disabled)',
	'input:not(:disabled):not([type="hidden"])',
	'select:not(:disabled)',
	'textarea:not(:disabled)',
	'[tabindex]:not([tabindex="-1"])'
].join(', ');

function isFocusableDomElement(el: Element | null): el is FocusableDomElement {
	return el instanceof HTMLElement || el instanceof SVGElement;
}

function focusSafely(target: FocusableDomElement, preventScroll = false) {
	if (!target.isConnected) return;
	try {
		target.focus(preventScroll ? { preventScroll: true } : undefined);
	} catch {
		target.focus();
	}
}

function getFocusableElements(container: HTMLElement): FocusableDomElement[] {
	return Array.from(container.querySelectorAll(FOCUSABLE_SELECTOR)).filter(
		(el): el is FocusableDomElement => {
			if (!isFocusableDomElement(el)) return false;
			if (el.hasAttribute('disabled') || el.getAttribute('aria-hidden') === 'true') return false;
			const style = window.getComputedStyle(el);
			if (style.display === 'none' || style.visibility === 'hidden') return false;
			return el.getClientRects().length > 0;
		}
	);
}

export const focusTrap: Action<HTMLElement, FocusTrapOptions> = (node, initialOptions) => {
	let options = initialOptions;
	let isActive = false;
	let previousFocus: FocusableDomElement | null = null;

	function focusInitial() {
		if (!isActive) return;
		const selector = options.initialFocusSelector;
		if (selector) {
			const explicit = node.querySelector(selector);
			if (isFocusableDomElement(explicit) && explicit.getClientRects().length > 0) {
				focusSafely(explicit);
				return;
			}
		}
		const focusables = getFocusableElements(node);
		if (focusables.length > 0) {
			focusSafely(focusables[0]);
			return;
		}
		if (!node.hasAttribute('tabindex')) {
			node.setAttribute('tabindex', '-1');
		}
		focusSafely(node);
	}

	function handleKeydown(event: KeyboardEvent) {
		if (!isActive) return;

		if (event.key === 'Escape') {
			if (options.onEscape) {
				event.preventDefault();
				event.stopPropagation();
				options.onEscape();
			}
			return;
		}

		if (event.key !== 'Tab') return;

		const focusables = getFocusableElements(node);
		if (focusables.length === 0) {
			event.preventDefault();
			focusSafely(node);
			return;
		}

		const first = focusables[0];
		const last = focusables[focusables.length - 1];
		const activeElement = document.activeElement;

		if (!activeElement || !node.contains(activeElement)) {
			event.preventDefault();
			focusSafely(event.shiftKey ? last : first);
			return;
		}

		if (event.shiftKey && activeElement === first) {
			event.preventDefault();
			focusSafely(last);
		} else if (!event.shiftKey && activeElement === last) {
			event.preventDefault();
			focusSafely(first);
		}
	}

	function activate() {
		if (isActive) return;
		isActive = true;
		const active = document.activeElement;
		previousFocus = isFocusableDomElement(active) ? active : null;
		document.addEventListener('keydown', handleKeydown, true);
		queueMicrotask(() => {
			if (isActive) focusInitial();
		});
	}

	function deactivate(shouldRestore = options.restoreFocus !== false) {
		if (!isActive) return;
		isActive = false;
		document.removeEventListener('keydown', handleKeydown, true);
		if (shouldRestore && previousFocus && previousFocus.isConnected) {
			const target = previousFocus;
			previousFocus = null;
			queueMicrotask(() => {
				focusSafely(target, true);
			});
		} else {
			previousFocus = null;
		}
	}

	if (options?.active) {
		activate();
	}

	return {
		update(nextOptions: FocusTrapOptions) {
			const wasRestore = options?.restoreFocus !== false;
			options = nextOptions;
			if (nextOptions.active && !isActive) {
				activate();
			} else if (!nextOptions.active && isActive) {
				deactivate(nextOptions.restoreFocus !== undefined ? nextOptions.restoreFocus : wasRestore);
			}
		},
		destroy() {
			deactivate(options?.restoreFocus !== false);
		}
	};
};
