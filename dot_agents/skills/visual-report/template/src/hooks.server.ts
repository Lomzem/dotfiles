import type { Handle } from '@sveltejs/kit/hooks';
import { themeScript } from '#lib/theme-script.js';

export const handle: Handle = ({ event, resolve }) =>
	resolve(event, {
		transformPageChunk: ({ html }) => html.replace('%report.themeScript%', themeScript),
	});
