#!/usr/bin/env python3
"""Capture and diff full NLP pipeline outputs across sample contracts.

Usage:
  python scripts/snapshot.py --out evaluation/snapshots/before
  python scripts/snapshot.py --diff evaluation/snapshots/before evaluation/snapshots/after
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

SKIP_FILES = {
    "corrupted_contract.pdf",
    "empty_contract.pdf",
    "malicious_renamed.exe.pdf",
}

VOLATILE_KEYS = {
    "timestamp",
    "latency",
    "latency_ms",
    "latency_sec",
    "avg_latency_sec",
    "total_latency_sec",
    "stage_latencies",
    "duration_sec",
    "extraction_ms",
    "classification_ms",
    "summarization_ms",
    "risk_ms",
    "total_ms",
}


def _fact_to_dict(fact: Any) -> dict[str, Any]:
    return {
        "value": fact.value,
        "source_page": fact.source_page,
        "evidence_quote": fact.evidence_quote,
    }


def _run_contract_pipeline(
    contract_path: Path,
) -> tuple[dict[str, Any], Any, list[Any]]:
    from app.nlp.clause_classifier import classify_clause
    from app.nlp.document_classifier import classify_document_type
    from app.nlp.evidence import extract_evidence_quote
    from app.nlp.extraction import extract_document
    from app.nlp.importance import calculate_clause_importance
    from app.nlp.key_info import extract_contract_key_info
    from app.nlp.missing_provisions import detect_missing_provisions
    from app.nlp.parties import detect_affected_party, extract_document_parties
    from app.nlp.risk_engine import detect_clause_risks
    from app.nlp.segmentation import create_chunks, segment_clauses
    from app.nlp.simplification import simplify_clause
    from app.nlp.summarizer import generate_extractive_summary

    ext = extract_document(contract_path.read_bytes(), contract_path.name)
    segmented = segment_clauses(ext.full_text, ext.pages, ext.sections)
    chunks = create_chunks(ext.pages, ext.sections)

    doc_type, type_conf = classify_document_type(ext.full_text, contract_path.name)
    parties = extract_document_parties(ext.full_text[:1500])

    clauses_out: list[dict[str, Any]] = []
    clause_objs: list[SimpleNamespace] = []

    for seg in segmented:
        category, custom_label, confidence, method = classify_clause(
            title=seg.title,
            original_text=seg.original_text,
            section_reference=seg.section_reference,
        )
        importance = calculate_clause_importance(
            category=category,
            original_text=seg.original_text,
            title=seg.title,
        )
        affected_party = detect_affected_party(
            original_text=seg.original_text,
            document_parties=parties,
            category=category,
        )
        evidence_quote, quote_verified = extract_evidence_quote(
            original_text=seg.original_text,
            category=category,
            title=seg.title,
        )
        simp = simplify_clause(
            original_text=seg.original_text,
            category=category,
            affected_party=affected_party,
        )

        clause_dict = {
            "clause_index": seg.clause_index,
            "title": seg.title,
            "section_reference": seg.section_reference,
            "source_page": seg.source_page,
            "start_offset": seg.start_offset,
            "end_offset": seg.end_offset,
            "original_text": seg.original_text,
            "category": category,
            "custom_label": custom_label,
            "confidence": round(float(confidence), 4),
            "classification_method": method,
            "importance": importance,
            "affected_party": affected_party,
            "evidence_quote": evidence_quote,
            "quote_verified": quote_verified,
            "simplifications": {
                "simple": simp["simple_english"],
                "detailed": simp["detailed"],
                "professional": simp["professional"],
            },
        }
        clauses_out.append(clause_dict)
        clause_objs.append(
            SimpleNamespace(
                title=seg.title,
                category=category,
                original_text=seg.original_text,
                source_page=seg.source_page,
                section_reference=seg.section_reference,
            )
        )

    governing_law_stated = any(
        c.category == "GOVERNING_LAW" or "governing law" in c.title.lower()
        for c in clause_objs
    )
    risks = detect_clause_risks(
        clauses=clause_objs,
        full_text=ext.full_text,
        governing_law_stated=governing_law_stated,
    )
    missing = detect_missing_provisions(
        clauses=clause_objs,
        document_type=doc_type or "",
        full_text=ext.full_text,
    )
    key_info = extract_contract_key_info(ext.full_text, ext.pages)
    summary = generate_extractive_summary(
        full_text=ext.full_text,
        pages=ext.pages,
        document_type=doc_type or "General Contract",
        parties=parties,
    )

    key_info_dict = {
        "contract_amount": _fact_to_dict(key_info.contract_amount),
        "payment_deadlines": _fact_to_dict(key_info.payment_deadlines),
        "penalties": _fact_to_dict(key_info.penalties),
        "start_date": _fact_to_dict(key_info.start_date),
        "end_date": _fact_to_dict(key_info.end_date),
        "renewal_date": _fact_to_dict(key_info.renewal_date),
        "notice_period": _fact_to_dict(key_info.notice_period),
        "termination_conditions": _fact_to_dict(key_info.termination_conditions),
        "important_dates": key_info.important_dates,
    }

    summary_dict = {
        "purpose": summary.purpose,
        "summary_short": summary.summary_short,
        "summary_detailed": summary.summary_detailed,
        "main_conditions": summary.main_conditions,
        "obligations_summary": summary.obligations_summary,
        "financial_terms_summary": summary.financial_terms_summary,
    }

    analysis_stub = SimpleNamespace(
        document_type=doc_type,
        parties=parties,
        summary_short=summary.summary_short,
        extracted_information=SimpleNamespace(
            contract_amount=key_info.contract_amount.value,
            contract_amount_page=key_info.contract_amount.source_page,
            payment_deadlines=key_info.payment_deadlines.value,
            payment_deadlines_page=key_info.payment_deadlines.source_page,
            penalties=key_info.penalties.value,
            penalties_page=key_info.penalties.source_page,
            start_date=key_info.start_date.value,
            start_date_page=key_info.start_date.source_page,
            end_date=key_info.end_date.value,
            end_date_page=key_info.end_date.source_page,
            renewal_date=key_info.renewal_date.value,
            renewal_date_page=key_info.renewal_date.source_page,
            notice_period=key_info.notice_period.value,
            notice_period_page=key_info.notice_period.source_page,
            termination_conditions=key_info.termination_conditions.value,
            termination_conditions_page=key_info.termination_conditions.source_page,
        ),
        clauses=clause_objs,
        risks=[],
    )

    chunk_objs = [
        SimpleNamespace(
            chunk_index=ch.chunk_index,
            page_number=ch.page_number,
            content=ch.content,
            token_count=ch.token_count,
        )
        for ch in chunks
    ]

    snapshot_data = {
        "filename": contract_path.name,
        "page_count": ext.page_count,
        "is_scanned": ext.is_scanned,
        "document_type": doc_type,
        "type_confidence": round(float(type_conf), 4),
        "parties": parties,
        "clauses": clauses_out,
        "risks": risks,
        "missing_provisions": missing,
        "key_info": key_info_dict,
        "summary": summary_dict,
    }
    return snapshot_data, analysis_stub, chunk_objs


def capture_snapshot(out_dir: Path) -> None:
    from app.nlp.qa_engine import answer_document_query
    from evaluation.evaluate_nlp_stack import (
        benchmark_pipeline_latencies,
        evaluate_clauses_and_quotes,
        evaluate_document_chat,
        evaluate_key_info_defaults,
        evaluate_risks_and_guardrails,
    )

    out_dir.mkdir(parents=True, exist_ok=True)
    contracts_dir = ROOT_DIR / "samples" / "contracts"
    contract_cache: dict[str, tuple[Any, list[Any]]] = {}

    for contract_path in sorted(contracts_dir.iterdir()):
        if not contract_path.is_file() or contract_path.name in SKIP_FILES:
            continue
        print(f"Snapshotting {contract_path.name}...")
        data, analysis_stub, chunk_objs = _run_contract_pipeline(contract_path)
        contract_cache[f"samples/contracts/{contract_path.name}"] = (
            analysis_stub,
            chunk_objs,
        )
        out_file = out_dir / f"{contract_path.stem}.json"
        out_file.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")

    # Chat Q&A snapshot
    chat_questions = json.loads(
        (ROOT_DIR / "evaluation" / "chat_questions.json").read_text()
    )
    chat_answers: list[dict[str, Any]] = []
    for q in chat_questions:
        rel_path = q["contract_file"]
        if rel_path not in contract_cache:
            full_path = ROOT_DIR / rel_path
            _, analysis_stub, chunk_objs = _run_contract_pipeline(full_path)
            contract_cache[rel_path] = (analysis_stub, chunk_objs)
        analysis_stub, chunk_objs = contract_cache[rel_path]
        resp = answer_document_query(q["question"], analysis_stub, chunk_objs)
        chat_answers.append(
            {
                "id": q["id"],
                "contract_file": rel_path,
                "question": q["question"],
                "answer": resp.get("answer"),
                "addressedInDocument": resp.get("addressedInDocument"),
                "citations": resp.get("citations", []),
                "confidence": round(float(resp.get("confidence", 0.0)), 4),
            }
        )
    (out_dir / "chat_answers.json").write_text(
        json.dumps(chat_answers, indent=2, ensure_ascii=False) + "\n"
    )

    # Evaluation metrics snapshot
    print("Running evaluation suite...")
    gold_files = [
        "samples/gold/clean_nda_gold.json",
        "samples/gold/rental_agreement_gold.json",
        "samples/gold/employment_agreement_gold.json",
    ]
    risk_contracts = [
        "one_sided_agreement.pdf",
        "rental_agreement.pdf",
        "clean_nda.pdf",
    ]
    sample_contracts = [
        "clean_nda.pdf",
        "rental_agreement.pdf",
        "one_sided_agreement.pdf",
        "employment_agreement.pdf",
    ]
    eval_summary = {
        "clauses": evaluate_clauses_and_quotes(gold_files),
        "risks": evaluate_risks_and_guardrails(risk_contracts),
        "key_info": evaluate_key_info_defaults(risk_contracts),
        "chat": evaluate_document_chat("evaluation/chat_questions.json"),
        "latency": benchmark_pipeline_latencies(sample_contracts),
    }
    (out_dir / "eval_results.json").write_text(
        json.dumps(eval_summary, indent=2, ensure_ascii=False) + "\n"
    )
    print(f"Snapshot saved to {out_dir}")


def _diff_values(a: Any, b: Any, path: str, diffs: list[str]) -> None:
    if isinstance(a, dict) and isinstance(b, dict):
        all_keys = sorted(set(a.keys()) | set(b.keys()))
        for k in all_keys:
            if k in VOLATILE_KEYS:
                continue
            sub_path = f"{path}.{k}" if path else k
            if k not in a:
                diffs.append(f"+ {sub_path}: {b[k]!r}")
            elif k not in b:
                diffs.append(f"- {sub_path}: {a[k]!r}")
            else:
                _diff_values(a[k], b[k], sub_path, diffs)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            diffs.append(f"~ {path}: list length {len(a)} -> {len(b)}")
        for idx, (va, vb) in enumerate(zip(a, b)):
            _diff_values(va, vb, f"{path}[{idx}]", diffs)
    elif isinstance(a, float) and isinstance(b, float):
        if abs(a - b) > 1e-3:
            diffs.append(f"~ {path}: {a} -> {b}")
    else:
        if a != b:
            diffs.append(f"~ {path}: {a!r} -> {b!r}")


def diff_snapshots(before_dir: Path, after_dir: Path) -> int:
    before_files = {p.name for p in before_dir.glob("*.json")}
    after_files = {p.name for p in after_dir.glob("*.json")}
    all_files = sorted(before_files | after_files)

    total_diffs = 0
    for fname in all_files:
        if fname not in before_files:
            print(f"[ADDED FILE] {fname}")
            total_diffs += 1
            continue
        if fname not in after_files:
            print(f"[REMOVED FILE] {fname}")
            total_diffs += 1
            continue

        a = json.loads((before_dir / fname).read_text())
        b = json.loads((after_dir / fname).read_text())
        diffs: list[str] = []
        _diff_values(a, b, "", diffs)
        if diffs:
            print(f"[DIFF] {fname} ({len(diffs)} differences):")
            for line in diffs[:30]:
                print(f"  {line}")
            if len(diffs) > 30:
                print(f"  ... and {len(diffs) - 30} more")
            total_diffs += len(diffs)

    if total_diffs == 0:
        print("OK: snapshots match identically (ignoring volatile timing fields).")
        return 0
    print(f"TOTAL DIFFERENCES: {total_diffs}")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture or diff NLP snapshots.")
    parser.add_argument("--out", type=Path, help="Output directory for snapshot")
    parser.add_argument(
        "--diff",
        nargs=2,
        type=Path,
        metavar=("BEFORE", "AFTER"),
        help="Diff two snapshot directories",
    )
    args = parser.parse_args()

    if args.out:
        capture_snapshot(args.out)
        return 0
    if args.diff:
        return diff_snapshots(args.diff[0], args.diff[1])

    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
