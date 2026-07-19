import path from "node:path";
import { pathToFileURL } from "node:url";
import { chromium } from "playwright-core";

const browser = await chromium.launch({
  headless: true,
  executablePath: "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
});
const context = await browser.newContext({ offline: true });
const page = await context.newPage();
const errors = [];
page.on("pageerror", (error) => errors.push(error.message));
page.on("requestfailed", (request) => {
  if (!request.url().startsWith("file:")) errors.push(`failed request: ${request.url()}`);
});

await page.setViewportSize({ width: 390, height: 844 });
await page.goto(
  pathToFileURL(path.resolve("case-study/offline/index.html")).href,
  { waitUntil: "networkidle" },
);

const overflow = await page.evaluate(
  () => document.documentElement.scrollWidth > document.documentElement.clientWidth,
);
if (overflow) errors.push("offline page has horizontal overflow at 390px");
if ((await page.locator("main section").count()) !== 9) {
  errors.push("offline page does not contain all nine narrative sections");
}
if ((await page.locator('a[href="exports/lean-6s-case-study.pdf"]').count()) !== 1) {
  errors.push("offline PDF link is missing");
}
await page.getByRole("tab", { name: "维度变化" }).click();
if (await page.locator("#panel-dimension").getAttribute("hidden")) {
  errors.push("offline evaluation tabs are not interactive");
}

await browser.close();
if (errors.length) throw new Error(errors.join("\n"));
console.log("Offline case study passed clean-browser mobile checks.");
