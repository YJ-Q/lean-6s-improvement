import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { chromium } from "playwright-core";

const publicOutput = path.resolve("case-study/exports/lean-6s-case-study.pdf");
const artifactOutput = path.resolve("output/pdf/lean-6s-case-study.pdf");
fs.mkdirSync(path.dirname(publicOutput), { recursive: true });
fs.mkdirSync(path.dirname(artifactOutput), { recursive: true });

const browser = await chromium.launch({
  headless: true,
  executablePath: "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
});
const page = await browser.newPage();
const errors = [];
page.on("pageerror", (error) => errors.push(error.message));
await page.goto(pathToFileURL(path.resolve("case-study/print.html")).href, {
  waitUntil: "networkidle",
});
await page.emulateMedia({ media: "print" });
const overflow = await page.$$eval('[data-page-check="true"]', (pages) =>
  pages.flatMap((item, index) => {
    const pageErrors = [];
    if (item.scrollHeight > item.clientHeight + 1) pageErrors.push(`page-${index + 1} vertical overflow`);
    if (item.scrollWidth > item.clientWidth + 1) pageErrors.push(`page-${index + 1} horizontal overflow`);
    return pageErrors;
  }),
);
if (overflow.length || errors.length) {
  await browser.close();
  throw new Error([...overflow, ...errors].join("\n"));
}
await page.pdf({
  path: publicOutput,
  printBackground: true,
  preferCSSPageSize: true,
  margin: { top: 0, right: 0, bottom: 0, left: 0 },
});
await browser.close();
fs.copyFileSync(publicOutput, artifactOutput);
console.log(publicOutput);
console.log(artifactOutput);
