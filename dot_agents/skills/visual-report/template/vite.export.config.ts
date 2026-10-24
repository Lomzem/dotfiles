import { svelte } from '@sveltejs/vite-plugin-svelte';
import tailwindcss from '@tailwindcss/vite';
import { fileURLToPath } from 'node:url';
import { defineConfig } from 'vite';
import { viteSingleFile } from 'vite-plugin-singlefile';
import { title } from './src/lib/report/meta.ts';
import { themeScript } from './src/lib/theme-script.ts';

const escapeHtml = (text: string) => text.replace(/[&<>"]/g, (char) => `&#${char.charCodeAt(0)};`);

// Builds the report into one HTML file with every script, style, and asset inlined.
export default defineConfig({
	root: 'src/export',
	resolve: {
		alias: [{ find: /^#lib/, replacement: fileURLToPath(new URL('src/lib', import.meta.url)) }],
	},
	plugins: [
		tailwindcss(),
		svelte({ compilerOptions: { runes: true } }),
		viteSingleFile(),
		{
			name: 'report-head',
			transformIndexHtml: (html) =>
				html
					.replace('%report.title%', escapeHtml(title))
					.replace('%report.themeScript%', themeScript),
		},
	],
	build: { outDir: '../../dist', emptyOutDir: true },
});
