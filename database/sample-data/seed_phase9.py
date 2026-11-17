import os
import json
import uuid
import requests
import psycopg2
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

def register_or_login(email, password, full_name):
    reg_resp = requests.post(f"{BASE_URL}/auth/register", json={
        "email": email,
        "password": password,
        "fullName": full_name
    })
    if reg_resp.status_code == 201:
        data = reg_resp.json()
        return data["token"], data["user"]["id"]
    elif reg_resp.status_code == 409:
        login_resp = requests.post(f"{BASE_URL}/auth/login", json={
            "email": email,
            "password": password
        })
        if login_resp.status_code == 200:
            data = login_resp.json()
            return data["token"], data["user"]["id"]
        else:
            raise RuntimeError(f"Login failed: {login_resp.text}")
    else:
        raise RuntimeError(f"Registration failed: {reg_resp.text}")

def seed_sample_data():
    print("=== SEEDING PHASE 9 SAMPLE DATA FOR TWO ISOLATED USERS ===")

    # 1. Register User A (Alice)
    email_a = f"alice_phase9_{uuid.uuid4().hex[:6]}@lexilegal.ai"
    token_a, user_a_id = register_or_login(email_a, "Password123!", "Alice Walker")
    print(f"Created User A: {email_a} (ID: {user_a_id})")

    # 2. Register User B (Bob)
    email_b = f"bob_phase9_{uuid.uuid4().hex[:6]}@lexilegal.ai"
    token_b, user_b_id = register_or_login(email_b, "Password123!", "Bob Miller")
    print(f"Created User B: {email_b} (ID: {user_b_id})")

    conn = get_db_connection()
    cur = conn.cursor()

    # -------------------------------------------------------------
    # User A: Document 1 (Residential Lease)
    # -------------------------------------------------------------
    doc1_id = str(uuid.uuid4())
    cur.execute("""
        INSERT INTO documents (id, user_id, original_filename, storage_path, file_type, file_size, file_hash, page_count, is_scanned, status, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW());
    """, (doc1_id, user_a_id, "rental_agreement.pdf", f"/tmp/{doc1_id}.pdf", "PDF", 35000, uuid.uuid4().hex, 2, False, "COMPLETED"))

    analysis1_id = str(uuid.uuid4())
    cur.execute("""
        INSERT INTO document_analyses (id, document_id, title, document_type, purpose, parties, summary_short, summary_detailed, main_conditions, obligations_summary, financial_terms_summary, llm_provider, llm_model, verification_rate, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, '[]'::jsonb, '[]'::jsonb, '[]'::jsonb, %s, %s, %s, NOW(), NOW());
    """, (
        analysis1_id, doc1_id, "Residential Lease Agreement", "Residential Lease",
        "Lease of residential apartment unit.",
        json.dumps([{"name": "Metro Properties LLC", "role": "Landlord"}, {"name": "Sarah Jenkins", "role": "Tenant"}]),
        "One-year residential lease for Unit 4B at $1,400 per month.",
        "Detailed residential tenancy agreement containing monthly rent covenants, security deposit conditions, and repair obligations.",
        "gemini", "gemini-3.5-flash-lite", 100.0
    ))

    # Add 7 Clauses for Doc 1
    for i in range(1, 8):
        cur.execute("""
            INSERT INTO extracted_clauses (id, analysis_id, title, category, original_text, simplified_simple, simplified_detailed, simplified_professional, importance, affected_party, source_page, section_reference, evidence_quote, quote_verified, provenance, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW());
        """, (
            str(uuid.uuid4()), analysis1_id, f"Lease Term & Condition {i}", "Contractual",
            f"Original legal text of lease condition {i} specifying tenant compliance covenants.",
            f"Simple explanation of lease condition {i}.",
            f"Detailed breakdown of lease condition {i} regarding tenant responsibilities.",
            f"Professional analysis of lease condition {i}.",
            "HIGH" if i <= 2 else "MEDIUM", "Tenant", (i % 2) + 1, f"Section {i}",
            f"Evidence quote for condition {i}", True, "EXTRACTED"
        ))

    # Add 1 Risk for Doc 1
    cur.execute("""
        INSERT INTO risk_findings (id, analysis_id, category, level, title, original_clause, explanation, why_it_matters, possible_consequences, suggested_questions, source_page, evidence_quote, quote_verified, provenance, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW());
    """, (
        str(uuid.uuid4()), analysis1_id, "CONTRACTUAL", "MEDIUM", "Strict 14-Day Cure Notice",
        "Tenant must cure any violation within fourteen calendar days.",
        "Short period to remedy maintenance or structural concerns.",
        "Leaves little margin for error or dispute resolution.",
        "Potential eviction proceedings if notice window expires.",
        json.dumps(["Can the cure period be extended to 30 days?"]), 2,
        "within fourteen calendar days", True, "AI_INTERPRETATION"
    ))

    # Add Key Info for Doc 1
    cur.execute("""
        INSERT INTO extracted_information (id, analysis_id, contract_amount, contract_amount_page, payment_deadlines, payment_deadlines_page, penalties, penalties_page, start_date, start_date_page, end_date, end_date_page, renewal_date, renewal_date_page, notice_period, notice_period_page, termination_conditions, termination_conditions_page, obligations, important_dates, created_at, updated_at)
        VALUES (%s, %s, %s, 1, %s, 1, %s, 1, %s, 1, %s, 1, %s, 2, %s, 2, %s, 2, '[]'::jsonb, '[]'::jsonb, NOW(), NOW());
    """, (
        str(uuid.uuid4()), analysis1_id, "$1,400.00 / month", "1st of each month", "$50 late fee",
        "2026-08-01", "2027-07-31", "60 days before expiry", "30 days notice", "Termination upon default"
    ))

    # Add 2 Missing Provisions for Doc 1
    cur.execute("""
        INSERT INTO missing_clause_warnings (id, analysis_id, category, clause_name, why_it_matters, typical_provision, risk_level, label, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW());
    """, (str(uuid.uuid4()), analysis1_id, "Financial", "Rent Increase Cap", "Protects tenant against uncapped rent increases on renewal.", "Annual rent increases capped at 4%.", "MEDIUM", "Possible omission"))
    cur.execute("""
        INSERT INTO missing_clause_warnings (id, analysis_id, category, clause_name, why_it_matters, typical_provision, risk_level, label, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW());
    """, (str(uuid.uuid4()), analysis1_id, "Maintenance", "Emergency Repair Reimbursement", "Allows tenant to fix urgent plumbing/heating issues.", "Tenant may deduct emergency repairs up to $500.", "LOW", "Possible omission"))

    # -------------------------------------------------------------
    # User A: Document 2 (Clean Mutual NDA — 0 Risks)
    # -------------------------------------------------------------
    doc2_id = str(uuid.uuid4())
    cur.execute("""
        INSERT INTO documents (id, user_id, original_filename, storage_path, file_type, file_size, file_hash, page_count, is_scanned, status, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW());
    """, (doc2_id, user_a_id, "clean_nda.pdf", f"/tmp/{doc2_id}.pdf", "PDF", 24000, uuid.uuid4().hex, 2, False, "COMPLETED"))

    analysis2_id = str(uuid.uuid4())
    cur.execute("""
        INSERT INTO document_analyses (id, document_id, title, document_type, purpose, parties, summary_short, summary_detailed, main_conditions, obligations_summary, financial_terms_summary, llm_provider, llm_model, verification_rate, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, '[]'::jsonb, '[]'::jsonb, '[]'::jsonb, %s, %s, %s, NOW(), NOW());
    """, (
        analysis2_id, doc2_id, "Mutual Non-Disclosure Agreement", "Non-Disclosure Agreement",
        "Mutual exchange of proprietary technical evaluations.",
        json.dumps([{"name": "Apex Innovations Inc", "role": "Party A"}, {"name": "Nexus Dynamics Corp", "role": "Party B"}]),
        "Standard mutual NDA protecting trade secrets for 3 years.",
        "Balanced bilateral confidentiality agreement with standard exclusions and return requirements.",
        "gemini", "gemini-3.5-flash-lite", 100.0
    ))

    # Add 5 Clauses for Doc 2
    for i in range(1, 6):
        cur.execute("""
            INSERT INTO extracted_clauses (id, analysis_id, title, category, original_text, simplified_simple, simplified_detailed, simplified_professional, importance, affected_party, source_page, section_reference, evidence_quote, quote_verified, provenance, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW());
        """, (
            str(uuid.uuid4()), analysis2_id, f"Confidentiality Provision {i}", "Confidentiality",
            f"Original text of mutual confidentiality provision {i}.",
            f"Both parties must keep shared materials private.",
            f"Detailed obligation on information marking and standard of care for provision {i}.",
            f"Mutual trade secret protection covenants for provision {i}.",
            "HIGH" if i == 1 else "MEDIUM", "Both Parties", 1, f"Section {i}",
            f"Evidence quote for confidentiality {i}", True, "EXTRACTED"
        ))

    # 0 Risks for Doc 2 (Testing empty risk section handling!)

    # Add Key Info for Doc 2
    cur.execute("""
        INSERT INTO extracted_information (id, analysis_id, contract_amount, contract_amount_page, payment_deadlines, payment_deadlines_page, penalties, penalties_page, start_date, start_date_page, end_date, end_date_page, renewal_date, renewal_date_page, notice_period, notice_period_page, termination_conditions, termination_conditions_page, obligations, important_dates, created_at, updated_at)
        VALUES (%s, %s, %s, NULL, %s, NULL, %s, NULL, %s, 1, %s, 2, %s, NULL, %s, NULL, %s, 2, '[]'::jsonb, '[]'::jsonb, NOW(), NOW());
    """, (
        str(uuid.uuid4()), analysis2_id, "Not specified", "Not specified", "Not specified",
        "2026-05-15", "2029-05-15", "Not specified", "Not specified", "3 years from effective date"
    ))

    # -------------------------------------------------------------
    # User B: Document 1 (One-Sided Vendor Agreement with Unicode ₹, §, quotes, long clauses)
    # -------------------------------------------------------------
    doc3_id = str(uuid.uuid4())
    cur.execute("""
        INSERT INTO documents (id, user_id, original_filename, storage_path, file_type, file_size, file_hash, page_count, is_scanned, status, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW());
    """, (doc3_id, user_b_id, "one_sided_agreement.pdf", f"/tmp/{doc3_id}.pdf", "PDF", 42000, uuid.uuid4().hex, 2, False, "COMPLETED"))

    analysis3_id = str(uuid.uuid4())
    cur.execute("""
        INSERT INTO document_analyses (id, document_id, title, document_type, purpose, parties, summary_short, summary_detailed, main_conditions, obligations_summary, financial_terms_summary, llm_provider, llm_model, verification_rate, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, '[]'::jsonb, '[]'::jsonb, '[]'::jsonb, %s, %s, %s, NOW(), NOW());
    """, (
        analysis3_id, doc3_id, "Enterprise Master Services Agreement", "Service Agreement",
        "Cloud software and professional deployment terms.",
        json.dumps([{"name": "OmniCorp Software Ltd", "role": "Vendor"}, {"name": "Apex Global Client Inc", "role": "Customer"}]),
        "One-sided commercial vendor agreement featuring unilateral termination and accelerated liabilities.",
        "Extremely vendor-favorable master services agreement with uncapped customer indemnification, auto-renewal traps, and a $100 vendor liability cap.",
        "gemini", "gemini-3.5-flash-lite", 100.0
    ))

    # 6 Clauses for User B — including Unicode ₹, §, curly quotes, and a very long clause for wrapping
    cur.execute("""
        INSERT INTO extracted_clauses (id, analysis_id, title, category, original_text, simplified_simple, simplified_detailed, simplified_professional, importance, affected_party, source_page, section_reference, evidence_quote, quote_verified, provenance, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW());
    """, (
        str(uuid.uuid4()), analysis3_id, "Statutory Late Surcharge & Penalties", "Financial",
        "Under Section § 4.2, overdue balances accrue interest at 2.5% per month, plus an immediate administrative fee of ₹ 1,50,000 for each default occurrence.",
        "If you pay late, you are charged 2.5% monthly interest and a flat ₹ 1,50,000 penalty fee.",
        "Section § 4.2 establishes a compound late interest charge of 2.5% per month, along with an administrative liquidated penalty of ₹ 1,50,000.",
        "Contractual liquidated damages clause imposing 2.5% monthly compound interest and a fixed surcharge of ₹ 1,50,000.",
        "HIGH", "Customer", 1, "Section § 4.2", "₹ 1,50,000 for each default occurrence", True, "EXTRACTED"
    ))

    # Clause with curly quotes and em-dash
    cur.execute("""
        INSERT INTO extracted_clauses (id, analysis_id, title, category, original_text, simplified_simple, simplified_detailed, simplified_professional, importance, affected_party, source_page, section_reference, evidence_quote, quote_verified, provenance, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW());
    """, (
        str(uuid.uuid4()), analysis3_id, "Proprietary Data Ownership", "Intellectual Property",
        "All “Customer proprietary data” and ‘developed intellectual works’—regardless of source—shall immediately transfer to Vendor without further royalty or assignment notice.",
        "The vendor owns all your data and work products automatically—without any extra permission.",
        "Vendor claims full transfer of all “Customer proprietary data” and ‘developed intellectual works’—irrevocably.",
        "Broad IP assignment divesting customer of all proprietary data and intellectual work products.",
        "HIGH", "Customer", 1, "Section 7.1", "All “Customer proprietary data” and ‘developed intellectual works’—regardless of source", True, "EXTRACTED"
    ))

    # Very long clause (1,200+ characters) to verify proper table wrapping and pagination!
    long_clause_text = (
        "Customer agrees to defend, indemnify, and hold harmless Vendor, its parent entities, subsidiaries, officers, directors, employees, "
        "agents, successors, and assigns from and against any and all claims, demands, liabilities, damages, losses, costs, and expenses "
        "(including, without limitation, reasonable attorneys' fees, court costs, and expert witness fees) arising out of, relating to, or "
        "resulting from: (a) Customer's breach of any covenant, representation, or warranty under this Agreement; (b) any infringement or "
        "misappropriation of any third-party intellectual property or privacy rights; (c) any acts, omissions, or gross negligence of "
        "Customer's personnel; (d) any statutory, administrative, regulatory, or criminal investigations commenced by any governing body; "
        "and (e) any business interruption, loss of profits, loss of goodwill, or punitive damages asserted against Vendor by any third party, "
        "whether foreseeable or unforeseeable, regardless of whether Vendor was advised of the possibility of such damages in advance."
    )
    cur.execute("""
        INSERT INTO extracted_clauses (id, analysis_id, title, category, original_text, simplified_simple, simplified_detailed, simplified_professional, importance, affected_party, source_page, section_reference, evidence_quote, quote_verified, provenance, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW());
    """, (
        str(uuid.uuid4()), analysis3_id, "Comprehensive Uncapped Indemnification", "Liability",
        long_clause_text,
        "You must pay all of the vendor's legal fees and damages for almost any problem or lawsuit that happens.",
        "Extensive indemnification clause requiring customer to cover vendor legal fees, penalties, and losses for all breach types.",
        "Uncapped, one-sided indemnity exposing customer to comprehensive defense obligations and consequential damages.",
        "HIGH", "Customer", 2, "Section 8.1", "defend, indemnify, and hold harmless Vendor", True, "EXTRACTED"
    ))

    # Add 3 more clauses for Doc 3
    for i in range(4, 7):
        cur.execute("""
            INSERT INTO extracted_clauses (id, analysis_id, title, category, original_text, simplified_simple, simplified_detailed, simplified_professional, importance, affected_party, source_page, section_reference, evidence_quote, quote_verified, provenance, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW());
        """, (
            str(uuid.uuid4()), analysis3_id, f"Commercial Service Covenant {i}", "Contractual",
            f"Provisions governing service tier obligations and performance schedule {i}.",
            f"Simple description of service covenant {i}.",
            f"Detailed breakdown of service tier covenants {i}.",
            f"Professional analysis of vendor service tier covenant {i}.",
            "MEDIUM", "Customer", 2, f"Section {i}",
            f"Evidence quote for covenant {i}", True, "EXTRACTED"
        ))

    # 3 High Risks for User B
    cur.execute("""
        INSERT INTO risk_findings (id, analysis_id, category, level, title, original_clause, explanation, why_it_matters, possible_consequences, suggested_questions, source_page, evidence_quote, quote_verified, provenance, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW());
    """, (
        str(uuid.uuid4()), analysis3_id, "LIABILITY", "HIGH", "Uncapped Customer Indemnification",
        "Customer shall defend, indemnify, and hold harmless Vendor against all third-party claims.",
        "Customer assumes unlimited defense and liability costs without any financial cap.",
        "Exposes customer balance sheet to third-party litigation without limitation.",
        "Potentially ruinous financial exposure for vendor-side operational errors.",
        json.dumps(["Can we cap indemnification to fees paid in the preceding 12 months?", "Can mutual indemnity be inserted?"]), 2,
        "indemnify, and hold harmless Vendor", True, "AI_INTERPRETATION"
    ))

    cur.execute("""
        INSERT INTO risk_findings (id, analysis_id, category, level, title, original_clause, explanation, why_it_matters, possible_consequences, suggested_questions, source_page, evidence_quote, quote_verified, provenance, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW());
    """, (
        str(uuid.uuid4()), analysis3_id, "CONTRACTUAL", "HIGH", "Unilateral Vendor Termination Right",
        "Vendor may terminate immediately at any time with or without cause.",
        "Vendor can cancel service arbitrarily, but customer is locked into the full multi-year term.",
        "Leaves customer business operations vulnerable to sudden service withdrawal.",
        "Mission-critical workflow interruption with zero transition period.",
        json.dumps(["Can termination for convenience require 90 days prior written notice?"]), 2,
        "terminate immediately at any time with or without cause", True, "AI_INTERPRETATION"
    ))

    cur.execute("""
        INSERT INTO risk_findings (id, analysis_id, category, level, title, original_clause, explanation, why_it_matters, possible_consequences, suggested_questions, source_page, evidence_quote, quote_verified, provenance, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW());
    """, (
        str(uuid.uuid4()), analysis3_id, "FINANCIAL", "HIGH", "180-Day Auto-Renewal Trap",
        "Contract automatically renews for 3-year periods unless written notice is given 180 days prior.",
        "Unusually long advance notice window makes avoiding auto-renewal difficult.",
        "Missing the 6-month window commits customer to another 3 full years of fees.",
        "Accelerated full multi-year fees become immediately due upon missed notice.",
        json.dumps(["Can the non-renewal notice period be reduced to 30 or 60 days?"]), 1,
        "at least 180 days prior to the expiration", True, "AI_INTERPRETATION"
    ))

    # Add Key Info for Doc 3
    cur.execute("""
        INSERT INTO extracted_information (id, analysis_id, contract_amount, contract_amount_page, payment_deadlines, payment_deadlines_page, penalties, penalties_page, start_date, start_date_page, end_date, end_date_page, renewal_date, renewal_date_page, notice_period, notice_period_page, termination_conditions, termination_conditions_page, obligations, important_dates, created_at, updated_at)
        VALUES (%s, %s, %s, 1, %s, 1, %s, 1, %s, 1, %s, 1, %s, 1, %s, 1, %s, 2, '[]'::jsonb, '[]'::jsonb, NOW(), NOW());
    """, (
        str(uuid.uuid4()), analysis3_id, "$120,000.00 / year", "Net 3 days of invoice", "2.5% monthly + ₹ 1,50,000 fee",
        "2026-09-01", "2029-08-31", "180 days notice prior to renewal", "180 days written notice", "Vendor termination for convenience; Customer locked"
    ))

    # Add 2 Missing Provisions for Doc 3
    cur.execute("""
        INSERT INTO missing_clause_warnings (id, analysis_id, category, clause_name, why_it_matters, typical_provision, risk_level, label, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW());
    """, (str(uuid.uuid4()), analysis3_id, "Liability", "Mutual Limitation of Liability", "Restricts both parties' maximum financial exposure.", "Liability capped at fees paid in preceding 12 months.", "HIGH", "Possible omission"))
    cur.execute("""
        INSERT INTO missing_clause_warnings (id, analysis_id, category, clause_name, why_it_matters, typical_provision, risk_level, label, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW());
    """, (str(uuid.uuid4()), analysis3_id, "Data Privacy", "Data Return and Deletion Protocol", "Ensures client data is destroyed upon contract expiry.", "Vendor shall return and delete all customer data within 30 days.", "HIGH", "Possible omission"))

    conn.commit()
    conn.close()

    print("\n[SEED COMPLETE]: Successfully seeded:")
    print(f"  User A ({email_a}): 2 documents (Doc 1: {doc1_id}, Doc 2: {doc2_id})")
    print(f"  User B ({email_b}): 1 document (Doc 3: {doc3_id})")

    return {
        "userA": {"email": email_a, "id": user_a_id, "token": token_a, "doc1_id": doc1_id, "doc2_id": doc2_id},
        "userB": {"email": email_b, "id": user_b_id, "token": token_b, "doc3_id": doc3_id}
    }

if __name__ == "__main__":
    seed_sample_data()

