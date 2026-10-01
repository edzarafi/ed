// Render web/index.html frame-by-frame with headless Chromium and encode with ffmpeg.
//   node render.mjs                -> out/jev-explainer.mp4
//   node render.mjs --stills 3 12  -> build/stills/t003.00.png ... (quick visual checks)
import { chromium } from "playwright-core";
import { spawn } from "node:child_process";
import { mkdirSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";

const ROOT = path.dirname(fileURLToPath(import.meta.url));
const FPS = 30, W = 1920, H = 1080;
const exe = process.env.CHROMIUM || ["/opt/pw-browsers/chromium-1194/chrome-linux/chrome"].find(existsSync);

const browser = await chromium.launch({ executablePath: exe, args: ["--allow-file-access-from-files", "--font-render-hinting=none"] });
const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
page.on("pageerror", e => console.error("page error:", e.message));
await page.goto("file://" + path.join(ROOT, "web/index.html"));
await page.evaluate(() => window.READY);
const total = await page.evaluate(() => window.TOTAL);

const args = process.argv.slice(2);
if (args[0] === "--stills") {
  const dir = path.join(ROOT, "build/stills");
  mkdirSync(dir, { recursive: true });
  for (const t of args.slice(1).map(Number)) {
    await page.evaluate(t => window.seek(t), t);
    await page.screenshot({ path: path.join(dir, `t${t.toFixed(2).padStart(6, "0")}.png`) });
  }
  await browser.close();
  process.exit(0);
}

mkdirSync(path.join(ROOT, "out"), { recursive: true });
const out = path.join(ROOT, "out/jev-explainer.mp4");
const ff = spawn("ffmpeg", [
  "-y", "-v", "error",
  "-f", "image2pipe", "-framerate", String(FPS), "-c:v", "mjpeg", "-i", "-",
  "-i", path.join(ROOT, "build/mix.wav"),
  "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
  "-c:a", "aac", "-b:a", "192k", "-shortest", out,
], { stdio: ["pipe", "inherit", "inherit"] });

const frames = Math.ceil(total * FPS);
const t0 = Date.now();
for (let f = 0; f < frames; f++) {
  await page.evaluate(t => window.seek(t), f / FPS);
  const buf = await page.screenshot({ type: "jpeg", quality: 95 });
  if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once("drain", r));
  if (f % 300 === 0) console.log(`frame ${f}/${frames}  ${((Date.now() - t0) / 1000).toFixed(0)}s`);
}
ff.stdin.end();
await new Promise((res, rej) => ff.on("close", c => (c === 0 ? res() : rej(new Error("ffmpeg exit " + c)))));
await browser.close();
console.log("wrote", out);
