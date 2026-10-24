<script lang="ts" generics="Value extends string">
	import type { Snippet } from 'svelte';

	// The WAI-ARIA tabs pattern: arrow keys, Home, and End move between tabs and select them.
	let {
		tabs,
		value = $bindable(tabs[0].value),
		label,
		panel,
	}: {
		tabs: { value: Value; label: string }[];
		value?: Value;
		/** Names the tab list for screen readers. */
		label: string;
		panel: Snippet<[Value]>;
	} = $props();

	const id = $props.id();
	const buttons: HTMLButtonElement[] = [];

	function onkeydown(event: KeyboardEvent, index: number) {
		const last = tabs.length - 1;
		const next = {
			ArrowRight: index === last ? 0 : index + 1,
			ArrowLeft: index === 0 ? last : index - 1,
			Home: 0,
			End: last,
		}[event.key];
		if (next === undefined) return;
		event.preventDefault();
		value = tabs[next].value;
		buttons[next].focus();
	}
</script>

<div class="flex flex-col gap-4">
	<div role="tablist" aria-label={label} class="flex w-fit flex-wrap gap-1 rounded-lg bg-muted p-1">
		{#each tabs as tab, index (tab.value)}
			<button
				bind:this={buttons[index]}
				type="button"
				role="tab"
				id="{id}-tab-{tab.value}"
				aria-selected={value === tab.value}
				aria-controls="{id}-panel-{tab.value}"
				tabindex={value === tab.value ? 0 : -1}
				onclick={() => (value = tab.value)}
				onkeydown={(event) => onkeydown(event, index)}
				class="rounded-md px-3 py-1 text-sm font-medium text-muted-foreground transition-colors focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none aria-selected:bg-background aria-selected:text-foreground"
			>
				{tab.label}
			</button>
		{/each}
	</div>
	{#each tabs as tab (tab.value)}
		<div
			role="tabpanel"
			id="{id}-panel-{tab.value}"
			aria-labelledby="{id}-tab-{tab.value}"
			hidden={value !== tab.value}
		>
			{#if value === tab.value}
				{@render panel(tab.value)}
			{/if}
		</div>
	{/each}
</div>
