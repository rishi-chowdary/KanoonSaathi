"""Tests for offline evaluation benchmarks across sample contracts."""

import json
from pathlib import Path

from evaluation.evaluate_nlp_stack import (
    benchmark_pipeline_latencies,
    evaluate_clauses_and_quotes,
    evaluate_document_chat,
    evaluate_key_info_defaults,
    evaluate_risks_and_guardrails,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class TestEvaluationSuiteParity:
    def test_clause_extraction_and_quote_offsets(self):
        gold_files = [
            "samples/gold/clean_nda_gold.json",
            "samples/gold/rental_agreement_gold.json",
            "samples/gold/employment_agreement_gold.json",
        ]
        metrics = evaluate_clauses_and_quotes(gold_files)

        assert (
            metrics["clause_recall"] >= 0.80
        ), f"Clause recall {metrics['clause_recall']*100:.1f}% below 80% target"
        assert (
            metrics["clause_precision"] >= 0.75
        ), f"Clause precision {metrics['clause_precision']*100:.1f}% below 75% target"
        assert (
            metrics["quote_verification_rate"] == 1.0
        ), f"Quote offset match rate {metrics['quote_verification_rate']*100:.1f}% must be 100%"
        assert metrics["true_positives"] > 0

    def test_risk_detection_and_non_advisory_phrasing(self):
        risk_contracts = [
            "one_sided_agreement.pdf",
            "rental_agreement.pdf",
            "clean_nda.pdf",
        ]
        metrics = evaluate_risks_and_guardrails(risk_contracts)

        assert (
            metrics["risk_recall"] >= 0.80
        ), f"Risk recall {metrics['risk_recall']*100:.1f}% below 80% target"
        assert (
            metrics["risk_precision"] >= 0.70
        ), f"Risk precision {metrics['risk_precision']*100:.1f}% below 70% target"
        assert (
            metrics["predatory_traps_detected"] == 3
        ), f"Predatory traps detected {metrics['predatory_traps_detected']}/3"
        assert (
            metrics["disallowed_legal_claim_count"] == 0
        ), f"Found {metrics['disallowed_legal_claim_count']} disallowed legal claims"

    def test_key_info_extraction_and_defaults(self):
        contracts = ["clean_nda.pdf", "rental_agreement.pdf", "one_sided_agreement.pdf"]
        metrics = evaluate_key_info_defaults(contracts)

        assert (
            metrics["key_info_accuracy"] >= 0.80
        ), f"Key info accuracy {metrics['key_info_accuracy']*100:.1f}% below 80% target"
        assert (
            metrics["invented_field_count"] == 0
        ), f"Found {metrics['invented_field_count']} invented values for missing fields"

    def test_document_chat_answers_and_refusals(self):
        metrics = evaluate_document_chat("evaluation/chat_questions.json")

        assert (
            metrics["answer_correctness_rate"] >= 0.80
        ), f"Chat answer correctness {metrics['answer_correctness_rate']*100:.1f}% below 80%"
        assert (
            metrics["citation_page_accuracy"] >= 0.80
        ), f"Citation page accuracy {metrics['citation_page_accuracy']*100:.1f}% below 80%"
        assert (
            metrics["honest_refusal_rate"] == 1.0
        ), f"Unanswerable refusal rate {metrics['honest_refusal_rate']*100:.1f}% must be 100%"

    def test_pipeline_latencies_under_budget(self):
        sample_contracts = ["clean_nda.pdf", "rental_agreement.pdf"]
        lat = benchmark_pipeline_latencies(sample_contracts)

        assert "total_pipeline" in lat
        assert lat["total_pipeline"] < 5.0

    def test_generated_results_markdown_and_json(self):
        json_path = (
            PROJECT_ROOT / "evaluation" / "results" / "nlp_stack_eval_results.json"
        )
        md_path = PROJECT_ROOT / "evaluation" / "RESULTS.md"

        assert json_path.exists(), "nlp_stack_eval_results.json missing"
        assert md_path.exists(), "RESULTS.md missing"

        with open(json_path, encoding="utf-8") as f:
            saved_results = json.load(f)

        assert "clauses" in saved_results
        assert "risks" in saved_results
        assert "chat" in saved_results
        assert "latency" in saved_results

        md_content = md_path.read_text(encoding="utf-8")
        assert "100.0%" in md_content
        assert "Source offset match" in md_content
        assert "Disallowed legal claims" in md_content
        assert "Unanswerable refusal" in md_content
