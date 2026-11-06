import { afterAll, expect, test } from 'bun:test';
import { existsSync, mkdtempSync, mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { basename, join, resolve } from 'node:path';

const script = resolve(import.meta.dir, '../template/scripts/finish-export.ts');
const home = mkdtempSync(join(tmpdir(), 'visual-report-export-test-'));
afterAll(() => rmSync(home, { recursive: true, force: true }));

// `{dir}` in the body stands for the report directory. Every case writes the same
// sibling assets beside the export, so a local reference would resolve.
async function exportReport(body: string) {
	const dir = mkdtempSync(join(home, 'report-'));
	mkdirSync(join(dir, 'dist'));
	const html = `<!doctype html><html lang="en"><title>Report</title><body>${body.replaceAll('{dir}', dir)}</body></html>`;
	writeFileSync(join(dir, 'dist/index.html'), html);
	writeFileSync(join(dir, 'dist/asset.css'), 'body { color: red; }');
	writeFileSync(join(dir, 'dist/asset.png'), '');
	writeFileSync(join(dir, 'asset.png'), '');
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

test('exports a self-contained report with inline assets and an outbound citation link', async () => {
	const result = await exportReport(
		'<h1>Report</h1><a href="https://example.com/source">Citation</a>' +
			'<style>body { color: blue; }</style><img alt="Dot" src="data:image/gif;base64,R0lGODlhAQABAAAAACw=">' +
			'<a href="#top">Top</a><script>URL.createObjectURL(new Blob(["x"]));</script>',
	);
	expect(result.stderr).toBe('');
	expect(result.exitCode).toBe(0);
	expect(readFileSync(join(result.dir, `${basename(result.dir)}.html`), 'utf8')).toBe(result.html);
});

// Each case names the URL the report must not load; `{dir}` is the report directory.
test.each([
	['remote script', '<script src="https://example.com/asset.js"></script>', 'https://example.com/asset.js'],
	['remote image', '<img src="https://example.com/asset.png" alt="Chart">', 'https://example.com/asset.png'],
	[
		'lazy remote image',
		'<img loading="lazy" style="margin-top: 10000px" src="https://example.com/asset.png" alt="Chart">',
		'https://example.com/asset.png',
	],
	[
		'remote stylesheet',
		'<link rel="stylesheet" href="https://example.com/asset.css">',
		'https://example.com/asset.css',
	],
	[
		'fetch hidden in a variable',
		'<script>const url = "https://example.com/data"; fetch(url).catch(() => {});</script>',
		'https://example.com/data',
	],
	[
		'remote font',
		'<style>@font-face { font-family: Remote; src: url(https://example.com/font.woff2); } body { font-family: Remote; }</style>Text',
		'https://example.com/font.woff2',
	],
	['sibling stylesheet', '<link rel="stylesheet" href="asset.css">', 'file://{dir}/dist/asset.css'],
	['sibling image', '<img src="./asset.png" alt="Chart">', 'file://{dir}/dist/asset.png'],
	[
		'lazy sibling image',
		'<img loading="lazy" style="margin-top: 10000px" src="asset.png" alt="Chart">',
		'file://{dir}/dist/asset.png',
	],
	['absolute file image', '<img src="file://{dir}/asset.png" alt="Chart">', 'file://{dir}/asset.png'],
])('rejects an external %s', async (_name, markup, url) => {
	const result = await exportReport(markup);
	expect(result.exitCode).not.toBe(0);
	expect(result.stderr).toContain(url.replace('{dir}', result.dir));
	expect(existsSync(join(result.dir, `${basename(result.dir)}.html`))).toBe(false);
});
