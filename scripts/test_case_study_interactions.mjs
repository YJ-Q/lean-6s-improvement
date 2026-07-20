import path from "node:path";
import { pathToFileURL } from "node:url";
import { chromium } from "playwright-core";

const browser = await chromium.launch({
  headless: true,
  executablePath: "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
});
const page = await browser.newPage();
const errors = [];
page.on("pageerror", (error) => errors.push(error.message));
const target = pathToFileURL(path.resolve("case-study/index.html")).href;

for (const viewport of [
  { width: 1440, height: 1000 },
  { width: 1024, height: 768 },
  { width: 390, height: 844 },
]) {
  await page.setViewportSize(viewport);
  await page.goto(target, { waitUntil: "networkidle" });
  const overflow = await page.evaluate(
    () => document.documentElement.scrollWidth > document.documentElement.clientWidth,
  );
  if (overflow) throw new Error(`horizontal overflow at ${viewport.width}px`);
}

await page.getByRole("tab", { name: "维度变化" }).click();
if (await page.locator("#panel-dimension").getAttribute("hidden")) {
  throw new Error("dimension panel stayed hidden after click");
}
await page.getByRole("tab", { name: "维度变化" }).press("ArrowRight");
if ((await page.getByRole("tab", { name: "可信边界" }).getAttribute("aria-selected")) !== "true") {
  throw new Error("ArrowRight did not activate the next tab");
}

await browser.close();
if (errors.length) throw new Error(errors.join("\n"));
