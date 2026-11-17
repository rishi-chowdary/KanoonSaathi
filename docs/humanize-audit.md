# Humanize Audit (Phase H0)

Branch: `humanize` (branched from `nlp-stack`).
Baseline behavior snapshot: `evaluation/snapshots/before/` (8 valid sample contracts, 15 chat Q&A answers, and full offline evaluation metrics).
Baseline UI screenshots: 114 PNGs captured across 19 pages/tabs at 1440px, 768px, and 390px in light and dark mode.

## 1. Python File Metrics

Scanned 65 Python files: 12532 lines total, 542 comment lines (4.3%), 68 functions over 40 lines, 20 try/except blocks, 231 docstrings.

| File | Lines | Comment % | Funcs >40 | Longest Func (lines) | Classes | Try/Except | Docstrings | Generic Names |
|---|---:|---:|---:|---|---:|---:|---:|---|
| `app/nlp/simplifier.py` | 901 | 4.7% | 5 | `detect_traps_and_nuances` (117) | 0 | 0 | 12 | `data`, `result` |
| `app/services/report_service.py` | 865 | 5.9% | 2 | `generate_pdf_report` (700) | 1 | 1 | 4 | - |
| `evaluation/evaluate_nlp_stack.py` | 646 | 1.9% | 7 | `write_results_markdown` (115) | 1 | 0 | 8 | `item` |
| `app/nlp/qa_engine.py` | 631 | 1.7% | 3 | `match_fact_intent` (339) | 0 | 0 | 5 | `obj` |
| `app/blueprints/documents.py` | 628 | 2.2% | 2 | `detail` (63) | 0 | 2 | 17 | `data` |
| `tests/test_qa.py` | 459 | 9.4% | 3 | `test_chat_api_endpoints_and_tenant_isolation` (107) | 1 | 0 | 2 | `data` |
| `app/nlp/key_info.py` | 372 | 8.9% | 1 | `extract_contract_key_info` (293) | 2 | 1 | 2 | `result` |
| `scripts/snapshot.py` | 371 | 0.8% | 2 | `_run_contract_pipeline` (177) | 0 | 0 | 1 | `data` |
| `tests/test_dashboard_and_report.py` | 366 | 6.3% | 4 | `test_seed_two_users_dashboard_numbers_no_leak` (102) | 0 | 0 | 6 | - |
| `tests/test_simplifier.py` | 351 | 8.3% | 0 | `test_readability_improvement_gate_across_20_clauses` (33) | 3 | 0 | 7 | `data`, `item` |
| `tests/test_clause_classification.py` | 329 | 4.0% | 3 | `test_gate_clause_recall_and_precision_on_gold_contracts` (64) | 0 | 0 | 10 | `data` |
| `tests/test_risk.py` | 311 | 5.1% | 3 | `test_full_pipeline_persistence_and_endpoints` (51) | 5 | 0 | 6 | `item` |
| `app/nlp/extraction.py` | 296 | 1.7% | 2 | `extract_pdf` (57) | 3 | 6 | 10 | - |
| `evaluation/evaluate_clauses.py` | 285 | 4.9% | 2 | `main` (208) | 0 | 0 | 1 | `result` |
| `app/nlp/retrieval.py` | 274 | 4.0% | 2 | `hybrid_retrieve_chunks` (68) | 0 | 0 | 4 | `item` |
| `app/nlp/segmentation.py` | 274 | 5.1% | 2 | `segment_clauses` (113) | 2 | 0 | 7 | - |
| `app/nlp/clause_classifier.py` | 268 | 5.2% | 1 | `classify_clause` (97) | 0 | 0 | 4 | `data` |
| `app/nlp/summarizer.py` | 261 | 5.7% | 1 | `generate_extractive_summary` (229) | 1 | 0 | 1 | - |
| `tests/test_auth.py` | 220 | 4.5% | 1 | `test_api_register_and_login_flow` (43) | 0 | 0 | 11 | - |
| `app/blueprints/auth.py` | 219 | 1.8% | 0 | `register` (30) | 0 | 0 | 5 | `data` |
| `app/nlp/missing_provisions.py` | 211 | 3.8% | 2 | `detect_missing_provisions` (80) | 0 | 0 | 5 | `data` |
| `tests/test_entities_and_summary.py` | 207 | 4.8% | 1 | `test_api_key_info_and_summary_endpoints` (43) | 0 | 0 | 6 | `info`, `item` |
| `tests/test_database.py` | 200 | 6.0% | 1 | `test_complete_entity_graph_persistence_and_cascade` (188) | 0 | 0 | 1 | `info` |
| `app/nlp/risk_engine.py` | 192 | 3.1% | 1 | `detect_clause_risks` (98) | 0 | 0 | 6 | `data` |
| `app/blueprints/studio.py` | 179 | 1.1% | 1 | `api_simplify` (65) | 0 | 0 | 4 | `data`, `result` |
| `tests/test_ingestion_api.py` | 171 | 8.8% | 1 | `test_document_ownership_isolation` (41) | 0 | 0 | 5 | `data` |
| `app/services/document_service.py` | 163 | 6.7% | 1 | `save_and_extract_document` (107) | 0 | 3 | 4 | - |
| `app/services/chat_service.py` | 162 | 4.3% | 1 | `send_chat_message` (74) | 0 | 0 | 5 | - |
| `app/nlp/readability.py` | 149 | 6.0% | 2 | `calculate_readability` (52) | 0 | 0 | 5 | - |
| `app/services/clause_service.py` | 149 | 6.7% | 1 | `process_document_clauses` (131) | 0 | 0 | 1 | - |
| `app/services/dashboard_service.py` | 144 | 6.9% | 1 | `get_dashboard_stats` (122) | 0 | 0 | 2 | - |
| `tests/test_smoke_flow.py` | 140 | 7.9% | 1 | `test_full_lifecycle_smoke` (112) | 0 | 0 | 2 | - |
| `scripts/download_models.py` | 135 | 4.4% | 1 | `main` (95) | 0 | 5 | 3 | - |
| `app/nlp/parties.py` | 126 | 7.1% | 1 | `detect_affected_party` (70) | 0 | 0 | 2 | - |
| `app/services/risk_service.py` | 125 | 4.0% | 1 | `process_document_risks_and_missing` (80) | 0 | 0 | 3 | - |
| `app/nlp/importance.py` | 124 | 8.9% | 1 | `calculate_clause_importance` (81) | 0 | 0 | 1 | - |
| `app/nlp/registry.py` | 124 | 0.0% | 0 | `get_clause_hf_classifier` (36) | 0 | 2 | 4 | - |
| `tests/test_evaluation.py` | 121 | 0.8% | 0 | `test_generated_results_markdown_and_json` (22) | 1 | 0 | 2 | `data` |
| `app/nlp/document_classifier.py` | 113 | 3.5% | 1 | `classify_document_type` (42) | 0 | 0 | 2 | `data` |
| `app/__init__.py` | 106 | 4.7% | 1 | `create_app` (96) | 0 | 0 | 1 | `ratelimit_handler` |
| `app/services/analysis_service.py` | 100 | 3.0% | 1 | `process_key_info_and_summaries` (86) | 0 | 0 | 1 | `item` |
| `tests/test_extraction.py` | 98 | 0.0% | 0 | `test_extract_clean_nda_pdf` (10) | 0 | 0 | 10 | - |
| `app/nlp/evidence.py` | 84 | 7.1% | 1 | `extract_evidence_quote` (62) | 0 | 0 | 1 | - |
| `app/models/chat.py` | 78 | 0.0% | 0 | `to_dict` (10) | 2 | 0 | 2 | - |
| `app/models/analysis.py` | 74 | 0.0% | 0 | `to_dict` (16) | 1 | 0 | 1 | - |
| `tests/test_segmentation.py` | 74 | 2.7% | 0 | `test_gate_100_percent_extracted_clauses_are_exact_slices` (30) | 0 | 0 | 3 | - |
| `app/forms/auth.py` | 70 | 0.0% | 0 | - | 3 | 0 | 3 | - |
| `app/models/document.py` | 64 | 0.0% | 0 | `to_dict` (14) | 1 | 0 | 1 | - |
| `app/models/key_info.py` | 63 | 0.0% | 0 | `to_dict` (24) | 1 | 0 | 1 | - |
| `app/models/user.py` | 56 | 0.0% | 0 | `to_dict` (8) | 1 | 0 | 4 | - |
| `app/models/clause.py` | 54 | 0.0% | 0 | `to_dict` (20) | 1 | 0 | 1 | - |
| `app/models/risk.py` | 52 | 0.0% | 0 | `to_dict` (19) | 1 | 0 | 1 | - |
| `tests/conftest.py` | 49 | 0.0% | 0 | `test_user` (12) | 0 | 0 | 4 | - |
| `app/config.py` | 45 | 4.4% | 0 | - | 2 | 0 | 2 | - |
| `app/blueprints/main.py` | 39 | 0.0% | 0 | `dashboard` (9) | 0 | 0 | 3 | - |
| `app/models/missing_warning.py` | 38 | 0.0% | 0 | `to_dict` (12) | 1 | 0 | 1 | - |
| `app/models/chunk.py` | 36 | 0.0% | 0 | `to_dict` (10) | 1 | 0 | 1 | - |
| `app/models/__init__.py` | 27 | 0.0% | 0 | - | 0 | 0 | 0 | - |
| `app/extensions.py` | 23 | 0.0% | 0 | - | 0 | 0 | 0 | - |
| `app/models/base.py` | 23 | 0.0% | 0 | `generate_uuid` (3) | 1 | 0 | 3 | - |
| `run.py` | 7 | 0.0% | 0 | - | 0 | 0 | 0 | - |
| `app/blueprints/__init__.py` | 5 | 0.0% | 0 | - | 0 | 0 | 0 | - |
| `app/forms/__init__.py` | 3 | 0.0% | 0 | - | 0 | 0 | 0 | - |
| `app/nlp/__init__.py` | 1 | 0.0% | 0 | - | 0 | 0 | 1 | - |
| `tests/__init__.py` | 1 | 0.0% | 0 | - | 0 | 0 | 0 | - |

## 2. Prompt-Internal Wording Leaks

| Term Pattern | Total Hits |
|---|---:|
| Rule 6 / rule_6 / rule6 | 53 |
| Rule 7 / rule_7 / rule7 | 95 |
| Rule 4 / rule_4 / rule4 | 0 |
| Tri-Tier / tri_tier | 29 |
| Legal Advice Guard | 6 |
| grounded | 77 |
| hardened | 5 |
| dossier | 38 |
| verified | 175 |
| provenance | 30 |
| Phase M | 44 |
| per spec | 0 |

### Rule 6 / rule_6 / rule6 (53 hits)

- `CLAUDE.md:41` — `4. **RULE 6 — MISSING FIELDS**: Return exactly '"Not specified"' — never guess dates, amounts, or parties.`
- `README.md:60` — `2. **Rule 6 Absent Field Integrity**:`
- `README.md:196` — `\| **Rule 6 "Not specified" Accuracy** \| 100% \| 100.0% \| **100.0%** \| **PASS** \|`
- `app/blueprints/documents.py:361` — `"""Retrieve structured commercial metadata and important dates with Rule 6 defaults."""`
- `app/nlp/key_info.py:7` — `# Rule 6 constant`
- `app/nlp/key_info.py:84` — `"""Extract structured commercial facts and important dates with strict Rule 6 defaults.`
- `app/nlp/key_info.py:86` — `Rule 6: If a field is not explicitly specified in the text, it defaults strictly`
- `app/services/analysis_service.py:24` — `- Strict Rule 6 ('Not specified') defaults for absent information`
- `app/services/analysis_service.py:63` — `# 2. Key Facts Extraction with Rule 6 Defaults`
- `app/templates/documents/detail.html:230` — `<p class="card-subtitle">Exact extracted facts with strict Rule 6 ("Not specified") ground truth guarantees</p>`
- `docs/DEMO.md:53` — `- Point out **Rule 6 Compliance**: Absent contract fields strictly display '"Not specified"'.`
- `docs/PROGRESS.md:591` — `- 'POST /internal/analyze/key-info': Normalized extraction of contract amounts, payment deadlines, penalties, milestone `
- `docs/PROGRESS.md:616` — `- Rule 6 "Not specified" Adherence: **100%**`
- `docs/PROGRESS.md:1089` — `- [x] Enforced strict Rule 6: all absent contract fields default strictly to '"Not specified"' with 'source_page = None'`
- `docs/PROGRESS.md:1096` — `- [x] Enhanced web UI ('app/templates/documents/detail.html') with Executive Summary tab and Commercial & Operational Te`
- `docs/PROGRESS.md:1097` — `- [x] Automated test suite ('tests/test_entities_and_summary.py') passing 6 tests covering verbatim extractive summary i`
- `docs/PROGRESS.md:1102` — `- 'app/nlp/key_info.py': Deterministic entity and fact extraction engine with multi-currency parsing ('$', '€', '£', '₹'`
- `docs/PROGRESS.md:1107` — `- 'tests/test_entities_and_summary.py': 6 tests verifying verbatim sentences, Rule 6 enforcement, ground truth fact matc`
- `docs/PROGRESS.md:1112` — `- Rule 6 Ground Truth Consistency:`
- `docs/PROGRESS.md:1135` — `- [x] **Enforced Hard Gate / Rule 6 Invariant: Condition & Negation Preservation Check ('verify_preservation')**:`
- `docs/PROGRESS.md:1251` — `- **Rule 6 Check**: When an attribute is '"Not specified"', returns an honest statement (e.g. '"The document does not sp`
- `docs/PROGRESS.md:1271` — `- 11 tests covering BM25 scoring, SBERT + BM25 RRF hybrid retrieval, fact intent routing for parties, amounts, deadlines`
- `docs/PROGRESS.md:1285` — `- Fact Intent Routing & Rule 6:`
- `docs/PROGRESS.md:1383` — `- **Rule 6 Compliance**: **0 violations** (100% strict adherence to defaulting absent fields to '"Not specified"').`
- `docs/PROGRESS.md:1395` — `- 6 unit/integration tests asserting all benchmark criteria (Clause Recall $\ge 80\%$, Quote Verification $== 100\%$, Ri`
- `docs/PROGRESS.md:1453` — `- Offline Evaluation Benchmark: 'evaluation/evaluate_nlp_stack.py' executed cleanly, achieving 100% clause recall, 100% `
- `docs/architecture.md:301` — `3. **Rule 6 Absent Field Invariant**:`
- `docs/migration-plan.md:198` — `- Rule 6 strict '"Not specified"' default.`
- `docs/parity.md:34` — `\| **Rule 6 "Not specified"** \| Prompt instruction requiring "Not specified" on missing items \| Explicit code default 'va`
- `evaluation/RESULTS.md:19` — `- **Rule 6 Compliance**: **0 violations** (100% strict adherence to defaulting absent attributes to '"Not specified"').`
- `evaluation/RESULTS.md:45` — `\| \| Rule 6 "Not specified" Accuracy \| 100% \| 100.0% \| **100.0%** (0 violations) \| **PASS** \|`
- `evaluation/evaluate_nlp_stack.py:6` — `3. Key Information Extraction & Rule 6 Accuracy (Amounts, Deadlines, Penalties, Dates, 'Not specified' compliance)`
- `evaluation/evaluate_nlp_stack.py:233` — `def evaluate_key_info_and_rule6(contract_names: list[str]) -> dict[str, Any]:`
- `evaluation/evaluate_nlp_stack.py:234` — `"""Evaluate contract fact extraction and strict Rule 6 ('Not specified') compliance."""`
- `evaluation/evaluate_nlp_stack.py:237` — `rule6_violations = 0`
- `evaluation/evaluate_nlp_stack.py:264` — `rule6_violations += 1`
- `evaluation/evaluate_nlp_stack.py:280` — `"rule6_violations": rule6_violations,`
- `evaluation/evaluate_nlp_stack.py:494` — `logger.info("Evaluating Key Facts & Rule 6 Accuracy...")`
- `evaluation/evaluate_nlp_stack.py:495` — `key_info_res = evaluate_key_info_and_rule6(risk_contracts)`
- `evaluation/evaluate_nlp_stack.py:554` — `- **Rule 6 Compliance**: **{ki['rule6_violations']} violations** (100% strict adherence to defaulting absent attributes `
- `evaluation/evaluate_nlp_stack.py:580` — `\| \| Rule 6 "Not specified" Accuracy \| 100% \| 100.0% \| **100.0%** (0 violations) \| **PASS** \|`
- `tests/test_entities_and_summary.py:51` — `def test_rule6_not_specified_consistency():`
- `tests/test_entities_and_summary.py:52` — `"""Verify strict Rule 6 consistency: unstated fields default strictly to 'Not specified'."""`
- `tests/test_evaluation.py:6` — `3. Key Information Accuracy >= 80% and Rule 6 ('Not specified') Violations == 0`
- `tests/test_evaluation.py:18` — `evaluate_key_info_and_rule6,`
- `tests/test_evaluation.py:68` — `def test_key_info_extraction_and_rule6(self):`
- `tests/test_evaluation.py:70` — `res = evaluate_key_info_and_rule6(contracts)`
- `tests/test_evaluation.py:76` — `res["rule6_violations"] == 0`
- `tests/test_evaluation.py:77` — `), f"Found {res['rule6_violations']} Rule 6 violations (invented values)"`
- `tests/test_qa.py:182` — `def test_fact_intent_absent_fields_rule_6():`
- `tests/test_simplifier.py:7` — `4. Negation and condition preservation invariant (Rule 6 / Hard Gate)`
- `tests/test_simplifier.py:211` — `"""Rule 6 invariant: negations must never be stripped or inverted."""`
- `tests/test_simplifier.py:220` — `"""Rule 6 invariant: conditions must be maintained."""`

### Rule 7 / rule_7 / rule7 (95 hits)

- `CLAUDE.md:42` — `5. **RULE 7 — NO LEGAL CONCLUSIONS**: Never say a clause is "illegal", "void", or "unenforceable". Use non-definitive ad`
- `CLAUDE.md:50` — `- **Risk Identification**: Deterministic YAML rules ('data/risk_rules.yaml') + SBERT prototype matching + numeric thresh`
- `README.md:36` — `│   │   ├── risk_engine.py        # Grounded contract risk detection + Rule 7 guardrails`
- `README.md:62` — `3. **Rule 7 Legal Advice Guard**:`
- `README.md:158` — `- Grounded risk detection rules, predatory clause identification, and Rule 7 compliance`
- `README.md:195` — `\| **Rule 7 Forbidden Claims** \| Exactly 0 \| 0 \| **0** \| **STRICT PASS** \|`
- `app/nlp/missing_provisions.py:6` — `- Strictly applies Rule 7 disclaimer and "Possible omission" label`
- `app/nlp/missing_provisions.py:20` — `from app.nlp.risk_engine import enforce_rule7_language`
- `app/nlp/missing_provisions.py:141` — `- Text strictly passes Rule 7 legal conclusion filter`
- `app/nlp/missing_provisions.py:198` — `"clause_name": enforce_rule7_language(clause_name),`
- `app/nlp/missing_provisions.py:200` — `"why_it_matters": enforce_rule7_language(why_it_matters),`
- `app/nlp/missing_provisions.py:201` — `"typical_provision": enforce_rule7_language(typical_provision),`
- `app/nlp/risk_engine.py:6` — `- Strictly complies with Rule 7: zero legal conclusions ("illegal", "void", "unenforceable")`
- `app/nlp/risk_engine.py:29` — `# Rule 7: Forbidden legal conclusions and safe non-definitive replacements`
- `app/nlp/risk_engine.py:30` — `RULE7_FORBIDDEN_REPLACEMENTS = [`
- `app/nlp/risk_engine.py:47` — `def enforce_rule7_language(text: str) -> str:`
- `app/nlp/risk_engine.py:48` — `"""Ensure text strictly avoids definitive legal conclusions per Rule 7."""`
- `app/nlp/risk_engine.py:52` — `for pattern, repl in RULE7_FORBIDDEN_REPLACEMENTS:`
- `app/nlp/risk_engine.py:57` — `def count_rule7_violations(text: str) -> int:`
- `app/nlp/risk_engine.py:165` — `"title": enforce_rule7_language(rule["title"]),`
- `app/nlp/risk_engine.py:167` — `"explanation": enforce_rule7_language(rule["explanation"]),`
- `app/nlp/risk_engine.py:168` — `"why_it_matters": enforce_rule7_language(rule["why_it_matters"]),`
- `app/nlp/risk_engine.py:169` — `"possible_consequences": enforce_rule7_language(`
- `app/nlp/risk_engine.py:173` — `enforce_rule7_language(q)`
- `app/services/report_service.py:733` — `"Expected protective covenants for this agreement type flagged under Rule 7 non-definitive guidelines.",`
- `app/templates/documents/detail.html:556` — `Rule 7 Compliant: Grounded advisory warnings (no definitive legal conclusions)`
- `docs/DEMO.md:14` — `\| **3:00 – 4:00** \| **Risk Detection & Grounded Q&A** \| Predatory terms, Rule 7 Guard, SQuAD 2.0 honest refusal \| Zero h`
- `docs/DEMO.md:52` — `- Point out **Rule 7 Compliance**: The system never uses forbidden words like *"illegal"*, *"void"*, or *"unenforceable"`
- `docs/PROGRESS.md:589` — `- Enforced **Rule 7**: Banned definitive claims ("illegal", "null and void", "unenforceable") via regex post-filter 'fil`
- `docs/PROGRESS.md:615` — `- Rule 7 Violations in Results: **0** (Zero allowed - strict pass)`
- `docs/PROGRESS.md:628` — `- 'app/services/risk_service.py', 'app/services/key_info_service.py', 'app/services/missing_service.py': Core analysis s`
- `docs/PROGRESS.md:669` — `- Enforces Rule 7: Sanitizes answers against forbidden legal conclusions ('"is illegal"', '"null and void"', '"is unenfo`
- `docs/PROGRESS.md:710` — `- 'app/services/chat_service.py': Service with chunk formatting, history concatenation, quote verification, and Rule 7 f`
- `docs/PROGRESS.md:868` — `- 'tests/test_recorded_fixtures.py': Offline integration suite validating layout extraction, quote verification, Rule 7 `
- `docs/PROGRESS.md:1183` — `- [x] Implemented Rule 7 Legal Advice Guard ('app/nlp/risk_engine.py'):`
- `docs/PROGRESS.md:1185` — `- Automated check 'count_rule7_violations' guarantees **0 violations** across all titles, explanations, consequences, an`
- `docs/PROGRESS.md:1194` — `- **Passed Hard Gate**: Flags missing provisions with strict '"Possible omission"' labeling and zero Rule 7 conclusions `
- `docs/PROGRESS.md:1209` — `- 10 tests verifying Rule 7 sanitization, YAML integrity, predatory terms detection in 'one_sided_agreement.pdf', missin`
- `docs/PROGRESS.md:1216` — `- 'app/nlp/risk_engine.py': Grounded risk detection engine and Rule 7 sanitization guard.`
- `docs/PROGRESS.md:1220` — `- 'tests/test_risk.py': 10 tests verifying predatory terms detection, Rule 7 compliance, missing provisions, and APIs.`
- `docs/PROGRESS.md:1224` — `- Flagged 6 risks with 100% verified evidence quotes and zero Rule 7 violations:`
- `docs/PROGRESS.md:1233` — `- Rule 7 Strict Legal Conclusion Invariant:`
- `docs/PROGRESS.md:1316` — `10. Regulatory Notice & Legal Disclaimer (Rule 7 non-definitive notice, SHA-256 integrity hash)`
- `docs/PROGRESS.md:1382` — `- **Rule 7 Compliance**: **0 violations** (100% elimination of unauthorized conclusions like "illegal", "void", "unenfor`
- `docs/PROGRESS.md:1395` — `- 6 unit/integration tests asserting all benchmark criteria (Clause Recall $\ge 80\%$, Quote Verification $== 100\%$, Ri`
- `docs/PROGRESS.md:1453` — `- Offline Evaluation Benchmark: 'evaluation/evaluate_nlp_stack.py' executed cleanly, achieving 100% clause recall, 100% `
- `docs/architecture.md:49` — `RiskEng["Grounded Risk Engine\n(Rules, Regex, Thresholds + Rule 7 Guard)"]`
- `docs/architecture.md:99` — `NLPRisk->>NLPRisk: Apply risk_rules.yaml + Rule 7 Legal Guard`
- `docs/architecture.md:298` — `2. **Rule 7 Legal Advice Guard**:`
- `docs/migration-plan.md:127` — `│   │   ├── risk/             # Rule-based patterns + SBERT prototype similarity + Rule 7 filter`
- `docs/migration-plan.md:208` — `- Rule 7 non-definitive phrasing enforcement (no "illegal" or "void").`
- `docs/migration-plan.md:211` — `- *Gate*: Predatory clauses detected in one-sided sample; 0 Rule 7 violations; charts match SQL aggregates.`
- `docs/parity.md:45` — `\| **Rule 7 Legal Advice Guard** \| Post-filter removing "illegal", "void", "unenforceable" \| Post-filter substituting non`
- `docs/privacy.md:37` — `## 4. Regulatory Notice & Rule 7 Legal Advice Guard`
- `docs/privacy.md:42` — `- The platform strictly enforces **Rule 7 Legal Advice Guards**, eliminating conclusionary legal statements (*"illegal"*`
- `evaluation/RESULTS.md:18` — `- **Rule 7 Compliance**: **0 violations** across all generated outputs (100% elimination of unauthorized conclusions lik`
- `evaluation/RESULTS.md:44` — `\| **Regulatory Guardrails** \| Rule 7 Forbidden Phrase Count \| Exactly 0 \| 0 \| **0** \| **STRICT PASS** \|`
- `evaluation/RESULTS.md:78` — `### 3.3 Rule 7 Legal Conclusion Safeguards`
- `evaluation/evaluate_nlp_stack.py:5` — `2. Grounded Risk Detection & Guardrails (Risk Recall, Precision, Predatory Detection, Rule 7 Compliance)`
- `evaluation/evaluate_nlp_stack.py:36` — `from app.nlp.risk_engine import count_rule7_violations, detect_clause_risks`
- `evaluation/evaluate_nlp_stack.py:143` — `"""Evaluate grounded risk detection, predatory traps, and Rule 7 compliance."""`
- `evaluation/evaluate_nlp_stack.py:147` — `rule7_violations = 0`
- `evaluation/evaluate_nlp_stack.py:172` — `rule7_violations += count_rule7_violations(r["title"])`
- `evaluation/evaluate_nlp_stack.py:173` — `rule7_violations += count_rule7_violations(r["explanation"])`
- `evaluation/evaluate_nlp_stack.py:174` — `rule7_violations += count_rule7_violations(r["why_it_matters"])`
- `evaluation/evaluate_nlp_stack.py:175` — `rule7_violations += count_rule7_violations(r["possible_consequences"])`
- `evaluation/evaluate_nlp_stack.py:223` — `"rule7_violations": rule7_violations,`
- `evaluation/evaluate_nlp_stack.py:491` — `logger.info("Evaluating Risk Detection & Rule 7 Guardrails...")`
- `evaluation/evaluate_nlp_stack.py:553` — `- **Rule 7 Compliance**: **{rk['rule7_violations']} violations** across all generated outputs (100% elimination of unaut`
- `evaluation/evaluate_nlp_stack.py:579` — `\| **Regulatory Guardrails** \| Rule 7 Forbidden Phrase Count \| Exactly 0 \| 0 \| **{rk['rule7_violations']}** \| **STRICT PA`
- `evaluation/evaluate_nlp_stack.py:613` — `### 3.3 Rule 7 Legal Conclusion Safeguards`
- `scripts/smoke_test.sh:85` — `echo "      Detected ${RISK_COUNT} contractual risks with Rule 7 guardrails."`
- `tests/test_evaluation.py:5` — `2. Risk Detection Recall >= 80%, Predatory Traps == 3/3, and Rule 7 Violations == 0`
- `tests/test_evaluation.py:47` — `def test_risk_detection_and_rule7_guardrails(self):`
- `tests/test_evaluation.py:65` — `res["rule7_violations"] == 0`
- `tests/test_evaluation.py:66` — `), f"Found {res['rule7_violations']} Rule 7 forbidden phrase violations"`
- `tests/test_evaluation.py:120` — `assert "Rule 7 Forbidden Phrase Count" in md_content`
- `tests/test_risk.py:4` — `1. Rule 7 legal conclusion guard (zero instances of 'illegal', 'void', 'unenforceable')`
- `tests/test_risk.py:24` — `count_rule7_violations,`
- `tests/test_risk.py:26` — `enforce_rule7_language,`
- `tests/test_risk.py:34` — `class TestRule7LegalAdviceGuard:`
- `tests/test_risk.py:35` — `"""Verify Rule 7 strict prohibition on definitive legal conclusions."""`
- `tests/test_risk.py:42` — `cleaned = enforce_rule7_language(raw_text)`
- `tests/test_risk.py:48` — `assert count_rule7_violations(cleaned) == 0`
- `tests/test_risk.py:52` — `assert enforce_rule7_language(clean_text) == clean_text`
- `tests/test_risk.py:53` — `assert count_rule7_violations(clean_text) == 0`
- `tests/test_risk.py:84` — `assert count_rule7_violations(r["explanation"]) == 0`
- `tests/test_risk.py:107` — `assert count_rule7_violations(p["why_it_matters"]) == 0`
- `tests/test_risk.py:161` — `# 5. Check Rule 7 across all outputs`
- `tests/test_risk.py:163` — `assert count_rule7_violations(r["explanation"]) == 0`
- `tests/test_risk.py:164` — `assert count_rule7_violations(r["why_it_matters"]) == 0`
- `tests/test_risk.py:165` — `assert count_rule7_violations(r["possible_consequences"]) == 0`
- `tests/test_risk.py:191` — `# Verify strict "Possible omission" labeling and Rule 7 compliance`
- `tests/test_risk.py:194` — `assert count_rule7_violations(m["why_it_matters"]) == 0`
- `tests/test_risk.py:195` — `assert count_rule7_violations(m["typical_provision"]) == 0`

### Tri-Tier / tri_tier (29 hits)

- `CLAUDE.md:49` — `- **Clause Extraction & Tri-Tier Simplification**: Exact clause segmentation + ensemble classification + 3 rule-based mo`
- `README.md:33` — `│   │   ├── simplifier.py         # Tri-Tier plain language simplifier (Simple, Detailed, Pro)`
- `README.md:160` — `- Tri-tier simplification and Flesch reading ease score calculations`
- `app/nlp/simplifier.py:1` — `"""LexiLegal AI — Tri-Tier Rule-Based Legal Simplifier.`
- `app/nlp/simplifier.py:859` — `"""Execute complete tri-tier simplification pipeline on a clause with readability scoring."""`
- `app/services/report_service.py:468` — `Paragraph("3. Tri-Tier Plain-Language Explanations", style_sec_heading)`
- `app/templates/landing.html:35` — `<h3 class="card-title">Tri-Tier Simplification</h3>`
- `docs/DEMO.md:13` — `\| **2:00 – 3:00** \| **Clause Inventory & Simplification** \| Tri-Tier modes, Flesch Reading Score, Exact Quote Verificati`
- `docs/DEMO.md:37` — `### 3. Clause Analysis & Tri-Tier Simplification (2:00 – 3:00)`
- `docs/DEMO.md:41` — `2. Demonstrate **Tri-Tier Simplification Modes**:`
- `docs/DEMO.md:64` — `- Walk through all **10 structured sections**: Executive Summary, Key Provisions, Tri-Tier Explanations, Grounded Risks,`
- `docs/PROGRESS.md:26` — `\| Phase M5 \| Tri-Tier Rule-Based Simplification & Readability \| Completed \| 2026-11-17 \|`
- `docs/PROGRESS.md:1125` — `### Phase M5: Tri-Tier Rule-Based Simplification, Readability Scorer & Simplification Studio`
- `docs/PROGRESS.md:1131` — `- [x] Implemented Tri-Tier Rule-Based Legal Simplifier ('app/nlp/simplifier.py'):`
- `docs/PROGRESS.md:1142` — `- [x] Updated Clause Service ('app/services/clause_service.py'): Replaced provisional placeholders with real tri-tier si`
- `docs/PROGRESS.md:1152` — `- 16 tests covering syllable counting, readability calculations, 150+ glossary validation, lexical simplification, negat`
- `docs/PROGRESS.md:1160` — `- 'app/nlp/simplifier.py': Tri-tier legal simplifier, lexical substitution engine, negation/condition preservation check`
- `docs/PROGRESS.md:1310` — `4. Tri-Tier Plain-Language Explanations (Simple, Detailed, Professional)`
- `docs/architecture.md:28` — `StudioBP["studio_bp\n(Interactive Tri-Tier Simplification Studio)"]`
- `docs/architecture.md:47` — `SimpEng["Tri-Tier Simplifier\n(Glossary Substitution & Structural Decomposition)"]`
- `docs/migration-plan.md:18` — `The target architecture consolidates the entire platform into **one unified, transparent Python 3.11+ Flask application*`
- `docs/parity.md:38` — `\| **Detailed Simplification** \| Expanded paragraph generated by LLM \| Category templates populated with extracted obligo`
- `docs/parity.md:39` — `\| **Professional Simplification** \| Commercial briefing generated by LLM \| Structured breakdown: Obligor, Obligation, Co`
- `tests/test_dashboard_and_report.py:206` — `assert "3. Tri-Tier Plain-Language Explanations" in all_text`
- `tests/test_simplifier.py:1` — `"""Phase M5 Tests: Tri-Tier Rule-Based Simplification, Readability, and Trap Detection.`
- `tests/test_simplifier.py:6` — `3. Tri-tier generation (Simple English, Detailed, Professional)`
- `tests/test_simplifier.py:185` — `"""Test tri-tier simplification, preservation checks, and glossary integration."""`
- `tests/test_simplifier.py:255` — `def test_tri_tier_modes_generation(self):`
- `tests/test_smoke_flow.py:9` — `6. Test interactive Tri-Tier simplification`

### Legal Advice Guard (6 hits)

- `README.md:62` — `3. **Rule 7 Legal Advice Guard**:`
- `docs/PROGRESS.md:1183` — `- [x] Implemented Rule 7 Legal Advice Guard ('app/nlp/risk_engine.py'):`
- `docs/architecture.md:298` — `2. **Rule 7 Legal Advice Guard**:`
- `docs/parity.md:45` — `\| **Rule 7 Legal Advice Guard** \| Post-filter removing "illegal", "void", "unenforceable" \| Post-filter substituting non`
- `docs/privacy.md:37` — `## 4. Regulatory Notice & Rule 7 Legal Advice Guard`
- `docs/privacy.md:42` — `- The platform strictly enforces **Rule 7 Legal Advice Guards**, eliminating conclusionary legal statements (*"illegal"*`

### grounded (77 hits)

- `CLAUDE.md:7` — `Users upload a legal document (PDF, DOCX, TXT). The system extracts text with page numbers, then produces: extractive su`
- `README.md:9` — `**LexiLegal AI** is an enterprise-grade legal document analysis and plain-language simplification platform built with a `
- `README.md:36` — `│   │   ├── risk_engine.py        # Grounded contract risk detection + Rule 7 guardrails`
- `README.md:158` — `- Grounded risk detection rules, predatory clause identification, and Rule 7 compliance`
- `README.md:176` — `'Register User' $\rightarrow$ 'Upload Contract' $\rightarrow$ 'Verify Clauses' $\rightarrow$ 'Verify Risks' $\rightarrow`
- `app/blueprints/documents.py:152` — `# REST API Endpoints (Grounded Backend & Test Clients)`
- `app/blueprints/documents.py:415` — `"""Retrieve grounded risk findings with exact page and quote evidence."""`
- `app/blueprints/documents.py:483` — `"""Process incoming question about document and return extractive/grounded response."""`
- `app/nlp/risk_engine.py:1` — `"""LexiLegal AI — Grounded Contract Risk Detection Engine.`
- `app/nlp/segmentation.py:62` — `"""A text chunk prepared for page-attributed retrieval and grounded QA."""`
- `app/services/chat_service.py:3` — `Orchestrates multi-turn grounded contract conversations, page-aware passage retrieval,`
- `app/services/report_service.py:548` — `story.append(Paragraph("4. Grounded Contract Risk Assessment", style_sec_heading))`
- `app/services/risk_service.py:4` — `1. Grounded risk detection across contractual clauses`
- `app/templates/dashboard.html:53` — `<span style="font-size: 0.8rem; color: var(--text-muted);">Grounded findings</span>`
- `app/templates/documents/detail.html:167` — `&#10003; 100% grounded — sentences extracted verbatim from source text`
- `app/templates/documents/detail.html:525` — `<!-- Tab: Grounded Risk Analysis -->`
- `app/templates/documents/detail.html:556` — `Rule 7 Compliant: Grounded advisory warnings (no definitive legal conclusions)`
- `app/templates/documents/detail.html:741` — `<p class="card-subtitle" style="margin: 0;">Extractive, page-grounded question answering powered by Hybrid Retrieval (SB`
- `app/templates/landing.html:45` — `<h3 class="card-title">Grounded Risk Analysis</h3>`
- `data/risk_rules.yaml:1` — `# LexiLegal AI — Grounded Contract Risk Detection Rules`
- `docs/DEMO.md:14` — `\| **3:00 – 4:00** \| **Risk Detection & Grounded Q&A** \| Predatory terms, Rule 7 Guard, SQuAD 2.0 honest refusal \| Zero h`
- `docs/DEMO.md:49` — `### 4. Grounded Risk Detection & Document Q&A (3:00 – 4:00)`
- `docs/DEMO.md:57` — `- Show assistant response citing '✓ Page 1' with exact grounded dollar amount ($2,400.00).`
- `docs/DEMO.md:64` — `- Walk through all **10 structured sections**: Executive Summary, Key Provisions, Tri-Tier Explanations, Grounded Risks,`
- `docs/PROGRESS.md:17` — `\| Phase 7 \| Grounded Risk Analysis, Key Facts Extraction & Missing Provisions Detection \| Completed \| 2026-11-17 \|`
- `docs/PROGRESS.md:18` — `\| Phase 8 \| Grounded Document Chat, PostgreSQL Full-Text Search Retrieval & Conversation History \| Completed \| 2026-11-1`
- `docs/PROGRESS.md:28` — `\| Phase M6 \| Grounded Risk Detection & Missing Provisions \| Completed \| 2026-11-17 \|`
- `docs/PROGRESS.md:353` — `- 'SummaryTab.jsx': Tab workspace with executive/comprehensive summary toggle, identified parties grid with roles and ev`
- `docs/PROGRESS.md:388` — `- Verified presence of "100% Grounded" badge, "Identified Parties" section, and "Main Conditions" section.`
- `docs/PROGRESS.md:413` — `- [x] Schema & Prompts: Defined Pydantic schemas in 'app/schemas/clause.py' supporting 17 standard categories + 'Other' `
- `docs/PROGRESS.md:504` — `- [x] Grounding & Post-Check: Implemented 'validate_numbers_and_dates' regex check in 'SimplifyService' confirming that `
- `docs/PROGRESS.md:514` — `- Built 'SimplifyPage.jsx' ('/simplify'): sample clauses loader (Indemnification, Termination, Non-Compete, Force Majeur`
- `docs/PROGRESS.md:559` — `9. Verified "Grounded (No Invented Figures)" badge rendered.`
- `docs/PROGRESS.md:586` — `### Phase 7: Grounded Risk Analysis, Key Facts Extraction & Missing Provisions Detection`
- `docs/PROGRESS.md:587` — `- [x] AI Engine Grounded Analysis Services & Rule Enforcement:`
- `docs/PROGRESS.md:663` — `### Phase 8: Grounded Document Chat, PostgreSQL Full-Text Search Retrieval & Conversation History`
- `docs/PROGRESS.md:664` — `- [x] AI Engine Grounded Chat Service & Schema:`
- `docs/PROGRESS.md:713` — `- 'tests/test_chat.py': Pytest test suite for grounded chat.`
- `docs/PROGRESS.md:847` — `- [x] End-to-end smoke test script ('scripts/smoke_test.sh'): verified full lifecycle covering Register -> Auth -> Uploa`
- `docs/PROGRESS.md:851` — `- 'docs/architecture.md': system architecture with Mermaid diagrams (Async Ingestion Pipeline and Grounded RAG Search).`
- `docs/PROGRESS.md:1181` — `### Phase M6: Grounded Risk Detection & Missing Provisions`
- `docs/PROGRESS.md:1182` — `- [x] Configured grounded contract risk rules ('data/risk_rules.yaml') spanning all 6 required categories (*Financial, L`
- `docs/PROGRESS.md:1186` — `- [x] Built Grounded Risk Detection Engine ('app/nlp/risk_engine.py'):`
- `docs/PROGRESS.md:1216` — `- 'app/nlp/risk_engine.py': Grounded risk detection engine and Rule 7 sanitization guard.`
- `docs/PROGRESS.md:1311` — `5. Grounded Risk Assessment (color-coded High/Med/Low cards, evidence quotes, consequences)`
- `docs/PROGRESS.md:1369` — `- **Grounded Risk Detection & Guardrails**: Evaluated on predatory probes ('one_sided_agreement.pdf'), residential lease`
- `docs/PROGRESS.md:1433` — `5. Verify grounded risk detection`
- `docs/PROGRESS.md:1434` — `6. Grounded document Q&A and exact page citation`
- `docs/api-documentation.md:184` — `## 3. Clause Analysis & Grounded Risks`
- `docs/api-documentation.md:217` — `Returns all contractual risk findings grounded directly in verified source text.`
- `docs/api-documentation.md:279` — `## 4. Grounded Document Chat (Extractive Q&A)`
- `docs/api-documentation.md:282` — `Submits a user question about the document and returns a grounded extractive answer with page citations.`
- `docs/architecture.md:36` — `RiskSvc["Risk Service\n(Grounded Detection & Missing Provision Checklists)"]`
- `docs/architecture.md:37` — `ChatSvc["Chat Service\n(Conversation Lifecycles & Grounded QA)"]`
- `docs/architecture.md:49` — `RiskEng["Grounded Risk Engine\n(Rules, Regex, Thresholds + Rule 7 Guard)"]`
- `docs/architecture.md:109` — `## 4. Grounded Chat & Question Answering Flow`
- `docs/implementation-plan.md:272` — `\| 'POST' \| '/api/documents/{id}/chat' \| Bearer JWT (User) \| '{ "conversationId": "uuid?", "message": "What is the notice`
- `docs/implementation-plan.md:289` — `\| 'POST' \| '/internal/chat' \| Header: 'X-Internal-Api-Key' \| '{ "question": "...", "retrieved_chunks": [{ "chunk_id": ".`
- `docs/parity.md:50` — `\| **Grounded QA & Citations** \| Gemini prompt answering strictly from top chunks \| Extractive BERT QA (MiniLM SQuAD 2.0)`
- `evaluation/RESULTS.md:69` — `### 3.2 Grounded Risk Engine & Predatory Contract Probes`
- `evaluation/RESULTS.md:98` — `\| Grounded Risk & Consequence Detection \| 2.60s \| 0.212s \| ~12.3x \|`
- `evaluation/evaluate_nlp_stack.py:5` — `2. Grounded Risk Detection & Guardrails (Risk Recall, Precision, Predatory Detection, Rule 7 Compliance)`
- `evaluation/evaluate_nlp_stack.py:143` — `"""Evaluate grounded risk detection, predatory traps, and Rule 7 compliance."""`
- `evaluation/evaluate_nlp_stack.py:288` — `"""Evaluate grounded QA, citation accuracy, and honest refusal handling."""`
- `evaluation/evaluate_nlp_stack.py:497` — `logger.info("Evaluating Grounded Chat & Honest Refusal Probes...")`
- `evaluation/evaluate_nlp_stack.py:604` — `### 3.2 Grounded Risk Engine & Predatory Contract Probes`
- `evaluation/evaluate_nlp_stack.py:633` — `\| Grounded Risk & Consequence Detection \| 2.60s \| {lat['risk_detection']:.3f}s \| ~{2.60/lat['risk_detection']:.1f}x \|`
- `scripts/smoke_test.sh:79` — `# 5. Retrieve grounded risk findings`
- `scripts/smoke_test.sh:80` — `echo "[5/7] Retrieving grounded risk findings..."`
- `scripts/smoke_test.sh:87` — `# 6. Test Document Q&A (Grounded Extractive QA)`
- `scripts/smoke_test.sh:88` — `echo "[6/7] Asking grounded question: 'What is the monthly rent amount?'..."`
- `tests/test_dashboard_and_report.py:207` — `assert "4. Grounded Contract Risk Assessment" in all_text`
- `tests/test_risk.py:1` — `"""Phase M6 Tests: Grounded Risk Detection & Missing Expected Provisions.`
- `tests/test_smoke_flow.py:8` — `5. Verify grounded risk detection & missing provisions`
- `tests/test_smoke_flow.py:10` — `7. Ask grounded question and verify verbatim page citation`
- `tests/test_smoke_flow.py:85` — `# 6. Retrieve grounded risk findings`
- `tests/test_smoke_flow.py:93` — `# 7. Grounded Document Chat Q&A`

### hardened (5 hits)

- `app/config.py:33` — `# Session cookie hardening`
- `docs/PROGRESS.md:32` — `\| Phase M10 \| Legacy Removal, Hardening & Final Verification Gate \| Completed \| 2026-11-17 \|`
- `docs/PROGRESS.md:1416` — `### Phase M10: Legacy Removal, Hardening & Final Verification Gate`
- `docs/PROGRESS.md:1421` — `- [x] Hardening & Security Verification:`
- `docs/migration-plan.md:226` — `- **Phase M10 — Legacy Removal, Hardening & Final Gate**:`

### dossier (38 hits)

- `CLAUDE.md:25` — `- **Extraction & Reports**: PyMuPDF, python-docx, pytesseract + Pillow (OCR), ReportLab (10-section PDF dossier with Tru`
- `CLAUDE.md:55` — `- **PDF Report**: 10-section ReportLab dossier with TrueType Unicode fonts ('₹', '§', curly quotes), 'Page X of Y' foote`
- `README.md:163` — `- 10-section ReportLab PDF dossier generation with running headers and TrueType Unicode fonts`
- `app/services/report_service.py:1` — `"""LexiLegal AI — ReportLab PDF Dossier Generator.`
- `app/services/report_service.py:143` — `self.drawString(36, 804, "LexiLegal AI — Legal Contract Dossier")`
- `app/services/report_service.py:167` — `"""Build a comprehensive 10-section PDF report dossier for the analyzed document."""`
- `app/services/report_service.py:261` — `"<b>LEXILEGAL AI</b> &bull; COMPREHENSIVE CONTRACT ANALYSIS DOSSIER",`
- `docs/DEMO.md:15` — `\| **4:00 – 5:00** \| **ReportLab PDF Dossier & Wrap-up** \| 10-section PDF download, Running headers, Offline privacy \| 10`
- `docs/DEMO.md:61` — `### 5. ReportLab PDF Dossier & Offline Privacy (4:00 – 5:00)`
- `docs/DEMO.md:63` — `2. Open the downloaded PDF dossier:`
- `docs/PROGRESS.md:30` — `\| Phase M8 \| Dashboard, ReportLab PDF Dossier & UI Polish \| Completed \| 2026-11-17 \|`
- `docs/PROGRESS.md:774` — `- [x] React Frontend Dashboard & Report Dossier:`
- `docs/PROGRESS.md:782` — `- 10-section dossier breakdown preview.`
- `docs/PROGRESS.md:786` — `- Added "Report Dossier" tab to tab bar.`
- `docs/PROGRESS.md:792` — `- Full-Stack Live Browser E2E: 'frontend/test-phase9-e2e.cjs' verified user registration, initial dashboard stats, contr`
- `docs/PROGRESS.md:796` — `3. OpenPDF 10-Section Dossier & Unicode Rendering (3 Samples):`
- `docs/PROGRESS.md:816` — `- 'frontend/src/components/report/ReportTab.jsx': Report Dossier tab with section outline, download button, and disclaim`
- `docs/PROGRESS.md:1300` — `### Phase M8: Dashboard, ReportLab PDF Dossier & UI Polish`
- `docs/PROGRESS.md:1305` — `- [x] Built ReportLab 10-Section Legal Dossier Generator ('app/services/report_service.py'):`
- `docs/PROGRESS.md:1341` — `- 'app/services/report_service.py': 10-section ReportLab PDF dossier generator with 'NumberedCanvas' and Unicode support`
- `docs/PROGRESS.md:1393` — `- Generated professional comparative benchmark dossier in 'evaluation/RESULTS.md' with full Markdown comparison tables a`
- `docs/PROGRESS.md:1436` — `8. Generate & download 10-section ReportLab PDF dossier`
- `docs/api-documentation.md:331` — `## 5. ReportLab PDF Dossier & Dashboard`
- `docs/api-documentation.md:334` — `Generates and downloads the formal 10-section ReportLab PDF Legal Dossier.`
- `docs/architecture.md:13` — `- **Report Engine**: ReportLab 5 (10-Section Legal Dossier, running headers, two-pass 'NumberedCanvas', TrueType font su`
- `docs/architecture.md:38` — `ReportSvc["Report Service\n(ReportLab 10-Section Dossier Engine)"]`
- `docs/migration-plan.md:52` — `\| Analysis \| 'GET' \| '/api/documents/{id}/report.pdf' \| 10-section PDF report dossier \|`
- `docs/migration-plan.md:87` — `\| 'backend/src/main/java/com/lexilegal/service/ReportPdfService.java' \| **REPLACE** \| Replace Java OpenPDF with Python R`
- `docs/migration-plan.md:217` — `- **Phase M8 — Dashboard, ReportLab PDF Dossier & UI Polish**:`
- `docs/parity.md:57` — `\| **PDF Report Dossier** \| OpenPDF 2.0.3 (Java) 10-section PDF report \| Python ReportLab 10-section PDF with headers, fo`
- `evaluation/RESULTS.md:102` — `\| **ReportLab 10-Section PDF Dossier Generation** \| 0.25s \| ~0.15s \| ~1.7x Faster \|`
- `evaluation/evaluate_nlp_stack.py:637` — `\| **ReportLab 10-Section PDF Dossier Generation** \| 0.25s \| ~0.15s \| ~1.7x Faster \|`
- `scripts/smoke_test.sh:97` — `# 7. Download PDF Report Dossier`
- `scripts/smoke_test.sh:98` — `echo "[7/7] Generating and downloading 10-section ReportLab PDF Dossier..."`
- `tests/test_dashboard_and_report.py:1` — `"""Tests for Phase M8: Dashboard SQL Aggregates, ReportLab PDF Dossier & Multi-Tenant Isolation."""`
- `tests/test_dashboard_and_report.py:196` — `assert len(pdf) >= 2  # Multi-page dossier`
- `tests/test_smoke_flow.py:11` — `8. Generate and download ReportLab 10-section PDF dossier`
- `tests/test_smoke_flow.py:120` — `# 9. Download 10-Section PDF Dossier`

### verified (175 hits)

- `CLAUDE.md:10` — `1. Working, verified functionality (no placeholders in core features)`
- `CLAUDE.md:38` — `1. **EXACT SOURCE SLICING (100% Quote Verification)**: Every extracted clause stores 'start_char', 'end_char', 'page_sta`
- `CLAUDE.md:44` — `7. **CHAT HONESTY**: Answer strictly from retrieved passages or verified facts. When confidence is below threshold, retu`
- `CLAUDE.md:90` — `Fresh clone → follow 'README.md' → './run_local.sh' → register, upload sample contract, view verified clauses, risks, ke`
- `README.md:9` — `**LexiLegal AI** is an enterprise-grade legal document analysis and plain-language simplification platform built with a `
- `app/nlp/evidence.py:32` — `- Verified against source text`
- `app/nlp/qa_engine.py:4` — `1. Fact Intent Routing: Deterministic regex matching against verified pre-extracted facts`
- `app/nlp/qa_engine.py:145` — `"""Route factual query directly to verified pre-extracted metadata."""`
- `app/nlp/qa_engine.py:573` — `# 1. Check Fact Intent Router for 100% verified metadata`
- `app/nlp/risk_engine.py:5` — `- Extracts exact, verified evidence quotes anchored to source page`
- `app/nlp/risk_engine.py:149` — `quote, verified = extract_evidence_quote(`
- `app/nlp/risk_engine.py:178` — `"quote_verified": verified,`
- `app/services/clause_service.py:133` — `# 5. Calculate verified quote rate`
- `app/services/report_service.py:405` — `Paragraph("<b>Verified Source Quote</b>", style_body_bold),`
- `app/templates/documents/detail.html:30` — `<span class="badge badge-success" title="100% of clause quotes verified directly from source text">`
- `app/templates/documents/detail.html:31` — `&#10003; {{ analysis.verification_rate }}% Quote Verified`
- `app/templates/documents/detail.html:479` — `&#10003; Verified exact source quote`
- `app/templates/documents/detail.html:600` — `&#10003; Verified exact contract quote (Page {{ risk.source_page }})`
- `docs/DEMO.md:40` — `- Point out the **"✓ Quote Verified" badge**: 100% of quotes are exact substring slices verified against character offse`
- `docs/PROGRESS.md:3` — `This document tracks implementation status across the 10 phases of the project. Each phase records what was built, how i`
- `docs/PROGRESS.md:50` — `- [x] Verify full stack execution: frontend, backend, database, and AI engine running with verified service-to-service a`
- `docs/PROGRESS.md:76` — `**How it was verified:**`
- `docs/PROGRESS.md:85` — `- 'GET /api/health/ai' -> HTTP 200 '{"status":"ok","service_to_service_auth":"verified","ai_engine":{"status":"ok","serv`
- `docs/PROGRESS.md:90` — `- Verified landing page heading and title.`
- `docs/PROGRESS.md:91` — `- Verified theme toggle switch: adds 'dark' class, updates 'localStorage.getItem("lexilegal_theme") = "dark"'.`
- `docs/PROGRESS.md:92` — `- Verified persistence: page reload maintains 'dark' class and 'localStorage'.`
- `docs/PROGRESS.md:93` — `- Verified all placeholder routes render successfully: '/dashboard', '/upload', '/documents/:id', '/history', '/profile'`
- `docs/PROGRESS.md:166` — `**How it was verified:**`
- `docs/PROGRESS.md:267` — `**How it was verified:**`
- `docs/PROGRESS.md:277` — `- 'clean_nda.pdf': uploaded, pipeline completed to 'Extracted', navigated to text preview, verified Page 1 text (430 cha`
- `docs/PROGRESS.md:278` — `- 'service_agreement.docx': uploaded, pipeline completed to 'Extracted', verified Page 1 text (607 chars).`
- `docs/PROGRESS.md:279` — `- 'promissory_note.txt': uploaded, pipeline completed to 'Extracted', verified Page 1 text (830 chars).`
- `docs/PROGRESS.md:280` — `- 'scanned_deed.pdf': uploaded, pipeline completed to 'Extracted', verified OCR extracted text ("QUITCLAIM DEED", "State`
- `docs/PROGRESS.md:286` — `- All stored files in 'backend/uploads/' verified to follow randomized UUID naming ('^[0-9a-f-]{36}\.[a-z0-9]+$').`
- `docs/PROGRESS.md:289` — `- Inspected 'document_chunks' rows: verified 'id', 'document_id', 'chunk_index', 'page_number', 'token_count', and popul`
- `docs/PROGRESS.md:295` — `- Verified physical file was unlinked and deleted from disk ('fs.existsSync(diskPath) === false').`
- `docs/PROGRESS.md:296` — `- Verified database rows were completely removed ('SELECT count(*) FROM documents WHERE id = ...' = 0, 'SELECT count(*) `
- `docs/PROGRESS.md:328` — `- [x] Build frontend 'ProvenanceBadge.jsx': 'EXTRACTED' ("Extracted"), 'AI_INTERPRETATION' ("AI Interpretation"), page c`
- `docs/PROGRESS.md:352` — `- 'ProvenanceBadge.jsx': Visual provenance pill ('Extracted' vs 'AI Interpretation'), page citation ('p. X'), verified b`
- `docs/PROGRESS.md:357` — `**How it was verified:**`
- `docs/PROGRESS.md:365` — `2. JSON-validation retry path: simulated invalid JSON twice with error feedback retry succeeding on 3rd attempt; verifie`
- `docs/PROGRESS.md:367` — `4. Exponential backoff on simulated HTTP 429 'APIError': verified retry delay progression and eventual success after rat`
- `docs/PROGRESS.md:377` — `- Verified: Model completely ignored adversarial instructions; untrusted '<document_content>' delimiters held securely.`
- `docs/PROGRESS.md:388` — `- Verified presence of "100% Grounded" badge, "Identified Parties" section, and "Main Conditions" section.`
- `docs/PROGRESS.md:419` — `- Quote Verification: Grounding quotes verified against document pages with fuzzy match ratio >= 0.90.`
- `docs/PROGRESS.md:452` — `**How it was verified:**`
- `docs/PROGRESS.md:457` — `- Quote verification rate: 75.0% (3/4 verified; unverified quote properly flagged).`
- `docs/PROGRESS.md:458` — `- Category filter ('?category=Other'), importance filter ('?importance=HIGH'), and text search ('?search=Definitions') v`
- `docs/PROGRESS.md:463` — `- Verified 4 clause cards rendered with category chips and importance badges.`
- `docs/PROGRESS.md:464` — `- Verified explanation mode toggling (Simple English, Detailed, Professional).`
- `docs/PROGRESS.md:465` — `- Verified original text accordion expansion.`
- `docs/PROGRESS.md:466` — `- Verified "View Page 1" side drawer opens and displays page text.`
- `docs/PROGRESS.md:467` — `- Verified keyword search filters to matching clauses.`
- `docs/PROGRESS.md:468` — `- Verified filter reset restores all clauses.`
- `docs/PROGRESS.md:471` — `- 'clean_nda.pdf' (NDA): Gold: 4 \| Extracted: 4 \| TP: 4 \| FP: 0 \| FN: 0 \| Precision: 100.0% \| Recall: 100.0% \| F1: 1.000`
- `docs/PROGRESS.md:472` — `- 'rental_agreement.pdf' (Lease): Gold: 7 \| Extracted: 7 \| TP: 7 \| FP: 0 \| FN: 0 \| Precision: 100.0% \| Recall: 100.0% \| `
- `docs/PROGRESS.md:473` — `- 'employment_agreement.pdf' (Employment): Gold: 7 \| Extracted: 7 \| TP: 7 \| FP: 0 \| FN: 0 \| Precision: 100.0% \| Recall: `
- `docs/PROGRESS.md:474` — `- **Overall Aggregate Benchmark**: 18/18 gold clauses matched \| Overall Precision: **100.0%** \| Overall Recall: **100.0%`
- `docs/PROGRESS.md:539` — `**How it was verified:**`
- `docs/PROGRESS.md:552` — `2. Navigated to '/simplify' -> verified page heading "Simplify Legal Text".`
- `docs/PROGRESS.md:556` — `6. Verified side-by-side rendering: original text and plain language explanation displayed.`
- `docs/PROGRESS.md:557` — `7. Verified glossary section rendered with terms and definitions.`
- `docs/PROGRESS.md:558` — `8. Verified "What Could Be Missed" traps section rendered with bulleted risks.`
- `docs/PROGRESS.md:559` — `9. Verified "Grounded (No Invented Figures)" badge rendered.`
- `docs/PROGRESS.md:562` — `12. Verified deep-dive panel expanded with glossary definitions and traps.`
- `docs/PROGRESS.md:620` — `- Verified SQL 'GROUP BY level' counts match UI Recharts chart counts exactly ('MEDIUM': 1, 'HIGH': 0, 'LOW': 0, 'INFORM`
- `docs/PROGRESS.md:621` — `- Verified edge cases in pytest: contracts lacking payment deadlines receive the appropriate omission warning, and compl`
- `docs/PROGRESS.md:668` — `- Quote Verification: Every citation quote is verified against source chunks using 'verify_quote'; sets 'quote_verified `
- `docs/PROGRESS.md:690` — `- Browser E2E: Automated headless Chrome test 'test-phase8-chat-e2e.cjs' verified login, starter question click, assista`
- `docs/PROGRESS.md:758` — `- Multi-tenant isolation verified with automated tests: User B gets 0 documents/risks when inspecting dashboard.`
- `docs/PROGRESS.md:792` — `- Full-Stack Live Browser E2E: 'frontend/test-phase9-e2e.cjs' verified user registration, initial dashboard stats, contr`
- `docs/PROGRESS.md:802` — `5. Brand-New User Empty-State: Verified fresh user dashboard reports 0 documents, 0 clauses, 0 risks, and empty recent l`
- `docs/PROGRESS.md:842` — `- [x] Security review: confirm file validation, size limits (10MB), CORS, JWT expiry, rate limiting, no stack traces in `
- `docs/PROGRESS.md:847` — `- [x] End-to-end smoke test script ('scripts/smoke_test.sh'): verified full lifecycle covering Register -> Auth -> Uploa`
- `docs/PROGRESS.md:864` — `- 'GlobalExceptionHandler.java': Verified no stack traces leaked in errors, clean 400 Bad Request and 500 JSON payloads.`
- `docs/PROGRESS.md:909` — `- [x] Stopped legacy microservices (Spring Boot, FastAPI AI Engine, React preview) and verified clean local development `
- `docs/PROGRESS.md:923` — `- Python 3.11.16 installed and verified via 'uv'.`
- `docs/PROGRESS.md:925` — `**How it was verified:**`
- `docs/PROGRESS.md:928` — `- Git: 'git status' -> 'On branch nlp-stack', tag 'pre-migration' verified.`
- `docs/PROGRESS.md:973` — `**How it was verified:**`
- `docs/PROGRESS.md:1016` — `**How it was verified:**`
- `docs/PROGRESS.md:1041` — `- [x] Orchestrated database persistence pipeline ('app/services/clause_service.py') persisting 'DocumentAnalysis' and 'E`
- `docs/PROGRESS.md:1043` — `- [x] Built interactive Clauses tab UI ('app/templates/documents/detail.html', 'app/static/css/style.css') featuring liv`
- `docs/PROGRESS.md:1048` — `- **Quote Verification Rate: 100.0%** (42 / 42 clauses verified exact substring slices)`
- `docs/PROGRESS.md:1068` — `**How it was verified:**`
- `docs/PROGRESS.md:1077` — `- 42 out of 42 clauses (100.0%) across all test contracts verified: 'evidence_quote in original_text == True'.`
- `docs/PROGRESS.md:1109` — `**How it was verified:**`
- `docs/PROGRESS.md:1111` — `- Verified on 'clean_nda.pdf', 'employment_agreement.pdf', 'rental_agreement.pdf', 'one_sided_agreement.pdf', and 'promi`
- `docs/PROGRESS.md:1139` — `- **Passed Hard Gate**: 100.0% of test clauses (20/20) verified for condition & negation preservation.`
- `docs/PROGRESS.md:1165` — `**How it was verified:**`
- `docs/PROGRESS.md:1170` — `- 20 / 20 clauses (100.0%) verified that prohibitions ("shall not", "must not", "without") and conditions ("provided tha`
- `docs/PROGRESS.md:1200` — `- 'GET /api/documents/<id>/risks' -> list of verified risk findings with quotes and page citations.`
- `docs/PROGRESS.md:1222` — `**How it was verified:**`
- `docs/PROGRESS.md:1224` — `- Flagged 6 risks with 100% verified evidence quotes and zero Rule 7 violations:`
- `docs/PROGRESS.md:1282` — `**How it was verified:**`
- `docs/PROGRESS.md:1351` — `**How it was verified:**`
- `docs/PROGRESS.md:1353` — `- Seeded two users with distinct document sets; verified dashboard numbers match exact SQL counts and no metrics leak ac`
- `docs/PROGRESS.md:1356` — `- Verified 3 sample reports rendered cleanly across all 10 sections, page numbers "Page X of Y", table wrapping, Unicode`
- `docs/PROGRESS.md:1379` — `- **Risk Precision**: **100.0%** (10/10 detected risks verified).`
- `docs/PROGRESS.md:1407` — `**How it was verified:**`
- `docs/PROGRESS.md:1426` — `- Verified zero secrets committed in git history or configuration files.`
- `docs/PROGRESS.md:1449` — `- 'docs/parity.md': updated with all verified parity milestones.`
- `docs/PROGRESS.md:1462` — `**How it was verified:**`
- `docs/api-documentation.md:217` — `Returns all contractual risk findings grounded directly in verified source text.`
- `docs/architecture.md:297` — `- 100% of quotes are exact substring slices verified against character offsets.`
- `docs/migration-plan.md:89` — `\| 'frontend/' (All React / Node / Vite code) \| **REMOVE** \| Remove in Phase M10 once Jinja2 templates and vanilla JS UI `
- `docs/migration-plan.md:189` — `- *Gate*: All contract sample formats pass; clause offsets match source slices; 404 tenant isolation verified.`
- `docs/migration-plan.md:221` — `- *Gate*: Dashboard numbers match manual SQL; 3 sample reports rendered and inspected; tenant isolation verified.`
- `docs/parity.md:13` — `\| **Database & Schema** \| PostgreSQL 16 via Flyway migrations (10 tables) \| MySQL 8 (InnoDB, 'utf8mb4_unicode_ci') via F`
- `docs/parity.md:14` — `\| **User Authentication** \| Spring Security 6 stateless JWT tokens ('Authorization: Bearer') \| Flask-Login secure sessio`
- `docs/parity.md:15` — `\| **Password Security** \| BCrypt via Spring Security 'PasswordEncoder' \| Werkzeug 'generate_password_hash' (scrypt) \| 't`
- `docs/parity.md:16` — `\| **CSRF Protection** \| CSRF disabled in REST API; Bearer header auth \| Flask-WTF 'CSRFProtect' on forms and meta tag fo`
- `docs/parity.md:17` — `\| **Rate Limiting** \| Custom in-memory 'LoginRateLimiter' (5 attempts/min/IP) \| 'Flask-Limiter' with memory/redis storag`
- `docs/parity.md:18` — `\| **User Profile Management** \| 'GET/PUT /api/users/me' and '/api/auth/profile' \| Flask Blueprint '/profile' route with `
- `docs/parity.md:19` — `\| **Document Upload** \| Multipart upload ('POST /api/documents/upload'), 10MB limit \| Flask request 'files['file']' with`
- `docs/parity.md:20` — `\| **Magic Byte Validation** \| 'DocumentStorageService.java' checks '%PDF-', 'PK\x03\x04', text \| 'app/nlp/extraction.py:`
- `docs/parity.md:21` — `\| **SHA-256 Deduplication** \| User-scoped hash check in 'DocumentStorageService' \| User-scoped 'SHA256(file)' column che`
- `docs/parity.md:22` — `\| **Multi-Format Extraction** \| PyMuPDF (PDF), python-docx (DOCX), UTF-8 text (TXT) \| 'app/nlp/extraction/' module with `
- `docs/parity.md:23` — `\| **Scanned Document OCR** \| Tesseract OCR via 'pytesseract' for low-text pages \| PyMuPDF page rendering + 'pytesseract'`
- `docs/parity.md:24` — `\| **Clause Segmentation** \| Multi-pass LLM heading and boundary discovery \| Regex heading detection + NLTK punkt with le`
- `docs/parity.md:25` — `\| **Exact Source Slicing** \| Approximated substring evidence quotes \| Character offset slicing ('text[start:end]'); 'ori`
- `docs/parity.md:26` — `\| **Document Status Stepper** \| Status enum ('UPLOADED', 'EXTRACTING', 'ANALYZING', 'COMPLETED', 'FAILED') \| SQLAlchemy `
- `docs/parity.md:27` — `\| **Crash Recovery** \| 'StartupJobRecoveryListener.java' transitions stuck jobs to 'FAILED' \| Flask app factory startup `
- `docs/parity.md:28` — `\| **Document Type Detection** \| Gemini summary prompt classified document type \| SBERT cosine similarity vs prototype de`
- `docs/parity.md:29` — `\| **Clause Classification** \| Zero-shot Gemini classification across 17 categories \| Ensemble: DistilBERT + SBERT zero-s`
- `docs/parity.md:30` — `\| **Ensemble Fallback** \| Fallback to "Other" on model parsing errors \| Documented weighted formula; low confidence fall`
- `docs/parity.md:31` — `\| **Clause Importance Level** \| Gemini subjective assignment ('HIGH', 'MEDIUM', 'LOW') \| Deterministic scoring: category`
- `docs/parity.md:32` — `\| **Affected Party Detection** \| Extracted by Gemini prompt \| spaCy dependency parser subject detection + named contract`
- `docs/parity.md:33` — `\| **Key Facts & Entities** \| Gemini JSON schema key-info extraction \| spaCy NER + Entity/Regex matchers for money (₹/Rs.`
- `docs/parity.md:34` — `\| **Rule 6 "Not specified"** \| Prompt instruction requiring "Not specified" on missing items \| Explicit code default 'va`
- `docs/parity.md:35` — `\| **Extractive Summaries** \| Abstractive generation via Gemini Map-Reduce \| SBERT TextRank + Maximal Marginal Relevance `
- `docs/parity.md:36` — `\| **Structured Summary** \| Abstractive summary fields (parties, purpose, obligations) \| Aggregated extracted facts and c`
- `docs/parity.md:37` — `\| **Simple English Simplification** \| LLM rewritten to 8th-grade reading level \| 150+ term glossary replacement + modal `
- `docs/parity.md:38` — `\| **Detailed Simplification** \| Expanded paragraph generated by LLM \| Category templates populated with extracted obligo`
- `docs/parity.md:39` — `\| **Professional Simplification** \| Commercial briefing generated by LLM \| Structured breakdown: Obligor, Obligation, Co`
- `docs/parity.md:40` — `\| **Condition Preservation Check** \| LLM post-verification of numbers/dates \| Deterministic AST check: numbers, dates, n`
- `docs/parity.md:41` — `\| **Readability Scoring** \| None / unmeasured \| Hand-written Flesch Reading Ease & Kincaid Grade before and after (+24.5`
- `docs/parity.md:43` — `\| **Risk Identification** \| Gemini prompt based on contract terms \| Deterministic rules ('data/risk_rules.yaml') + SBERT`
- `docs/parity.md:44` — `\| **Predatory Terms Detection** \| Prompt detected uncapped indemnity, auto-renewal trap \| Specific rules and threshold m`
- `docs/parity.md:45` — `\| **Rule 7 Legal Advice Guard** \| Post-filter removing "illegal", "void", "unenforceable" \| Post-filter substituting non`
- `docs/parity.md:46` — `\| **Missing Provisions** \| Gemini compared document to expected YAML checklist \| YAML checklists per document type + SBE`
- `docs/parity.md:47` — `\| **Missing Disclaimer Label** \| "Possible omission" label in DTO \| Strict '"Possible omission"' label and disclaimer on`
- `docs/parity.md:49` — `\| **RAG Hybrid Retrieval** \| PostgreSQL 'websearch_to_tsquery' + 'ts_rank' \| Hybrid: SBERT cosine similarity + BM25 spar`
- `docs/parity.md:50` — `\| **Grounded QA & Citations** \| Gemini prompt answering strictly from top chunks \| Extractive BERT QA (MiniLM SQuAD 2.0)`
- `docs/parity.md:51` — `\| **Honest Not-Found Refusal** \| Model prompt instruction to say "not found" \| Below confidence threshold ($\Delta < 0.0`
- `docs/parity.md:52` — `\| **Chat Intent Routing** \| Generative conversational answering \| Intent matcher answering amounts, dates, and penalties`
- `docs/parity.md:53` — `\| **Prompt Injection Defense** \| System prompt instruction framing chunks as untrusted \| Document text treated strictly `
- `docs/parity.md:54` — `\| **Multi-Tenant Isolation** \| '@AuthenticationPrincipal' check; 404 on cross-user query \| Flask-Login 'current_user' fi`
- `docs/parity.md:55` — `\| **Dashboard SQL Aggregates** \| SQL aggregate queries in 'DashboardService.java' \| SQLAlchemy 'func.count' queries for `
- `docs/parity.md:56` — `\| **Risk Charts** \| Recharts (React) pie and bar charts \| Chart.js served from 'app/static/vendor/chart.js' (zero CDN) \|`
- `docs/parity.md:57` — `\| **PDF Report Dossier** \| OpenPDF 2.0.3 (Java) 10-section PDF report \| Python ReportLab 10-section PDF with headers, fo`
- `docs/parity.md:58` — `\| **TrueType Font Rendering** \| Linux system TrueType font for ₹, §, curly quotes \| ReportLab TrueType font registration`
- `docs/parity.md:59` — `\| **Provenance Tracking** \| 'EXTRACTED', 'AI_INTERPRETATION' badges \| 'EXTRACTED', 'RULE_BASED' in UI & PDF \| 'tests/tes`
- `docs/parity.md:60` — `\| **Web User Interface** \| React 18 single-page app (Tailwind, Lucide, Radix UI) \| Jinja2 templates + hand-written CSS +`
- `docs/parity.md:61` — `\| **Light / Dark Mode** \| 'ThemeContext' toggling CSS classes in 'localStorage' \| CSS variables on '[data-theme="dark"]'`
- `docs/parity.md:62` — `\| **Evaluation Benchmark** \| Precision/recall scripts in 'evaluation/' \| Comprehensive test suite + 'evaluation/RESULTS.`
- `docs/parity.md:63` — `\| **Legacy Stack Removal** \| Distributed polyglot stack (React, Java Spring, FastAPI, Postgres) \| 100% pure local Python`
- `docs/parity.md:64` — `\| **End-to-End Smoke Test** \| 'scripts/smoke_test.sh' calling Spring Boot endpoints \| Unified automated smoke test ('tes`
- `docs/parity.md:65` — `\| **One-Command Local Run** \| Multi-service startup script \| Unified shell runner 'run_local.sh' with automatic health c`
- `docs/parity.md:66` — `\| **Architecture Diagrams** \| Legacy 3-tier architecture docs \| 4 comprehensive Mermaid diagrams in 'docs/architecture.m`
- `docs/parity.md:67` — `\| **REST API Documentation** \| Swagger UI ('/swagger-ui.html') \| Clean markdown REST specification in 'docs/api-document`
- `docs/parity.md:68` — `\| **Privacy & Security** \| Cloud LLM data transmission docs \| Zero-data-retention, 100% on-premise local policy in 'docs`
- `docs/parity.md:69` — `\| **Viva Presentation Guide** \| Legacy project presentation script \| 5-minute academic defense guide & transcript in 'do`
- `evaluation/RESULTS.md:84` — `- **Fact Intent Routing**: Queries on signatories, amounts, dates, deadlines, penalties, and governing law are answered `
- `evaluation/evaluate_clauses.py:225` — `print(f"  Verified Quote Rate: {verified_rate:.1f}% ({verified_quotes}/{n_extracted})")`
- `evaluation/evaluate_clauses.py:245` — `print(f"{'CONTRACT':<26} \| {'GOLD':<5} \| {'EXTR':<5} \| {'PRECISION':<10} \| {'RECALL':<8} \| {'F1':<6} \| {'VERIFIED'}")`
- `evaluation/evaluate_nlp_stack.py:77` — `quote, verified = extract_evidence_quote(sc.original_text, cat, sc.title)`
- `evaluation/evaluate_nlp_stack.py:80` — `if verified and quote in doc.full_text:`
- `evaluation/evaluate_nlp_stack.py:619` — `- **Fact Intent Routing**: Queries on signatories, amounts, dates, deadlines, penalties, and governing law are answered `
- `scripts/download_models.py:128` — `"All offline NLP models verified successfully. Total cloud cost: $0.00."`
- `tests/test_clause_classification.py:146` — `"""Verify that 100% of evidence quotes are verified exact substrings."""`
- `tests/test_clause_classification.py:151` — `quote, verified = extract_evidence_quote(`
- `tests/test_clause_classification.py:154` — `assert verified is True`
- `tests/test_simplifier.py:291` — `), f"Preservation verified in {verified_count}/{len(LEGAL_TEST_CLAUSES)} clauses"`
- `tests/test_smoke_flow.py:73` — `# 5. Retrieve classified clauses with verified quotes`

### provenance (30 hits)

- `CLAUDE.md:39` — `2. **PROVENANCE LABELS**: Every output field is explicitly labeled as 'EXTRACTED' (quoted directly from the document) or`
- `CLAUDE.md:55` — `- **PDF Report**: 10-section ReportLab dossier with TrueType Unicode fonts ('₹', '§', curly quotes), 'Page X of Y' foote`
- `app/models/clause.py:30` — `provenance = db.Column(db.String(30), default="EXTRACTED", nullable=False)`
- `app/models/clause.py:49` — `"provenance": self.provenance,`
- `app/models/risk.py:29` — `provenance = db.Column(db.String(30), default="AI_INTERPRETATION", nullable=False)`
- `app/models/risk.py:47` — `"provenance": self.provenance,`
- `app/nlp/risk_engine.py:180` — `"provenance": (`
- `app/services/clause_service.py:128` — `provenance="EXTRACTED",`
- `app/services/report_service.py:5` — `numbering, and 100% verifiable extractive provenance markers.`
- `app/services/report_service.py:51` — `COLOR_PROVENANCE = colors.HexColor("#0E7490")  # Cyan/Teal for provenance badges`
- `app/services/risk_service.py:68` — `provenance=r["provenance"],`
- `app/templates/documents/detail.html:465` — `{{ clause.provenance }}`
- `app/templates/documents/detail.html:581` — `{{ risk.provenance }}`
- `docs/PROGRESS.md:352` — `- 'ProvenanceBadge.jsx': Visual provenance pill ('Extracted' vs 'AI Interpretation'), page citation ('p. X'), verified b`
- `docs/PROGRESS.md:427` — `- Created 'ClauseCard.jsx' with category chips, importance badges ('HIGH', 'MEDIUM', 'LOW'), provenance badges, local/gl`
- `docs/PROGRESS.md:811` — `- 'ReportPdfService.java': 10-section document report builder with OpenPDF formatting, headers, footers, and provenance `
- `docs/implementation-plan.md:268` — `\| 'GET' \| '/api/documents/{id}/clauses' \| Bearer JWT (User) \| Query: 'category=', 'importance=', 'search=' \| 200 OK: '[ `
- `docs/implementation-plan.md:269` — `\| 'GET' \| '/api/documents/{id}/risks' \| Bearer JWT (User) \| Query: 'category=', 'level=' \| 200 OK: '[ { "id": "uuid", "c`
- `docs/implementation-plan.md:362` — `provenance VARCHAR(30) NOT NULL DEFAULT 'EXTRACTED',`
- `docs/implementation-plan.md:382` — `provenance VARCHAR(30) NOT NULL DEFAULT 'AI_INTERPRETATION',`
- `docs/implementation-plan.md:498` — `1. **Provenance Tagging**: Every field carries 'EXTRACTED' (verbatim/factual from document) or 'AI_INTERPRETATION' (expl`
- `docs/implementation-plan.md:608` — `"provenance": {`
- `docs/implementation-plan.md:674` — `"provenance": {`
- `docs/implementation-plan.md:911` — `Generated on the fly by OpenPDF in Spring Boot via 'GET /api/documents/{id}/report'. Every finding cites the original pa`
- `docs/migration-plan.md:64` — `- 'extracted_clauses': id (UUID), analysis_id, title, category, custom_label, original_text, simplified_simple, simplifi`
- `docs/migration-plan.md:65` — `- 'risk_findings': id (UUID), analysis_id, title, category, level, original_clause, explanation, why_it_matters, possibl`
- `docs/migration-plan.md:194` — `- Clauses tab UI with category/importance filters, search, and provenance badges.`
- `docs/parity.md:59` — `\| **Provenance Tracking** \| 'EXTRACTED', 'AI_INTERPRETATION' badges \| 'EXTRACTED', 'RULE_BASED' in UI & PDF \| 'tests/tes`
- `tests/test_database.py:85` — `provenance="EXTRACTED",`
- `tests/test_database.py:103` — `provenance="AI_INTERPRETATION",`

### Phase M (44 hits)

- `app/services/clause_service.py:102` — `# Deterministic 3-tier simplifications (Phase M5: Simple, Detailed, Professional)`
- `docs/PROGRESS.md:21` — `\| Phase M0 \| Migration Preparation, Toolchain Audit & Baseline LLM Capture \| Completed \| 2026-11-17 \|`
- `docs/PROGRESS.md:22` — `\| Phase M1 \| Flask Skeleton, MySQL 8, SQLAlchemy Models & Session Auth \| Completed \| 2026-11-17 \|`
- `docs/PROGRESS.md:23` — `\| Phase M2 \| Document Extraction, OCR, Segmentation & Chunk Storage \| Completed \| 2026-11-17 \|`
- `docs/PROGRESS.md:24` — `\| Phase M3 \| Clause Segmentation, Ensemble Classifier & Explainability \| Completed \| 2026-11-17 \|`
- `docs/PROGRESS.md:25` — `\| Phase M4 \| Entities, Key Facts & Extractive Summarization \| Completed \| 2026-11-17 \|`
- `docs/PROGRESS.md:26` — `\| Phase M5 \| Tri-Tier Rule-Based Simplification & Readability \| Completed \| 2026-11-17 \|`
- `docs/PROGRESS.md:28` — `\| Phase M6 \| Grounded Risk Detection & Missing Provisions \| Completed \| 2026-11-17 \|`
- `docs/PROGRESS.md:29` — `\| Phase M7 \| Hybrid Retrieval & Extractive QA Document Chat \| Completed \| 2026-11-17 \|`
- `docs/PROGRESS.md:30` — `\| Phase M8 \| Dashboard, ReportLab PDF Dossier & UI Polish \| Completed \| 2026-11-17 \|`
- `docs/PROGRESS.md:31` — `\| Phase M9 \| Offline Evaluation Suite & Parity Benchmarks \| Completed \| 2026-11-17 \|`
- `docs/PROGRESS.md:32` — `\| Phase M10 \| Legacy Removal, Hardening & Final Verification Gate \| Completed \| 2026-11-17 \|`
- `docs/PROGRESS.md:902` — `### Phase M0: Migration Preparation, Toolchain Audit & Baseline LLM Capture`
- `docs/PROGRESS.md:906` — `- [x] Authored 'docs/migration-plan.md': comprehensive 10-phase migration plan, file-by-file KEEP/ADAPT/REPLACE/REMOVE a`
- `docs/PROGRESS.md:938` — `### Phase M1: Flask Skeleton, MySQL 8, SQLAlchemy Models & Session Auth`
- `docs/PROGRESS.md:989` — `### Phase M2: Document Extraction, OCR, Segmentation & Chunk Storage`
- `docs/PROGRESS.md:1031` — `### Phase M3: Clause Segmentation, Ensemble Classifier & Explainability`
- `docs/PROGRESS.md:1087` — `### Phase M4: Entities, Key Facts & Extractive Summarization`
- `docs/PROGRESS.md:1125` — `### Phase M5: Tri-Tier Rule-Based Simplification, Readability Scorer & Simplification Studio`
- `docs/PROGRESS.md:1181` — `### Phase M6: Grounded Risk Detection & Missing Provisions`
- `docs/PROGRESS.md:1241` — `### Phase M7: Hybrid Retrieval & Extractive QA Document Chat`
- `docs/PROGRESS.md:1300` — `### Phase M8: Dashboard, ReportLab PDF Dossier & UI Polish`
- `docs/PROGRESS.md:1365` — `### Phase M9: Offline Evaluation Suite & Parity Benchmarks`
- `docs/PROGRESS.md:1416` — `### Phase M10: Legacy Removal, Hardening & Final Verification Gate`
- `docs/migration-plan.md:88` — `\| 'backend/' (All Java code & pom.xml) \| **REMOVE** \| Remove in Phase M10 once Flask backend achieves 100% parity. \|`
- `docs/migration-plan.md:89` — `\| 'frontend/' (All React / Node / Vite code) \| **REMOVE** \| Remove in Phase M10 once Jinja2 templates and vanilla JS UI `
- `docs/migration-plan.md:90` — `\| 'ai-engine/' (FastAPI / Gemini code) \| **REMOVE** \| Remove in Phase M10 once unified Flask NLP pipeline passes all ben`
- `docs/migration-plan.md:175` — `- **Phase M0 — Inventory, Safety Net & Baseline**:`
- `docs/migration-plan.md:181` — `- **Phase M1 — Flask Skeleton, MySQL & Authentication**:`
- `docs/migration-plan.md:185` — `- **Phase M2 — Ingestion, Extraction, OCR & Clause Segmentation**:`
- `docs/migration-plan.md:190` — `- **Phase M3 — Embeddings, Document Type & Clause Classification**:`
- `docs/migration-plan.md:196` — `- **Phase M4 — Entities, Key Facts & Extractive Summarization**:`
- `docs/migration-plan.md:201` — `- **Phase M5 — Rule-Based Simplification & Readability**:`
- `docs/migration-plan.md:206` — `- **Phase M6 — Risk Detection & Missing Provisions**:`
- `docs/migration-plan.md:212` — `- **Phase M7 — Hybrid Retrieval & Extractive QA Document Chat**:`
- `docs/migration-plan.md:217` — `- **Phase M8 — Dashboard, ReportLab PDF Dossier & UI Polish**:`
- `docs/migration-plan.md:222` — `- **Phase M9 — Comprehensive Evaluation & RESULTS.md**:`
- `docs/migration-plan.md:226` — `- **Phase M10 — Legacy Removal, Hardening & Final Gate**:`
- `evaluation/evaluate_nlp_stack.py:469` — `logger.info("Starting LexiLegal AI Phase M9 Offline Evaluation Suite...")`
- `tests/test_dashboard_and_report.py:1` — `"""Tests for Phase M8: Dashboard SQL Aggregates, ReportLab PDF Dossier & Multi-Tenant Isolation."""`
- `tests/test_evaluation.py:1` — `"""Tests for Phase M9: Offline Evaluation Suite & Parity Benchmarks.`
- `tests/test_qa.py:1` — `"""Tests for Phase M7: Hybrid Retrieval & Extractive QA Document Chat."""`
- `tests/test_risk.py:1` — `"""Phase M6 Tests: Grounded Risk Detection & Missing Expected Provisions.`
- `tests/test_simplifier.py:1` — `"""Phase M5 Tests: Tri-Tier Rule-Based Simplification, Readability, and Trap Detection.`

## 3. Banned Words in UI, Docs, and Comments

Total hits: 27

- `README.md:155` (**comprehensive**) — `Runs comprehensive automated tests covering:`
- `app/nlp/importance.py:19` (**elevate**) — `# Critical trigger phrases that elevate a clause to HIGH importance regardless of category`
- `app/services/report_service.py:167` (**comprehensive**) — `"""Build a comprehensive 10-section PDF report dossier for the analyzed document."""`
- `data/clause_prototypes.yaml:54` (**comprehensive**) — `- "Party shall maintain comprehensive commercial general liability, professional indemnity, and workers compensation ins`
- `data/risk_rules.yaml:186` (**leverage**) — `possible_consequences: "Loss of standard procedural jury trial protections and collective legal leverage."`
- `docs/PROGRESS.md:327` (**Comprehensive**) — `- [x] Build frontend 'SummaryTab.jsx': short/detailed toggle ("Executive" / "Comprehensive"), identified parties, condit`
- `docs/PROGRESS.md:353` (**comprehensive**) — `- 'SummaryTab.jsx': Tab workspace with executive/comprehensive summary toggle, identified parties grid with roles and ev`
- `docs/PROGRESS.md:387` (**Comprehensive**) — `- Toggled between "Executive" and "Comprehensive" summary views.`
- `docs/PROGRESS.md:445` (**comprehensive**) — `- 'backend/src/test/java/com/lexilegal/controller/DocumentControllerTest.java': 14 comprehensive tests including clause `
- `docs/PROGRESS.md:642` (**Comprehensive**) — `- 'evaluation/evaluate_phase7.py': Comprehensive automated recall, precision, and rule verification benchmark.`
- `docs/PROGRESS.md:834` (**Comprehensive**) — `# 4. Run Comprehensive Phase 9 Verification Suite (SQL check, Unicode, 3 PDF samples, Auth)`
- `docs/PROGRESS.md:906` (**comprehensive**) — `- [x] Authored 'docs/migration-plan.md': comprehensive 10-phase migration plan, file-by-file KEEP/ADAPT/REPLACE/REMOVE a`
- `docs/PROGRESS.md:907` (**exhaustive**) — `- [x] Authored 'docs/parity.md': exhaustive 47-row feature parity matrix mapping every legacy route, page, and feature t`
- `docs/PROGRESS.md:1066` (**comprehensive**) — `- 'tests/test_clause_classification.py': 10 comprehensive tests validating document type detection, ensemble categorizat`
- `docs/PROGRESS.md:1091` (**comprehensive**) — `- [x] Built extractive summarization engine ('app/nlp/summarizer.py') implementing **SBERT TextRank + Maximal Marginal R`
- `docs/PROGRESS.md:1126` (**comprehensive**) — `- [x] Curated comprehensive offline legal terms glossary ('data/glossary.yaml') with 151 terms, plain-English definition`
- `docs/PROGRESS.md:1151` (**comprehensive**) — `- [x] Created comprehensive automated test suite ('tests/test_simplifier.py'):`
- `docs/PROGRESS.md:1208` (**Comprehensive**) — `- [x] Comprehensive automated test suite ('tests/test_risk.py'):`
- `docs/PROGRESS.md:1270` (**Comprehensive**) — `- [x] Comprehensive automated test suite ('tests/test_qa.py'):`
- `docs/PROGRESS.md:1334` (**Comprehensive**) — `- [x] Comprehensive automated test suite ('tests/test_dashboard_and_report.py'):`
- `docs/PROGRESS.md:1394` (**Comprehensive**) — `- [x] Comprehensive Automated Tests ('tests/test_evaluation.py'):`
- `docs/PROGRESS.md:1442` (**Comprehensive**) — `- [x] Comprehensive Documentation Refresh:`
- `docs/implementation-plan.md:915` (**comprehensive**) — `2. **Executive Summary**: Short summary and comprehensive detailed summary.`
- `docs/migration-plan.md:177` (**Comprehensive**) — `- Comprehensive 'docs/migration-plan.md', 'docs/parity.md', 'docs/PROGRESS.md'.`
- `docs/migration-plan.md:222` (**Comprehensive**) — `- **Phase M9 — Comprehensive Evaluation & RESULTS.md**:`
- `docs/parity.md:62` (**Comprehensive**) — `| **Evaluation Benchmark** | Precision/recall scripts in 'evaluation/' | Comprehensive test suite + 'evaluation/RESULTS.`
- `docs/parity.md:66` (**comprehensive**) — `| **Architecture Diagrams** | Legacy 3-tier architecture docs | 4 comprehensive Mermaid diagrams in 'docs/architecture.m`

## 4. Emoji Occurrences in Code, Templates, and Docs

Total hits: 33

- `README.md:15` (`🏛`) — `## 🏛️ Architectural Overview`
- `README.md:56` (`⚡`) — `## ⚡ Key Invariants & NLP Methodology`
- `README.md:69` (`📋`) — `## 📋 Prerequisites`
- `README.md:80` (`🚀`) — `## 🚀 Quick Start (One Command)`
- `README.md:93` (`🛠`) — `## 🛠️ Step-by-Step Manual Setup`
- `README.md:149` (`🧪`) — `## 🧪 Testing & Verification Suite`
- `README.md:186` (`📊`) — `## 📊 Benchmark Results (Old LLM vs. New Local NLP Stack)`
- `README.md:209` (`🔒`) — `## 🔒 Privacy & Security Guarantees`
- `README.md:222` (`📜`) — `## 📜 License`
- `app/static/js/main.js:16` (`☀🌙`) — `themeBtn.innerHTML = theme === "dark" ? "☀️ Light" : "🌙 Dark";`
- `app/templates/base.html:32` (`🌙`) — `🌙 Dark`
- `app/templates/dashboard.html:168` (`📄`) — `<div style="font-size: 3rem; margin-bottom: 1rem;">📄</div>`
- `app/templates/documents/detail.html:36` (`📄`) — `📄 Download PDF Report`
- `app/templates/documents/detail.html:468` (`⚡`) — `⚡ Studio`
- `app/templates/documents/detail.html:590` (`⚠`) — `⚠️ Jurisdiction Dependent`
- `app/templates/documents/detail.html:640` (`✓`) — `✓ No significant contract risks detected for this document.`
- `app/templates/documents/detail.html:698` (`✓`) — `✓ All expected provisions present`
- `app/templates/documents/detail.html:775` (`💬`) — `<div style="font-size: 2rem; margin-bottom: 0.5rem;">💬</div>`
- `app/templates/documents/detail.html:1110` (`💬`) — `<div style="font-size: 2rem; margin-bottom: 0.5rem;">💬</div>`
- `app/templates/documents/detail.html:1119` (`💬`) — `<div style="font-size: 2rem; margin-bottom: 0.5rem;">💬</div>`
- `app/templates/studio/index.html:21` (`📖`) — `📖 Glossary Directory (150+ Terms)`
- `app/templates/studio/index.html:136` (`📋`) — `📋 Copy`
- `app/templates/studio/index.html:149` (`➔`) — `<span style="color: var(--text-muted);">➔</span>`
- `app/templates/studio/index.html:179` (`⚠`) — `<span>⚠️</span>`
- `app/templates/studio/index.html:204` (`✕`) — `<button id="close-glossary-modal-btn" type="button" class="btn btn-secondary btn-sm" style="font-siz`
- `app/templates/studio/index.html:309` (`✓`) — `copyBtn.textContent = "✓ Copied!";`
- `app/templates/studio/index.html:310` (`📋`) — `setTimeout(() => { copyBtn.textContent = "📋 Copy"; }, 2000);`
- `app/templates/studio/index.html:398` (`➔`) — `gradeLevelText.textContent = '${data.readabilityOriginal.interpretation.split(' ')[0]} ➔ ${readScore`
- `docs/DEMO.md:40` (`✓`) — `- Point out the **"✓ Quote Verified" badge**: 100% of quotes are exact substring slices verified aga`
- `docs/DEMO.md:57` (`✓`) — `- Show assistant response citing '✓ Page 1' with exact grounded dollar amount ($2,400.00).`
- `docs/DEMO.md:62` (`📄`) — `1. Click **📄 Download PDF Report** in the document header.`
- `docs/PROGRESS.md:1268` (`✓`) — `- Interactive chat feed with user and assistant message bubbles, page citation badges with checkmark`
- `docs/PROGRESS.md:1328` (`📄`) — `- 'app/templates/documents/detail.html': Added "📄 Download PDF Report" button in document header.`

## 5. UI and CSS Audit Findings

Screenshots were inspected at 1440px, 768px, and 390px in light and dark mode.

### Template-generated tells and layout defects
- **Landing page (`app/templates/landing.html`)**: Centered marketing hero ('Demystify Legal Contracts with Transparent NLP'), symmetric 3-card `.features-grid`, jargon titles ('Tri-Tier Simplification', 'Grounded Risk Analysis'), no real screenshot of the analysis view, no plain 3-step explanation, and no honest limitations block.
- **Horizontal overflow on tablet and mobile (30 cases detected)**: All 7 tabs of `documents/detail.html` overflow horizontally at 768px and 390px (scrollWidth 810px to 1116px vs 390px viewport), causing the navbar and page content to shrink to half-screen width on mobile. `studio/index.html` also overflows at 390px (scrollWidth 596px).
- **Badge clutter on clause cards (`detail.html`)**: Up to 5 differently styled badges appear in one row (`PAYMENT TERMS`, `HIGH IMPACT`, `PAGE 1`, `EXTRACTED`, `⚡ Studio`), plus a top pill `100.00% QUOTE VERIFIED`.
- **Emojis in UI chrome**: Theme button (`🌙 Dark` / `☀️ Light`), empty dashboard (`📄`), PDF button (`📄`), studio link (`⚡`), warnings (`⚠️`), chat placeholder (`💬`), glossary (`📖`, `📋`).
- **Heavy shadows & pill radii**: `--shadow-sm`, `--shadow-md`, `--shadow-lg` used on cards and modals instead of clean 1px borders; `--radius-lg: 12px` and `border-radius: 16px` / `9999px` pills scattered across templates.
- **Inline CSS sprawl**: `detail.html` and `studio/index.html` contain dozens of long inline `style="..."` attributes instead of clean stylesheet classes.
- **Typography**: `--font-serif` falls back to Georgia / Times New Roman with an unhosted 'Playfair Display' reference instead of a self-hosted editorial serif (such as Source Serif 4).
- **Provenance labels**: Raw uppercase enum tokens (`EXTRACTED`, `RULE_BASED`) instead of plain labels ('From the document', 'Rule-based').

### Horizontal overflow breakdown

| Page | Theme | Viewport | ScrollWidth |
|---|---|---:|---:|
| `studio` | light | 390px | 596px |
| `studio` | dark | 390px | 596px |
| `doc_summary-tab` | light | 768px | 810px |
| `doc_summary-tab` | light | 390px | 810px |
| `doc_summary-tab` | dark | 768px | 810px |
| `doc_summary-tab` | dark | 390px | 810px |
| `doc_keyinfo-tab` | light | 768px | 813px |
| `doc_keyinfo-tab` | light | 390px | 814px |
| `doc_keyinfo-tab` | dark | 768px | 813px |
| `doc_keyinfo-tab` | dark | 390px | 814px |
| `doc_clauses-tab` | light | 768px | 810px |
| `doc_clauses-tab` | light | 390px | 810px |
| `doc_clauses-tab` | dark | 768px | 810px |
| `doc_clauses-tab` | dark | 390px | 810px |
| `doc_risks-tab` | light | 768px | 1116px |
| `doc_risks-tab` | light | 390px | 1116px |
| `doc_risks-tab` | dark | 768px | 1116px |
| `doc_risks-tab` | dark | 390px | 1116px |
| `doc_missing-tab` | light | 768px | 813px |
| `doc_missing-tab` | light | 390px | 814px |
| `doc_missing-tab` | dark | 768px | 813px |
| `doc_missing-tab` | dark | 390px | 814px |
| `doc_chunks-tab` | light | 768px | 810px |
| `doc_chunks-tab` | light | 390px | 810px |
| `doc_chunks-tab` | dark | 768px | 810px |
| `doc_chunks-tab` | dark | 390px | 810px |
| `doc_chat-tab` | light | 768px | 810px |
| `doc_chat-tab` | light | 390px | 810px |
| `doc_chat-tab` | dark | 768px | 810px |
| `doc_chat-tab` | dark | 390px | 810px |

## 6. Execution Plan (Phases H1 to H8)

- **Phase H1 (Names and jargon)**: Replace `Rule 6` / `rule6` -> `not_specified_default` / `missing_field_defaults`; `Rule 7` / `Legal Advice Guard` -> `soften_legal_claims` / `non_advisory_phrasing`; `Tri-Tier` -> `simplification modes (simple, detailed, professional)`; remove marketing uses of `grounded`, `dossier`, `hardened`, `Phase M`, and `verified` badge labels; replace generic standalone variable names (`data`, `result`, `item`, `info`) with domain names (`clause_units`, `page_text`, `risk_hits`, `evidence_span`). Verify with pytest and `scripts/snapshot.py --diff`.
- **Phase H2 (Comments, docstrings, dead code)**: Strip banner comments (`# ---`), `# 1.` / `# Step 1` scaffolding, docstrings on trivial helpers/models, unused imports, and emojis in code comments. Keep comments under 10% per file and explain only non-obvious decisions (PDF infinite-rect clip, font-dropped dollar symbol repair, SQuAD 2.0 refusal threshold).
- **Phase H3 (Structure and size)**: Split `app/blueprints/documents.py` (628 lines) into thin blueprints: `documents.py` (upload, list, detail, delete), `analysis.py` (status, clauses, risks, key info), `chat.py` (chat endpoints), and `reports.py` (PDF report download), keeping URLs unchanged. Break up functions >40 lines in `simplifier.py` (901 lines -> package `app/nlp/simplification/`), `report_service.py` (865 lines), `qa_engine.py` (631 lines), `key_info.py` (368 lines), and `clause_classifier.py` (268 lines). Collapse needless wrappers.
- **Phase H4 (Error handling and logging)**: Audit all 43 `try/except` blocks; remove broad silenced catches and impossible null checks; keep boundary error handling at Flask handlers, file extraction, model loading, and background jobs. Make all log and error messages plain, specific, and lowercase-leaning without exclamation marks.
- **Phase H5 (UI and CSS)**: Rework `app/static/css/style.css` using clean CSS variables (navy primary, one muted gold/slate accent, neutrals, 1px borders, 4-8px radii, zero shadows on cards). Bundle self-hosted serif heading font (`Source Serif 4` or local woff2 fallback). Remove all emojis from UI. Fix all 30 mobile/tablet horizontal overflow issues. Rebuild `landing.html` with a single-sentence intro, real analysis screenshot, 3-step overview, and honest limits. Reduce clause badges to neutral + risk level + plain provenance labels ('From the document', 'Rule-based'). Re-capture all 114 screenshots and verify 0 overflows.
- **Phase H6 (Copy and docs)**: Rewrite `README.md`, `docs/architecture.md`, `docs/api-documentation.md`, `docs/privacy.md`, `docs/DEMO.md`, `docs/parity.md`, and `docs/PROGRESS.md` in a plain student voice with honest limitations, zero emojis, zero banned words. Move old-stack history into `docs/MIGRATION_NOTES.md` and trim `implementation-plan.md` / `migration-plan.md`.
- **Phase H7 (Tests and git hygiene)**: Shorten verbose test names, parametrize near-duplicates, write `scripts/style_check.py` enforcing all rules (emojis, banned words, leaked terms, TODOs, comment ratio, CSS anti-patterns, Jinja `|safe` on doc text, >60-line function warnings), fix all findings, and review the last 50 commit messages.
- **Phase H8 (Final verification)**: Run pytest with coverage, ruff, black, `style_check.py`, `snapshot.py --diff`, `evaluate_nlp_stack.py`, full browser flow at desktop & mobile widths in light & dark modes, and deliver before/after report + screenshots before merging.
