// News image entry: "The World in One Day — 27 November 2026".
// Node 22, standard library only. Reads the committed entry.png, checks it is
// really a whole 1024x1024 PNG under 1 MiB, and writes the exact same bytes to
// the output directory, then re-reads the output and verifies the bytes match,
// so both runs of the program write the same bytes.
// To redraw the image from scratch: python3 tools/render.py (Pillow, no
// network, deterministic).
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { createHash } from "node:crypto";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const source = join(here, "entry.png");
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const target = join(outDir, "entry.png");

const PNG_MAGIC = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);

function sha256(buf: Buffer): string {
  return createHash("sha256").update(buf).digest("hex");
}

function checkPng(buf: Buffer): void {
  if (buf.length < 33) throw new Error(`PNG too short: ${buf.length} bytes`);
  if (!buf.subarray(0, 8).equals(PNG_MAGIC)) throw new Error("not a PNG file");
  const width = buf.readUInt32BE(16);
  const height = buf.readUInt32BE(20);
  if (width !== 1024 || height !== 1024) {
    throw new Error(`expected a 1024x1024 image, got ${width}x${height}`);
  }
  if (buf.length > 1024 * 1024) {
    throw new Error(`image over the 1 MiB limit: ${buf.length} bytes`);
  }
}

const input = await readFile(source);
checkPng(input);
await mkdir(outDir, { recursive: true });
await writeFile(target, input);
const output = await readFile(target);
if (!output.equals(input)) throw new Error("output bytes differ from entry.png");
checkPng(output);
console.log(
  `wrote ${target} (${output.length} bytes, sha256 ${sha256(output)})`
);
