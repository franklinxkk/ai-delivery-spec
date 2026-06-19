const fs = require("fs");
const path = require("path");
const { spawnSync } = require("child_process");
const { chromium } = require("playwright");
const ffmpegPath = require("ffmpeg-static");

const root = path.resolve(__dirname);
const htmlPath = path.join(root, "vertical-promo.html");
const framesDir = path.join(root, "frames");
const outputDir = path.join(root, "dist");
const outputPath = path.join(outputDir, "ai-delivery-spec-promo-vertical.mp4");

const width = 1080;
const height = 1920;
const durationSeconds = 45;
const fps = Number(process.env.PROMO_FPS || 12);
const totalFrames = durationSeconds * fps;

async function main() {
  fs.rmSync(framesDir, { recursive: true, force: true });
  fs.mkdirSync(framesDir, { recursive: true });
  fs.mkdirSync(outputDir, { recursive: true });

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: 1 });
  await page.goto(`file://${htmlPath.replace(/\\/g, "/")}`);
  await page.evaluate(() => document.fonts && document.fonts.ready);

  for (let i = 0; i < totalFrames; i += 1) {
    const t = i / fps;
    await page.evaluate((time) => window.renderAt(time), t);
    const framePath = path.join(framesDir, `frame_${String(i).padStart(5, "0")}.png`);
    await page.screenshot({ path: framePath, type: "png" });
    if (i % fps === 0) {
      process.stdout.write(`rendered ${Math.round(t)}s / ${durationSeconds}s\r`);
    }
  }

  await browser.close();

  const args = [
    "-y",
    "-framerate", String(fps),
    "-i", path.join(framesDir, "frame_%05d.png"),
    "-c:v", "libx264",
    "-pix_fmt", "yuv420p",
    "-r", "30",
    "-movflags", "+faststart",
    outputPath
  ];

  const result = spawnSync(ffmpegPath, args, { stdio: "inherit" });
  if (result.status !== 0) {
    throw new Error(`ffmpeg failed with status ${result.status}`);
  }

  console.log(`\nVideo written to ${outputPath}`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
