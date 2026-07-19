import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { chromium } from "playwright-core";

fs.mkdirSync("case-study/assets/screenshots", { recursive: true });
const browser = await chromium.launch({
  headless: true,
  executablePath: "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
});
const page = await browser.newPage({
  viewport: { width: 1440, height: 1000 },
  deviceScaleFactor: 1,
});
const errors = [];
page.on("pageerror", (error) => errors.push(error.message));
const target = pathToFileURL(path.resolve("case-study/index.html")).href;
await page.goto(target, { waitUntil: "networkidle" });
await page.screenshot({
  path: "case-study/assets/screenshots/sample-desktop.png",
  fullPage: true,
});
await page.setViewportSize({ width: 390, height: 844 });
await page.reload({ waitUntil: "networkidle" });
await page.screenshot({
  path: "case-study/assets/screenshots/sample-mobile.png",
  fullPage: true,
});
await browser.close();
if (errors.length) throw new Error(errors.join("\n"));
