<script lang="ts">
	import type { HTMLButtonAttributes } from 'svelte/elements';

	let { checked = $bindable(false), ...rest }: HTMLButtonAttributes & { checked?: boolean } =
		$props();
</script>

<button
	type="button"
	role="switch"
	aria-checked={checked}
	onclick={() => (checked = !checked)}
	class="group inline-flex h-5 w-9 shrink-0 items-center rounded-full bg-input p-0.5 transition-colors focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:outline-none aria-checked:bg-primary"
	{...rest}
>
	<span
		class="block size-4 rounded-full bg-background transition-transform group-aria-checked:translate-x-4"
	></span>
</button>
