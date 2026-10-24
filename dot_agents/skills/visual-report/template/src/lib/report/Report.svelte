<script lang="ts">
	import * as Tabs from '#lib/components/ui/tabs/index.js';
</script>

<section aria-labelledby="summary-heading" class="flex flex-col gap-4">
	<h2 id="summary-heading" class="text-xl font-semibold">Summary</h2>
	<p class="max-w-prose text-muted-foreground">Replace this starter with the report.</p>
</section>

<Tabs.Root value="overview">
	<Tabs.List>
		<Tabs.Trigger value="overview">Overview</Tabs.Trigger>
		<Tabs.Trigger value="details">Details</Tabs.Trigger>
	</Tabs.List>
	<Tabs.Content value="overview">
		<p class="max-w-prose">Overview panel.</p>
	</Tabs.Content>
	<Tabs.Content value="details">
		<p class="max-w-prose">Details panel.</p>
	</Tabs.Content>
</Tabs.Root>
