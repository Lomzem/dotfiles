import { afterAll, expect, test } from 'bun:test';
import { existsSync, mkdtempSync, mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { basename, join, resolve } from 'node:path';

const script = resolve(import.meta.dir, '../template/scripts/finish-export.ts');
const home = mkdtempSync(join(tmpdir(), 'visual-report-export-test-'));
afterAll(() => rmSync(home, { recursive: true, force: true }));

async function exportReport(body: string) {
	const dir = mkdtempSync(join(home, 'report-'));
	mkdirSync(join(dir, 'dist'));
	const html = `<!doctype html><html lang="en"><title>Report</title><body>${body}</body></html>`;
	writeFileSync(join(dir, 'dist/index.html'), html);
	const process = Bun.spawn(['bun', script], {
		cwd: dir,
		stdout: 'pipe',
		stderr: 'pipe',
	});
	const [exitCode, stdout, stderr] = await Promise.all([
		process.exited,
		new Response(process.stdout).text(),
		new Response(process.stderr).text(),
	]);
	return { dir, html, exitCode, stdout, stderr };
}

test('exports an offline report with an outbound citation link', async () => {
	const result = await exportReport(
		'<h1>Report</h1><a href="https://example.com/source">Citation</a>',
	);
	expect(result.stderr).toBe('');
	expect(result.exitCode).toBe(0);
	expect(readFileSync(join(result.dir, `${basename(result.dir)}.html`), 'utf8')).toBe(result.html);
});

test.each([
	['script', '<script src="https://example.com/asset.js"></script>'],
	['image', '<img src="https://example.com/asset.png" alt="Chart">'],
	[
		'lazy image',
		'<img loading="lazy" style="margin-top: 10000px" src="https://example.com/asset.png" alt="Chart">',
	],
	['stylesheet', '<link rel="stylesheet" href="https://example.com/asset.css">'],
	[
		'fetch hidden in a variable',
		'<script>const url = "https://example.com/data"; fetch(url).catch(() => {});</script>',
	],
	[
		'font',
		'<style>@font-face { font-family: Remote; src: url(https://example.com/font.woff2); } body { font-family: Remote; }</style>Text',
	],
])('rejects a network-dependent %s', async (_name, markup) => {
	const result = await exportReport(markup);
	expect(result.exitCode).not.toBe(0);
	expect(result.stderr).toContain('The report loads remote resources');
	expect(result.stderr).toContain('https://example.com/');
	expect(existsSync(join(result.dir, `${basename(result.dir)}.html`))).toBe(false);
});
