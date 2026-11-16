const puppeteer = require("puppeteer-core");
const path = require("path");

async function run() {
  const browser = await puppeteer.launch({
    executablePath: "/usr/bin/google-chrome",
    args: ["--no-sandbox", "--disable-setuid-sandbox", "--headless=new"],
  });

  const page = await browser.newPage();
  const baseUrl = "http://127.0.0.1:5173";
  const ts = Date.now();
  const email = `p3_browser_${ts}@example.com`;
  const password = "Password123";
  const filePath = path.resolve(__dirname, "../samples/contracts/clean_nda.pdf");

  console.log("=== Phase 3 Frontend E2E Verification ===");

  // 1. Register & Login
  console.log("\n1. Registering user for browser flow...");
  await page.goto(`${baseUrl}/register`, { waitUntil: "networkidle0" });
  await page.type('input[placeholder="Jane Doe"]', `Browser Tester ${ts}`);
  await page.type('input[placeholder="name@example.com"]', email);
  await page.type('input[type="password"]', password);
  await page.click('button[type="submit"]');
  await page.waitForFunction(() => window.location.pathname === "/dashboard", { timeout: 8000 });
  console.log("   Authenticated and on /dashboard");

  // 2. Go to Upload Page
  console.log("\n2. Navigating to /upload...");
  await page.goto(`${baseUrl}/upload`, { waitUntil: "networkidle0" });
  const uploadTitle = await page.$eval("h1", (el) => el.innerText);
  console.log("   Upload Page Heading:", uploadTitle);

  // 3. Upload File
  console.log("   Attaching sample clean_nda.pdf to input...");
  const fileInput = await page.$('input[type="file"]');
  await fileInput.uploadFile(filePath);

  // Verify file info card rendered
  await page.waitForFunction(() => {
    const btns = Array.from(document.querySelectorAll("button"));
    return btns.some((b) => b.innerText.includes("Upload & Process"));
  }, { timeout: 5000 });

  const fileText = await page.evaluate(() => {
    const el = document.querySelector(".font-medium");
    return el ? el.innerText : "";
  });
  console.log("   Selected file recognized in UI:", fileText);

  // Click Upload & Process
  console.log("   Submitting upload...");
  const uploadBtn = await page.evaluateHandle(() => {
    const btns = Array.from(document.querySelectorAll("button"));
    return btns.find((b) => b.innerText.includes("Upload & Process"));
  });
  await uploadBtn.click();

  // Wait for pipeline completion (EXTRACTED)
  console.log("   Waiting for processing stepper to complete...");
  await page.waitForFunction(
    () => document.body.innerText.includes("Document extracted and indexed") ||
          document.body.innerText.includes("View Extracted Text"),
    { timeout: 15000 }
  );
  console.log("   Pipeline completed: Stepper shows Extracted!");

  // 4. Click "View Extracted Text"
  console.log("\n3. Navigating to Document Text Viewer...");
  const viewLink = await page.$('a[href*="/documents/"]');
  await viewLink.click();
  await page.waitForFunction(() => window.location.pathname.startsWith("/documents/"), { timeout: 8000 });
  console.log("   Document Analysis Page URL:", page.url());

  // Wait for Page 1 text to render
  await page.waitForFunction(
    () => document.body.innerText.includes("NON-DISCLOSURE AND CONFIDENTIALITY AGREEMENT"),
    { timeout: 8000 }
  );
  console.log("   Verified Page 1 text rendered in document viewer!");

  // Click Next page
  console.log("   Clicking Next page button...");
  const nextBtn = await page.evaluateHandle(() => {
    const btns = Array.from(document.querySelectorAll("button"));
    return btns.find(b => b.innerText.includes("Next"));
  });
  await nextBtn.click();

  // Wait for Page 2 text to render
  await page.waitForFunction(
    () => document.body.innerText.includes("Delaware") || document.body.innerText.includes("Term and Termination"),
    { timeout: 8000 }
  );
  console.log("   Verified Page 2 text rendered in document viewer!");

  // 5. Navigate to Document History
  console.log("\n4. Navigating to Document History page (/history)...");
  await page.goto(`${baseUrl}/history`, { waitUntil: "networkidle0" });
  await page.waitForFunction(
    () => document.body.innerText.includes("clean_nda.pdf"),
    { timeout: 8000 }
  );
  console.log("   Document found in History table!");

  // Check status badge
  const badgeText = await page.$eval("table tbody tr td:nth-child(5)", (el) => el.innerText);
  console.log("   Status badge in table:", badgeText);

  // 6. Delete Document
  console.log("\n5. Testing Document Deletion from History...");
  page.on("dialog", async (dialog) => {
    console.log("   Confirming dialog:", dialog.message());
    await dialog.accept();
  });

  const deleteBtn = await page.$('table tbody tr td:last-child button[title="Delete document"]');
  await deleteBtn.click();

  // Wait for row to disappear
  await page.waitForFunction(
    () => document.body.innerText.includes("No documents uploaded yet") ||
          document.body.innerText.includes("No matching documents found"),
    { timeout: 8000 }
  );
  console.log("   Document deleted successfully, history table is empty!");

  await browser.close();
  console.log("\n=== ALL PHASE 3 FRONTEND E2E CHECKS PASSED PERFECTLY ===");
}

run().catch((err) => {
  console.error("Phase 3 E2E test failed:", err);
  process.exit(1);
});
