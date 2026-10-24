import path from 'node:path';
import js from '@eslint/js';
import { plugin as shadcn } from '@shadcn/lint';
import svelte from 'eslint-plugin-svelte';
import { defineConfig, includeIgnoreFile } from 'eslint/config';
import globals from 'globals';
import ts from 'typescript-eslint';

const gitignorePath = path.resolve(import.meta.dirname, '.gitignore');

// Theme tokens keep both themes at WCAG contrast; these rules hold report code to them.
// Components under ui/ are vendored from shadcn-svelte and own their styling.
const designSystemRules = {
	'shadcn/no-raw-colors': 'error',
	'shadcn/no-arbitrary-values': 'error',
	'shadcn/no-unknown-classes': 'error',
	'shadcn/require-static-classes': 'error',
	'shadcn/no-restyle': ['error', { allow: ['layout'] }],
};

export default defineConfig(
	includeIgnoreFile(gitignorePath),
	js.configs.recommended,
	ts.configs.recommended,
	svelte.configs.recommended,
	{
		languageOptions: { globals: { ...globals.browser, ...globals.node } },
		rules: {
			// TypeScript checks undefined names; see https://typescript-eslint.io/troubleshooting/faqs/eslint/
			'no-undef': 'off',
			// A report is one page, and the export runs without the SvelteKit router.
			'svelte/no-navigation-without-resolve': 'off',
		},
	},
	{
		files: ['**/*.svelte', '**/*.svelte.ts', '**/*.svelte.js'],
		languageOptions: {
			parserOptions: {
				projectService: true,
				extraFileExtensions: ['.svelte'],
				parser: ts.parser,
			},
		},
	},
	{
		// Playwright fixtures that use no other fixture take an empty pattern.
		files: ['tests/**/*.ts'],
		rules: { 'no-empty-pattern': 'off' },
	},
	{
		files: ['src/**/*.svelte', 'src/**/*.ts'],
		ignores: ['src/lib/components/ui/**'],
		plugins: { shadcn },
		rules: designSystemRules,
	},
);
