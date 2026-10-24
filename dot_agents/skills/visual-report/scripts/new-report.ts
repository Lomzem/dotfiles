// Creates a report project: bun new-report.ts <kebab-slug> "<Title>"
// Prints the report directory on the last line of output.
import { $ } from 'bun';
import { cpSync, existsSync, mkdirSync, writeFileSync } from 'node:fs';
import { homedir } from 'node:os';
import { basename, join, relative, resolve } from 'node:path';

const fail = (message: string): never => {
	console.error(message);
	process.exit(1);
};

const [slug, title] = process.argv.slice(2);
if (!slug || !title) fail('Usage: bun new-report.ts <kebab-slug> "<Title>"');
if (!/^[a-z0-9]+(-[a-z0-9]+)*$/.test(slug)) fail(`The slug must be lowercase kebab case: ${slug}`);

const template = resolve(import.meta.dir, '../template');
const home = resolve(
	process.env.VISUAL_REPORT_HOME ?? join(homedir(), '.local/share/visual-report/reports'),
);
const isInside = (dir: string, parent: string) => !relative(parent, dir).startsWith('..');

// Reports change on every edit; dotfile sources must stay clean.
const chezmoiSource = (await $`chezmoi source-path`.nothrow().quiet().text()).trim();
if (chezmoiSource && isInside(home, chezmoiSource)) {
	fail(`Reports must live outside the chezmoi source directory: ${home}`);
}
if (isInside(home, resolve(import.meta.dir, '..'))) {
	fail(`Reports must live outside the skill directory: ${home}`);
}

const date = new Date().toLocaleDateString('sv-SE'); // YYYY-MM-DD, local time
const dir = join(home, `${date}-${slug}`);
if (existsSync(dir)) fail(`A report already exists at ${dir}. Edit it instead.`);

const ignored = new Set(['node_modules', '.svelte-kit', 'dist', 'test-results', 'playwright-report', '.git']);
mkdirSync(home, { recursive: true });
cpSync(template, dir, {
	recursive: true,
	filter: (source) => {
		const name = basename(source);
		const atRoot = resolve(source, '..') === template;
		return !ignored.has(name) && !(atRoot && name.endsWith('.html'));
	},
});

writeFileSync(
	join(dir, 'src/lib/report/meta.ts'),
	`/** The report title: the page \`<h1>\` and the document \`<title>\`. */\nexport const title = ${JSON.stringify(title)};\n`,
);

await $`git init --quiet`.cwd(dir);
await $`bun install --frozen-lockfile`.cwd(dir).quiet();
await $`bunx prettier --write src/lib/report/meta.ts`.cwd(dir).quiet();
await $`git add --all`.cwd(dir);
await $`git commit --quiet --message ${`Start report: ${title}`}`.cwd(dir).env({ ...process.env, LEFTHOOK: '0' });

console.log(dir);
