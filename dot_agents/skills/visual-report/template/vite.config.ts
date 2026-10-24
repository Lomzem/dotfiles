import tailwindcss from '@tailwindcss/vite';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

// Dev preview with hot reload: `bun run dev`. The standalone export uses vite.export.config.ts.
export default defineConfig({
	plugins: [tailwindcss(), sveltekit({ compilerOptions: { runes: true } })],
});
