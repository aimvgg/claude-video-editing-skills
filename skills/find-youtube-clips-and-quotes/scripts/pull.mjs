#!/usr/bin/env node
// Cuts one span out of any URL yt-dlp reads (YouTube, TikTok, Instagram, X), then tells you where the speech starts
// and stops so the cut can land between words, and draws a contact sheet so you can see who is on screen.
//   node pull.mjs <url> --probe
//   node pull.mjs "ytsearch10:<query>" --probe
//   node pull.mjs <url> [--from 8578 --to 8590 | --whole] [--pad 0.5] [--out clips] [--name dylan-huawei]
//     [--used audio|video|audio+video] [--speaker "Dylan Patel"] [--found '{"call":"search","input":{...}}']
// --probe prints each video's id, length, rough download size and title, and downloads nothing.
// --from and --to are source seconds and come as a pair. Without them the whole video downloads, and a video over
// 10 minutes needs --whole, so a long download is always a choice.
// --found records how the clip was found (the Arcmira call and its input, the upload it was found in, or a note), so the
// recipe can say so. Without it the clip is logged as found manually. --used says what the edit takes from the clip
// (default audio+video).
// Run it from the project folder. It writes <out>/<name>/clip.mp4, info.json and sheet.jpg under the current folder,
// prints a JSON summary, and appends a row to <out>/clips.json. It refuses to write inside the skill's own folder.
// Needs ffmpeg and either uv (preferred; runs the yt-dlp release pinned by YTDLP_VERSION) or yt-dlp on PATH.
import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const argv = process.argv.slice(2);
const BOOL = new Set(['--probe', '--whole']);
const url = argv.find((a, i) => !a.startsWith('--') && (i === 0 || !argv[i - 1].startsWith('--') || BOOL.has(argv[i - 1])));
const flag = (k, d) => (argv.includes(`--${k}`) ? argv[argv.indexOf(`--${k}`) + 1] : d);
const fail = (msg, code = 2) => { console.error(msg); process.exit(code); };
if (!url) fail('usage: node pull.mjs <url> [--probe] [--from s --to s | --whole] [--pad s] [--out dir] [--name slug]');
const probeOnly = argv.includes('--probe');
const whole = argv.includes('--whole');
const from = flag('from') === undefined ? null : Number(flag('from'));
const to = flag('to') === undefined ? null : Number(flag('to'));
if ((from === null) !== (to === null)) fail('pass both --from and --to, or neither');
if (from !== null && !(Number.isFinite(from) && Number.isFinite(to) && to > from)) fail('--from and --to are source seconds, with --to after --from');
const pad = Number(flag('pad', 0.5));
const name = flag('name', `clip-${Date.now()}`).replace(/[^a-z0-9-]/gi, '-');
const outRoot = path.resolve(process.cwd(), flag('out', 'clips'));
const used = flag('used', 'audio+video');
const speaker = flag('speaker') ?? null;
if (!['audio', 'video', 'audio+video'].includes(used)) fail('--used is audio, video or audio+video');
let found = { via: 'manual' };
if (flag('found') !== undefined) {
  try { found = JSON.parse(flag('found')); } catch { fail('--found must be JSON'); }
  found.via ??= found.call ? 'arcmira' : found.in ? 'url' : 'manual';
}

// The clip log belongs to the user's project. A plugin update replaces the skill folder, so never write into it.
const skillDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
if (!probeOnly && (outRoot === skillDir || outRoot.startsWith(skillDir + path.sep))) {
  fail(`pull.mjs: run it from the project folder; ${path.relative(process.cwd(), outRoot) || '.'} is inside the skill`);
}

const has = (bin) => spawnSync('which', [bin]).status === 0;
const run = (cmd, args) => {
  const r = spawnSync(cmd, args, { encoding: 'utf8', maxBuffer: 1 << 26 });
  if (r.error) throw new Error(`${cmd} failed: ${r.error.message}`);
  if (r.status !== 0) throw new Error(`${cmd} failed:\n${(r.stderr || '').split('\n').filter((l) => !/https?:\/\//.test(l)).slice(-8).join('\n')}`);
  return r.stdout + r.stderr;
};
// yt-dlp runs at a pinned stable release, never an unpinned latest. YouTube changes break old releases, so when
// downloads fail, set YTDLP_VERSION to a newer stable release that is at least a day old (see SKILL.md).
// --exclude-newer freezes yt-dlp's own dependencies to the days around that release, so a dependency published
// later never runs. TikTok refuses plain requests from many networks; curl-cffi lets yt-dlp present as Chrome.
const YTDLP_VERSION = process.env.YTDLP_VERSION || '2026.8.19';
const release = YTDLP_VERSION.match(/^(\d{4})\.(\d{1,2})\.(\d{1,2})/);
const EXCLUDE_NEWER = process.env.YTDLP_EXCLUDE_NEWER
  || (release ? new Date(Date.UTC(+release[1], +release[2] - 1, +release[3] + 3)).toISOString().slice(0, 10) : null);
const impersonate = /youtu\.?be|^ytsearch/.test(url) ? [] : ['--impersonate', 'chrome'];
let ytdlp;
if (has('uvx')) {
  ytdlp = ['uvx', [...(EXCLUDE_NEWER ? ['--exclude-newer', EXCLUDE_NEWER] : []),
    '--from', `yt-dlp[default,curl-cffi]==${YTDLP_VERSION}`, 'yt-dlp', ...impersonate]];
} else if (has('yt-dlp')) {
  console.error('pull.mjs: uv is not installed, so this runs the yt-dlp on PATH, which is not pinned. Install uv to pin it.');
  ytdlp = ['yt-dlp', []];
} else {
  fail('pull.mjs: needs uv (preferred) or yt-dlp. On a Mac: brew install uv');
}
const FORMAT = ['-f', 'bv*+ba/b', '-S', 'res:1080,vcodec:h264,acodec:m4a'];

// One JSON line per video: id, length, rough size of the format a download would pick, title, page URL.
const probe = (target) => run(ytdlp[0], [
  ...ytdlp[1], '--no-warnings', '--flat-playlist', ...FORMAT,
  '--print', '%(.{id,duration,filesize_approx,title,webpage_url,url})j', target,
]).split('\n').filter((l) => l.startsWith('{')).map((l) => {
  const v = JSON.parse(l);
  return { id: v.id, duration_s: v.duration ?? null, size_mb: v.filesize_approx ? Math.round(v.filesize_approx / 1e6) : null,
    title: v.title ?? null, url: v.webpage_url ?? v.url ?? null };
});

if (probeOnly) {
  for (const v of probe(url)) console.log(JSON.stringify(v));
  process.exit(0);
}

const span = from !== null ? [Math.max(0, from - pad), to + pad] : null;
if (!span && !whole) {
  const [v] = probe(url);
  if (!v || v.duration_s === null || v.duration_s > 600) {
    const size = v?.size_mb ? `, about ${v.size_mb} MB` : '';
    fail(`pull.mjs: ${v?.duration_s ? `${Math.round(v.duration_s / 60)} minutes${size}` : 'unknown length'}. `
      + 'Pass --from and --to for a span, or --whole once the user agrees to the whole download.', 3);
  }
}

const dir = path.join(outRoot, name);
fs.mkdirSync(dir, { recursive: true });
run(ytdlp[0], [
  ...ytdlp[1], '--no-warnings', '--no-playlist', ...FORMAT,
  '--merge-output-format', 'mp4', '--write-info-json',
  ...(span ? ['--download-sections', `*${span[0]}-${span[1]}`, '--force-keyframes-at-cuts'] : []),
  '-o', path.join(dir, 'clip.%(ext)s'), url,
]);
fs.renameSync(path.join(dir, 'clip.info.json'), path.join(dir, 'info.json'));
const file = path.join(dir, 'clip.mp4');

const meta = JSON.parse(run('ffprobe', ['-v', 'error', '-show_entries', 'format=duration:stream=codec_type,width,height,r_frame_rate', '-of', 'json', file]));
const video = meta.streams.find((s) => s.codec_type === 'video');
const duration = Number(meta.format.duration);

// Speech gaps: silences of 80 ms or more under -30 dB. Transcript times are not cut points (caption lines start
// mid-phrase and can be 0.4 s off), so cut inside one of these gaps.
const gaps = [...run('ffmpeg', ['-hide_banner', '-i', file, '-af', 'silencedetect=noise=-30dB:d=0.08', '-f', 'null', '-'])
  .matchAll(/silence_start: ([\d.]+)[\s\S]*?silence_end: ([\d.]+)/g)]
  .map(([, a, b]) => [+(+a).toFixed(2), +(+b).toFixed(2)]);

const tiles = Math.min(12, Math.max(4, Math.round(duration)));
run('ffmpeg', ['-hide_banner', '-v', 'error', '-y', '-i', file, '-vf', `fps=${tiles}/${duration},scale=480:-2,tile=4x${Math.ceil(tiles / 4)}`, '-frames:v', '1', path.join(dir, 'sheet.jpg')]);

// Paths in the log are relative to the project folder, so the log can be published as it is.
const rel = (p) => path.relative(process.cwd(), p);
const info = JSON.parse(fs.readFileSync(path.join(dir, 'info.json'), 'utf8'));
const row = {
  name, url: info.webpage_url ?? url, title: info.title, uploader: info.uploader ?? info.channel ?? null,
  cut: from !== null ? [from, to] : null, source_seconds: span, file: rel(file),
  width: video?.width, height: video?.height, fps: video?.r_frame_rate, duration: +duration.toFixed(2),
  speech_gaps: gaps, used, speaker, found, pulled: new Date().toISOString(),
};
const ledger = path.join(outRoot, 'clips.json');
const rows = fs.existsSync(ledger) ? JSON.parse(fs.readFileSync(ledger, 'utf8')).filter((r) => r.name !== name) : [];
fs.writeFileSync(ledger, `${JSON.stringify([...rows, row], null, 2)}\n`);
console.log(JSON.stringify({ ...row, sheet: rel(path.join(dir, 'sheet.jpg')) }, null, 2));
