const puppeteer = require("puppeteer-core");

async function run() {
  const browser = await puppeteer.launch({
    executablePath: "/usr/bin/google-chrome",
    args: ["--no-sandbox", "--disable-setuid-sandbox", "--headless=new"],
  });

  const page = await browser.newPage();
  const baseUrl = "http://127.0.0.1:5173";

  console.log("1. Testing Landing Page and Theme Toggle...");
  await page.goto(baseUrl, { waitUntil: "networkidle0" });

  const title = await page.title();
  console.log("   Page Title:", title);

  const heading = await page.$eval("h1", (el) => el.innerText);
  console.log("   Landing Heading:", heading.trim());

  // Check initial theme
  const initialClass = await page.evaluate(() => document.documentElement.className);
  console.log("   Initial html class:", initialClass || "(none)");

  // Click toggle
  console.log("2. Clicking Theme Toggle button...");
  const toggleBtn = await page.$('button[aria-label="Toggle theme"]');
  if (!toggleBtn) throw new Error("Theme toggle button not found");
  await toggleBtn.click();

  const newClass = await page.evaluate(() => document.documentElement.className);
  const savedTheme = await page.evaluate(() => localStorage.getItem("lexilegal_theme"));
  console.log("   New html class:", newClass);
  console.log("   Saved in localStorage:", savedTheme);

  // Reload page to verify persistence
  console.log("3. Reloading page to test persistence...");
  await page.reload({ waitUntil: "networkidle0" });
  const reloadedClass = await page.evaluate(() => document.documentElement.className);
  const reloadedTheme = await page.evaluate(() => localStorage.getItem("lexilegal_theme"));
  console.log("   Persisted html class after reload:", reloadedClass);
  console.log("   Persisted in localStorage:", reloadedTheme);

  // Verify routes: auth pages and protected redirects
  console.log("4. Verifying routes...");
  const publicRoutes = [
    { path: "/", expected: "Clear, grounded explanations" },
    { path: "/login", expected: "Sign In" },
    { path: "/register", expected: "Create Account" },
  ];

  for (const r of publicRoutes) {
    await page.goto(`${baseUrl}${r.path}`, { waitUntil: "networkidle0" });
    const h1 = await page.$eval("h1", (el) => el.innerText);
    const matches = h1.includes(r.expected);
    console.log(`   Public Route ${r.path} -> "${h1.trim()}" (Matches: ${matches})`);
    if (!matches) {
      throw new Error(`Expected "${r.expected}" on ${r.path}, but got "${h1}"`);
    }
  }

  const protectedRoutes = ["/dashboard", "/upload", "/history", "/profile"];
  for (const p of protectedRoutes) {
    await page.goto(`${baseUrl}${p}`, { waitUntil: "networkidle0" });
    await page.waitForFunction(() => window.location.pathname === "/login");
    console.log(`   Protected Route ${p} correctly redirected to /login`);
  }

  await browser.close();
  console.log("\nALL FRONTEND CHECKS PASSED SUCCESSFULLY!");
}

run().catch((err) => {
  console.error("Test failed:", err);
  process.exit(1);
});

