import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { chromium } from "playwright-core";

fs.mkdirSync("case-study/assets/screenshots", { recursive: true });
const browser = await chromium.launch({
  headless: true,
  executablePath: "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
});
const page = await browser.newPage({ deviceScaleFactor: 1 });
const errors = [];
page.on("pageerror", (error) => errors.push(error.message));
const target = pathToFileURL(path.resolve("case-study/index.html")).href;
const captures = [
  [1440, 1000, "sample-desktop.png"],
  [1024, 768, "sample-tablet.png"],
  [390, 844, "sample-mobile.png"],
];
for (const [width, height, filename] of captures) {
  await page.setViewportSize({ width, height });
  await page.goto(target, { waitUntil: "networkidle" });
  await page.screenshot({
    path: `case-study/assets/screenshots/${filename}`,
    fullPage: true,
  });
}
await browser.close();
if (errors.length) throw new Error(errors.join("\n"));
