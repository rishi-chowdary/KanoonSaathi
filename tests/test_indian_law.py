"""Tests for Indian statute support: BNS 2023, IPC 1860, Constitution of India, and Studio lookup."""

from pathlib import Path

from app.nlp.clause_classifier import classify_clause
from app.nlp.document_classifier import classify_document_type
from app.nlp.extraction import extract_document
from app.nlp.indian_law import (
    detect_statute_references,
    load_indian_statutes,
    search_indian_statutes,
)
from app.nlp.missing_provisions import detect_missing_provisions
from app.nlp.segmentation import segment_clauses
from app.nlp.simplification import simplify_clause

SAMPLES_DIR = Path("samples/contracts")


def test_indian_statutes_yaml_loaded():
    data = load_indian_statutes()
    assert len(data["criminal_sections"]) >= 25
    assert len(data["constitutional_articles"]) >= 14


def test_bns_and_ipc_cross_reference_detection():
    bns_refs = detect_statute_references(
        "Under Section 318(4) BNS and Section 103 of the Bharatiya Nyaya Sanhita."
    )
    bns_nums = {r["bns_section"] for r in bns_refs}
    assert "318" in bns_nums
    assert "103" in bns_nums
    cheating = next(r for r in bns_refs if r["bns_section"] == "318")
    assert "420" in cheating["ipc_section"]

    ipc_refs = detect_statute_references(
        "Charged under Section 420 IPC and u/s 302 IPC."
    )
    mapped_bns = {r["bns_section"] for r in ipc_refs}
    assert "318" in mapped_bns
    assert "103" in mapped_bns


def test_constitutional_article_detection():
    refs = detect_statute_references(
        "Petition filed under Article 32 invoking Article 21 and Article 19(1)(a) of the Constitution."
    )
    articles = {r["article"] for r in refs}
    assert {"32", "21", "19"}.issubset(articles)


def test_search_indian_statutes_filters():
    cheating = search_indian_statutes("420", "bns")
    assert any(s["bns_section"] == "318" for s in cheating)

    art21 = search_indian_statutes("personal liberty", "constitution")
    assert any(s["article"] == "21" for s in art21)

    all_entries = search_indian_statutes("", "all")
    assert len(all_entries) >= 39


def test_simplify_bns_ipc_and_constitutional_clauses():
    bns_text = (
        "Section 318. (4) Whoever cheats and thereby dishonestly induces the person deceived "
        "to deliver any property to any person shall be punished with imprisonment of either "
        "description for a term which may extend to seven years, and shall also be liable to fine."
    )
    bns_out = simplify_clause(
        bns_text, category="BNS_SECTION", affected_party="Accused"
    )
    assert "faces up to seven years" in bns_out["simple_english"].lower()
    assert "Bharatiya Nyaya Sanhita" in bns_out["detailed"]
    assert any(t["term"] == "dishonestly" for t in bns_out["glossary_terms"])

    art21_text = (
        "Article 21. Protection of life and personal liberty. "
        "No person shall be deprived of his life or personal liberty except according to procedure established by law."
    )
    art_out = simplify_clause(art21_text, category="CONSTITUTIONAL_CLAUSE")
    assert "fair, lawful legal process" in art_out["simple_english"].lower()
    assert any(r["article"] == "21" for r in art_out["statute_references"])


def test_bns_ipc_constitution_pdfs_extract_segment_and_classify():
    for fname, expected_doc_type, expected_cat in [
        (
            "bns_selected_sections.pdf",
            "Bharatiya Nyaya Sanhita (BNS) Statute",
            "Criminal Offence and Punishment",
        ),
        (
            "ipc_selected_sections.pdf",
            "Indian Penal Code (IPC) Statute",
            "Criminal Offence and Punishment",
        ),
        (
            "constitution_fundamental_rights.pdf",
            "Constitution of India",
            "Constitutional Right and Provision",
        ),
    ]:
        raw = (SAMPLES_DIR / fname).read_bytes()
        extracted = extract_document(raw, fname)
        assert extracted.page_count == 2

        doc_type, conf = classify_document_type(extracted.full_text, fname)
        assert doc_type == expected_doc_type
        assert conf >= 0.8

        clauses = segment_clauses(
            extracted.full_text, extracted.pages, extracted.sections
        )
        assert len(clauses) >= 7
        for cl in clauses:
            assert (
                extracted.full_text[cl.start_offset : cl.end_offset] == cl.original_text
            )

        cats = [
            classify_clause(cl.title, cl.original_text, cl.section_reference)[0]
            for cl in clauses
        ]
        assert cats.count(expected_cat) >= 5

        # Statutory documents should not receive commercial contract missing-clause warnings
        assert detect_missing_provisions(clauses, doc_type, extracted.full_text) == []


def test_api_statutes_and_studio_indian_presets(client):
    resp = client.get("/studio")
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert "BNS / IPC / Constitution Lookup" in html
    assert "BNS Sec. 318" in html

    api_resp = client.get("/api/statutes?q=302&type=bns")
    assert api_resp.status_code == 200
    payload = api_resp.get_json()
    assert payload["count"] >= 1
    assert any(s["bns_section"] == "103" for s in payload["statutes"])

    art_resp = client.get("/api/statutes?q=21&type=constitution")
    assert art_resp.status_code == 200
    assert any(s["article"] == "21" for s in art_resp.get_json()["statutes"])


def test_upload_bns_pdf_full_pipeline_and_detail_view(client, test_user):
    client.post(
        "/api/auth/login",
        json={"email": test_user.email, "password": "SecurePassword123!"},
    )
    pdf_path = SAMPLES_DIR / "bns_selected_sections.pdf"
    with open(pdf_path, "rb") as f:
        up = client.post(
            "/api/documents/upload",
            data={"file": (f, "bns_selected_sections.pdf")},
            content_type="multipart/form-data",
        )
    assert up.status_code == 201
    doc_id = up.get_json()["id"]

    detail = client.get(f"/documents/{doc_id}")
    assert detail.status_code == 200
    html = detail.get_data(as_text=True)
    assert "BNS 103" in html
    assert "IPC 302" in html
    assert "BNS 318" in html
