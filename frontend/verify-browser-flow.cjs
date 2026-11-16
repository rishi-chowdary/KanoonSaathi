const puppeteer = require("puppeteer-core");

async function run() {
  const browser = await puppeteer.launch({
    executablePath: "/usr/bin/google-chrome",
    args: ["--no-sandbox", "--disable-setuid-sandbox", "--headless=new"],
  });

  const page = await browser.newPage();
  const baseUrl = "http://127.0.0.1:5173";
  const ts = Date.now();
  const email = `flow_${ts}@example.com`;
  const password = "Password123";
  const initialName = `Flow User ${ts}`;
  const editedName = `Flow User Edited ${ts}`;

  console.log("=== Step 4: Browser Flow Verification ===");

  // 1. Register
  console.log("\n1. Flow: Registering new account on /register...");
  await page.goto(`${baseUrl}/register`, { waitUntil: "networkidle0" });
  await page.type('input[placeholder="Jane Doe"]', initialName);
  await page.type('input[placeholder="name@example.com"]', email);
  await page.type('input[type="password"]', password);
  await page.click('button[type="submit"]');

  await page.waitForFunction(() => window.location.pathname === "/dashboard", { timeout: 8000 });
  console.log("   Registration success, redirected to:", page.url());

  // 2. Logout first so we can test explicit Login
  console.log("\n2. Flow: Logging out to test explicit login...");
  const userBtn = await page.$("header .relative button");
  await userBtn.click();
  await page.waitForSelector("header .relative button + div button", { timeout: 2000 });
  const signoutBtn = await page.$("header .relative button + div button");
  await signoutBtn.click();
  await page.waitForFunction(() => window.location.pathname === "/login", { timeout: 5000 });
  console.log("   Logged out, redirected to:", page.url());

  // 3. Login
  console.log("\n3. Flow: Logging in with registered credentials on /login...");
  await page.type('input[placeholder="name@example.com"]', email);
  await page.type('input[type="password"]', password);
  await page.click('button[type="submit"]');
  await page.waitForFunction(() => window.location.pathname === "/dashboard", { timeout: 8000 });
  console.log("   Login success, redirected to:", page.url());

  // 4. Profile Edit
  console.log("\n4. Flow: Editing profile on /profile...");
  await page.goto(`${baseUrl}/profile`, { waitUntil: "networkidle0" });
  await page.evaluate(() => {
    const input = document.querySelector('input[type="text"]');
    input.value = "";
  });
  await page.type('input[type="text"]', editedName);
  await page.click('button[type="submit"]');
  await page.waitForSelector(".text-emerald-700", { timeout: 5000 });
  const successAlert = await page.$eval(".text-emerald-700", (el) => el.innerText);
  console.log("   Profile update alert:", successAlert);

  // Verify updated name in navbar
  const navbarName = await page.$eval("header button span", (el) => el.innerText);
  console.log("   Navbar shows updated name:", navbarName);
  if (!navbarName.includes(editedName)) {
    throw new Error(`Expected navbar to show "${editedName}", but got "${navbarName}"`);
  }

  // 5. Logout
  console.log("\n5. Flow: Logging out...");
  const userBtnAfterEdit = await page.$("header .relative button");
  await userBtnAfterEdit.click();
  await page.waitForSelector("header .relative button + div button", { timeout: 2000 });
  const signoutBtnAfterEdit = await page.$("header .relative button + div button");
  await signoutBtnAfterEdit.click();
  await page.waitForFunction(() => window.location.pathname === "/login", { timeout: 5000 });
  console.log("   Logged out, currently on:", page.url());

  // 6. Visiting /dashboard redirects to /login
  console.log("\n6. Flow: Visiting /dashboard directly while logged out...");
  await page.goto(`${baseUrl}/dashboard`, { waitUntil: "networkidle0" });
  await page.waitForFunction(() => window.location.pathname === "/login", { timeout: 5000 });
  console.log("   Redirected to:", page.url());
  if (!page.url().includes("/login")) {
    throw new Error(`Expected redirect to /login, but URL is ${page.url()}`);
  }

  await browser.close();
  console.log("\n=== Step 4: BROWSER FLOW VERIFICATION SUCCEEDED ===");
}

run().catch((err) => {
  console.error("Browser flow failed:", err);
  process.exit(1);
});
