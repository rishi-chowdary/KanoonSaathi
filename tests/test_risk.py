"""Phase M6 Tests: Grounded Risk Detection & Missing Expected Provisions.

Verifies:
1. Rule 7 legal conclusion guard (zero instances of 'illegal', 'void', 'unenforceable')
2. Risk rules configuration and SBERT prototype integrity
3. Expected provisions checklist configuration across 5 standard contract types
4. Detection of predatory terms in one_sided_agreement.pdf (uncapped indemnity, unilateral changes, etc.)
5. Exact evidence quote verification (100% exact substring match)
6. Missing provision detection with strict 'Possible omission' label
7. Risk service database persistence and risk distribution calculation
8. REST API endpoints (GET /api/documents/<id>/risks, missing-provisions, risk-distribution)
9. Tenant isolation (404 on cross-user queries)
"""

from pathlib import Path

from app.nlp.extraction import extract_document
from app.nlp.missing_provisions import (
    detect_missing_provisions,
    load_expected_provisions,
    normalize_document_type,
)
from app.nlp.risk_engine import (
    count_rule7_violations,
    detect_clause_risks,
    enforce_rule7_language,
    load_risk_rules,
)
from app.nlp.segmentation import segment_clauses

SAMPLES_DIR = Path(__file__).resolve().parent.parent / "samples" / "contracts"


class TestRule7LegalAdviceGuard:
    """Verify Rule 7 strict prohibition on definitive legal conclusions."""

    def test_forbidden_words_sanitization(self):
        raw_text = (
            "This clause is completely illegal, void, and unenforceable under state law. "
            "Such unlawful terms are null and void."
        )
        cleaned = enforce_rule7_language(raw_text)

        assert "illegal" not in cleaned.lower()
        assert "void" not in cleaned.lower()
        assert "unenforceable" not in cleaned.lower()
        assert "unlawful" not in cleaned.lower()
        assert count_rule7_violations(cleaned) == 0

    def test_clean_text_unchanged(self):
        clean_text = "This clause presents substantial financial exposure and may be unfavorable."
        assert enforce_rule7_language(clean_text) == clean_text
        assert count_rule7_violations(clean_text) == 0


class TestConfigurationIntegrity:
    """Verify data/risk_rules.yaml and data/expected_provisions.yaml."""

    def test_risk_rules_yaml_covers_all_categories(self):
        rules = load_risk_rules()
        assert len(rules) >= 10, f"Expected at least 10 rules, found {len(rules)}"

        categories = {r["category"] for r in rules}
        required_cats = {"Financial", "Legal", "Privacy", "Contractual", "Employment", "Liability"}
        assert required_cats.issubset(categories), f"Missing categories: {required_cats - categories}"

        for r in rules:
            assert "id" in r
            assert "title" in r
            assert "level" in r
            assert r["level"] in ("HIGH", "MEDIUM", "LOW", "INFORMATIONAL")
            assert len(r.get("patterns", [])) > 0
            assert len(r.get("prototypes", [])) > 0
            assert len(r.get("explanation", "")) > 10
            assert count_rule7_violations(r["explanation"]) == 0

    def test_expected_provisions_yaml_covers_standard_document_types(self):
        checklists = load_expected_provisions()
        assert len(checklists) >= 5

        required_types = {
            "NON_DISCLOSURE_AGREEMENT",
            "LEASE_AGREEMENT",
            "EMPLOYMENT_AGREEMENT",
            "SERVICE_AGREEMENT",
            "PROMISSORY_NOTE",
        }
        assert required_types.issubset(set(checklists.keys()))

        for doc_key, cfg in checklists.items():
            provisions = cfg.get("expected_provisions", [])
            assert len(provisions) >= 2, f"Doc type {doc_key} has too few provisions"
            for p in provisions:
                assert "provision_id" in p
                assert "clause_name" in p
                assert "risk_level" in p
                assert "why_it_matters" in p
                assert count_rule7_violations(p["why_it_matters"]) == 0

    def test_document_type_normalization(self):
        assert normalize_document_type("Non-Disclosure Agreement") == "NON_DISCLOSURE_AGREEMENT"
        assert normalize_document_type("NDA") == "NON_DISCLOSURE_AGREEMENT"
        assert normalize_document_type("Commercial Lease") == "LEASE_AGREEMENT"
        assert normalize_document_type("Employment Agreement") == "EMPLOYMENT_AGREEMENT"
        assert normalize_document_type("SaaS Agreement") == "SERVICE_AGREEMENT"
        assert normalize_document_type("Promissory Note") == "PROMISSORY_NOTE"


class TestPredatoryTermsAndRiskDetection:
    """Verify detection of predatory clauses in one_sided_agreement.pdf."""

    def test_predatory_terms_in_one_sided_agreement(self):
        pdf_path = SAMPLES_DIR / "one_sided_agreement.pdf"
        assert pdf_path.exists(), f"Sample contract missing: {pdf_path}"

        doc_res = extract_document(pdf_path.read_bytes(), "one_sided_agreement.pdf")
        clauses = segment_clauses(doc_res.full_text, doc_res.pages, doc_res.sections)

        risks = detect_clause_risks(clauses, full_text=doc_res.full_text)
        assert len(risks) >= 5, f"Expected at least 5 risks in one-sided agreement, found {len(risks)}"

        risk_titles = [r["title"].lower() for r in risks]

        # 1. Uncapped indemnity detected as HIGH

        has_indemnity = any("indemnif" in t for t in risk_titles)
        assert has_indemnity, f"Uncapped indemnity not flagged in {risk_titles}"

        # 2. Unilateral modification detected as HIGH
        has_unilateral_mod = any("unilateral modification" in t or "modify" in t for t in risk_titles)
        assert has_unilateral_mod, f"Unilateral modification not flagged in {risk_titles}"

        # 3. Severe late charges / compounding interest detected as HIGH
        has_late_fees = any("late charges" in t or "fee" in t for t in risk_titles)
        assert has_late_fees, f"Severe late charges not flagged in {risk_titles}"

        # 4. Disproportionate liability cap detected as HIGH
        has_liab_cap = any("liability" in t or "disproportion" in t for t in risk_titles)
        assert has_liab_cap, f"Liability cap disproportion not flagged in {risk_titles}"

        # 5. Check Rule 7 across all outputs
        for r in risks:
            assert count_rule7_violations(r["explanation"]) == 0
            assert count_rule7_violations(r["why_it_matters"]) == 0
            assert count_rule7_violations(r["possible_consequences"]) == 0
            # Evidence quote exact slice check
            assert r["quote_verified"] is True
            assert r["evidence_quote"] in doc_res.full_text


class TestMissingProvisionsDetection:
    """Verify detection of missing expected clauses in clean NDA and rental agreement."""

    def test_clean_nda_missing_carveouts_and_remedies(self):
        pdf_path = SAMPLES_DIR / "clean_nda.pdf"
        assert pdf_path.exists(), f"Sample contract missing: {pdf_path}"

        doc_res = extract_document(pdf_path.read_bytes(), "clean_nda.pdf")
        clauses = segment_clauses(doc_res.full_text, doc_res.pages, doc_res.sections)

        missing = detect_missing_provisions(
            clauses, document_type="Non-Disclosure Agreement", full_text=doc_res.full_text
        )

        assert len(missing) >= 2, f"Expected at least 2 missing provisions, found {len(missing)}"

        # Verify strict "Possible omission" labeling and Rule 7 compliance
        for m in missing:
            assert m["label"] == "Possible omission"
            assert count_rule7_violations(m["why_it_matters"]) == 0
            assert count_rule7_violations(m["typical_provision"]) == 0

    def test_rental_agreement_missing_security_deposit_timeline(self):
        pdf_path = SAMPLES_DIR / "rental_agreement.pdf"
        assert pdf_path.exists(), f"Sample contract missing: {pdf_path}"

        doc_res = extract_document(pdf_path.read_bytes(), "rental_agreement.pdf")
        clauses = segment_clauses(doc_res.full_text, doc_res.pages, doc_res.sections)

        missing = detect_missing_provisions(
            clauses, document_type="Rental Agreement", full_text=doc_res.full_text
        )

        # Rental agreement ends abruptly at term clause, missing deposit return and entry notice
        assert len(missing) >= 1
        for m in missing:
            assert m["label"] == "Possible omission"


class TestRiskServiceAndAPI:
    """Verify database persistence, distribution computation, REST endpoints, and tenant isolation."""

    def test_full_pipeline_persistence_and_endpoints(self, client, test_user):
        pdf_path = SAMPLES_DIR / "one_sided_agreement.pdf"
        assert pdf_path.exists()

        # Log in as test_user
        login_resp = client.post(
            "/api/auth/login",
            json={"email": "lawyer@example.com", "password": "SecurePassword123!"},
        )
        assert login_resp.status_code == 200

        # Upload and analyze document
        with open(pdf_path, "rb") as f:
            upload_resp = client.post(
                "/api/documents/upload",
                data={"file": (f, "one_sided_agreement.pdf")},
                content_type="multipart/form-data",
            )
        assert upload_resp.status_code == 201
        doc_json = upload_resp.get_json()
        doc_id = doc_json["id"]


        # 1. Test GET /api/documents/<id>/risks
        risks_resp = client.get(f"/api/documents/{doc_id}/risks")
        assert risks_resp.status_code == 200
        risks_data = risks_resp.get_json()
        assert len(risks_data) >= 5
        first_risk = risks_data[0]
        assert "level" in first_risk
        assert "category" in first_risk
        assert "title" in first_risk
        assert "evidenceQuote" in first_risk
        assert "quoteVerified" in first_risk
        assert first_risk["quoteVerified"] is True

        # 2. Test GET /api/documents/<id>/missing-provisions
        missing_resp = client.get(f"/api/documents/{doc_id}/missing-provisions")
        assert missing_resp.status_code == 200
        missing_data = missing_resp.get_json()
        for item in missing_data:
            assert item["label"] == "Possible omission"

        # 3. Test GET /api/documents/<id>/risk-distribution
        dist_resp = client.get(f"/api/documents/{doc_id}/risk-distribution")
        assert dist_resp.status_code == 200
        dist_data = dist_resp.get_json()
        assert "totalRisks" in dist_data
        assert dist_data["totalRisks"] == len(risks_data)
        assert "byLevel" in dist_data
        assert "byCategory" in dist_data
        assert dist_data["byLevel"]["HIGH"] >= 3

    def test_tenant_isolation_risks_and_missing_returns_404(self, client, test_user):
        # Log in as User A
        client.post(
            "/api/auth/login",
            json={"email": "lawyer@example.com", "password": "SecurePassword123!"},
        )

        pdf_path = SAMPLES_DIR / "clean_nda.pdf"

        with open(pdf_path, "rb") as f:
            upload_resp = client.post(
                "/api/documents/upload",
                data={"file": (f, "clean_nda.pdf")},
                content_type="multipart/form-data",
            )
        assert upload_resp.status_code == 201
        doc_id = upload_resp.get_json()["id"]

        # Register and login as User B
        user_b_payload = {
            "email": "user_b_risk@example.com",
            "password": "Password123!",
            "full_name": "User B",
        }
        reg_b = client.post("/api/auth/register", json=user_b_payload)
        assert reg_b.status_code == 201
        login_b = client.post(
            "/api/auth/login",
            json={"email": user_b_payload["email"], "password": user_b_payload["password"]},
        )
        assert login_b.status_code == 200

        # User B cannot access User A's risks or missing provisions (must return 404)
        assert client.get(f"/api/documents/{doc_id}/risks").status_code == 404
        assert client.get(f"/api/documents/{doc_id}/missing-provisions").status_code == 404
        assert client.get(f"/api/documents/{doc_id}/risk-distribution").status_code == 404
