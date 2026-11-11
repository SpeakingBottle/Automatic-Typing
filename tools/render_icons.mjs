import { mkdir } from "node:fs/promises";
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

const keyboardSvg = (await fetchSvg("keyboard")).replaceAll("currentColor", "#FFFFFF");
const keyboardPng = await sharp(Buffer.from(keyboardSvg), { density: 384 })
  .resize(128, 128)
  .png()
  .toBuffer();

const background = Buffer.from(`
  <svg width="256" height="256" xmlns="http://www.w3.org/2000/svg">
    <rect width="256" height="256" rx="56" fill="#4F46E5"/>
  </svg>
`);

await sharp(background)
  .composite([{ input: keyboardPng, gravity: "center" }])
  .png()
  .toFile("assets/app.png");

console.log(`Rendered ${ICONS.length} icons in 3 variants.`);
