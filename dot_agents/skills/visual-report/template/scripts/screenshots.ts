// Baseline screenshots of the delivered report file for visual inspection.
// Saves full-page PNGs to test-results/screenshots/ and prints their paths.
import { chromium, type Page } from '@playwright/test';
import { openSelfContained, reportUrl } from './self-contained.ts';

const outDir = 'test-results/screenshots';
const useLightTheme = async (page: Page) => {
	await page.getByRole('switch', { name: 'Dark theme' }).click();
	await page.waitForTimeout(500); // Let color transitions settle.
};
const shots: { name: string; width: number; prepare?: (page: Page) => Promise<void> }[] = [
	{ name: 'desktop-dark', width: 1280 },
	{ name: 'desktop-light', width: 1280, prepare: useLightTheme },
	{ name: 'phone-375-dark', width: 375 },
	{ name: 'phone-320-dark', width: 320 },
];

const browser = await chromium.launch();
try {
	for (const { name, width, prepare } of shots) {
		const page = await browser.newPage({ viewport: { width, height: 800 } });
		await openSelfContained(page, reportUrl);
		await prepare?.(page);
		const path = `${outDir}/${name}.png`;
		await page.screenshot({ path, fullPage: true });
		console.log(path);
		await page.close();
	}
} finally {
	await browser.close();
}
