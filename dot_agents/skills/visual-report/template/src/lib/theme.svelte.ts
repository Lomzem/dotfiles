import { themeStorageKey } from './theme-script.js';

/** Dark is the default. Storage can be blocked (sandboxed frames), so the choice is best-effort. */
export function createTheme() {
	let dark = $state(document.documentElement.classList.contains('dark'));

	return {
		get dark() {
			return dark;
		},
		set dark(value: boolean) {
			dark = value;
			document.documentElement.classList.toggle('dark', value);
			try {
				localStorage.setItem(themeStorageKey, value ? 'dark' : 'light');
			} catch {
				// The theme still changes; it just won't persist.
			}
		},
	};
}
