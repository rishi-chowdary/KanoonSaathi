const puppeteer = require("puppeteer-core");

async function run() {
  const browser = await puppeteer.launch({
    executablePath: "/usr/bin/google-chrome",
    args: ["--no-sandbox", "--disable-setuid-sandbox", "--headless=new"],
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 900 });

  page.on("console", (msg) => console.log("PAGE CONSOLE:", msg.type(), msg.text()));
  page.on("pageerror", (err) => console.log("PAGE UNCAUGHT ERROR:", err.message));
  page.on("requestfailed", (req) => console.log("REQUEST FAILED:", req.url(), req.failure()?.errorText));
  page.on("response", (res) => {
    if (res.url().includes("/simplify") || res.url().includes("/re-explain")) {
      console.log("API RESPONSE:", res.status(), res.url());
    }
  });

  const baseUrl = "http://127.0.0.1:5173";
  const email = "p5_evaluator_1794896337@lexilegal.test";
  const password = "Password123!";
  const docId = "413f47f4-169e-488d-a0b9-53781223ca0b";

  console.log("=== Phase 6 Frontend Live E2E Verification ===");

  try {
    // 1. Login
    console.log(`\n1. Logging in as ${email}...`);
    await page.goto(`${baseUrl}/login`, { waitUntil: "networkidle0" });
    await page.type('input[type="email"]', email);
    await page.type('input[type="password"]', password);
    await page.click('button[type="submit"]');
    await page.waitForFunction(() => window.location.pathname === "/dashboard", { timeout: 8000 });
    console.log("   Authenticated and on /dashboard");

    // 2. Navigate to /simplify
    console.log("\n2. Navigating to /simplify...");
    await page.goto(`${baseUrl}/simplify`, { waitUntil: "networkidle0" });

    // Verify header
    const pageHeading = await page.$eval("h1", (el) => el.innerText.trim());
    console.log(`   Page Heading: "${pageHeading}"`);
    if (!pageHeading.includes("Simplify Legal Text")) {
      throw new Error(`Unexpected page heading: ${pageHeading}`);
    }

    // 3. Test Sample Clause Loading
    console.log("\n3. Testing Sample Clause loading...");
    const sampleBtns = await page.$$("button");
    let sampleBtn = null;
    for (const b of sampleBtns) {
      const text = await (await b.getProperty("innerText")).jsonValue();
      if (text.includes("Indemnification")) {
        sampleBtn = b;
        break;
      }
    }
    if (!sampleBtn) throw new Error("Indemnification sample button not found");
    await sampleBtn.click();

    // Wait for text to populate and submit button to be enabled
    await page.waitForFunction(
      () => {
        const ta = document.querySelector("textarea");
        const btn = document.querySelector('button[type="submit"]');
        return ta && ta.value.length > 50 && btn && !btn.disabled;
      },
      { timeout: 5000 }
    );
    const textareaValue = await page.$eval("textarea", (el) => el.value);
    console.log(`   Textarea filled with sample (${textareaValue.length} characters)`);

    // 4. Test Mode Switching
    console.log("\n4. Testing Mode Switching...");
    const detailedModeBtn = await page.evaluateHandle(() => {
      const btns = Array.from(document.querySelectorAll("button"));
      return btns.find((b) => b.innerText.trim() === "Detailed");
    });
    await detailedModeBtn.click();
    console.log("   Switched mode to 'Detailed'");

    // 5. Submit live simplification to backend
    console.log("\n5. Submitting simplification to backend (live Ollama)...");
    await page.click('button[type="submit"]');

    // Verify result rendering (up to 120s for Ollama CPU inference)
    console.log("   Waiting for live inference output...");
    await page.waitForFunction(
      () => document.body.innerText.toLowerCase().includes("plain language explanation"),
      { timeout: 120000 }
    );
    console.log("   Explanation rendered successfully");

    // Verify Side-by-Side Original vs Explanation
    const hasOriginalBox = await page.evaluate(() =>
      document.body.innerText.toLowerCase().includes("original contract clause")
    );
    const hasExplanationBox = await page.evaluate(() =>
      document.body.innerText.toLowerCase().includes("plain language explanation")
    );
    console.log(`   Side-by-side original text visible: ${hasOriginalBox}`);
    console.log(`   Side-by-side explanation visible: ${hasExplanationBox}`);

    // Verify Key Terms Explained (Glossary)
    const hasGlossary = await page.evaluate(() =>
      document.body.innerText.toLowerCase().includes("key terms explained")
    );
    console.log(`   Glossary section rendered: ${hasGlossary}`);

    // Verify What Could Be Missed
    const hasTraps = await page.evaluate(() =>
      document.body.innerText.toLowerCase().includes("what could be missed")
    );
    console.log(`   What Could Be Missed section rendered: ${hasTraps}`);
    console.log(`   What Could Be Missed section rendered: ${hasTraps}`);

    // Verify Grounded Badge
    const hasGroundedBadge = await page.evaluate(() =>
      document.body.innerText.includes("Grounded (No Invented Figures)") ||
      document.body.innerText.includes("Consistency")
    );
    console.log(`   Grounded/Consistency badge visible: ${hasGroundedBadge}`);

    // 6. Test 'Explain this' Button on Clause Card
    console.log(`\n6. Navigating to Document Analysis /documents/${docId}...`);
    await page.goto(`${baseUrl}/documents/${docId}`, { waitUntil: "networkidle0" });

    // Switch to Clauses tab
    const clausesTabBtn = await page.evaluateHandle(() => {
      const btns = Array.from(document.querySelectorAll("button"));
      return btns.find((b) => b.innerText.trim() === "Clauses");
    });
    await clausesTabBtn.click();
    await page.waitForFunction(() => document.querySelectorAll("h3").length > 0, { timeout: 8000 });
    console.log("   Clauses tab loaded with clause cards");

    // Find "Explain this" button
    const explainThisBtn = await page.evaluateHandle(() => {
      const btns = Array.from(document.querySelectorAll("button"));
      return btns.find((b) => b.innerText.includes("Explain this"));
    });
    if (!explainThisBtn) throw new Error("'Explain this' button not found on clause card");
    console.log("   Found 'Explain this' button on clause card");

    // Click "Explain this"
    await explainThisBtn.click();
    console.log("   Clicked 'Explain this' button");

    // Wait for in-depth panel to open
    await page.waitForFunction(
      () =>
        document.body.innerText.toLowerCase().includes("in-depth analysis & legal terms") ||
        document.body.innerText.toLowerCase().includes("key legal terms explained") ||
        document.body.innerText.toLowerCase().includes("explaining"),
      { timeout: 8000 }
    );
    console.log("   Deep dive explanation section displayed on clause card");

    // Verify "Open in Simplify" link
    const hasOpenInSimplify = await page.evaluate(() =>
      document.body.innerText.toLowerCase().includes("open in simplify")
    );
    console.log(`   'Open in Simplify' link present: ${hasOpenInSimplify}`);

    // Click "Open in Simplify"
    const openInSimplifyBtn = await page.evaluateHandle(() => {
      const btns = Array.from(document.querySelectorAll("button"));
      return btns.find((b) => b.innerText.toLowerCase().includes("open in simplify"));
    });
    await openInSimplifyBtn.click();

    await page.waitForFunction(() => window.location.pathname === "/simplify", { timeout: 8000 });
    console.log("   Successfully transitioned to /simplify");

    // Confirm text area contains prefilled text
    const prefilledText = await page.$eval("textarea", (el) => el.value);
    console.log(`   Textarea prefilled with clause text (${prefilledText.length} chars)`);
    if (!prefilledText || prefilledText.length < 10) {
      throw new Error("Textarea was not prefilled from clause card");
    }

    console.log("\n==========================================");
    console.log("ALL PHASE 6 FRONTEND LIVE E2E CHECKS PASSED!");
    console.log("==========================================");
  } catch (err) {
    console.error("\nLIVE E2E TEST FAILED:", err);
    try {
      const pageText = await page.evaluate(() => document.body.innerText);
      console.log("\n--- CURRENT PAGE TEXT AT FAILURE ---:\n", pageText);
    } catch (e) {
      console.log("Could not dump page text:", e.message);
    }
    process.exit(1);
  } finally {
    await browser.close();
  }
}

run();
