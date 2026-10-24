import AxeBuilder from '@axe-core/playwright';
import { expect, reportUrl, test } from './report-file';

const themeSwitch = (page: import('@playwright/test').Page) =>
	page.getByRole('switch', { name: 'Dark theme' });

test('opens offline without remote requests or errors', async ({
	report,
	remoteRequests,
	errors,
}) => {
	await expect(report.getByRole('heading', { level: 1 })).toBeVisible();
	await expect(report.getByRole('main')).toBeVisible();
	expect(remoteRequests).toEqual([]);
	expect(errors).toEqual([]);
});

test('starts in the dark theme', async ({ report }) => {
	await expect(report.locator('html')).toHaveClass(/\bdark\b/);
	await expect(themeSwitch(report)).toBeChecked();
});

test('theme switch changes the theme and remembers the choice', async ({ report }) => {
	await themeSwitch(report).click();
	await expect(report.locator('html')).not.toHaveClass(/\bdark\b/);
	await report.reload();
	await expect(report.locator('html')).not.toHaveClass(/\bdark\b/);
	await expect(themeSwitch(report)).not.toBeChecked();

	await themeSwitch(report).press('Space');
	await expect(report.locator('html')).toHaveClass(/\bdark\b/);
});

test('skip link is the first tab stop and moves focus to the main content', async ({ report }) => {
	await report.keyboard.press('Tab');
	const skipLink = report.getByRole('link', { name: 'Skip to content' });
	await expect(skipLink).toBeFocused();
	await report.keyboard.press('Enter');
	await expect(report.getByRole('main')).toBeFocused();
});

for (const theme of ['dark', 'light'] as const) {
	test(`has no WCAG 2.2 AA violations in the ${theme} theme`, async ({ report }) => {
		if (theme === 'light') await themeSwitch(report).click();
		const results = await new AxeBuilder({ page: report })
			.withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa', 'best-practice'])
			.analyze();
		expect(results.violations).toEqual([]);
	});
}

test('reflows at 320 CSS pixels without horizontal scrolling', async ({ report }) => {
	await report.setViewportSize({ width: 320, height: 640 });
	const overflow = await report.evaluate(
		() => document.documentElement.scrollWidth - document.documentElement.clientWidth,
	);
	expect(overflow).toBeLessThanOrEqual(0);
});

test('theme switch works when storage is blocked, as in a sandboxed frame', async ({ page }) => {
	await page.addInitScript(() => {
		Object.defineProperty(window, 'localStorage', {
			get() {
				throw new DOMException('Blocked', 'SecurityError');
			},
		});
	});
	const errors: string[] = [];
	page.on('pageerror', (error) => errors.push(error.message));
	await page.goto(reportUrl);

	await expect(page.locator('html')).toHaveClass(/\bdark\b/);
	await themeSwitch(page).click();
	await expect(page.locator('html')).not.toHaveClass(/\bdark\b/);
	expect(errors).toEqual([]);
});
