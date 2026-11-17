"""Tests for Phase M9: Offline Evaluation Suite & Parity Benchmarks.

Verifies:
1. Clause Recall >= 80% and Quote Verification Rate == 100%
2. Risk Detection Recall >= 80%, Predatory Traps == 3/3, and Rule 7 Violations == 0
3. Key Information Accuracy >= 80% and Rule 6 ('Not specified') Violations == 0
4. Extractive QA & Document Chat: Answer Accuracy >= 80%, Page Accuracy >= 80%, Honest Refusal == 100%
5. Offline Evaluation Runner executes cleanly and generates RESULTS.md
"""

import json
from pathlib import Path

from evaluation.evaluate_nlp_stack import (
    benchmark_pipeline_latencies,
    evaluate_clauses_and_quotes,
    evaluate_document_chat,
    evaluate_key_info_and_rule6,
    evaluate_risks_and_guardrails,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class TestEvaluationSuiteParity:
    """Validate core offline evaluation metrics against gold benchmarks."""

    def test_clause_extraction_and_quote_verification(self):
        gold_files = [
            "samples/gold/clean_nda_gold.json",
            "samples/gold/rental_agreement_gold.json",
            "samples/gold/employment_agreement_gold.json",
        ]
        res = evaluate_clauses_and_quotes(gold_files)

        assert (
            res["clause_recall"] >= 0.80
        ), f"Clause recall {res['clause_recall']*100:.1f}% below 80% target"
        assert (
            res["clause_precision"] >= 0.75
        ), f"Clause precision {res['clause_precision']*100:.1f}% below 75% target"
        assert (
            res["quote_verification_rate"] == 1.0
        ), f"Quote verification rate {res['quote_verification_rate']*100:.1f}% must be 100%"
        assert res["true_positives"] > 0

    def test_risk_detection_and_rule7_guardrails(self):
        risk_contracts = [
            "one_sided_agreement.pdf",
            "rental_agreement.pdf",
            "clean_nda.pdf",
        ]
        res = evaluate_risks_and_guardrails(risk_contracts)

        assert (
            res["risk_recall"] >= 0.80
        ), f"Risk recall {res['risk_recall']*100:.1f}% below 80% target"
        assert (
            res["risk_precision"] >= 0.70
        ), f"Risk precision {res['risk_precision']*100:.1f}% below 70% target"
        assert (
            res["predatory_traps_detected"] == 3
        ), f"Predatory traps detected {res['predatory_traps_detected']}/3"
        assert (
            res["rule7_violations"] == 0
        ), f"Found {res['rule7_violations']} Rule 7 forbidden phrase violations"

    def test_key_info_extraction_and_rule6(self):
        contracts = ["clean_nda.pdf", "rental_agreement.pdf", "one_sided_agreement.pdf"]
        res = evaluate_key_info_and_rule6(contracts)

        assert (
            res["key_info_accuracy"] >= 0.80
        ), f"Key info accuracy {res['key_info_accuracy']*100:.1f}% below 80% target"
        assert (
            res["rule6_violations"] == 0
        ), f"Found {res['rule6_violations']} Rule 6 violations (invented values)"

    def test_document_chat_grounding_and_honest_refusal(self):
        res = evaluate_document_chat("evaluation/chat_questions.json")

        assert (
            res["answer_correctness_rate"] >= 0.80
        ), f"Chat answer correctness {res['answer_correctness_rate']*100:.1f}% below 80%"
        assert (
            res["citation_page_accuracy"] >= 0.80
        ), f"Citation page accuracy {res['citation_page_accuracy']*100:.1f}% below 80%"
        assert (
            res["honest_refusal_rate"] == 1.0
        ), f"Honest refusal rate {res['honest_refusal_rate']*100:.1f}% must be 100%"

    def test_pipeline_latencies_sub_second(self):
        sample_contracts = ["clean_nda.pdf", "rental_agreement.pdf"]
        lat = benchmark_pipeline_latencies(sample_contracts)

        assert "total_pipeline" in lat
        # Local NLP pipeline must run under 5 seconds per contract (vs 12.4s in Gemini API)
        assert lat["total_pipeline"] < 5.0

    def test_generated_results_markdown_and_json(self):
        json_path = (
            PROJECT_ROOT / "evaluation" / "results" / "nlp_stack_eval_results.json"
        )
        md_path = PROJECT_ROOT / "evaluation" / "RESULTS.md"

        assert json_path.exists(), "nlp_stack_eval_results.json missing"
        assert md_path.exists(), "RESULTS.md missing"

        with open(json_path, encoding="utf-8") as f:
            data = json.load(f)

        assert "clauses" in data
        assert "risks" in data
        assert "chat" in data
        assert "latency" in data

        md_content = md_path.read_text(encoding="utf-8")
        assert "100.0%" in md_content
        assert "Quote Verification Rate" in md_content
        assert "Rule 7 Forbidden Phrase Count" in md_content
        assert "Honest Refusal" in md_content
