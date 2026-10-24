<script lang="ts">
	import Switch from './switch.svelte';
	import { createTheme } from '#lib/theme.svelte.js';

	const theme = createTheme();
</script>

<div class="flex items-center gap-2">
	<Switch id="theme-switch" bind:checked={() => theme.dark, (value) => (theme.dark = value)} />
	<label for="theme-switch" class="text-sm font-medium">Dark theme</label>
</div>
