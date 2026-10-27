// Screenshots of the served report (`bun run serve`) for visual inspection.
// Saves full-page PNGs to test-results/screenshots/ and prints their paths.
import { chromium, type Page } from '@playwright/test';

const url = 'http://localhost:4173/';
const outDir = 'test-results/screenshots';
const shots: { name: string; width: number; prepare?: (page: Page) => Promise<void> }[] = [
	{ name: 'desktop-dark', width: 1280 },
	{
		name: 'desktop-light',
		width: 1280,
		prepare: async (page) => {
			await page.getByRole('switch', { name: 'Dark theme' }).click();
			await page.waitForTimeout(500); // Let color transitions settle.
		},
	},
	{ name: 'phone-dark', width: 375 },
];

const browser = await chromium.launch();
for (const { name, width, prepare } of shots) {
	const page = await browser.newPage({ viewport: { width, height: 800 } });
	await page.goto(url);
	await prepare?.(page);
	const path = `${outDir}/${name}.png`;
	await page.screenshot({ path, fullPage: true });
	console.log(path);
	await page.close();
}
await browser.close();
