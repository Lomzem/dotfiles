import { expect, test } from './report-file';

// One test per interaction this report offers. Replace these with the report's own.

test('tabs switch the visible panel', async ({ report }) => {
	await report.getByRole('tab', { name: 'Details' }).click();
	await expect(report.getByRole('tabpanel', { name: 'Details' })).toBeVisible();
});
