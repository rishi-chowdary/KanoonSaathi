"""Phase M5 Tests: Tri-Tier Rule-Based Simplification, Readability, and Trap Detection.

Verifies:
1. Readability formulas (Flesch Reading Ease and Flesch-Kincaid Grade Level)
2. Readability improvement across 20+ diverse legal clauses
3. Tri-tier generation (Simple English, Detailed, Professional)
4. Negation and condition preservation invariant (Rule 6 / Hard Gate)
5. 150+ legal terms glossary loading and extraction
6. Contract subtle trap detection (uncapped indemnity, short cure windows, unilateral changes, etc.)
7. REST API (POST /api/simplify, GET /api/glossary) and Web View (GET /studio)
"""

from app.nlp.readability import (
    calculate_readability,
    count_syllables_text,
    count_syllables_word,
)
from app.nlp.simplifier import (
    detect_traps_and_nuances,
    extract_clause_glossary,
    get_glossary,
    get_sorted_glossary_terms,
    lexical_simplify,
    simplify_clause,
    verify_preservation,
)

# 20 diverse legal clauses spanning 8 standard contract categories
LEGAL_TEST_CLAUSES = [
    # 1. Indemnity
    (
        "The Tenant shall indemnify, defend, and hold harmless the Landlord from and against any and all claims, liabilities, damages, losses, costs, and expenses (including reasonable attorneys' fees) resulting from the Tenant's use, occupancy, or conduct on the Leased Premises, or from any breach by the Tenant in the performance of any agreement herein, provided that the Landlord gives prompt written notice of such claim within thirty (30) days.",
        "INDEMNITY",
        "Tenant",
    ),
    # 2. Confidentiality
    (
        "The Receiving Party agrees that it shall not disclose, reproduce, summarize, or distribute any Confidential Information to any third party without the express prior written consent of the Disclosing Party, and shall use such information solely for the Purpose.",
        "CONFIDENTIALITY",
        "Receiving Party",
    ),
    # 3. Non-Compete
    (
        "During the Employment Term and for a period of one (1) year following termination of employment, the Employee shall not, directly or indirectly, engage in, perform services for, or contribute knowledge to any business that competes with the Company within the territory.",
        "NON_COMPETE",
        "Employee",
    ),
    # 4. Termination
    (
        "Either party may terminate this Agreement immediately upon written notice to the other party in the event that the other party breaches any material term or condition of this Agreement and fails to cure such breach within thirty (30) calendar days after receipt of written notice specifying the default.",
        "TERMINATION",
        "Either party",
    ),
    # 5. Governing Law
    (
        "This Agreement and any dispute arising out of or related to this Agreement shall be governed by, and construed in accordance with, the laws of the State of Delaware, without giving effect to any principles of conflicts of law.",
        "GOVERNING_LAW",
        "Both parties",
    ),
    # 6. Severability
    (
        "In the event that any provision of this Agreement is determined by a court of competent jurisdiction to be illegal, invalid, or otherwise unenforceable, such provision shall be deemed severed and deleted, and the remaining provisions of this Agreement shall continue in full force and effect.",
        "SEVERABILITY",
        "Both parties",
    ),
    # 7. Payment Terms
    (
        "Client shall pay all invoiced amounts due to Vendor within thirty (30) days of the date of Vendor's invoice. Unpaid amounts shall accrue interest at the rate of 1.5% per month or the highest legal rate.",
        "PAYMENT",
        "Client",
    ),
    # 8. Limitation of Liability
    (
        "In no event shall either party be liable to the other for any indirect, incidental, consequential, special, or punitive damages arising out of or in connection with this Agreement, even if advised of the possibility of such damages.",
        "LIABILITY",
        "Both parties",
    ),
    # 9. Force Majeure
    (
        "Neither party shall be liable for any failure or delay in the performance of its obligations hereunder by reason of acts of God, flood, fire, war, terrorism, or other events beyond its reasonable control.",
        "FORCE_MAJEURE",
        "Neither party",
    ),
    # 10. Non-Solicitation
    (
        "For a period of two (2) years following the Effective Date, the Consultant covenants and agrees not to solicit, entice, or induce any employee, contractor, or customer of the Company to terminate their relationship with the Company.",
        "NON_SOLICITATION",
        "Consultant",
    ),
    # 11. Intellectual Property
    (
        "All inventions, improvements, software, designs, and patentable works conceived or developed by Employee during employment shall be deemed work made for hire and shall belong exclusively to the Company.",
        "INTELLECTUAL_PROPERTY",
        "Employee",
    ),
    # 12. Entire Agreement
    (
        "This Agreement constitutes the entire and sole agreement between the parties with respect to the subject matter hereof and supersedes all prior agreements, representations, and understandings, whether written or oral.",
        "ENTIRE_AGREEMENT",
        "Both parties",
    ),
    # 13. Notice Requirements
    (
        "All notices, requests, consents, and other communications hereunder shall be in writing and shall be deemed to have been duly given when delivered by hand or sent by certified mail, postage prepaid, return receipt requested.",
        "NOTICES",
        "Both parties",
    ),
    # 14. Survival
    (
        "The provisions of Sections 4 (Confidentiality), 6 (Indemnification), and 8 (Limitation of Liability) shall survive the termination or expiration of this Agreement for any reason.",
        "SURVIVAL",
        "Both parties",
    ),
    # 15. Waiver
    (
        "No waiver of any breach or default of any term, condition, or covenant of this Agreement shall be deemed to constitute a waiver of any other subsequent breach or default.",
        "WAIVER",
        "Both parties",
    ),
    # 16. Cumulative Remedies
    (
        "All rights and remedies provided in this Agreement are cumulative and not exclusive of any other rights or remedies that may be available to the parties at law or in equity.",
        "REMEDIES",
        "Both parties",
    ),
    # 17. Assignment
    (
        "Neither party may assign or transfer any of its rights or delegate any of its duties under this Agreement without the prior written consent of the other party, which consent shall not be unreasonably withheld.",
        "ASSIGNMENT",
        "Neither party",
    ),
    # 18. Amendments
    (
        "No supplement, modification, amendment, or alteration of this Agreement shall be binding unless executed in writing by authorized representatives of both parties.",
        "AMENDMENT",
        "Both parties",
    ),
    # 19. Dispute Resolution / Arbitration
    (
        "Any dispute, controversy, or claim arising out of or relating to this contract, or the breach thereof, shall be settled by binding arbitration in accordance with the Commercial Arbitration Rules of the American Arbitration Association.",
        "DISPUTE_RESOLUTION",
        "Both parties",
    ),
    # 20. Warranty Disclaimer
    (
        "Except as expressly set forth herein, the Provider disclaims all warranties, express or implied, including the implied warranties of merchantability and fitness for a particular purpose.",
        "WARRANTY",
        "Provider",
    ),
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
    """Test tri-tier simplification, preservation checks, and glossary integration."""

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

    def test_negation_preservation_invariant(self):
        """Rule 6 invariant: negations must never be stripped or inverted."""
        orig_prohibition = "The Employee shall not disclose any proprietary secrets."
        cand_bad = "The Employee must disclose proprietary secrets."
        cand_good = "The Employee must not share proprietary secrets."

        assert verify_preservation(orig_prohibition, cand_good) is True
        assert verify_preservation(orig_prohibition, cand_bad) is False

    def test_condition_preservation_invariant(self):
        """Rule 6 invariant: conditions must be maintained."""
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

        # 4. Jury trial waiver
        jury = "Each party hereby waives any right to a jury trial in any proceeding."
        traps_4 = detect_traps_and_nuances(jury)
        assert any(t["trap"] == "Waiver of Jury Trial / Class Action" for t in traps_4)

    def test_tri_tier_modes_generation(self):
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

    def test_readability_improvement_gate_across_20_clauses(self):
        """Hard Gate: On average, Flesch Reading Ease score must improve across 20 legal clauses."""
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
        assert "Load Pre-loaded Sample Clauses" in html
        assert "Glossary Directory" in html

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
