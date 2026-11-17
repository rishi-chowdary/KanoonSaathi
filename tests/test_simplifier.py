"""Tests for rule-based simplification, readability scoring, and trap detection."""

import json
from pathlib import Path

from app.nlp.readability import (
    calculate_readability,
    count_syllables_text,
    count_syllables_word,
)
from app.nlp.simplification import (
    detect_traps_and_nuances,
    extract_clause_glossary,
    get_glossary,
    get_sorted_glossary_terms,
    lexical_simplify,
    simplify_clause,
    verify_preservation,
)

FIXTURES_DIR = Path(__file__).parent / "fixtures"
LEGAL_TEST_CLAUSES = [
    (entry["text"], entry["category"], entry["party"])
    for entry in json.loads(
        (FIXTURES_DIR / "sample_clauses.json").read_text(encoding="utf-8")
    )
]


class TestReadabilityScorer:
    """Test pure-Python syllable counting and Flesch readability calculations."""

    def test_syllable_counting(self):
        assert count_syllables_word("the") == 1
        assert count_syllables_word("clause") == 1
        assert count_syllables_word("contract") == 2
        assert count_syllables_word("liability") == 5
        assert count_syllables_word("indemnification") == 6
        assert count_syllables_word("") == 0

    def test_text_syllable_counting(self):
        words, syllables = count_syllables_text("The tenant must pay rent.")
        assert words == 5
        assert syllables >= 5

    def test_empty_text_readability(self):
        res = calculate_readability("")
        assert res["word_count"] == 0
        assert res["flesch_reading_ease"] == 0.0

    def test_readability_metrics_keys(self):
        res = calculate_readability("This is a simple sentence about contracts.")
        assert "flesch_reading_ease" in res
        assert "flesch_kincaid_grade" in res
        assert "word_count" in res
        assert "sentence_count" in res
        assert "interpretation" in res
        assert res["word_count"] == 7


class TestSimplificationEngine:
    def test_glossary_loaded_and_exceeds_150_terms(self):
        glossary = get_glossary()
        assert (
            len(glossary) >= 150
        ), f"Expected at least 150 glossary terms, got {len(glossary)}"
        sorted_terms = get_sorted_glossary_terms()
        assert len(sorted_terms) >= 150

    def test_extract_clause_glossary(self):
        text = "The Tenant agrees to indemnify and hold harmless the Landlord."
        found = extract_clause_glossary(text)
        terms_found = {item["term"].lower() for item in found}
        assert "indemnify" in terms_found
        assert "hold harmless" in terms_found

    def test_lexical_simplify(self):
        text = "The Lessee covenants and agrees that it shall forthwith notify Lessor."
        simplified = lexical_simplify(text)
        assert "covenants and agrees" not in simplified.lower()
        assert "agrees" in simplified.lower()
        assert "forthwith" not in simplified.lower()
        assert "immediately" in simplified.lower()

    def test_negation_preservation(self):
        orig_prohibition = "The Employee shall not disclose any proprietary secrets."
        cand_bad = "The Employee must disclose proprietary secrets."
        cand_good = "The Employee must not share proprietary secrets."

        assert verify_preservation(orig_prohibition, cand_good) is True
        assert verify_preservation(orig_prohibition, cand_bad) is False

    def test_condition_preservation(self):
        orig_condition = "The agreement shall terminate unless payment is received."
        cand_good = "The agreement will end unless payment is made."
        cand_bad = "The agreement will end."

        assert verify_preservation(orig_condition, cand_good) is True
        assert verify_preservation(orig_condition, cand_bad) is False

    def test_trap_detection(self):
        # 1. Uncapped indemnity
        uncapped = (
            "The Vendor shall indemnify and hold harmless Customer from all claims."
        )
        traps_1 = detect_traps_and_nuances(uncapped)
        assert any(t["trap"] == "Uncapped Indemnification" for t in traps_1)

        # 2. Unilateral modification
        unilateral = "The Company reserves the right to modify these terms in its sole discretion without notice."
        traps_2 = detect_traps_and_nuances(unilateral)
        assert any(t["trap"] == "Unilateral Modification" for t in traps_2)

        # 3. Short cure window
        short_cure = (
            "Party must cure any default within five business days of written notice."
        )
        traps_3 = detect_traps_and_nuances(short_cure)
        assert any(
            t["trap"] == "Abnormally Short Notice / Cure Window" for t in traps_3
        )

        # 4. Court / collective remedy waiver
        waiver = "Each party hereby waives any right to a jury trial in any proceeding."
        traps_4 = detect_traps_and_nuances(waiver)
        assert any(
            t["trap"] == "Waiver of Standard Court / Collective Remedies"
            for t in traps_4
        )

    def test_simplification_modes_generation(self):
        text = LEGAL_TEST_CLAUSES[0][0]
        res = simplify_clause(text, category="INDEMNITY", affected_party="Tenant")

        assert len(res["simple_english"]) > 20
        assert len(res["detailed"]) > 50
        assert len(res["professional"]) > 50
        assert "Obligor / Bound Party" in res["professional"]
        assert "Covenant Type" in res["professional"]
        assert "Core Duty" in res["professional"]
        assert res["preservation_verified"] is True
        assert len(res["glossary_terms"]) >= 1

    def test_readability_improves_across_sample_clauses(self):
        """Flesch Reading Ease should improve on average across the 20 sample clauses."""
        improvements = []
        verified_count = 0

        for text, category, party in LEGAL_TEST_CLAUSES:
            res = simplify_clause(text, category=category, affected_party=party)
            orig_fre = res["readability_original"]["flesch_reading_ease"]
            simp_fre = res["readability_simple"]["flesch_reading_ease"]

            diff = simp_fre - orig_fre
            improvements.append(diff)

            if res["preservation_verified"]:
                verified_count += 1

        avg_improvement = sum(improvements) / len(improvements)
        positive_improvements = [d for d in improvements if d >= 0]

        # Assert hard gate thresholds:
        # 1. 100% of clauses pass the negation & condition preservation check
        assert verified_count == len(
            LEGAL_TEST_CLAUSES
        ), f"Preservation verified in {verified_count}/{len(LEGAL_TEST_CLAUSES)} clauses"
        # 2. Average readability improves by at least +10 points
        assert (
            avg_improvement >= 10.0
        ), f"Expected average FRE improvement >= 10.0, got {avg_improvement:.2f}"
        # 3. At least 80% of clauses show positive readability gain
        positive_rate = len(positive_improvements) / len(LEGAL_TEST_CLAUSES)
        assert (
            positive_rate >= 0.80
        ), f"Expected >= 80% clauses to improve readability, got {positive_rate * 100:.1f}%"


class TestStudioEndpoints:
    """Test Simplification Studio web view and REST APIs."""

    def test_studio_web_view_loads(self, client):
        resp = client.get("/studio")
        assert resp.status_code == 200
        html = resp.get_data(as_text=True)
        assert "Simplification Studio" in html
        assert "Sample clauses" in html
        assert "Glossary" in html

    def test_api_simplify_success(self, client):
        payload = {
            "text": "The Tenant shall indemnify and hold harmless the Landlord from all claims.",
            "mode": "simple_english",
            "category": "INDEMNITY",
            "affected_party": "Tenant",
        }
        resp = client.post("/api/simplify", json=payload)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["mode"] == "simple_english"
        assert "explanation" in data
        assert "simpleEnglish" in data
        assert "detailed" in data
        assert "professional" in data
        assert "readabilityOriginal" in data
        assert "readabilitySimple" in data
        assert "glossary" in data
        assert "traps" in data
        assert data["preservationVerified"] is True

    def test_api_simplify_empty_text_returns_400(self, client):
        resp = client.post("/api/simplify", json={"text": ""})
        assert resp.status_code == 400
        data = resp.get_json()
        assert "error" in data

    def test_api_glossary_returns_all_terms(self, client):
        resp = client.get("/api/glossary")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["count"] >= 150
        assert len(data["terms"]) >= 150
        first_term = data["terms"][0]
        assert "term" in first_term
        assert "plainReplacement" in first_term
        assert "definition" in first_term
        assert "category" in first_term
