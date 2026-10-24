import { test as base, expect, type Page } from '@playwright/test';
import { basename, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

/** The exported report: `<report dir>/<report dir name>.html`. */
export const reportPath = resolve(`${basename(process.cwd())}.html`);
export const reportUrl = pathToFileURL(reportPath).href;
const localSchemes = ['file:', 'data:', 'blob:', 'about:'];

/**
 * A page that opens the exported report with the network blocked.
 * `remoteRequests` and `errors` collect what the report must never produce.
 */
export const test = base.extend<{
	report: Page;
	remoteRequests: string[];
	errors: string[];
}>({
	remoteRequests: async ({}, use) => use([]),
	errors: async ({}, use) => use([]),
	report: async ({ page, remoteRequests, errors }, use) => {
		await page.route('**/*', (route) => {
			const url = route.request().url();
			if (localSchemes.includes(new URL(url).protocol)) return route.continue();
			remoteRequests.push(url);
			return route.abort();
		});
		page.on('pageerror', (error) => errors.push(error.message));
		page.on('console', (message) => {
			if (message.type() === 'error') errors.push(message.text());
		});
		await page.goto(reportUrl);
		await use(page);
	},
});

export { expect };
