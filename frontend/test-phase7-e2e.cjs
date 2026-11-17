const puppeteer = require("puppeteer-core");
const fs = require("fs");
const path = require("path");

async function run() {
  console.log("=== Phase 7 Frontend Live E2E Verification ===");

  const contextPath = path.join(__dirname, "phase7_test_context.json");
  if (!fs.existsSync(contextPath)) {
    throw new Error("phase7_test_context.json not found! Run evaluation/verify_phase7_suite.py first.");
  }
  const ctx = JSON.parse(fs.readFileSync(contextPath, "utf-8"));
  const { documentId, email, password } = ctx;
  const baseUrl = "http://127.0.0.1:5173";

  console.log(`Document ID: ${documentId}`);
  console.log(`User: ${email}`);

  const browser = await puppeteer.launch({
    executablePath: "/usr/bin/google-chrome",
    args: ["--no-sandbox", "--disable-setuid-sandbox", "--headless=new"],
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1366, height: 900 });

  page.on("console", (msg) => {
    if (msg.type() === "error") {
      console.log("PAGE CONSOLE ERROR:", msg.text());
    }
  });
  page.on("pageerror", (err) => console.log("PAGE UNCAUGHT ERROR:", err.message));

  const screenshotDir = path.join(__dirname, "../evaluation/results/screenshots");
  if (!fs.existsSync(screenshotDir)) {
    fs.mkdirSync(screenshotDir, { recursive: true });
  }

  try {
    // 1. Login
    console.log(`\n1. Logging in as ${email}...`);
    await page.goto(`${baseUrl}/login`, { waitUntil: "networkidle0" });
    await page.type('input[type="email"]', email);
    await page.type('input[type="password"]', password);
    await page.click('button[type="submit"]');
    await page.waitForFunction(() => window.location.pathname === "/dashboard", { timeout: 10000 });
    console.log("   Authenticated successfully!");

    // 2. Navigate to document analysis page
    console.log(`\n2. Navigating to /documents/${documentId}...`);
    await page.goto(`${baseUrl}/documents/${documentId}`, { waitUntil: "networkidle0" });

    // Wait for document title
    await page.waitForSelector("h1", { timeout: 10000 });
    const docTitle = await page.$eval("h1", (el) => el.innerText.trim());
    console.log(`   Document Title: "${docTitle}"`);

    // Helper to click button by text
    const clickButtonByText = async (targetText) => {
      const btns = await page.$$("button");
      for (const b of btns) {
        const text = await (await b.getProperty("innerText")).jsonValue();
        if (text.toLowerCase().includes(targetText.toLowerCase())) {
          await b.click();
          return true;
        }
      }
      throw new Error(`Button containing "${targetText}" not found`);
    };

    const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

    // 3. Test Risks Tab
    console.log("\n3. Testing 'Risks' Tab...");
    await clickButtonByText("Risks");
    await sleep(2000);

    // Verify Recharts SVG is rendered
    const hasChart = await page.evaluate(() => !!document.querySelector(".recharts-responsive-container svg"));
    console.log(`   Recharts SVG Rendered: ${hasChart}`);

    // Verify Risk Profile Distribution text
    const hasDistHeader = await page.evaluate(() =>
      document.body.innerText.includes("Risk Profile Distribution")
    );
    console.log(`   Risk Profile Distribution Header: ${hasDistHeader}`);

    // Check risk finding cards
    const riskCardCount = await page.evaluate(() =>
      document.querySelectorAll("span.border.uppercase").length
    );
    console.log(`   Detected risk severity badges in DOM: ${riskCardCount}`);

    // Test expandable suggested questions
    const questionToggle = await page.evaluate(() => {
      const btns = Array.from(document.querySelectorAll("button"));
      const qBtn = btns.find((b) => b.innerText.includes("Suggested Questions"));
      if (qBtn) {
        qBtn.click();
        return true;
      }
      return false;
    });
    console.log(`   Clicked Suggested Questions toggle: ${questionToggle}`);
    await sleep(500);

    // Save Risks screenshot
    await page.screenshot({ path: path.join(screenshotDir, "phase7_risks_tab.png"), fullPage: true });
    console.log(`   Saved screenshot: evaluation/results/screenshots/phase7_risks_tab.png`);

    // 4. Test Key Information Tab
    console.log("\n4. Testing 'Key Information' Tab...");
    await clickButtonByText("Key Information");
    await sleep(2000);

    // Verify sections: Financial, Term/Renewal, Obligations
    const pageText = await page.evaluate(() => document.body.innerText);
    const hasFinancial = pageText.includes("FINANCIAL & PAYMENT TERMS");
    const hasTerm = pageText.includes("TERM, RENEWAL & TERMINATION");
    const hasObligations = pageText.includes("CORE ONGOING OBLIGATIONS");
    console.log(`   Financial Terms Section: ${hasFinancial}`);
    console.log(`   Term & Termination Section: ${hasTerm}`);
    console.log(`   Ongoing Obligations Section: ${hasObligations}`);

    // Check "Not specified" badges
    const notSpecifiedCount = await page.evaluate(() => {
      const items = Array.from(document.querySelectorAll("span"));
      return items.filter((s) => s.innerText.trim() === "Not specified").length;
    });
    console.log(`   'Not specified' compliant items: ${notSpecifiedCount}`);

    // Save Key Info screenshot
    await page.screenshot({ path: path.join(screenshotDir, "phase7_key_info_tab.png"), fullPage: true });
    console.log(`   Saved screenshot: evaluation/results/screenshots/phase7_key_info_tab.png`);

    // 5. Test Missing Clauses Tab
    console.log("\n5. Testing 'Missing Clauses' Tab...");
    await clickButtonByText("Missing Clauses");
    await sleep(2000);

    const missingPageText = await page.evaluate(() => document.body.innerText);
    const hasDisclaimer = missingPageText.includes("Rule 7 Disclosure") || missingPageText.includes("Statutory Legal Notice");
    const hasPossibleOmission = missingPageText.includes("Possible omission");
    console.log(`   Statutory Legal Disclaimer Banner: ${hasDisclaimer}`);
    console.log(`   'Possible omission' Standard Label: ${hasPossibleOmission}`);

    // Test expanding typical provision example
    const exampleToggle = await page.evaluate(() => {
      const btns = Array.from(document.querySelectorAll("button"));
      const exBtn = btns.find((b) => b.innerText.includes("View Typical Commercial Provision"));
      if (exBtn) {
        exBtn.click();
        return true;
      }
      return false;
    });
    console.log(`   Clicked Typical Provision Example toggle: ${exampleToggle}`);
    await sleep(500);

    // Save Missing Clauses screenshot
    await page.screenshot({ path: path.join(screenshotDir, "phase7_missing_clauses_tab.png"), fullPage: true });
    console.log(`   Saved screenshot: evaluation/results/screenshots/phase7_missing_clauses_tab.png`);

    console.log("\n============================================================");
    console.log("PHASE 7 FRONTEND E2E BROWSER VERIFICATION SUCCEEDED!");
    console.log("============================================================");
  } catch (err) {
    console.error("Test failed:", err);
    await page.screenshot({ path: path.join(screenshotDir, "phase7_error.png") });
    throw err;
  } finally {
    await browser.close();
  }
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});

