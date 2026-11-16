const puppeteer = require("puppeteer-core");

async function run() {
  const browser = await puppeteer.launch({
    executablePath: "/usr/bin/google-chrome",
    args: ["--no-sandbox", "--disable-setuid-sandbox", "--headless=new"],
  });

  const page = await browser.newPage();
  const baseUrl = "http://127.0.0.1:5173";
  const uniqueId = Date.now();
  const testEmail = `tester_${uniqueId}@example.com`;
  const testPassword = "Password123";
  const testName = `Test User ${uniqueId}`;
  const updatedName = `Updated User ${uniqueId}`;

  console.log("1. Testing Protected Route redirection...");
  await page.goto(`${baseUrl}/dashboard`, { waitUntil: "networkidle0" });
  await page.waitForFunction(() => window.location.pathname === "/login");
  console.log("   Navigated to /dashboard, redirected to:", page.url());

  console.log("\n2. Navigating to Register Page...");
  await page.goto(`${baseUrl}/register`, { waitUntil: "networkidle0" });
  const regTitle = await page.$eval("h1", (el) => el.innerText);
  console.log("   Register Heading:", regTitle);

  console.log("   Filling registration form...");
  await page.type('input[placeholder="Jane Doe"]', testName);
  await page.type('input[placeholder="name@example.com"]', testEmail);
  await page.type('input[type="password"]', testPassword);
  await page.click('button[type="submit"]');

  // Wait for SPA redirect to /dashboard
  await page.waitForFunction(() => window.location.pathname === "/dashboard", { timeout: 10000 });
  console.log("   Registration complete, current URL:", page.url());

  const dashTitle = await page.$eval("h1", (el) => el.innerText);
  console.log("   Dashboard Heading:", dashTitle);

  console.log("\n3. Verifying user menu in Navbar...");
  const navUserText = await page.evaluate(() => {
    const btn = document.querySelector("header button span");
    return btn ? btn.innerText : "";
  });
  console.log("   Navbar user label:", navUserText);

  console.log("\n4. Navigating to Profile Page...");
  await page.goto(`${baseUrl}/profile`, { waitUntil: "networkidle0" });
  const profileTitle = await page.$eval("h1", (el) => el.innerText);
  console.log("   Profile Heading:", profileTitle);

  console.log("   Updating profile name to:", updatedName);
  await page.evaluate(() => {
    const input = document.querySelector('input[type="text"]');
    input.value = "";
  });
  await page.type('input[type="text"]', updatedName);
  await page.click('button[type="submit"]');

  // Wait for update message
  await page.waitForSelector(".text-emerald-700", { timeout: 5000 });
  const successMsg = await page.$eval(".text-emerald-700", (el) => el.innerText);
  console.log("   Profile update feedback:", successMsg);

  console.log("\n5. Testing Sign Out...");
  const userBtn = await page.$("header .relative button");
  await userBtn.click();
  await page.waitForSelector("header .relative button + div button", { timeout: 2000 });
  const signoutBtn = await page.$("header .relative button + div button");
  await signoutBtn.click();

  await page.waitForFunction(() => window.location.pathname === "/login", { timeout: 5000 });
  console.log("   Current URL after logout:", page.url());

  console.log("\n6. Testing Sign In...");
  await page.type('input[placeholder="name@example.com"]', testEmail);
  await page.type('input[type="password"]', testPassword);
  await page.click('button[type="submit"]');

  await page.waitForFunction(() => window.location.pathname === "/dashboard", { timeout: 5000 });
  console.log("   Current URL after login:", page.url());

  await browser.close();
  console.log("\nALL FRONTEND AUTH & E2E CHECKS PASSED PERFECTLY!");
}

run().catch((err) => {
  console.error("Test failed:", err);
  process.exit(1);
});
