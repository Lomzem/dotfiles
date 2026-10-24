// Checks the built report against the limits of T3 Code's html_render tool, then
// copies it to `<report dir>/<report dir name>.html`.
import { chromium } from '@playwright/test';
import { basename, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

// Keep the single-file tool payload small. Transfer it through code, outside model context.
const maxCharacters = 100_000;

const html = await Bun.file('dist/index.html').text();
const problems: string[] = [];

if (html.length > maxCharacters) {
	problems.push(
		`The report is ${html.length} characters; the limit is ${maxCharacters}. Remove dependencies, large assets, or repeated markup.`,
	);
}

// html_render rejects viewport-height units: its frame grows to fit the page, so they loop.
const viewportUnits = html.match(/(?<![\w-])\d*\.?\d+[sld]?vh\b/g);
if (viewportUnits) {
	problems.push(
		`Viewport-height units (${[...new Set(viewportUnits)].join(', ')}) break html_render. Let content set the height.`,
	);
}

// Observe actual resource loads, including CSS fonts and URLs assembled in JavaScript.
// Anchors are outbound navigation, so they produce no request while opening the report.
if (problems.length === 0) {
	const remoteRequests = new Set<string>();
	const browser = await chromium.launch();
	try {
		const page = await browser.newPage({ serviceWorkers: 'block' });
		await page.route('**/*', (route) => {
			const url = route.request().url();
			if (['file:', 'data:', 'blob:', 'about:'].includes(new URL(url).protocol)) {
				return route.continue();
			}
			remoteRequests.add(url);
			return route.abort();
		});
		await page.goto(pathToFileURL(resolve('dist/index.html')).href, {
			waitUntil: 'networkidle',
		});
		// Lazy assets may not request anything at this viewport size.
		const deferredAssets = await page
			.locator('img[src], iframe[src]')
			.evaluateAll((elements) =>
				elements.map((element) => new URL(element.getAttribute('src')!, document.baseURI).href),
			);
		for (const url of deferredAssets) {
			if (!['file:', 'data:', 'blob:', 'about:'].includes(new URL(url).protocol)) {
				remoteRequests.add(url);
			}
		}
	} finally {
		await browser.close();
	}
	if (remoteRequests.size > 0) {
		problems.push(
			`The report loads remote resources (${[...remoteRequests].join(', ')}). Import or inline them so it works offline.`,
		);
	}
}

if (problems.length > 0) {
	console.error(problems.map((problem) => `✗ ${problem}`).join('\n'));
	process.exit(1);
}

const reportPath = resolve(`${basename(process.cwd())}.html`);
await Bun.write(reportPath, html);
console.log(`${reportPath} (${Math.round(html.length / 1000)} kB)`);
