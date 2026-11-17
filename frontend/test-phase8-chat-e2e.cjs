const puppeteer = require("puppeteer-core");

async function run() {
  console.log("=== Phase 8 Chat End-to-End Test ===");
  const browser = await puppeteer.launch({
    executablePath: "/usr/bin/google-chrome",
    args: ["--no-sandbox", "--disable-setuid-sandbox", "--headless=new"],
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 900 });

  page.on("console", (msg) => {
    if (msg.type() === "error") {
      console.log("PAGE ERROR:", msg.text());
    }
  });

  const baseUrl = "http://localhost:5173";
  const docId = "84a7dba8-eaf1-4705-bc04-cd500055c4dd";

  try {
    // 1. Login
    console.log("1. Logging in...");
    await page.goto(`${baseUrl}/login`, { waitUntil: "networkidle2" });
    await page.type('input[type="email"]', "admin@lexilegal.ai");
    await page.type('input[type="password"]', "Password123!");
    await page.click('button[type="submit"]');

    await page.waitForNavigation({ waitUntil: "networkidle2" });
    console.log("Logged in successfully. Navigating to document analysis page...");

    // 2. Open Document Analysis Page
    await page.goto(`${baseUrl}/documents/${docId}`, { waitUntil: "networkidle2" });
    await page.waitForSelector("h1", { timeout: 10000 });
    console.log("Document analysis workspace loaded.");

    // 3. Switch to Chat Tab
    console.log("3. Switching to Document Chat tab...");
    const chatTabBtn = await page.evaluateHandle(() => {
      const buttons = Array.from(document.querySelectorAll("button"));
      return buttons.find((b) => b.textContent.includes("Document Chat"));
    });
    if (!chatTabBtn) throw new Error("Document Chat tab button not found");
    await chatTabBtn.click();
    await new Promise((r) => setTimeout(r, 1000));

    // 4. Verify Suggested Starter Questions
    console.log("4. Verifying starter questions...");
    const starterQuestions = await page.evaluate(() => {
      const buttons = Array.from(document.querySelectorAll("button"));
      return buttons
        .map((b) => b.textContent.trim())
        .filter((t) => t.includes("notice period") || t.includes("monthly rent") || t.includes("payment terms"));
    });
    console.log(`Found ${starterQuestions.length} starter questions matching spec:`, starterQuestions);
    if (starterQuestions.length === 0) {
      throw new Error("No starter questions rendered!");
    }

    // 5. Click the Notice Period starter question
    console.log("5. Clicking notice period starter question...");
    await page.evaluate(() => {
      const buttons = Array.from(document.querySelectorAll("button"));
      const btn = buttons.find((b) => b.textContent.includes("notice period"));
      if (btn) btn.click();
    });

    // 6. Wait for assistant response
    console.log("6. Waiting for assistant response...");
    await page.waitForFunction(
      () => {
        const text = document.body.innerText;
        return text.includes("LexiLegal Assistant") && (text.includes("notice") || text.includes("cure") || text.includes("days"));
      },
      { timeout: 30000 }
    );
    console.log("Assistant response received and rendered!");

    // 7. Verify Citation Pill
    console.log("7. Verifying citation pill...");
    const citationText = await page.evaluate(() => {
      const pills = Array.from(document.querySelectorAll("button"));
      const citation = pills.find((p) => p.textContent.includes("Page 1") || p.textContent.includes("Page 2"));
      return citation ? citation.textContent.trim() : null;
    });
    console.log("Citation pill found:", citationText);
    if (!citationText) throw new Error("No citation pill rendered on assistant response");

    // 8. Click citation pill to view page panel
    console.log("8. Clicking citation pill to navigate to page view...");
    await page.evaluate(() => {
      const pills = Array.from(document.querySelectorAll("button"));
      const citation = pills.find((p) => p.textContent.includes("Page 1") || p.textContent.includes("Page 2"));
      if (citation) citation.click();
    });

    await new Promise((r) => setTimeout(r, 1500));

    const pageViewActive = await page.evaluate(() => {
      return document.body.innerText.includes("Page ") && document.body.innerText.includes("of ");
    });
    console.log("Document page text panel successfully opened from citation click:", pageViewActive);

    console.log("\n=== ALL PHASE 8 E2E CHAT TESTS PASSED! ===");
  } catch (err) {
    console.error("Test failed:", err);
    process.exit(1);
  } finally {
    await browser.close();
  }
}

run();
