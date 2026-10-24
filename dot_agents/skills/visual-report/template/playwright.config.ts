import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
	testDir: 'tests',
	forbidOnly: true,
	reporter: 'line',
	use: { ...devices['Desktop Chrome'] },
});
