<script lang="ts">
	import type { Snippet } from 'svelte';
	import ThemeSwitch from './theme-switch.svelte';

	let { title, children }: { title: string; children: Snippet } = $props();
</script>

<a
	href="#content"
	class="sr-only z-50 rounded-md bg-primary px-4 py-2 text-primary-foreground focus:not-sr-only focus:fixed focus:top-4 focus:left-4"
>
	Skip to content
</a>

<div class="mx-auto flex w-full max-w-5xl flex-col gap-8 px-4 py-6 sm:px-6 lg:px-8">
	<header class="flex flex-wrap items-center justify-between gap-4 border-b pb-4">
		<h1 class="text-2xl font-semibold tracking-tight text-balance sm:text-3xl">{title}</h1>
		<ThemeSwitch />
	</header>

	<main id="content" tabindex="-1" class="flex flex-col gap-8 outline-none">
		{@render children()}
	</main>
</div>
