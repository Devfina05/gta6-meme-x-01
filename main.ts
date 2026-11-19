// gta6-meme-x-01 entrypoint (Node 22, standard library only).
//
// The entry is the X post itself: this program's only job is to hand the
// post's address to the gate. It reads POST.json from the repository and
// writes it byte-for-byte to /output/POST.json, where the gate reads it.
// Nothing this program writes is judged; the house reads the post from X
// (its first picture and its text) and hands that to the judge.
//
// Output-dir rule: /output is a mount point inside the grading container,
// so this program NEVER removes the output directory itself. It only
// creates it (mkdirSync, recursive) and writes POST.json inside it.
// Removing a mount point throws "Device or resource busy" and fails.
//
// Outside the grader, MAKEFUN_BOT_DIR and MAKEFUN_OUTPUT_DIR stand in
// for /bot and /output:
//   mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts

import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

const BOT_DIR = process.env.MAKEFUN_BOT_DIR ?? '/bot';
const OUTPUT_DIR = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';

const SOURCE = join(BOT_DIR, 'POST.json');
const TARGET = join(OUTPUT_DIR, 'POST.json');

if (!existsSync(SOURCE)) {
  console.error(`main.ts: ${SOURCE} is missing; the repo must hold POST.json`);
  process.exit(1);
}

// Parse first so a malformed POST.json fails here with a clear error
// instead of handing the gate a file it cannot read.
let parsed: unknown;
let raw: Buffer;
try {
  raw = readFileSync(SOURCE);
  parsed = JSON.parse(raw.toString('utf-8'));
} catch (err) {
  console.error(`main.ts: POST.json could not be parsed: ${(err as Error).message}`);
  process.exit(1);
}
if (typeof parsed !== 'object' || parsed === null || Array.isArray(parsed)) {
  console.error('main.ts: POST.json must be a JSON object like {"url": "..."}');
  process.exit(1);
}
if (typeof (parsed as Record<string, unknown>).url !== 'string') {
  console.error('main.ts: POST.json must hold a string "url" field');
  process.exit(1);
}
const postUrl = (parsed as Record<string, unknown>).url as string;
// Warn (do not fail) when the url is not an X post address yet: the
// placeholder stays in place until the user posts the meme, and a pasted
// address with a typo should be caught at a glance in the run log.
if (!/^https:\/\/(www\.|mobile\.)?(x\.com|twitter\.com)\//.test(postUrl)) {
  console.error(
    `main.ts: warning: url does not look like an X post address: ${postUrl}`,
  );
}

// Create the output directory; never delete it (see the header note).
mkdirSync(OUTPUT_DIR, { recursive: true });

// Copy the file byte-for-byte so what the gate reads is exactly what
// the repository holds.
writeFileSync(TARGET, raw);

console.log(`wrote ${TARGET} (${raw.length} bytes)`);
console.log(`post url: ${(parsed as Record<string, unknown>).url}`);
