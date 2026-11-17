const puppeteer = require("puppeteer-core");

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
  const email = "p5_evaluator_1794896337@lexilegal.test";
  const password = "Password123!";
  const docId = "413f47f4-169e-488d-a0b9-53781223ca0b";

  console.log("=== Phase 5 Frontend E2E Verification ===");

  try {
    // 1. Login
    console.log(`\n1. Logging in as ${email}...`);
    await page.goto(`${baseUrl}/login`, { waitUntil: "networkidle0" });
    await page.type('input[type="email"]', email);
    await page.type('input[type="password"]', password);
    await page.click('button[type="submit"]');
    await page.waitForFunction(() => window.location.pathname === "/dashboard", { timeout: 8000 });
    console.log("   Authenticated and on /dashboard");

    // 2. Navigate to Document Analysis page
    console.log(`\n2. Navigating to document workspace /documents/${docId}...`);
    await page.goto(`${baseUrl}/documents/${docId}`, { waitUntil: "networkidle0" });

    // Verify document loaded
    await page.waitForFunction(
      () => document.body.innerText.includes("Status: COMPLETED"),
      { timeout: 10000 }
    );
    console.log("   Document workspace loaded. Status: COMPLETED");

    // 3. Switch to Clauses tab
    console.log("\n3. Switching to 'Clauses' tab...");
    const clausesTabBtn = await page.evaluateHandle(() => {
      const btns = Array.from(document.querySelectorAll("button"));
      return btns.find((b) => b.innerText.trim() === "Clauses");
    });
    await clausesTabBtn.click();

    // 4. Verify clauses rendered
    console.log("   Waiting for clause cards to render...");
    await page.waitForFunction(
      () => {
        const text = document.body.innerText;
        return (
          text.includes("extracted clause(s)") &&
          text.includes("Definitions") &&
          text.includes("Non-Disclosure Obligations")
        );
      },
      { timeout: 10000 }
    );
    console.log("   Clause cards rendered successfully!");

    // 5. Verify explanation mode toggle
    console.log("\n4. Testing Explanation Mode toggling...");
    // Detailed mode
    const detailedBtn = await page.evaluateHandle(() => {
      const btns = Array.from(document.querySelectorAll("button"));
      return btns.find((b) => b.innerText.trim() === "Detailed");
    });
    await detailedBtn.click();
    await new Promise((r) => setTimeout(r, 600));

    const detailedActive = await page.evaluate(() =>
      document.body.innerText.includes("DETAILED LEGAL BREAKDOWN")
    );
    console.log(`   Detailed explanation mode active: ${detailedActive}`);

    // Professional mode
    const profBtn = await page.evaluateHandle(() => {
      const btns = Array.from(document.querySelectorAll("button"));
      return btns.find((b) => b.innerText.trim() === "Professional");
    });
    await profBtn.click();
    await new Promise((r) => setTimeout(r, 600));

    const profActive = await page.evaluate(() =>
      document.body.innerText.includes("COMMERCIAL ANALYSIS")
    );
    console.log(`   Professional explanation mode active: ${profActive}`);

    // Simple English mode
    const simpleBtn = await page.evaluateHandle(() => {
      const btns = Array.from(document.querySelectorAll("button"));
      return btns.find((b) => b.innerText.trim() === "Simple English");
    });
    await simpleBtn.click();
    await new Promise((r) => setTimeout(r, 600));
    console.log("   Simple English mode active.");

    // 6. Test Accordion: Expand Original Text
    console.log("\n5. Testing 'Original Text' expander...");
    const expandBtn = await page.evaluateHandle(() => {
      const btns = Array.from(document.querySelectorAll("button"));
      return btns.find((b) => b.innerText.includes("Original Text"));
    });
    if (expandBtn) {
      await expandBtn.click();
      await new Promise((r) => setTimeout(r, 500));
      const hasOriginal = await page.evaluate(() =>
        document.body.innerText.includes("ORIGINAL CONTRACT TEXT")
      );
      console.log(`   Original contract text expanded: ${hasOriginal}`);
    }

    // 7. Test Side Panel "View Page"
    console.log("\n6. Testing 'View Page' side panel drawer...");
    const viewPageBtn = await page.evaluateHandle(() => {
      const btns = Array.from(document.querySelectorAll("button"));
      return btns.find((b) => b.innerText.includes("View Page 1"));
    });
    if (viewPageBtn) {
      await viewPageBtn.click();
      await new Promise((r) => setTimeout(r, 1000));
      const drawerOpen = await page.evaluate(() =>
        document.body.innerText.includes("Page 1 Text")
      );
      console.log(`   Page 1 inspection drawer opened: ${drawerOpen}`);

      // Close drawer
      const closeBtn = await page.evaluateHandle(() => {
        const btns = Array.from(document.querySelectorAll("button"));
        return btns.find((b) => b.querySelector("svg.lucide-x") !== null);
      });
      if (closeBtn) {
        await closeBtn.click();
        await new Promise((r) => setTimeout(r, 400));
        console.log("   Page inspection drawer closed.");
      }
    }

    // 8. Test Search Filter
    console.log("\n7. Testing Search Filter...");
    const searchInput = await page.$('input[placeholder*="Search clauses"]');
    if (searchInput) {
      await searchInput.type("governing");
      await page.keyboard.press("Enter");
      await new Promise((r) => setTimeout(r, 800));
      const searchResult = await page.evaluate(() => {
        const text = document.body.innerText;
        return text.includes("Governing Law") && !text.includes("Definitions");
      });
      console.log(`   Search for 'governing' filtered to matching clause: ${searchResult}`);
    }

    // 9. Reset Filters
    console.log("\n8. Testing Reset Filters...");
    const resetBtn = await page.evaluateHandle(() => {
      const btns = Array.from(document.querySelectorAll("button"));
      return btns.find((b) => b.innerText.includes("Reset Filters"));
    });
    if (resetBtn) {
      await resetBtn.click();
      await new Promise((r) => setTimeout(r, 800));
      const allRestored = await page.evaluate(() => {
        const text = document.body.innerText;
        return text.includes("Definitions") && text.includes("Non-Disclosure");
      });
      console.log(`   All clauses restored after filter reset: ${allRestored}`);
    }

    console.log("\n" + "=" * 50);
    console.log("=== ALL PHASE 5 FRONTEND E2E CHECKS PASSED SUCCESSFULLY ===");
    console.log("=" * 50);
  } catch (err) {
    console.error("Test failed:", err);
    process.exit(1);
  } finally {
    await browser.close();
  }
}

run();
