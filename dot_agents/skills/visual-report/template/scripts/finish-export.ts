// Verifies the export is self-contained, then copies it to `<report dir>/<report dir name>.html`.
import { chromium } from '@playwright/test';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
import { deferredExternalSources, openSelfContained, reportPath } from './self-contained.ts';

const exportPath = resolve('dist/index.html');
const exportUrl = pathToFileURL(exportPath).href;
const html = await Bun.file(exportPath).text();

// Observe actual loads, including CSS fonts and URLs assembled in JavaScript.
const browser = await chromium.launch();
const external = new Set<string>();
try {
	const page = await browser.newPage({ serviceWorkers: 'block' });
	for (const url of await openSelfContained(page, exportUrl)) external.add(url);
	for (const url of await deferredExternalSources(page, exportUrl)) external.add(url);
} finally {
	await browser.close();
}

if (external.size > 0) {
	console.error(
		`✗ The report loads resources outside its own file (${[...external].join(', ')}). Import them so the export inlines them.`,
	);
	process.exit(1);
}

await Bun.write(reportPath, html);
console.log(`${reportPath} (${Math.round(html.length / 1000)} kB)`);
