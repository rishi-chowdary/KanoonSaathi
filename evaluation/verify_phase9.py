import os
import sys
import json
import uuid
import requests
import psycopg2
import fitz  # PyMuPDF
from urllib.parse import urlparse

BASE_URL = os.environ.get("BACKEND_URL", "http://localhost:8080/api")

def get_db_connection():
    env = {}
    with open(".env") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip("\"")

    jdbc_url = env["SPRING_DATASOURCE_URL"].replace("jdbc:postgresql://", "postgresql://")
    parsed = urlparse(jdbc_url)
    user = env["SPRING_DATASOURCE_USERNAME"]
    password = env["SPRING_DATASOURCE_PASSWORD"]
    host = parsed.hostname
    port = parsed.port or 5432
    dbname = parsed.path.lstrip("/")

    return psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port,
        sslmode="require"
    )

def query_user_sql_counts(user_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT count(*) FROM documents WHERE user_id = %s;", (user_id,))
    total_docs = cur.fetchone()[0]

    cur.execute("SELECT count(*) FROM documents WHERE user_id = %s AND status = 'COMPLETED';", (user_id,))
    completed_docs = cur.fetchone()[0]

    cur.execute("""
        SELECT count(*) FROM extracted_clauses ec
        JOIN document_analyses da ON ec.analysis_id = da.id
        JOIN documents d ON da.document_id = d.id
        WHERE d.user_id = %s;
    """, (user_id,))
    total_clauses = cur.fetchone()[0]

    cur.execute("""
        SELECT count(*) FROM risk_findings rf
        JOIN document_analyses da ON rf.analysis_id = da.id
        JOIN documents d ON da.document_id = d.id
        WHERE d.user_id = %s;
    """, (user_id,))
    total_risks = cur.fetchone()[0]

    cur.execute("""
        SELECT rf.level, count(*) FROM risk_findings rf
        JOIN document_analyses da ON rf.analysis_id = da.id
        JOIN documents d ON da.document_id = d.id
        WHERE d.user_id = %s
        GROUP BY rf.level;
    """, (user_id,))
    risk_levels = {row[0].upper(): row[1] for row in cur.fetchall()}

    conn.close()
    return {
        "total_docs": total_docs,
        "completed_docs": completed_docs,
        "total_clauses": total_clauses,
        "total_risks": total_risks,
        "risk_levels": risk_levels
    }

def main():
    print("==================================================================")
    print("PHASE 9 VERIFICATION: DASHBOARD AGGREGATES, OPENPDF DOSSIER & AUTH")
    print("==================================================================")

    # -------------------------------------------------------------
    # 1. Seed two users with different data
    # -------------------------------------------------------------
    sys.path.append("database/sample-data")
    from seed_phase9 import seed_sample_data
    seed_data = seed_sample_data()

    user_a = seed_data["userA"]
    user_b = seed_data["userB"]

    print("\n--- TEST 1: CONFIRM DASHBOARD NUMBERS MATCH MANUAL SQL QUERIES (NO LEAKS) ---")
    sql_a = query_user_sql_counts(user_a["id"])
    sql_b = query_user_sql_counts(user_b["id"])

    res_a = requests.get(f"{BASE_URL}/dashboard/stats", headers={"Authorization": f"Bearer {user_a['token']}"}).json()
    res_b = requests.get(f"{BASE_URL}/dashboard/stats", headers={"Authorization": f"Bearer {user_b['token']}"}).json()

    print(f"User A SQL:  Docs={sql_a['total_docs']}, Clauses={sql_a['total_clauses']}, Risks={sql_a['total_risks']}, Levels={sql_a['risk_levels']}")
    print(f"User A API:  Docs={res_a['totalDocuments']}, Clauses={res_a['totalClauses']}, Risks={res_a['totalRisks']}, Levels={res_a['riskDistributionByLevel']}")
    assert res_a["totalDocuments"] == sql_a["total_docs"] == 2, "User A doc count mismatch"
    assert res_a["totalClauses"] == sql_a["total_clauses"] == 12, "User A clause count mismatch (7 + 5)"
    assert res_a["totalRisks"] == sql_a["total_risks"] == 1, "User A risk count mismatch"
    assert res_a["riskDistributionByLevel"].get("HIGH", 0) == 0, "User A should have 0 high risks"
    assert res_a["riskDistributionByLevel"].get("MEDIUM", 0) == 1, "User A should have 1 medium risk"
    print("  [PASS] User A dashboard numbers match SQL queries exactly.")

    print(f"\nUser B SQL:  Docs={sql_b['total_docs']}, Clauses={sql_b['total_clauses']}, Risks={sql_b['total_risks']}, Levels={sql_b['risk_levels']}")
    print(f"User B API:  Docs={res_b['totalDocuments']}, Clauses={res_b['totalClauses']}, Risks={res_b['totalRisks']}, Levels={res_b['riskDistributionByLevel']}")
    assert res_b["totalDocuments"] == sql_b["total_docs"] == 1, "User B doc count mismatch"
    assert res_b["totalClauses"] == sql_b["total_clauses"] == 6, "User B clause count mismatch"
    assert res_b["totalRisks"] == sql_b["total_risks"] == 3, "User B risk count mismatch"
    assert res_b["riskDistributionByLevel"].get("HIGH", 0) == 3, "User B should have 3 high risks"
    assert res_b["riskDistributionByLevel"].get("MEDIUM", 0) == 0, "User B should have 0 medium risks"
    print("  [PASS] User B dashboard numbers match SQL queries exactly and do not leak across users.")

    # -------------------------------------------------------------
    # 2. Delete a document; confirm dashboard counts update
    # -------------------------------------------------------------
    print("\n--- TEST 2: DELETE DOCUMENT AND CONFIRM DASHBOARD COUNTS UPDATE ---")
    doc2_id = user_a["doc2_id"]
    del_res = requests.delete(f"{BASE_URL}/documents/{doc2_id}", headers={"Authorization": f"Bearer {user_a['token']}"})
    assert del_res.status_code == 204, f"Delete failed: {del_res.status_code}"
    print(f"Deleted Document 2 ({doc2_id}) for User A.")

    # Re-fetch stats
    res_a_after = requests.get(f"{BASE_URL}/dashboard/stats", headers={"Authorization": f"Bearer {user_a['token']}"}).json()
    sql_a_after = query_user_sql_counts(user_a["id"])

    print(f"User A Updated API: Docs={res_a_after['totalDocuments']}, Clauses={res_a_after['totalClauses']}, Risks={res_a_after['totalRisks']}")
    assert res_a_after["totalDocuments"] == sql_a_after["total_docs"] == 1, "Doc count should decrement to 1"
    assert res_a_after["totalClauses"] == sql_a_after["total_clauses"] == 7, "Clause count should decrement to 7"
    assert len(res_a_after["recentDocuments"]) == 1, "Recent documents list should contain 1 document"
    print("  [PASS] Dashboard numbers updated immediately upon document deletion.")

    # -------------------------------------------------------------
    # 3. Generate PDF reports for 3 samples & render pages to PNG
    # -------------------------------------------------------------
    print("\n--- TEST 3: GENERATE PDF REPORTS FOR 3 SAMPLES & VERIFY VISUALLY ---")
    os.makedirs("evaluation/results/report_renders", exist_ok=True)

    samples = [
        {"name": "Sample 1 (Rental Agreement)", "docId": user_a["doc1_id"], "token": user_a["token"], "file": "report_sample1_rental.pdf"},
        {"name": "Sample 2 (Clean NDA - Empty Risk Test)", "docId": None, "token": user_a["token"], "file": "report_sample2_clean_nda.pdf"},
        {"name": "Sample 3 (One-Sided Vendor - Unicode & Traps)", "docId": user_b["doc3_id"], "token": user_b["token"], "file": "report_sample3_onesided.pdf"}
    ]

    # Re-seed clean NDA to doc2 for testing empty-risk report
    conn = get_db_connection()
    cur = conn.cursor()
    new_doc2_id = str(uuid.uuid4())
    cur.execute("""
        INSERT INTO documents (id, user_id, original_filename, storage_path, file_type, file_size, file_hash, page_count, is_scanned, status, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW());
    """, (new_doc2_id, user_a["id"], "clean_nda.pdf", f"/tmp/{new_doc2_id}.pdf", "PDF", 24000, uuid.uuid4().hex, 2, False, "COMPLETED"))
    new_analysis2_id = str(uuid.uuid4())
    cur.execute("""
        INSERT INTO document_analyses (id, document_id, title, document_type, purpose, parties, summary_short, summary_detailed, main_conditions, obligations_summary, financial_terms_summary, llm_provider, llm_model, verification_rate, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, '[]'::jsonb, '[]'::jsonb, '[]'::jsonb, %s, %s, %s, NOW(), NOW());
    """, (
        new_analysis2_id, new_doc2_id, "Mutual Non-Disclosure Agreement", "Non-Disclosure Agreement",
        "Mutual trade secret exchange.", "[]",
        "Standard mutual NDA protecting confidential information for 3 years.",
        "Comprehensive confidentiality agreement with mutual protections and standard return of materials upon termination.",
        "gemini", "gemini-3.5-flash-lite", 100.0
    ))
    # 4 clauses, 0 risks
    for i in range(1, 5):
        cur.execute("""
            INSERT INTO extracted_clauses (id, analysis_id, title, category, original_text, simplified_simple, simplified_detailed, simplified_professional, importance, affected_party, source_page, section_reference, evidence_quote, quote_verified, provenance, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW());
        """, (
            str(uuid.uuid4()), new_analysis2_id, f"Confidentiality Section {i}", "Confidentiality",
            f"Original confidentiality text {i}.", "Simple explanation.", "Detailed explanation.", "Professional legal summary.",
            "MEDIUM", "Both Parties", 1, f"Section {i}", "confidential information", True, "EXTRACTED"
        ))
    conn.commit()
    conn.close()
    samples[1]["docId"] = new_doc2_id

    # 10 mandatory section check strings
    expected_sections = [
        "1. Document Overview",
        "2. Executive Summary",
        "3. Important Clauses",
        "4. Plain-Language Clause Explanations",
        "5. Risk Analysis & Exposure Findings",
        "6. Financial Terms & Payment Schedule",
        "7. Important Dates & Milestones",
        "8. Missing & Ambiguous Provisions",
        "9. Suggested Questions to Ask",
        "10. Legal Notice & Disclaimer"
    ]

    for s in samples:
        print(f"\nGenerating {s['name']} (Doc ID: {s['docId']})...")
        resp = requests.get(f"{BASE_URL}/documents/{s['docId']}/report.pdf", headers={"Authorization": f"Bearer {s['token']}"})
        assert resp.status_code == 200, f"Failed to get report: {resp.status_code}"
        assert resp.headers.get("content-type") == "application/pdf", "Content type must be application/pdf"

        pdf_bytes = resp.content
        pdf_path = f"evaluation/results/{s['file']}"
        with open(pdf_path, "wb") as f:
            f.write(pdf_bytes)

        # Inspect with PyMuPDF
        doc = fitz.open(pdf_path)
        print(f"  Downloaded PDF: {len(pdf_bytes)} bytes across {len(doc)} pages.")

        all_text = ""
        for page_idx, page in enumerate(doc):
            all_text += page.get_text() + "\n"
            # Render page to PNG for visual inspection
            pix = page.get_pixmap(dpi=150)
            png_name = f"{s['file'].replace('.pdf', '')}_p{page_idx + 1}.png"
            pix.save(f"evaluation/results/report_renders/{png_name}")

        # Verify page numbers present in running footers
        for p_idx in range(1, len(doc) + 1):
            assert f"Page {p_idx}" in all_text, f"Missing 'Page {p_idx}' in running footer"

        # Verify running header & footer
        assert "NOT LEGAL ADVICE" in all_text, "Missing disclaimer in footer"
        if len(doc) > 1:
            assert "LexiLegal AI • Contract Analysis Report" in all_text, "Missing running header"

        # Verify section titles
        for sec in expected_sections:
            sec_num = sec.split(".")[0]
            sec_title = sec.split(".")[1].strip()
            found = sec_title.lower() in all_text.lower()
            print(f"  Section {sec_num} ({sec_title}): {'[FOUND]' if found else '[MISSING]'}")
            assert found, f"Missing section '{sec}' in {s['name']}"

        # Sample-specific checks:
        if s["file"] == "report_sample2_clean_nda.pdf":
            # Empty risk handling check
            assert "No specific risks identified in this agreement." in all_text, "Sample 2 must handle 0 risks gracefully"
            print("  [PASS] Empty risks section handled gracefully with clear informational message.")

        if s["file"] == "report_sample3_onesided.pdf":
            # Unicode check: ₹, §, curly quotes, em-dash
            print("  Checking Unicode symbols in Sample 3:")
            has_rupee = "₹" in all_text
            has_section = "§" in all_text
            has_curly = "“" in all_text or "”" in all_text or "‘" in all_text or "’" in all_text
            has_emdash = "—" in all_text
            print(f"    Rupee symbol (₹): {'[PRESERVED]' if has_rupee else '[NOT FOUND]'}")
            print(f"    Section symbol (§): {'[PRESERVED]' if has_section else '[NOT FOUND]'}")
            print(f"    Curly quotes (“ ”): {'[PRESERVED]' if has_curly else '[NOT FOUND]'}")
            print(f"    Em-dash (—): {'[PRESERVED]' if has_emdash else '[NOT FOUND]'}")
            assert has_rupee, "Rupee symbol ₹ must be preserved in OpenPDF output"
            assert has_section, "Section symbol § must be preserved"
            assert has_curly, "Curly quotes must be preserved"
            assert has_emdash, "Em-dash must be preserved"
            # Verify wrapping on long clause (1200+ characters)
            assert "hold harmless Vendor" in all_text, "Long clause text wrapped and preserved across table"
            print("  [PASS] Unicode characters (₹, §, quotes, dashes) and long-clause wrapping verified!")

    # -------------------------------------------------------------
    # 4. Confirm report endpoint authorization
    # -------------------------------------------------------------
    print("\n--- TEST 4: CONFIRM REPORT ENDPOINT AUTHORIZATION (404 FOR OTHER USER, 401 FOR UNAUTH) ---")
    doc_a_id = user_a["doc1_id"]

    # User B requests User A's report -> strictly 404
    cross_res = requests.get(f"{BASE_URL}/documents/{doc_a_id}/report.pdf", headers={"Authorization": f"Bearer {user_b['token']}"})
    print(f"User B GET /documents/{doc_a_id}/report.pdf -> HTTP {cross_res.status_code} (Expected 404)")
    assert cross_res.status_code == 404, f"Expected 404 but got {cross_res.status_code}"

    # Unauthenticated request -> strictly 401
    unauth_res = requests.get(f"{BASE_URL}/documents/{doc_a_id}/report.pdf")
    print(f"Unauthenticated GET /documents/{doc_a_id}/report.pdf -> HTTP {unauth_res.status_code} (Expected 401)")
    assert unauth_res.status_code == 401, f"Expected 401 but got {unauth_res.status_code}"
    print("  [PASS] Authorization confirmed: strictly 404 for cross-tenant, 401 for unauthenticated.")

    # -------------------------------------------------------------
    # 5. Empty-state dashboard for a brand-new user
    # -------------------------------------------------------------
    print("\n--- TEST 5: EMPTY-STATE DASHBOARD FOR A BRAND-NEW USER ---")
    email_c = f"empty_user_{uuid.uuid4().hex[:6]}@lexilegal.ai"
    reg_c = requests.post(f"{BASE_URL}/auth/register", json={
        "email": email_c,
        "password": "Password123!",
        "fullName": "New User Charlie"
    }).json()
    token_c = reg_c["token"]

    empty_stats = requests.get(f"{BASE_URL}/dashboard/stats", headers={"Authorization": f"Bearer {token_c}"}).json()
    print("Brand-new user stats:", json.dumps(empty_stats, indent=2))
    assert empty_stats["totalDocuments"] == 0, "totalDocuments should be 0"
    assert empty_stats["analyzedDocuments"] == 0, "analyzedDocuments should be 0"
    assert empty_stats["failedDocuments"] == 0, "failedDocuments should be 0"
    assert empty_stats["totalClauses"] == 0, "totalClauses should be 0"
    assert empty_stats["totalRisks"] == 0, "totalRisks should be 0"
    assert len(empty_stats["recentDocuments"]) == 0, "recentDocuments should be empty list"
    assert len(empty_stats["recentAnalyses"]) == 0, "recentAnalyses should be empty list"
    assert empty_stats["riskDistributionByLevel"]["HIGH"] == 0, "HIGH risks should be 0"
    print("  [PASS] Empty-state dashboard verified for brand-new user.")

    print("\n==================================================================")
    print("ALL PHASE 9 VERIFICATION CHECKS PASSED SUCCESSFULLY!")
    print("==================================================================")

if __name__ == "__main__":
    main()
