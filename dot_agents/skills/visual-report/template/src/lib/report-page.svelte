<script lang="ts">
	import ReportShell from '#lib/components/report-shell.svelte';
	import Report from '#lib/report/Report.svelte';
	import { title } from '#lib/report/meta.js';
</script>

<svelte:head>
	<title>{title}</title>
</svelte:head>

<ReportShell {title}>
	<Report />
</ReportShell>
