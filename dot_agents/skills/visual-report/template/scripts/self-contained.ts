// The self-contained export policy, shared by the export check and the report tests.
// The report may load only its own document and inline, data, or blob resources.
// Anchors are outbound navigation, so citation links load nothing while the report opens.
import type { Page } from '@playwright/test';
import { basename, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

/** The delivered report: `<report dir>/<report dir name>.html`. */
export const reportPath = resolve(`${basename(process.cwd())}.html`);
export const reportUrl = pathToFileURL(reportPath).href;

const inlineSchemes = ['data:', 'blob:', 'about:'];

function isExternal(url: string, documentUrl: string) {
	const { protocol } = new URL(url);
	if (inlineSchemes.includes(protocol)) return false;
	return url.split('#')[0] !== documentUrl.split('#')[0];
}

/**
 * Opens the report at `documentUrl` with every external load blocked.
 * `external` collects each blocked URL for as long as the page stays open.
 */
export async function openSelfContained(page: Page, documentUrl: string, external: string[] = []) {
	await page.route('**/*', (route) => {
		const url = route.request().url();
		if (!isExternal(url, documentUrl)) return route.continue();
		external.push(url);
		return route.abort();
	});
	await page.goto(documentUrl, { waitUntil: 'networkidle' });
	return external;
}

/** Element sources that would load later, such as lazy images below the viewport. */
export async function deferredExternalSources(page: Page, documentUrl: string) {
	const sources = await page
		.locator('[src]')
		.evaluateAll((elements) =>
			elements.map((element) => new URL(element.getAttribute('src')!, document.baseURI).href),
		);
	return sources.filter((url) => isExternal(url, documentUrl));
}
