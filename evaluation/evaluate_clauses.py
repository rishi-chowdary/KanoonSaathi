import difflib
import json
import os
import re
import sys
import time
from pathlib import Path
import requests

BASE_URL = "http://127.0.0.1:8080/api"

def normalize(text: str) -> str:
    if not text:
        return ""
    return re.sub(r"\s+", " ", text.lower()).strip()

def match_clause(gold: dict, extracted: dict) -> bool:
    """Determine if an extracted clause matches a gold reference clause."""
    gold_cat = normalize(gold.get("category", ""))
    alt_cats = [normalize(c) for c in gold.get("alternate_categories", [])]
    ext_cat = normalize(extracted.get("category", ""))
    if extracted.get("customLabel"):
        ext_cat_custom = normalize(extracted.get("customLabel"))
    else:
        ext_cat_custom = ""

    category_match = (
        gold_cat == ext_cat
        or ext_cat in alt_cats
        or (ext_cat == "other" and ext_cat_custom == gold_cat)
    )

    gold_sec = normalize(str(gold.get("section_reference", "")))
    ext_sec = normalize(str(extracted.get("sectionReference", "")))
    section_match = bool(gold_sec and ext_sec and (gold_sec in ext_sec or ext_sec in gold_sec))

    # Text / Quote overlap
    gold_quote = normalize(gold.get("key_quote", ""))
    ext_quote = normalize(extracted.get("evidenceQuote", ""))
    ext_orig = normalize(extracted.get("originalText", ""))

    quote_match = False
    if gold_quote:
        if gold_quote in ext_quote or gold_quote in ext_orig:
            quote_match = True
        elif ext_quote and len(ext_quote) > 15:
            ratio = difflib.SequenceMatcher(None, gold_quote, ext_quote).ratio()
            if ratio >= 0.65:
                quote_match = True

    # Title match
    gold_title = normalize(gold.get("title", ""))
    ext_title = normalize(extracted.get("title", ""))
    title_match = False
    if gold_title and ext_title:
        if gold_title in ext_title or ext_title in gold_title:
            title_match = True
        elif difflib.SequenceMatcher(None, gold_title, ext_title).ratio() >= 0.70:
            title_match = True

    # Match rules:
    # 1. Section match + (Category OR Quote OR Title)
    if section_match and (category_match or quote_match or title_match):
        return True
    # 2. Quote match + (Category OR Title)
    if quote_match and (category_match or title_match):
        return True
    # 3. Category match + Title match
    if category_match and title_match:
        return True

    return False

def main():
    print("=" * 80)
    print("LEXILEGAL AI — PHASE 5 CLAUSE EXTRACTION BENCHMARK & EVALUATION")
    print("=" * 80)

    # 1. Register test user
    ts = int(time.time())
    email = f"eval_runner_{ts}@lexilegal.test"
    password = "Password123!"
    print(f"\n[1] Registering evaluation user: {email}...")
    reg_resp = requests.post(
        f"{BASE_URL}/auth/register",
        json={"email": email, "password": password, "fullName": "Evaluation Runner"}
    )
    if reg_resp.status_code != 201:
        print(f"Error registering user: {reg_resp.text}")
        sys.exit(1)
    token = reg_resp.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("  Authenticated successfully.")

    test_cases = [
        {
            "name": "clean_nda.pdf",
            "file_path": "samples/contracts/clean_nda.pdf",
            "gold_path": "samples/gold/clean_nda_gold.json",
            "mime": "application/pdf",
        },
        {
            "name": "rental_agreement.pdf",
            "file_path": "samples/contracts/rental_agreement.pdf",
            "gold_path": "samples/gold/rental_agreement_gold.json",
            "mime": "application/pdf",
        },
        {
            "name": "employment_agreement.pdf",
            "file_path": "samples/contracts/employment_agreement.pdf",
            "gold_path": "samples/gold/employment_agreement_gold.json",
            "mime": "application/pdf",
        },
    ]

    all_results = []
    total_tp = 0
    total_fp = 0
    total_fn = 0
    total_extracted_clauses = 0
    total_verified_quotes = 0

    for tc in test_cases:
        print("\n" + "-" * 80)
        print(f"Evaluating Contract: {tc['name']}")
        print("-" * 80)

        # Load gold standard
        with open(tc["gold_path"], "r") as f:
            gold_data = json.load(f)
        gold_clauses = gold_data.get("gold_clauses", [])

        # Upload
        print(f"  Uploading {tc['file_path']}...")
        with open(tc["file_path"], "rb") as f:
            up_resp = requests.post(
                f"{BASE_URL}/documents/upload",
                headers=headers,
                files={"file": (tc["name"], f, tc["mime"])},
            )
        if up_resp.status_code != 202:
            print(f"  Upload failed: {up_resp.text}")
            continue

        doc_id = up_resp.json()["id"]

        # Poll status
        print(f"  Waiting for pipeline (Document ID: {doc_id})...")
        status = "UPLOADED"
        for attempt in range(200):
            time.sleep(3)
            stat_resp = requests.get(f"{BASE_URL}/documents/{doc_id}/status", headers=headers)
            if stat_resp.status_code == 200:
                status = stat_resp.json().get("status")
                if status == "COMPLETED":
                    print(f"  Document completed on attempt {attempt + 1}.")
                    break
                if status == "FAILED":
                    print(f"  Pipeline failed: {stat_resp.json().get('failureReason')}")
                    break

        if status != "COMPLETED":
            print(f"  Skipping {tc['name']} (status={status}).")
            continue

        # Fetch extracted clauses
        c_resp = requests.get(f"{BASE_URL}/documents/{doc_id}/clauses?size=50", headers=headers)
        if c_resp.status_code != 200:
            print(f"  Failed to fetch clauses: {c_resp.text}")
            continue

        extracted_clauses = c_resp.json().get("content", [])
        n_extracted = len(extracted_clauses)
        n_gold = len(gold_clauses)

        # Match gold against extracted
        matched_gold_ids = set()
        matched_ext_ids = set()

        for g in gold_clauses:
            for ext in extracted_clauses:
                if ext.get("id") in matched_ext_ids:
                    continue
                if match_clause(g, ext):
                    matched_gold_ids.add(g.get("id"))
                    matched_ext_ids.add(ext.get("id"))
                    break

        tp = len(matched_gold_ids)
        fn = n_gold - tp
        fp = n_extracted - len(matched_ext_ids)

        precision = (tp / n_extracted) if n_extracted > 0 else 0.0
        recall = (tp / n_gold) if n_gold > 0 else 0.0
        f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

        verified_quotes = sum(1 for c in extracted_clauses if c.get("quoteVerified"))
        verified_rate = (verified_quotes / n_extracted * 100.0) if n_extracted > 0 else 0.0

        total_tp += tp
        total_fp += fp
        total_fn += fn
        total_extracted_clauses += n_extracted
        total_verified_quotes += verified_quotes

        result = {
            "contract": tc["name"],
            "contract_type": gold_data.get("contract_type"),
            "gold_count": n_gold,
            "extracted_count": n_extracted,
            "true_positives": tp,
            "false_positives": fp,
            "false_negatives": fn,
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1, 4),
            "verified_quotes": verified_quotes,
            "verified_quote_rate": round(verified_rate, 2),
            "extracted_items": extracted_clauses,
        }
        all_results.append(result)

        print(f"  Gold Clauses: {n_gold} | Extracted: {n_extracted} | Matched (TP): {tp}")
        print(f"  Precision: {precision * 100:.1f}% | Recall: {recall * 100:.1f}% | F1: {f1:.3f}")
        print(f"  Verified Quote Rate: {verified_rate:.1f}% ({verified_quotes}/{n_extracted})")
        time.sleep(5)

    # Aggregate metrics
    overall_precision = (total_tp / (total_tp + total_fp)) if (total_tp + total_fp) > 0 else 0.0
    overall_recall = (total_tp / (total_tp + total_fn)) if (total_tp + total_fn) > 0 else 0.0
    overall_f1 = (
        (2 * overall_precision * overall_recall / (overall_precision + overall_recall))
        if (overall_precision + overall_recall) > 0
        else 0.0
    )
    overall_verified_rate = (
        (total_verified_quotes / total_extracted_clauses * 100.0)
        if total_extracted_clauses > 0
        else 0.0
    )

    print("\n" + "=" * 80)
    print("PHASE 5 CLAUSE EXTRACTION BENCHMARK SUMMARY")
    print("=" * 80)
    print(f"{'CONTRACT':<26} | {'GOLD':<5} | {'EXTR':<5} | {'PRECISION':<10} | {'RECALL':<8} | {'F1':<6} | {'VERIFIED'}")
    print("-" * 80)
    for r in all_results:
        print(
            f"{r['contract']:<26} | "
            f"{r['gold_count']:<5} | "
            f"{r['extracted_count']:<5} | "
            f"{r['precision'] * 100:>8.1f}% | "
            f"{r['recall'] * 100:>6.1f}% | "
            f"{r['f1_score']:>6.3f} | "
            f"{r['verified_quote_rate']:>6.1f}%"
        )
    print("-" * 80)
    print(
        f"{'OVERALL AGGREGATE':<26} | "
        f"{sum(r['gold_count'] for r in all_results):<5} | "
        f"{total_extracted_clauses:<5} | "
        f"{overall_precision * 100:>8.1f}% | "
        f"{overall_recall * 100:>6.1f}% | "
        f"{overall_f1:>6.3f} | "
        f"{overall_verified_rate:>6.1f}%"
    )
    print("=" * 80)

    # Save output to evaluation/results/
    out_path = Path("evaluation/results/clause_evaluation_results.json")
    summary_data = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "overall_precision": round(overall_precision, 4),
        "overall_recall": round(overall_recall, 4),
        "overall_f1_score": round(overall_f1, 4),
        "overall_verified_quote_rate": round(overall_verified_rate, 2),
        "results": all_results,
    }
    with open(out_path, "w") as f:
        json.dump(summary_data, f, indent=2)
    print(f"\nSaved full evaluation metrics to {out_path.resolve()}")

if __name__ == "__main__":
    main()

