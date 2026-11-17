const puppeteer = require("puppeteer-core");
const path = require("path");

async function run() {
  const browser = await puppeteer.launch({
    executablePath: "/usr/bin/google-chrome",
    args: ["--no-sandbox", "--disable-setuid-sandbox", "--headless=new"],
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 900 });

  page.on("console", (msg) => console.log("PAGE LOG:", msg.type(), msg.text()));
  page.on("pageerror", (err) => console.log("PAGE ERROR:", err.message));
  const baseUrl = "http://127.0.0.1:5173";
  const ts = Date.now();
  const email = `p4_browser_${ts}@example.com`;
  const password = "Password123";
  const filePath = path.resolve(__dirname, "../samples/contracts/clean_nda.pdf");

  console.log("=== Phase 4 Frontend E2E Verification ===");

  try {
    // 1. Register & Login
    console.log("\n1. Registering user for browser flow...");
    await page.goto(`${baseUrl}/register`, { waitUntil: "networkidle0" });
    await page.type('input[placeholder="Jane Doe"]', `Phase4 Tester ${ts}`);
    await page.type('input[placeholder="name@example.com"]', email);
    await page.type('input[type="password"]', password);
    await page.click('button[type="submit"]');
    await page.waitForFunction(() => window.location.pathname === "/dashboard", { timeout: 8000 });
    console.log("   Authenticated and on /dashboard");

    // 2. Upload Document
    console.log("\n2. Navigating to /upload and attaching clean_nda.pdf...");
    await page.goto(`${baseUrl}/upload`, { waitUntil: "networkidle0" });
    const fileInput = await page.$('input[type="file"]');
    await fileInput.uploadFile(filePath);

    // Verify file card is visible with Upload & Process button
    await page.waitForFunction(() => {
      const btns = Array.from(document.querySelectorAll("button"));
      return btns.some((b) => b.innerText.includes("Upload & Process"));
    }, { timeout: 5000 });

    console.log("   Submitting upload...");
    const uploadBtn = await page.evaluateHandle(() => {
      const btns = Array.from(document.querySelectorAll("button"));
      return btns.find((b) => b.innerText.includes("Upload & Process"));
    });
    await uploadBtn.click();

    // 3. Wait for extraction completion link on upload page
    console.log("   Waiting for processing stepper to complete on upload page...");
    await page.waitForFunction(
      () =>
        document.body.innerText.includes("Document extracted and indexed") ||
        document.body.innerText.includes("Document already exists") ||
        document.querySelector('a[href*="/documents/"]') !== null,
      { timeout: 30000 }
    );
    console.log("   Processing completed on upload page!");

    // 4. Click Document Link to open Workspace
    console.log("\n3. Navigating to Document Analysis workspace...");
    const viewLink = await page.$('a[href*="/documents/"]');
    await viewLink.click();
    await page.waitForFunction(() => window.location.pathname.startsWith("/documents/"), {
      timeout: 8000,
    });
    console.log("   Navigated to Document workspace:", page.url());

    // 5. Switch to Summary Tab
    console.log("\n4. Switching to Summary tab...");
    await page.waitForFunction(() => {
      const btns = Array.from(document.querySelectorAll("button"));
      return btns.some((b) => b.innerText.includes("Summary"));
    }, { timeout: 8000 });

    const summaryBtn = await page.evaluateHandle(() => {
      const btns = Array.from(document.querySelectorAll("button"));
      return btns.find((b) => b.innerText.includes("Summary"));
    });
    await summaryBtn.click();

    // 6. Wait for summary synthesis to finalize
    console.log("\n5. Waiting for analysis synthesis and grounding to complete in UI...");
    await page.waitForFunction(
      () => {
        const text = document.body.innerText.toLowerCase();
        return (
          text.includes("contract summary") &&
          (text.includes("executive") || text.includes("comprehensive"))
        );
      },
      { timeout: 120000 }
    );
    console.log("   Summary Tab loaded with synthesized contract analysis!");

    // 7. Verify Executive vs Comprehensive Toggle
    console.log("\n6. Testing Executive vs Comprehensive summary toggle...");
    const compBtn = await page.evaluateHandle(() => {
      const btns = Array.from(document.querySelectorAll("button"));
      return btns.find((b) => b.innerText.includes("Comprehensive"));
    });
    await compBtn.click();
    await new Promise((r) => setTimeout(r, 600));

    let summaryText = await page.evaluate(() => {
      const fontLegal = document.querySelector(".font-legal");
      return fontLegal ? fontLegal.innerText : "";
    });
    console.log("   Comprehensive Summary length:", summaryText.length);

    const execBtn = await page.evaluateHandle(() => {
      const btns = Array.from(document.querySelectorAll("button"));
      return btns.find((b) => b.innerText.includes("Executive"));
    });
    await execBtn.click();
    await new Promise((r) => setTimeout(r, 600));

    summaryText = await page.evaluate(() => {
      const fontLegal = document.querySelector(".font-legal");
      return fontLegal ? fontLegal.innerText : "";
    });
    console.log("   Executive Summary length:", summaryText.length);

    // 8. Verify Grounding Pill, Provenance Badges, and Metadata
    console.log("\n7. Verifying Grounding score pill and provenance badges...");
    const pageText = await page.evaluate(() => document.body.innerText);

    const hasGrounded = pageText.includes("Grounded");
    console.log("   Grounding pill present:", hasGrounded);

    const hasParties = pageText.includes("Identified Parties");
    console.log("   Identified Parties section present:", hasParties);

    const hasConditions = pageText.includes("Main Conditions");
    console.log("   Main Conditions section present:", hasConditions);

    if (!hasGrounded || !hasParties || !hasConditions) {
      throw new Error("One or more required Phase 4 summary elements were missing in the rendered page.");
    }

    console.log("\n=== Phase 4 Frontend E2E Verification PASSED ===");
  } finally {
    await browser.close();
  }
}

run().catch((err) => {
  console.error("Test failed:", err);
  process.exit(1);
});
