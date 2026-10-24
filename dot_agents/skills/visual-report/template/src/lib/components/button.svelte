<script lang="ts">
	import type { HTMLButtonAttributes } from 'svelte/elements';

	type Variant = 'default' | 'outline' | 'ghost';
	type Size = 'default' | 'sm';

	let {
		variant = 'default',
		size = 'default',
		type = 'button',
		children,
		...rest
	}: HTMLButtonAttributes & { variant?: Variant; size?: Size } = $props();

	const variants: Record<Variant, string> = {
		default: 'bg-primary text-primary-foreground hover:bg-primary/90',
		outline: 'border-input bg-background hover:bg-muted border',
		ghost: 'hover:bg-muted',
	};
	const sizes: Record<Size, string> = {
		default: 'h-9 px-4 text-sm',
		sm: 'h-8 px-3 text-xs',
	};
</script>

<button
	{type}
	class="inline-flex shrink-0 items-center justify-center gap-2 rounded-md font-medium whitespace-nowrap transition-colors focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:outline-none disabled:pointer-events-none disabled:opacity-50 {variants[
		variant
	]} {sizes[size]}"
	{...rest}
>
	{@render children?.()}
</button>
