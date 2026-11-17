import os
import sys
import time
import json
import subprocess
import requests

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8080/api")
PG_HOST = "127.0.0.1"
PG_PORT = "5433"
PG_USER = "postgres"
PG_PASS = "postgres"
PG_DB = "lexilegal"

def query_psql(sql):
    cmd = [
        "psql",
        "-h", PG_HOST,
        "-p", PG_PORT,
        "-U", PG_USER,
        "-d", PG_DB,
        "-t", "-A",
        "-F", "\t",
        "-c", sql
    ]
    env = os.environ.copy()
    env["PGPASSWORD"] = PG_PASS
    res = subprocess.run(cmd, env=env, capture_output=True, text=True, check=True)
    lines = [line.strip() for line in res.stdout.strip().split("\n") if line.strip()]
    return [line.split("\t") for line in lines]

def main():
    print("=" * 60)
    print("LEXILEGAL AI - PHASE 7 COMPREHENSIVE VERIFICATION SUITE")
    print("=" * 60)

    # 1. Register / Login User A
    user_a_email = "verify_p7_1794905856@lexilegal.test"
    password = "Password123!"
    doc_id = "97d98a15-ae6f-43e0-acee-4981b0896601"

    login_resp = requests.post(f"{BACKEND_URL}/auth/login", json={
        "email": user_a_email,
        "password": password
    })

    if login_resp.status_code == 200:
        print(f"\n[Step 1] Logged into existing User A ({user_a_email})...")
        token_a = login_resp.json()["token"]
        headers_a = {"Authorization": f"Bearer {token_a}"}
    else:
        user_a_email = f"verify_p7_{int(time.time())}@lexilegal.test"
        print(f"\n[Step 1] Registering fresh User A ({user_a_email})...")
        reg_resp = requests.post(f"{BACKEND_URL}/auth/register", json={
            "email": user_a_email,
            "password": password,
            "fullName": "Phase 7 Verification User"
        })
        assert reg_resp.status_code == 201, f"User A registration failed: {reg_resp.text}"
        token_a = reg_resp.json()["token"]
        headers_a = {"Authorization": f"Bearer {token_a}"}
        doc_id = None

    # Register User B for tenant isolation tests
    user_b_email = f"verify_p7_b_{int(time.time())}@lexilegal.test"
    reg_b_resp = requests.post(f"{BACKEND_URL}/auth/register", json={
        "email": user_b_email,
        "password": password,
        "fullName": "Phase 7 Tenant B"
    })
    token_b = reg_b_resp.json()["token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}
    print(f"  User B registered successfully for isolation checks.")

    # 2. Upload sample contract if needed
    if not doc_id:
        sample_file = "samples/contracts/rental_agreement.pdf"
        if not os.path.exists(sample_file):
            sample_file = "samples/contracts/clean_nda.pdf"
        print(f"\n[Step 2] Uploading sample contract: {sample_file}...")
        with open(sample_file, "rb") as f:
            upload_resp = requests.post(
                f"{BACKEND_URL}/documents/upload",
                headers=headers_a,
                files={"file": (os.path.basename(sample_file), f, "application/pdf")}
            )
        assert upload_resp.status_code == 202, f"Upload failed: {upload_resp.text}"
        doc_id = upload_resp.json()["id"]
        print(f"  Upload accepted. Document ID: {doc_id}")
    else:
        print(f"\n[Step 2] Attaching to existing pipeline document: {doc_id}")

    # 3. Wait for pipeline completion
    print("\n[Step 3] Polling document status until COMPLETED...")
    status = "UPLOADED"
    start_time = time.time()
    for _ in range(240):
        status_resp = requests.get(f"{BACKEND_URL}/documents/{doc_id}/status", headers=headers_a)
        assert status_resp.status_code == 200, f"Status check failed: {status_resp.text}"
        data = status_resp.json()
        status = data.get("status")
        progress = data.get("progressPercentage", 0)
        step = data.get("progressStep", "")
        print(f"  Status: {status} ({progress}%) - {step}")
        if status in ("COMPLETED", "FAILED"):
            break
        time.sleep(2)

    elapsed = time.time() - start_time
    print(f"  Pipeline finished in {elapsed:.1f}s with status: {status}")
    if status != "COMPLETED":
        print(f"FAILED REASON: {status_resp.json().get('failureReason')}")
        sys.exit(1)

    # 4. Database Validation
    print("\n[Step 4] Validating database persistence in PostgreSQL...")

    # Document Analysis
    analysis_rows = query_psql(f"SELECT id, title, document_type, verification_rate FROM document_analyses WHERE document_id = '{doc_id}'")
    assert len(analysis_rows) > 0, "document_analyses record missing!"
    analysis_id, title, doc_type, ver_rate = analysis_rows[0]
    print(f"  Analysis Record Found: ID={analysis_id}, Title='{title}', Type='{doc_type}', Verification Rate={ver_rate}%")

    # Risk Findings
    risk_stats_rows = query_psql(f"""
        SELECT count(*),
               count(*) FILTER (WHERE level = 'HIGH'),
               count(*) FILTER (WHERE level = 'MEDIUM'),
               count(*) FILTER (WHERE level = 'LOW'),
               count(*) FILTER (WHERE quote_verified = true),
               count(*) FILTER (WHERE jurisdiction_caveat IS NOT NULL)
        FROM risk_findings WHERE analysis_id = '{analysis_id}'
    """)
    total_risks, high_risks, med_risks, low_risks, verified_risks, caveat_risks = [int(x) for x in risk_stats_rows[0]]
    print(f"  Risk Findings in DB:")
    print(f"    Total: {total_risks} (HIGH: {high_risks}, MEDIUM: {med_risks}, LOW: {low_risks})")
    print(f"    Verified quotes: {verified_risks}/{total_risks}")
    print(f"    Jurisdiction caveats attached: {caveat_risks}")
    assert total_risks > 0, "Expected at least 1 risk finding in DB!"

    # Key Information
    info_rows = query_psql(f"""
        SELECT contract_amount, start_date, end_date, notice_period,
               jsonb_array_length(obligations), jsonb_array_length(important_dates)
        FROM extracted_information WHERE analysis_id = '{analysis_id}'
    """)
    assert len(info_rows) > 0, "extracted_information record missing!"
    c_amt, s_date, e_date, n_period, ob_count, dt_count = info_rows[0]
    print(f"  Extracted Information in DB:")
    print(f"    Amount: '{c_amt}'")
    print(f"    Start Date: '{s_date}'")
    print(f"    End Date: '{e_date}'")
    print(f"    Notice Period: '{n_period}'")
    print(f"    Obligations Count: {ob_count}")
    print(f"    Important Dates Count: {dt_count}")

    # Missing Clause Warnings
    missing_rows = query_psql(f"""
        SELECT count(*),
               count(*) FILTER (WHERE label = 'Possible omission')
        FROM missing_clause_warnings WHERE analysis_id = '{analysis_id}'
    """)
    missing_count, omission_labeled = [int(x) for x in missing_rows[0]]
    print(f"  Missing Clause Warnings in DB:")
    print(f"    Total warnings: {missing_count}")
    print(f"    Labeled 'Possible omission': {omission_labeled}")
    assert missing_count > 0, "Expected at least 1 missing provision warning!"
    assert missing_count == omission_labeled, "All missing warnings MUST be labeled 'Possible omission'!"

    # 5. REST API Endpoints Validation
    print("\n[Step 5] Validating REST API endpoints...")

    # 5.1 GET /api/documents/{id}/risks
    risks_resp = requests.get(f"{BACKEND_URL}/documents/{doc_id}/risks", headers=headers_a)
    assert risks_resp.status_code == 200, f"GET /risks failed: {risks_resp.text}"
    risks_data = risks_resp.json()
    assert len(risks_data) == total_risks, f"API count {len(risks_data)} != DB count {total_risks}"
    print(f"  GET /api/documents/{doc_id}/risks -> HTTP 200 ({len(risks_data)} findings)")

    # Sample risk inspection
    sample_risk = risks_data[0]
    print(f"    Sample: [{sample_risk['level']}] {sample_risk['title']} ({sample_risk['category']})")
    print(f"    Explanation: {sample_risk['explanation'][:80]}...")
    print(f"    Why It Matters: {sample_risk['whyItMatters'][:80]}...")
    print(f"    Suggested Questions: {len(sample_risk['suggestedQuestions'])} questions")
    assert "illegal" not in sample_risk['explanation'].lower(), "Rule 7 violation: 'illegal' in explanation!"
    assert "void" not in sample_risk['explanation'].lower(), "Rule 7 violation: 'void' in explanation!"
    assert "unenforceable" not in sample_risk['explanation'].lower(), "Rule 7 violation: 'unenforceable' in explanation!"

    # Filter by level
    if high_risks > 0:
        high_resp = requests.get(f"{BACKEND_URL}/documents/{doc_id}/risks?level=HIGH", headers=headers_a)
        assert high_resp.status_code == 200
        assert len(high_resp.json()) == high_risks
        print(f"    Filter level=HIGH -> HTTP 200 ({len(high_resp.json())} findings)")

    # 5.2 GET /api/documents/{id}/key-info
    info_resp = requests.get(f"{BACKEND_URL}/documents/{doc_id}/key-info", headers=headers_a)
    assert info_resp.status_code == 200, f"GET /key-info failed: {info_resp.text}"
    info_data = info_resp.json()
    print(f"  GET /api/documents/{doc_id}/key-info -> HTTP 200")
    print(f"    Contract Amount: {info_data.get('contractAmount')} (Page {info_data.get('contractAmountPage')})")
    print(f"    Payment Deadlines: {info_data.get('paymentDeadlines')}")
    print(f"    Notice Period: {info_data.get('noticePeriod')}")
    print(f"    Obligations: {len(info_data.get('obligations', []))} items")
    print(f"    Important Dates: {len(info_data.get('importantDates', []))} items")

    # 5.3 GET /api/documents/{id}/missing
    missing_resp = requests.get(f"{BACKEND_URL}/documents/{doc_id}/missing", headers=headers_a)
    assert missing_resp.status_code == 200, f"GET /missing failed: {missing_resp.text}"
    missing_data = missing_resp.json()
    print(f"  GET /api/documents/{doc_id}/missing -> HTTP 200 ({len(missing_data)} warnings)")
    for w in missing_data[:3]:
        assert w.get("label") == "Possible omission", f"Label {w.get('label')} != 'Possible omission'"
        print(f"    - [{w.get('riskLevel')}] {w.get('clauseName')} (Label: '{w.get('label')}')")

    # 5.4 Cross-tenant security: User B accessing User A's document returns HTTP 404
    print("\n[Step 6] Validating Tenant Isolation (User B accessing User A's resources)...")
    b_risks = requests.get(f"{BACKEND_URL}/documents/{doc_id}/risks", headers=headers_b)
    assert b_risks.status_code == 404, f"Tenant violation! Expected 404, got {b_risks.status_code}"

    b_info = requests.get(f"{BACKEND_URL}/documents/{doc_id}/key-info", headers=headers_b)
    assert b_info.status_code == 404, f"Tenant violation! Expected 404, got {b_info.status_code}"

    b_missing = requests.get(f"{BACKEND_URL}/documents/{doc_id}/missing", headers=headers_b)
    assert b_missing.status_code == 404, f"Tenant violation! Expected 404, got {b_missing.status_code}"
    print("  Cross-tenant isolation verified: all endpoints returned strict HTTP 404.")

    # 5.5 Unauthenticated security: returns HTTP 401
    print("\n[Step 7] Validating Unauthenticated Access...")
    unauth_risks = requests.get(f"{BACKEND_URL}/documents/{doc_id}/risks")
    assert unauth_risks.status_code == 401, f"Security violation! Expected 401, got {unauth_risks.status_code}"

    unauth_info = requests.get(f"{BACKEND_URL}/documents/{doc_id}/key-info")
    assert unauth_info.status_code == 401, f"Security violation! Expected 401, got {unauth_info.status_code}"

    unauth_missing = requests.get(f"{BACKEND_URL}/documents/{doc_id}/missing")
    assert unauth_missing.status_code == 401, f"Security violation! Expected 401, got {unauth_missing.status_code}"
    print("  Unauthenticated access blocked: all endpoints returned HTTP 401.")

    print("\n" + "=" * 60)
    print("PHASE 7 BACKEND, AI ENGINE & DATABASE VERIFICATION PASSED!")
    print(f"DOCUMENT ID FOR FRONTEND TEST: {doc_id}")
    print(f"USER EMAIL: {user_a_email}")
    print(f"USER PASSWORD: {password}")
    print("=" * 60)

    # Save credentials for frontend test script
    with open("frontend/phase7_test_context.json", "w") as f:
        json.dump({
            "documentId": doc_id,
            "email": user_a_email,
            "password": password
        }, f, indent=2)

if __name__ == "__main__":
    main()
