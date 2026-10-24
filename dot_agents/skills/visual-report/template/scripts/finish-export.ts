// Checks the built report against the limits of T3 Code's html_render tool, then
// copies it to `<report dir>/<report dir name>.html`.
import { basename, resolve } from 'node:path';

// The agent sends the whole file inline in one html_render call, and minified code costs about
// one token per two characters. The starter is about 64,000 characters.
const maxCharacters = 100_000;

const html = await Bun.file('dist/index.html').text();
const problems: string[] = [];

if (html.length > maxCharacters) {
	problems.push(
		`The report is ${html.length} characters; the limit is ${maxCharacters}. Remove dependencies, large assets, or repeated markup.`,
	);
}

// html_render rejects viewport-height units: its frame grows to fit the page, so they loop.
const viewportUnits = html.match(/(?<![\w-])\d*\.?\d+[sld]?vh\b/g);
if (viewportUnits) {
	problems.push(
		`Viewport-height units (${[...new Set(viewportUnits)].join(', ')}) break html_render. Let content set the height.`,
	);
}

const remoteReferences = html.match(
	/(?:src|href)=["']?(?:https?:)?\/\/[^"'\s>]+|url\(["']?(?:https?:)?\/\/[^)]+/g,
);
if (remoteReferences) {
	problems.push(
		`The report loads remote resources (${remoteReferences.join(', ')}). Import or inline them so it works offline.`,
	);
}

if (problems.length > 0) {
	console.error(problems.map((problem) => `✗ ${problem}`).join('\n'));
	process.exit(1);
}

const reportPath = resolve(`${basename(process.cwd())}.html`);
await Bun.write(reportPath, html);
console.log(`${reportPath} (${Math.round(html.length / 1000)} kB)`);
