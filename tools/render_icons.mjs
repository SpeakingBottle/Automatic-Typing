import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";
import sharp from "sharp";

const VERSION = "1.72.0";
const BASE = `https://unpkg.com/lucide-static@${VERSION}/icons`;
const OUT = "assets/icons";
const ICONS = [
  "keyboard",
  "clipboard",
  "trash-2",
  "play",
  "pause",
  "square",
  "x",
  "pin",
  "pin-off",
  "sun",
  "moon",
  "chevron-down",
  "chevron-up",
  "languages",
];
const VARIANTS = {
  light: "#475569",
  dark: "#CBD5E1",
  on_accent: "#FFFFFF",
};

async function fetchSvg(name) {
  const response = await fetch(`${BASE}/${name}.svg`);
  if (!response.ok) {
    throw new Error(`Failed to fetch ${name}: ${response.status}`);
  }
  return response.text();
}

for (const variant of Object.keys(VARIANTS)) {
  await mkdir(path.join(OUT, variant), { recursive: true });
}

for (const name of ICONS) {
  const svg = await fetchSvg(name);
  for (const [variant, color] of Object.entries(VARIANTS)) {
    const colored = svg.replaceAll("currentColor", color);
    const output = path.join(OUT, variant, `${name}.png`);
    await sharp(Buffer.from(colored), { density: 384 })
      .resize(40, 40)
      .png()
      .toFile(output);
  }
}

const APP_ICON_SVG = `
<svg width="256" height="256" viewBox="0 0 256 256" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bg" x1="24" y1="16" x2="232" y2="240" gradientUnits="userSpaceOnUse">
      <stop stop-color="#4F46E5"/>
      <stop offset="1" stop-color="#7C3AED"/>
    </linearGradient>
  </defs>
  <rect width="256" height="256" rx="58" fill="url(#bg)"/>
  <rect x="38" y="66" width="180" height="124" rx="30" fill="#FFFFFF"/>
  <g fill="#4F46E5">
    <rect x="64" y="92" width="28" height="22" rx="7"/>
    <rect x="102" y="92" width="28" height="22" rx="7"/>
    <rect x="140" y="92" width="28" height="22" rx="7"/>
    <rect x="178" y="92" width="16" height="22" rx="7"/>
    <rect x="64" y="124" width="28" height="22" rx="7"/>
    <rect x="102" y="124" width="28" height="22" rx="7"/>
    <rect x="140" y="124" width="28" height="22" rx="7"/>
    <rect x="178" y="124" width="16" height="22" rx="7"/>
    <rect x="78" y="156" width="100" height="16" rx="8"/>
  </g>
</svg>`;

const APP_ICON_SIZES = [16, 20, 24, 32, 40, 48, 64, 128, 256];
const appIconPngs = [];
for (const size of APP_ICON_SIZES) {
  appIconPngs.push(
    await sharp(Buffer.from(APP_ICON_SVG), { density: 384 })
      .resize(size, size)
      .png()
      .toBuffer(),
  );
}

await writeFile("assets/app.png", appIconPngs[appIconPngs.length - 1]);

function buildIco(sizes, pngs) {
  const header = Buffer.alloc(6);
  header.writeUInt16LE(0, 0);
  header.writeUInt16LE(1, 2);
  header.writeUInt16LE(sizes.length, 4);

  let offset = 6 + sizes.length * 16;
  const entries = [];
  for (let index = 0; index < sizes.length; index += 1) {
    const size = sizes[index];
    const png = pngs[index];
    const entry = Buffer.alloc(16);
    entry.writeUInt8(size >= 256 ? 0 : size, 0);
    entry.writeUInt8(size >= 256 ? 0 : size, 1);
    entry.writeUInt8(0, 2);
    entry.writeUInt8(0, 3);
    entry.writeUInt16LE(1, 4);
    entry.writeUInt16LE(32, 6);
    entry.writeUInt32LE(png.length, 8);
    entry.writeUInt32LE(offset, 12);
    entries.push(entry);
    offset += png.length;
  }
  return Buffer.concat([header, ...entries, ...pngs]);
}

await writeFile("assets/app.ico", buildIco(APP_ICON_SIZES, appIconPngs));

console.log(`Rendered ${ICONS.length} icons in 3 variants and ${APP_ICON_SIZES.length} app icon sizes.`);
