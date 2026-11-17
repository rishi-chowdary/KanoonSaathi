import json
import os
import sys
import time
from pathlib import Path
import requests

BASE_URL = "http://127.0.0.1:8080/api"

def main():
    print("=" * 75)
    print("LEXILEGAL AI — PHASE 5 IMPORTANT CLAUSES LIVE VERIFICATION")
    print("=" * 75)

    # 1. Register test user
    ts = int(time.time())
    email = f"p5_evaluator_{ts}@lexilegal.test"
    password = "Password123!"
    print(f"\n[1] Registering verification user: {email}...")
    reg_resp = requests.post(
        f"{BASE_URL}/auth/register",
        json={"email": email, "password": password, "fullName": "Phase 5 Evaluator"}
    )
    if reg_resp.status_code != 201:
        print(f"Error registering user: {reg_resp.text}")
        sys.exit(1)
    token = reg_resp.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("  User authenticated, token acquired.")

    # 2. Upload contract
    file_path = "samples/contracts/clean_nda.pdf"
    print(f"\n[2] Uploading sample contract: {file_path}...")
    with open(file_path, "rb") as f:
        upload_resp = requests.post(
            f"{BASE_URL}/documents/upload",
            headers=headers,
            files={"file": ("clean_nda.pdf", f, "application/pdf")},
        )
    if upload_resp.status_code != 202:
        print(f"Upload failed: {upload_resp.text}")
        sys.exit(1)

    doc_data = upload_resp.json()
    doc_id = doc_data["id"]
    print(f"  Document accepted (202). Document ID: {doc_id}")

    # 3. Poll until COMPLETED
    print("\n[3] Waiting for async pipeline (Extracting -> Analyzing -> Completed)...")
    status = "UPLOADED"
    for attempt in range(120):
        time.sleep(3)
        stat_resp = requests.get(f"{BASE_URL}/documents/{doc_id}/status", headers=headers)
        if stat_resp.status_code == 200:
            status = stat_resp.json().get("status")
            print(f"  Attempt {attempt + 1}: status = {status}")
            if status == "COMPLETED":
                break
            if status == "FAILED":
                print(f"  Pipeline failed: {stat_resp.json().get('failureReason')}")
                sys.exit(1)
    
    if status != "COMPLETED":
        print("  Timed out waiting for document analysis.")
        sys.exit(1)

    # 4. Fetch extracted clauses
    print(f"\n[4] Fetching extracted clauses from GET /api/documents/{doc_id}/clauses...")
    clauses_resp = requests.get(f"{BASE_URL}/documents/{doc_id}/clauses", headers=headers)
    if clauses_resp.status_code != 200:
        print(f"Failed to fetch clauses: {clauses_resp.text}")
        sys.exit(1)

    clauses_data = clauses_resp.json()
    total_elements = clauses_data.get("totalElements", 0)
    clauses = clauses_data.get("content", [])
    print(f"  Total extracted clauses: {total_elements}")
    assert total_elements > 0, "Expected at least 1 extracted clause"

    verified_count = sum(1 for c in clauses if c.get("quoteVerified"))
    verif_rate = (verified_count / len(clauses)) * 100.0 if clauses else 0.0

    print(f"  Quote verification rate: {verif_rate:.1f}% ({verified_count}/{len(clauses)})")
    print("\n" + "-" * 75)
    print(f"{'TITLE':<32} | {'CATEGORY':<20} | {'IMP':<6} | {'PAGE':<4} | {'VERIFIED'}")
    print("-" * 75)
    for c in clauses:
        title = c.get("title", "")[:30]
        cat = (c.get("customLabel") if c.get("category") == "Other" and c.get("customLabel") else c.get("category", ""))[:18]
        imp = c.get("importance", "")
        page = c.get("sourcePage", 1)
        v = "YES" if c.get("quoteVerified") else "NO"
        print(f"{title:<32} | {cat:<20} | {imp:<6} | {page:<4} | {v}")

        # Check 3 modes exist
        assert c.get("simplifiedSimple"), "Missing simplifiedSimple"
        assert c.get("simplifiedDetailed"), "Missing simplifiedDetailed"
        assert c.get("simplifiedProfessional"), "Missing simplifiedProfessional"

    print("-" * 75)
    first_clause = clauses[0]
    print("\nSample Clause Detail Check:")
    print(f"  Title: {first_clause.get('title')}")
    print(f"  Category: {first_clause.get('category')}")
    print(f"  Simple English: {first_clause.get('simplifiedSimple')[:120]}...")
    print(f"  Detailed: {first_clause.get('simplifiedDetailed')[:120]}...")
    print(f"  Professional: {first_clause.get('simplifiedProfessional')[:120]}...")
    print(f"  Evidence Quote: \"{first_clause.get('evidenceQuote')}\"")
    print(f"  Quote Verified: {first_clause.get('quoteVerified')}")
    print(f"  Provenance: {first_clause.get('provenance')}")

    # 5. Filter tests
    print("\n[5] Testing Filter Endpoints:")
    # Category filter
    test_cat = first_clause.get("category")
    cat_resp = requests.get(f"{BASE_URL}/documents/{doc_id}/clauses?category={test_cat}", headers=headers)
    assert cat_resp.status_code == 200
    cat_items = cat_resp.json().get("content", [])
    print(f"  Filter category='{test_cat}': found {len(cat_items)} item(s) (all match: {all(c['category'] == test_cat for c in cat_items)})")

    # Importance filter
    imp_resp = requests.get(f"{BASE_URL}/documents/{doc_id}/clauses?importance=HIGH", headers=headers)
    assert imp_resp.status_code == 200
    imp_items = imp_resp.json().get("content", [])
    print(f"  Filter importance='HIGH': found {len(imp_items)} item(s)")

    # Search filter
    search_query = first_clause.get("title").split()[0]
    search_resp = requests.get(f"{BASE_URL}/documents/{doc_id}/clauses?search={search_query}", headers=headers)
    assert search_resp.status_code == 200
    search_items = search_resp.json().get("content", [])
    print(f"  Search query='{search_query}': found {len(search_items)} item(s)")

    # 6. Tenant isolation test
    print("\n[6] Testing Tenant Isolation (Cross-User Access):")
    email_b = f"user_b_{ts}@lexilegal.test"
    reg_b = requests.post(f"{BASE_URL}/auth/register", json={"email": email_b, "password": password, "fullName": "User B"})
    token_b = reg_b.json()["token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    iso_resp = requests.get(f"{BASE_URL}/documents/{doc_id}/clauses", headers=headers_b)
    print(f"  User B requesting User A's clauses: HTTP {iso_resp.status_code} (Expect 404)")
    assert iso_resp.status_code == 404, f"Expected 404, got {iso_resp.status_code}"

    # 7. Unauthenticated test
    unauth_resp = requests.get(f"{BASE_URL}/documents/{doc_id}/clauses")
    print(f"  Unauthenticated request to clauses endpoint: HTTP {unauth_resp.status_code} (Expect 401)")
    assert unauth_resp.status_code == 401, f"Expected 401, got {unauth_resp.status_code}"

    print("\n" + "=" * 75)
    print("ALL PHASE 5 BACKEND & AI ENGINE CHECKS PASSED SUCCESSFULLY!")
    print("=" * 75)

if __name__ == "__main__":
    main()
