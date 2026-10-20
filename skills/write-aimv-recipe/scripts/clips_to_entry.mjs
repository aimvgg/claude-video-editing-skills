#!/usr/bin/env node
// Prints the entry's clips: block from the clips.json files that find-youtube-clips-and-quotes/scripts/pull.mjs writes.
//   node clips_to_entry.mjs clips/clips.json [more/clips.json ...] >> entry-clips.yml
// Each row keeps its source URL and span, what the edit used (audio, video or audio+video), the speaker, and how the
// clip was found. The span is the cut the edit asked for (`cut`), not the padded download (`source_seconds`), so a
// reader who follows at_s lands on the first word. The block is JSON inside YAML, so every value is quoted and a comma
// can never cut one short.
import fs from 'node:fs';

const args = process.argv.slice(2);
if (!args.length || args.includes('-h') || args.includes('--help')) {
  (args.length ? console.log : console.error)('usage: node clips_to_entry.mjs <clips.json> [more clips.json ...]\nPrints the entry clips: block to stdout.');
  process.exit(args.length ? 0 : 2);
}

const round = (x) => Math.round(x * 100) / 100;
const clips = args.flatMap((f) => JSON.parse(fs.readFileSync(f, 'utf8'))).map((r) => {
  const [a, b] = r.cut ?? r.source_seconds ?? [];
  const found = r.found && (r.found.via !== 'manual' || r.found.note) ? r.found : undefined;
  return Object.fromEntries(Object.entries({
    from: r.url,
    at_s: a !== undefined ? round(a) : undefined,
    len_s: a !== undefined && b !== undefined ? round(b - a) : r.duration,
    used: r.used ?? 'audio+video',
    speaker: r.speaker ?? undefined,
    what: r.title ?? undefined,
    found,
  }).filter(([, v]) => v !== undefined && v !== null));
});
const bad = clips.filter((c) => JSON.stringify(c.found?.input ?? {}).match(/@[\w-]+\.\w|\/Users\/|\/home\/|\/private\/|\/tmp\/|\/var\/folders\/|~\/|[A-Z]:\\\\/));
if (bad.length) {
  console.error(`clips_to_entry: ${bad.length} found.input value(s) hold an email or a local path; remove them first`);
  process.exit(1);
}
if (clips.some((c) => c.found?.call)) console.error('clips_to_entry: Arcmira found some clips, so list arcmira in made_with.tools');
console.log(`clips: ${JSON.stringify(clips, null, 2).replace(/\n/g, '\n  ')}`);
