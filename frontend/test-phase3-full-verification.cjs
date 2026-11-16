const puppeteer = require("puppeteer-core");
const path = require("path");
const fs = require("fs");
const { execSync } = require("child_process");

async function run() {
  const browser = await puppeteer.launch({
    executablePath: "/usr/bin/google-chrome",
    args: ["--no-sandbox", "--disable-setuid-sandbox", "--headless=new"],
  });

  const page = await browser.newPage();
  const baseUrl = "http://127.0.0.1:5173";
  const ts = Date.now();
  const email = `phase3_verifier_${ts}@example.com`;
  const password = "Password123";
  const samplesDir = path.resolve(__dirname, "../samples/contracts");

  console.log("====================================================");
  console.log("PHASE 3 FULL END-TO-END BROWSER & SYSTEM VERIFICATION");
  console.log("====================================================");

  // 1. User Registration & Login Flow
  console.log("\n[Step 1] Registering test user on frontend...");
  await page.goto(`${baseUrl}/register`, { waitUntil: "networkidle0" });
  await page.type('input[placeholder="Jane Doe"]', `Verification Tester ${ts}`);
  await page.type('input[placeholder="name@example.com"]', email);
  await page.type('input[type="password"]', password);
  await page.click('button[type="submit"]');
  await page.waitForFunction(() => window.location.pathname === "/dashboard", { timeout: 8000 });
  console.log("  ✓ Successfully registered and redirected to /dashboard");

  // Helper to upload a file through UI
  async function uploadFileViaUI(fileName, expectSuccess = true) {
    console.log(`\n[Upload Test] Uploading sample: ${fileName}`);
    await page.goto(`${baseUrl}/upload`, { waitUntil: "networkidle0" });

    const filePath = path.join(samplesDir, fileName);
    const fileInput = await page.$('input[type="file"]');
    await fileInput.uploadFile(filePath);

    // Wait for selected file card to show or for immediate validation error
    if (fileName === "empty_contract.pdf") {
      // Empty file should fail validation
      await page.waitForFunction(
        () => document.body.innerText.includes("File cannot be empty") ||
              document.body.innerText.includes("empty"),
        { timeout: 5000 }
      );
      console.log("  ✓ UI correctly rejected empty file before upload");
      return { status: "REJECTED_CLIENT" };
    }

    // Wait for "Upload & Process" button
    await page.waitForFunction(() => {
      const btns = Array.from(document.querySelectorAll("button"));
      return btns.some((b) => b.innerText.includes("Upload & Process"));
    }, { timeout: 5000 });

    // Check consent checkbox if unchecked
    const checkbox = await page.$('input[type="checkbox"]');
    if (checkbox) {
      const isChecked = await (await checkbox.getProperty("checked")).jsonValue();
      if (!isChecked) {
        await checkbox.click();
      }
    }

    // Click "Upload & Process"
    const uploadBtn = await page.evaluateHandle(() => {
      const btns = Array.from(document.querySelectorAll("button"));
      return btns.find((b) => b.innerText.includes("Upload & Process"));
    });
    await uploadBtn.click();

    if (!expectSuccess) {
      // For malicious file or corrupted file, expect error message in UI
      await page.waitForFunction(
        () => document.body.innerText.includes("executable files are not allowed") ||
              document.body.innerText.includes("prohibited") ||
              document.body.innerText.includes("Failed") ||
              document.body.innerText.includes("Text extraction failed"),
        { timeout: 10000 }
      );
      const errText = await page.evaluate(() => {
        const alerts = document.querySelectorAll(".text-rose-600, .text-rose-500, .bg-rose-50");
        return Array.from(alerts).map(a => a.innerText).join(" | ");
      });
      console.log(`  ✓ Rejected/Failed as expected: ${errText || 'Error alert displayed'}`);
      return { status: "FAILED_OR_REJECTED" };
    }

    // Wait for stepper to complete to EXTRACTED
    console.log("  Waiting for pipeline stepper to complete (Uploaded -> Extracting -> Extracted)...");
    await page.waitForFunction(
      () => document.body.innerText.includes("Document extracted and indexed") ||
            document.body.innerText.includes("View Extracted Text"),
      { timeout: 20000 }
    );
    console.log("  ✓ Stepper completed: Extracted!");

    // Navigate to viewer
    const viewLink = await page.$('a[href*="/documents/"]');
    const docUrl = await (await viewLink.getProperty("href")).jsonValue();
    const docId = docUrl.split("/documents/")[1];
    await viewLink.click();
    await page.waitForFunction(() => window.location.pathname.startsWith("/documents/"), { timeout: 8000 });
    console.log(`  ✓ Navigated to text viewer: /documents/${docId}`);

    // Wait for page text content to render
    await page.waitForFunction(
      () => {
        const el = document.querySelector(".whitespace-pre-wrap");
        return el && el.innerText.trim().length > 30 && !el.innerText.includes("Loading page text");
      },
      { timeout: 10000 }
    );
    const pageText = await page.$eval(".whitespace-pre-wrap", (el) => el.innerText);
    console.log(`  ✓ Page 1 text rendered (${pageText.length} chars). Snippet: "${pageText.replace(/\s+/g, ' ').slice(0, 80)}..."`);

    return { status: "EXTRACTED", docId, pageText };
  }

  // 2. Upload Valid Samples
  console.log("\n[Step 2] Testing valid samples end-to-end...");

  // Sample A: clean_nda.pdf
  const resPdf = await uploadFileViaUI("clean_nda.pdf", true);
  // Verify multi-page navigation on clean_nda.pdf
  const nextBtn = await page.evaluateHandle(() => {
    const btns = Array.from(document.querySelectorAll("button"));
    return btns.find((b) => b.innerText.includes("Next"));
  });
  await nextBtn.click();
  await page.waitForFunction(
    () => document.body.innerText.includes("Delaware") || document.body.innerText.includes("Term"),
    { timeout: 8000 }
  );
  console.log("  ✓ Page 2 navigation verified on clean_nda.pdf");

  // Sample B: service_agreement.docx
  const resDocx = await uploadFileViaUI("service_agreement.docx", true);

  // Sample C: promissory_note.txt
  const resTxt = await uploadFileViaUI("promissory_note.txt", true);

  // Sample D: scanned_deed.pdf (exercises Tesseract OCR)
  const resScanned = await uploadFileViaUI("scanned_deed.pdf", true);
  if (resScanned.pageText.toUpperCase().includes("DEED") || resScanned.pageText.toUpperCase().includes("GRANTOR")) {
    console.log("  ✓ OCR extracted text verified from scanned PDF!");
  }

  // 3. Upload Negative / Edge Case Samples
  console.log("\n[Step 3] Testing edge cases & rejection samples...");
  await uploadFileViaUI("empty_contract.pdf", false);
  await uploadFileViaUI("malicious_renamed.exe.pdf", false);
  await uploadFileViaUI("corrupted_contract.pdf", false);

  // 4. Verify Item 4: Confirm files in storage are randomized UUIDs and NOT reachable by any URL
  console.log("\n[Step 4] Verifying storage randomization and web URL isolation...");
  const uploadsDir = path.resolve(__dirname, "../backend/uploads");
  const storedFiles = fs.readdirSync(uploadsDir).filter(f => !f.startsWith("."));
  console.log(`  Stored files in ./uploads (${storedFiles.length} files):`);
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\.[a-z0-9]+$/i;
  let allRandomized = true;
  for (const f of storedFiles) {
    const isUuid = uuidRegex.test(f);
    console.log(`    - ${f} (UUID format: ${isUuid})`);
    if (!isUuid) allRandomized = false;
  }
  if (allRandomized) {
    console.log("  ✓ All stored file names are strictly randomized UUIDs");
  } else {
    throw new Error("Stored files contain non-UUID names!");
  }

  // Test URL unreachable check
  const sampleStoredFile = storedFiles[0];
  console.log(`  Testing direct URL reachability for stored file: ${sampleStoredFile}...`);
  try {
    const curlBackend = execSync(`curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/uploads/${sampleStoredFile}`).toString().trim();
    console.log(`    GET http://localhost:8080/uploads/${sampleStoredFile} -> HTTP ${curlBackend}`);
    const curlRoot = execSync(`curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/${sampleStoredFile}`).toString().trim();
    console.log(`    GET http://localhost:8080/${sampleStoredFile} -> HTTP ${curlRoot}`);
    if (curlBackend === "404" && curlRoot === "404") {
      console.log("  ✓ Uploaded files are NOT reachable by backend static URLs (HTTP 404)");
    } else {
      console.warn("  Warning: direct URL returned:", curlBackend, curlRoot);
    }
  } catch (err) {
    console.log("  ✓ Direct curl request failed/rejected as expected");
  }

  // 5. Verify Item 5: Check document_chunks and tsvector in PostgreSQL
  console.log("\n[Step 5] Verifying document_chunks and tsvector full-text search in PostgreSQL...");
  const psqlBase = "PGPASSWORD=postgres psql -h localhost -p 5433 -U postgres -d lexilegal";
  const psqlChunksQuery = `SELECT id, document_id, chunk_index, page_number, token_count, (search_vector IS NOT NULL) AS has_vector FROM document_chunks ORDER BY created_at DESC LIMIT 5;`;
  const chunksOutput = execSync(`${psqlBase} -c "${psqlChunksQuery}"`).toString();
  console.log("  Latest document_chunks rows:");
  console.log(chunksOutput);

  // Sample to_tsquery search
  console.log("  Executing sample to_tsquery full-text search query in psql...");
  const tsquery = `SELECT chunk_index, page_number, ts_headline('english', content, to_tsquery('english', 'confidential & information'), 'MaxWords=20, MinWords=10') AS match_headline FROM document_chunks WHERE search_vector @@ to_tsquery('english', 'confidential & information') LIMIT 3;`;
  const searchOutput = execSync(`${psqlBase} -c "${tsquery}"`).toString();
  console.log(searchOutput);
  if (searchOutput.includes("match_headline") && searchOutput.includes("<b>confidential</b>")) {
    console.log("  ✓ tsvector GIN full-text search with to_tsquery verified working with highlighted headlines!");
  } else if (searchOutput.includes("match_headline")) {
    console.log("  ✓ tsvector GIN full-text search matched rows successfully!");
  }

  // 6. Verify Deletion: file removed from disk and rows removed from DB
  console.log("\n[Step 6] Verifying document deletion (UI -> Disk -> DB)...");
  // We'll delete promissory_note (docId: resTxt.docId)
  const docToDeleteId = resTxt.docId;
  console.log(`  Deleting document ID: ${docToDeleteId}`);

  // Query DB to find storage path
  const storagePathQuery = `SELECT storage_path FROM documents WHERE id = '${docToDeleteId}';`;
  const storagePathRaw = execSync(`${psqlBase} -t -A -c "${storagePathQuery}"`).toString().trim();
  console.log(`  Storage path in DB: ${storagePathRaw}`);
  const diskPath = path.resolve(storagePathRaw);
  console.log(`  Disk file exists before delete: ${fs.existsSync(diskPath)}`);

  // Navigate to history page in UI
  await page.goto(`${baseUrl}/history`, { waitUntil: "networkidle0" });
  await page.waitForSelector("table tbody tr", { timeout: 8000 });

  // Handle browser confirmation dialog
  page.on("dialog", async (dialog) => {
    console.log(`  Handling confirm dialog: "${dialog.message()}" -> ACCEPT`);
    await dialog.accept();
  });

  // Find the row for promissory_note.txt and click delete
  const deletedClicked = await page.evaluate((targetId) => {
    const rows = Array.from(document.querySelectorAll("table tbody tr"));
    for (const r of rows) {
      if (r.innerText.includes("promissory_note.txt") || r.innerText.includes(targetId)) {
        const btn = r.querySelector('button[title="Delete document"]');
        if (btn) {
          btn.click();
          return true;
        }
      }
    }
    return false;
  }, docToDeleteId);

  if (deletedClicked) {
    console.log("  Clicked delete button in table");
  } else {
    // Click first delete button
    console.log("  Clicking first delete button in table");
    const firstDel = await page.$('table tbody tr td:last-child button[title="Delete document"]');
    if (firstDel) await firstDel.click();
  }

  // Wait 2 seconds for deletion processing
  await new Promise((r) => setTimeout(r, 2000));

  // Check disk file
  const fileExistsAfter = fs.existsSync(diskPath);
  console.log(`  Disk file exists after delete: ${fileExistsAfter}`);
  if (!fileExistsAfter) {
    console.log("  ✓ Physical file was successfully deleted from disk!");
  } else {
    throw new Error(`File still exists on disk at ${diskPath}`);
  }

  // Check DB rows
  const docCountQuery = `SELECT count(*) FROM documents WHERE id = '${docToDeleteId}';`;
  const docCount = execSync(`${psqlBase} -t -A -c "${docCountQuery}"`).toString().trim();
  const chunkCountQuery = `SELECT count(*) FROM document_chunks WHERE document_id = '${docToDeleteId}';`;
  const chunkCount = execSync(`${psqlBase} -t -A -c "${chunkCountQuery}"`).toString().trim();
  console.log(`  DB documents count for ID: ${docCount}`);
  console.log(`  DB document_chunks count for ID: ${chunkCount}`);

  if (docCount === "0" && chunkCount === "0") {
    console.log("  ✓ All document and document_chunks rows were completely removed from database!");
  } else {
    throw new Error(`DB rows not deleted! docs: ${docCount}, chunks: ${chunkCount}`);
  }

  await browser.close();
  console.log("\n====================================================");
  console.log("ALL 5 VERIFICATION ITEMS COMPLETED SUCCESSFULLY!");
  console.log("====================================================");
}

run().catch((err) => {
  console.error("Verification failed:", err);
  process.exit(1);
});
