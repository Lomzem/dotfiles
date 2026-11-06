import { test as base, expect, type Page } from '@playwright/test';
import { openSelfContained, reportUrl } from '../scripts/self-contained.ts';

/**
 * A page that opens the exported report with every load outside the file blocked.
 * `externalRequests` and `errors` collect what the report must never produce.
 */
export const test = base.extend<{
	report: Page;
	externalRequests: string[];
	errors: string[];
}>({
	externalRequests: async ({}, use) => use([]),
	errors: async ({}, use) => use([]),
	report: async ({ page, externalRequests, errors }, use) => {
		page.on('pageerror', (error) => errors.push(error.message));
		page.on('console', (message) => {
			if (message.type() === 'error') errors.push(message.text());
		});
		await openSelfContained(page, reportUrl, externalRequests);
		await use(page);
	},
});

export { expect, reportUrl };
