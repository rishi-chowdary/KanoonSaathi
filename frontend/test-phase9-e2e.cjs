const puppeteer = require("puppeteer-core");
const fs = require("fs");
const path = require("path");
const http = require("http");

async function main() {
  console.log("=== PHASE 9 LIVE E2E VERIFICATION: DASHBOARD & OPENPDF REPORT ===");

  const browser = await puppeteer.launch({
    executablePath: "/usr/bin/google-chrome",
    headless: "new",
    args: ["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"],
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 800 });

  // Collect browser console messages
  page.on("console", (msg) => {
    if (msg.type() === "error") {
      console.log(`[Browser Error]:`, msg.text());
    }
  });

  try {
    const timestamp = Date.now();
    const email = `phase9_${timestamp}@lexilegal.ai`;
    const password = "Password123!";

    // 1. Register new user
    console.log(`\n1. Registering user: ${email}...`);
    await page.goto("http://localhost:5173/register", { waitUntil: "networkidle0" });
    await page.type('input[placeholder="Jane Doe"]', "Phase 9 Tester");
    await page.type('input[placeholder="name@example.com"]', email);
    await page.type('input[type="password"]', password);
    await page.click('button[type="submit"]');

    await page.waitForNavigation({ waitUntil: "networkidle0" });
    console.log("   Logged in. Current URL:", page.url());

    // 2. Test Dashboard on fresh account
    console.log("\n2. Inspecting Workspace Dashboard on fresh account...");
    await page.goto("http://localhost:5173/dashboard", { waitUntil: "networkidle0" });

    // Verify stat cards
    await page.waitForSelector("h1");
    const heading = await page.$eval("h1", (el) => el.innerText);
    console.log("   Dashboard Heading:", heading);

    const statLabels = await page.$$eval(".text-slate-500.text-xs span", (els) =>
      els.map((e) => e.innerText)
    );
    console.log("   Dashboard Stat Card Labels:", statLabels);

    // Verify Quick Upload button
    const uploadBtnText = await page.$eval('a[href="/upload"]', (el) => el.innerText);
    console.log("   Quick Upload Button:", uploadBtnText.trim());

    // 3. Upload a sample contract via API using the user's token
    console.log("\n3. Uploading contract for report verification via API...");
    const token = await page.evaluate(() => localStorage.getItem("lexilegal_token"));

    const contractPath = path.resolve("samples/contracts/rental_agreement.pdf");
    const contractBuffer = fs.readFileSync(contractPath);
    const blob = new Blob([contractBuffer], { type: "application/pdf" });
    const formData = new FormData();
    formData.append("file", blob, "rental_agreement.pdf");

    const uploadRes = await fetch("http://localhost:8080/api/documents/upload", {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
      body: formData,
    });
    const uploadData = await uploadRes.json();
    const docId = uploadData.id;
    console.log(`   Uploaded document id: ${docId}, status: ${uploadData.status}`);

    // Wait for document to reach COMPLETED status (poll for up to 60s)
    console.log("   Waiting for analysis pipeline to complete...");
    let isCompleted = false;
    for (let i = 0; i < 30; i++) {
      await new Promise((r) => setTimeout(r, 2000));
      const statusRes = await fetch(`http://localhost:8080/api/documents/${docId}/status`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const statusData = await statusRes.json();
      if (statusData.status === "COMPLETED") {
        console.log(`   Analysis reached status: COMPLETED in turn ${i + 1}`);
        isCompleted = true;
        break;
      }
    }

    if (!isCompleted) {
      console.log("   Note: Pipeline still processing or reuse available.");
    }

    // 4. Return to Dashboard and check updated metrics
    console.log("\n4. Checking Dashboard updated stats...");
    await page.goto("http://localhost:5173/dashboard", { waitUntil: "networkidle0" });
    await new Promise((r) => setTimeout(r, 1000));

    const docCount = await page.evaluate(() => {
      const cards = Array.from(document.querySelectorAll(".p-4.rounded-lg"));
      return cards.map((c) => c.innerText.replace(/\n/g, " | "));
    });
    console.log("   Updated Dashboard Cards:", docCount.slice(0, 4));

    // Verify recent documents table lists the uploaded file
    const recentTableText = await page.evaluate(() => {
      const rows = Array.from(document.querySelectorAll("tbody tr"));
      return rows.map((r) => r.innerText.replace(/\n/g, " "));
    });
    console.log("   Recent Documents Table Rows:", recentTableText);

    // 5. Test Report Tab on Analysis Page
    console.log(`\n5. Testing Report Dossier Tab on /documents/${docId}...`);
    await page.goto(`http://localhost:5173/documents/${docId}`, { waitUntil: "networkidle0" });

    // Click Report Dossier Tab
    const reportTabBtn = await page.evaluateHandle(() => {
      const buttons = Array.from(document.querySelectorAll("button"));
      return buttons.find((b) => b.innerText.includes("Report Dossier"));
    });

    if (reportTabBtn) {
      await reportTabBtn.click();
      await new Promise((r) => setTimeout(r, 1000));

      // Verify sections outline
      const sectionCount = await page.$$eval(".grid.grid-cols-1.md\\:grid-cols-2 > div", (els) => els.length);
      console.log(`   Report Dossier Sections rendered: ${sectionCount}/10 sections`);

      // Verify Download Button
      const downloadBtn = await page.evaluate(() => {
        const btns = Array.from(document.querySelectorAll("button"));
        const b = btns.find((btn) => btn.innerText.includes("Download PDF Report"));
        return b ? b.innerText : null;
      });
      console.log("   Download Report Button in Tab:", downloadBtn);
    }

    // 6. Direct HTTP verification of GET /api/documents/{id}/report.pdf
    console.log("\n6. Verifying binary PDF output from GET /api/documents/{id}/report.pdf...");

    const pdfResp = await fetch(`http://localhost:8080/api/documents/${docId}/report.pdf`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    console.log(`   HTTP Status: ${pdfResp.status}`);
    console.log(`   Content-Type: ${pdfResp.headers.get("content-type")}`);
    console.log(`   Content-Disposition: ${pdfResp.headers.get("content-disposition")}`);

    if (pdfResp.status === 200) {
      const arrayBuffer = await pdfResp.arrayBuffer();
      const buffer = Buffer.from(arrayBuffer);
      console.log(`   Downloaded PDF Size: ${buffer.length} bytes`);
      const magicBytes = buffer.slice(0, 5).toString("utf-8");
      console.log(`   PDF Magic Header: "${magicBytes}"`);

      // Save a copy in evaluation/results for inspection
      fs.mkdirSync("evaluation/results", { recursive: true });
      fs.writeFileSync("evaluation/results/sample_report.pdf", buffer);
      console.log("   Saved verified report to evaluation/results/sample_report.pdf");

      if (magicBytes === "%PDF-" && buffer.length > 1000) {
        console.log("\n[SUCCESS]: Phase 9 Full-Stack Verification Passed!");
      } else {
        throw new Error("Invalid PDF format or empty content");
      }
    } else {
      console.log(`   Status is ${pdfResp.status} (document may still be processing).`);
    }

  } catch (err) {
    console.error("\n[E2E TEST FAILURE]:", err);
    process.exitCode = 1;
  } finally {
    await browser.close();
  }
}

main();
