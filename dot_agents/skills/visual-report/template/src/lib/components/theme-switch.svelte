<script lang="ts">
	import { Label } from '#lib/components/ui/label/index.js';
	import { Switch } from '#lib/components/ui/switch/index.js';
	import { createTheme } from '#lib/theme.svelte.js';

	const theme = createTheme();
</script>

<div class="flex items-center gap-2">
	<Switch id="theme-switch" bind:checked={() => theme.dark, (value) => (theme.dark = value)} />
	<Label for="theme-switch">Dark theme</Label>
</div>
