import { afterAll, expect, test } from 'bun:test';
import { existsSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const script = join(import.meta.dir, 'new-report.ts');
const home = mkdtempSync(join(tmpdir(), 'visual-report-test-'));
afterAll(() => rmSync(home, { recursive: true, force: true }));

function newReport(args: string[], reportHome = home) {
	const result = Bun.spawnSync(['bun', script, ...args], {
		env: { ...process.env, VISUAL_REPORT_HOME: reportHome },
	});
	return {
		exitCode: result.exitCode,
		stdout: result.stdout.toString().trim(),
		stderr: result.stderr.toString(),
	};
}

const git = (dir: string, ...args: string[]) =>
	Bun.spawnSync(['git', '-C', dir, ...args]).stdout.toString().trim();

const created = newReport(['cache-hit-rates', "Why the cache's hit rate fell"]);
const reportDir = created.stdout.split('\n').at(-1)!;

test('creates an editable report under the report home', () => {
	expect(created.exitCode).toBe(0);
	expect(reportDir.startsWith(home)).toBe(true);
	expect(reportDir).toMatch(/\/\d{4}-\d{2}-\d{2}-cache-hit-rates$/);
	expect(existsSync(join(reportDir, 'src/lib/report/Report.svelte'))).toBe(true);
	expect(readFileSync(join(reportDir, 'src/lib/report/meta.ts'), 'utf8')).toContain(
		"export const title = 'Why the cache\\'s hit rate fell';",
	);
});

test('commits the starting source and ignores dependencies and build output', () => {
	expect(git(reportDir, 'rev-list', '--count', 'HEAD')).toBe('1');
	expect(git(reportDir, 'status', '--porcelain')).toBe('');
	const tracked = git(reportDir, 'ls-files').split('\n');
	expect(tracked).toContain('src/lib/report/Report.svelte');
	expect(tracked).toContain('bun.lock');
	expect(tracked.filter((file) => /^(node_modules|\.svelte-kit|dist|test-results)\//.test(file))).toEqual([]);
});

test('installs the pre-commit hook', () => {
	expect(existsSync(join(reportDir, '.git/hooks/pre-commit'))).toBe(true);
});

test('never overwrites an existing report', () => {
	const report = join(reportDir, 'src/lib/report/Report.svelte');
	writeFileSync(report, '<p>Edited</p>\n');
	const again = newReport(['cache-hit-rates', 'Another title']);
	expect(again.exitCode).not.toBe(0);
	expect(readFileSync(report, 'utf8')).toBe('<p>Edited</p>\n');
});

test('refuses a report home inside the chezmoi source directory', () => {
	const source = Bun.spawnSync(['chezmoi', 'source-path']).stdout.toString().trim();
	const inside = join(source, 'visual-report-test-reports');
	const refused = newReport(['inside-chezmoi', 'Title'], inside);
	expect(refused.exitCode).not.toBe(0);
	expect(existsSync(inside)).toBe(false);
});

test('rejects a slug that is not lowercase kebab case', () => {
	expect(newReport(['Cache Hit Rates', 'Title']).exitCode).not.toBe(0);
});
