<script lang="ts">
	import Tabs from '#lib/components/tabs.svelte';
</script>

<section aria-labelledby="summary-heading" class="flex flex-col gap-4">
	<h2 id="summary-heading" class="text-xl font-semibold">Summary</h2>
	<p class="max-w-prose text-muted-foreground">Replace this starter with the report.</p>
</section>

<Tabs
	label="Starter views"
	tabs={[
		{ value: 'overview', label: 'Overview' },
		{ value: 'details', label: 'Details' },
	]}
>
	{#snippet panel(value)}
		<p class="max-w-prose">{value === 'overview' ? 'Overview panel.' : 'Details panel.'}</p>
	{/snippet}
</Tabs>
