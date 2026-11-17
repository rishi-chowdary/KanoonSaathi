"""LexiLegal AI — Tri-Tier Rule-Based Legal Simplifier.

Provides deterministic, offline simplification without generative LLMs:
1. Simple English (6th–8th grade plain language, glossary substitutions, short sentences)
2. Detailed (contextual explanation of duties, background rationale, and risks)
3. Professional (structured legal breakdown: Obligor, Obligation, Conditions, Exceptions, Timeline, Remedies)

Hard Invariant:
- Condition and Negation Preservation: Ensures 'shall not', 'unless', 'except', and conditions
  are never inverted. If a rule template fails verification, falls back to safe lexical replacement.
"""

from __future__ import annotations

import os
import re
from functools import lru_cache
from typing import Any

import yaml

from app.nlp.readability import calculate_readability
from app.nlp.segmentation import legal_sentence_tokenizer

_GLOSSARY_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "glossary.yaml"
)

# Standard legalese phrase substitutions (ordered from most specific multi-word to general)
LEGALESE_REPLACEMENTS: list[tuple[re.Pattern, str]] = [
    # Redundancy triplets and doublets
    (
        re.compile(r"\bindemnify,\s*defend,\s*and\s*hold harmless\b", re.IGNORECASE),
        "protect, defend, and pay legal costs for",
    ),
    (
        re.compile(r"\bindemnify\s+and\s+hold harmless\b", re.IGNORECASE),
        "protect and pay legal costs for",
    ),
    (re.compile(r"\bhold harmless\b", re.IGNORECASE), "protect from liability"),
    (re.compile(r"\bfrom and against\b", re.IGNORECASE), "against"),
    (re.compile(r"\bany and all\b", re.IGNORECASE), "all"),
    (
        re.compile(r"\barising out of or resulting from\b", re.IGNORECASE),
        "resulting from",
    ),
    (
        re.compile(r"\barising out of or in connection with\b", re.IGNORECASE),
        "related to",
    ),
    (re.compile(r"\barising out of\b", re.IGNORECASE), "resulting from"),
    (re.compile(r"\bterms and conditions\b", re.IGNORECASE), "terms"),
    (re.compile(r"\bcovenants and agrees that\b", re.IGNORECASE), "agrees that"),
    (re.compile(r"\bagrees and covenants that\b", re.IGNORECASE), "agrees that"),
    (re.compile(r"\bcovenants and agrees\b", re.IGNORECASE), "agrees"),
    (re.compile(r"\bcovenants and warranties\b", re.IGNORECASE), "promises"),
    (re.compile(r"\bnull and void\b", re.IGNORECASE), "invalid"),
    (re.compile(r"\bforce and effect\b", re.IGNORECASE), "effect"),
    (re.compile(r"\bsole and exclusive\b", re.IGNORECASE), "exclusive"),
    (re.compile(r"\bcosts,\s*and\s*expenses\b", re.IGNORECASE), "and costs"),
    (re.compile(r"\bbreach or default\b", re.IGNORECASE), "breach"),
    # Full standard legal boilerplate patterns
    (
        re.compile(
            r"\bno waiver of any breach or default of any term, condition, or covenant of this Agreement shall be deemed to constitute a waiver of any other subsequent breach or default\b",
            re.IGNORECASE,
        ),
        "Forgiving one contract breach does not count as waiving any future breach",
    ),
    (
        re.compile(
            r"\bno supplement, modification, amendment, or alteration of this Agreement shall be binding unless executed in writing by authorized representatives of both parties\b",
            re.IGNORECASE,
        ),
        "No changes to this agreement are valid unless agreed and signed in writing by both parties",
    ),
    (
        re.compile(
            r"\bconstitutes the entire and sole agreement between the parties with respect to the subject matter hereof and supersedes all prior agreements, representations, and understandings, whether written or oral\b",
            re.IGNORECASE,
        ),
        "is the complete agreement between the parties. It replaces all earlier talks and written agreements",
    ),
    (
        re.compile(
            r"\ball rights and remedies provided in this Agreement are cumulative and not exclusive of any other rights or remedies that may be available to the parties at law or in equity\b",
            re.IGNORECASE,
        ),
        "All legal rights in this agreement are cumulative and not exclusive. They add to any other rights allowed by law",
    ),
    (
        re.compile(
            r"\bshall survive the termination or expiration of this Agreement for any reason\b",
            re.IGNORECASE,
        ),
        "will stay in effect even after this agreement ends",
    ),
    (
        re.compile(r"\bthe provisions of Sections\b", re.IGNORECASE),
        "The terms in Sections",
    ),
    (
        re.compile(
            r"\bwhich consent shall not be unreasonably withheld\b", re.IGNORECASE
        ),
        ". Consent must not be held back without good reason",
    ),
    (
        re.compile(r"\bdisclaims all warranties, express or implied\b", re.IGNORECASE),
        "rejects all warranties",
    ),
    (
        re.compile(
            r"\bincluding the implied warranties of merchantability and fitness for a particular purpose\b",
            re.IGNORECASE,
        ),
        ". This includes any implied promise that the product or service works or fits a specific use",
    ),
    (
        re.compile(
            r"\bfailure or delay in the performance of its obligations hereunder\b",
            re.IGNORECASE,
        ),
        "delay in meeting its duties",
    ),
    (
        re.compile(r"\bby reason of acts of God\b", re.IGNORECASE),
        "due to natural disasters",
    ),
    (
        re.compile(
            r"\ball notices, requests, consents, and other communications hereunder\b",
            re.IGNORECASE,
        ),
        "All formal notices under this agreement",
    ),
    (
        re.compile(r"\band shall be deemed to have been duly given\b", re.IGNORECASE),
        ". They are considered delivered",
    ),
    (
        re.compile(
            r"\bwhen delivered by hand or sent by certified mail, postage prepaid, return receipt requested\b",
            re.IGNORECASE,
        ),
        "when delivered in person or sent by certified mail",
    ),
    (
        re.compile(
            r"\beven if advised of the possibility of such damages\b", re.IGNORECASE
        ),
        ". This applies even if warned that such damages could happen",
    ),
    (
        re.compile(r"\bin no event shall either party be liable\b", re.IGNORECASE),
        "Neither party will be liable",
    ),
    (
        re.compile(
            r"\ball inventions, improvements, software, designs, and patentable works conceived or developed by\b",
            re.IGNORECASE,
        ),
        "All inventions, software, and designs created by",
    ),
    (
        re.compile(
            r"\bshall be deemed work made for hire and shall belong exclusively to\b",
            re.IGNORECASE,
        ),
        "are considered work made for hire. They belong exclusively to",
    ),
    (
        re.compile(r"\band shall belong exclusively to\b", re.IGNORECASE),
        ". They belong exclusively to",
    ),
    # Common contract boilerplate phrases
    (
        re.compile(
            r"\bwithout (?:the )?(?:express )?prior written consent of\b", re.IGNORECASE
        ),
        "without written permission from",
    ),
    (
        re.compile(r"\bexpress prior written consent\b", re.IGNORECASE),
        "written permission",
    ),
    (re.compile(r"\bprior written consent\b", re.IGNORECASE), "written permission"),
    (
        re.compile(
            r"\bwithout giving effect to any principles of conflicts of law\b",
            re.IGNORECASE,
        ),
        "without applying conflict of laws rules",
    ),
    (
        re.compile(
            r"\bwithout regard to conflict(?:s)? of law(?:s)? principles\b",
            re.IGNORECASE,
        ),
        "without applying conflict of laws rules",
    ),
    (
        re.compile(
            r"\bwithout regard to its conflict(?:s)? of law(?:s)? provisions\b",
            re.IGNORECASE,
        ),
        "without applying conflict of laws rules",
    ),
    (re.compile(r"\bcourt of competent jurisdiction\b", re.IGNORECASE), "court"),
    (
        re.compile(
            r"\bsuch provision shall be (?:deemed )?severed(?: and deleted)?\b",
            re.IGNORECASE,
        ),
        "that clause will be removed",
    ),
    (
        re.compile(r"\bshall continue in full force and effect\b", re.IGNORECASE),
        "will continue in full effect",
    ),
    (
        re.compile(r"\bcontinue in full force and effect\b", re.IGNORECASE),
        "continue in full effect",
    ),
    (re.compile(r"\bmaterial term or condition\b", re.IGNORECASE), "important term"),
    (re.compile(r"\bmaterial breach\b", re.IGNORECASE), "serious breach"),
    (
        re.compile(r"\bafter receipt of written notice\b", re.IGNORECASE),
        "after receiving written notice",
    ),
    (re.compile(r"\bspecifying the default\b", re.IGNORECASE), "explaining the breach"),
    (
        re.compile(r"\bfails to cure such breach\b", re.IGNORECASE),
        "fails to fix the problem",
    ),
    (re.compile(r"\bfails to cure\b", re.IGNORECASE), "fails to fix the issue"),
    (re.compile(r"\bfor a period of\b", re.IGNORECASE), "for"),
    (
        re.compile(r"\bfollowing termination of employment\b", re.IGNORECASE),
        "after employment ends",
    ),
    (re.compile(r"\bfollowing termination\b", re.IGNORECASE), "after termination"),
    (re.compile(r"\bperform services for\b", re.IGNORECASE), "work for"),
    (re.compile(r"\bengage in\b", re.IGNORECASE), "participate in"),
    (
        re.compile(r"\bdisclose, reproduce, summarize, or distribute\b", re.IGNORECASE),
        "share, copy, summarize, or distribute",
    ),
    (
        re.compile(r"\bdisclose, reproduce, or distribute\b", re.IGNORECASE),
        "share, copy, or distribute",
    ),
    (re.compile(r"\bterminate this Agreement\b", re.IGNORECASE), "end this agreement"),
    (re.compile(r"\bterminate\b", re.IGNORECASE), "end"),
    (re.compile(r"\bterminates\b", re.IGNORECASE), "ends"),
    (re.compile(r"\btermination\b", re.IGNORECASE), "ending"),
    (re.compile(r"\bcalendar days\b", re.IGNORECASE), "days"),
    (re.compile(r"\bsolely for the purpose of\b", re.IGNORECASE), "only for"),
    (
        re.compile(r"\bsolely for the Purpose\b", re.IGNORECASE),
        "only for the agreed purpose",
    ),
    # Latin and archaic terms
    (
        re.compile(r"\bnotwithstanding anything to the contrary\b", re.IGNORECASE),
        "regardless of other terms",
    ),
    (
        re.compile(
            r"\bwithout limiting the generality of the foregoing\b", re.IGNORECASE
        ),
        "specifically including",
    ),
    (re.compile(r"\bin witness whereof\b", re.IGNORECASE), "to confirm this agreement"),
    (re.compile(r"\bmutatis mutandis\b", re.IGNORECASE), "with necessary changes"),
    (re.compile(r"\binter alia\b", re.IGNORECASE), "among other things"),
    (re.compile(r"\bdeemed to be\b", re.IGNORECASE), "considered"),
    (re.compile(r"\bby reason of\b", re.IGNORECASE), "because of"),
    (re.compile(r"\bfor the duration of\b", re.IGNORECASE), "during"),
    (re.compile(r"\bforthwith\b", re.IGNORECASE), "immediately"),
    (re.compile(r"\bpursuant to\b", re.IGNORECASE), "under"),
    (re.compile(r"\bin accordance with\b", re.IGNORECASE), "following"),
    (re.compile(r"\bwithout limitation\b", re.IGNORECASE), "including"),
    (re.compile(r"\bset forth in\b", re.IGNORECASE), "stated in"),
    (
        re.compile(r"\bto the extent permitted by law\b", re.IGNORECASE),
        "as allowed by law",
    ),
    (
        re.compile(r"\bin no event shall\b", re.IGNORECASE),
        "under no circumstances will",
    ),
    # Deictic references
    (re.compile(r"\bhereinabove\b", re.IGNORECASE), "earlier in this document"),
    (re.compile(r"\bhereinafter\b", re.IGNORECASE), "later in this document"),
    (re.compile(r"\bheretofore\b", re.IGNORECASE), "before this"),
    (re.compile(r"\bherein\b", re.IGNORECASE), "in this agreement"),
    (re.compile(r"\bhereof\b", re.IGNORECASE), "of this agreement"),
    (re.compile(r"\bhereto\b", re.IGNORECASE), "to this agreement"),
    (re.compile(r"\bhereunder\b", re.IGNORECASE), "under this agreement"),
    (re.compile(r"\bthereunder\b", re.IGNORECASE), "under that"),
    (re.compile(r"\bthereof\b", re.IGNORECASE), "of that"),
    (re.compile(r"\bthereto\b", re.IGNORECASE), "to that"),
    # Discretion and modals
    (re.compile(r"\bat its sole discretion\b", re.IGNORECASE), "at its own choice"),
    (re.compile(r"\bat their sole discretion\b", re.IGNORECASE), "at their own choice"),
    (re.compile(r"\bsole and absolute discretion\b", re.IGNORECASE), "sole choice"),
    (re.compile(r"\bshall not\b", re.IGNORECASE), "must not"),
    (re.compile(r"\bshall be entitled to\b", re.IGNORECASE), "has the right to"),
    (re.compile(r"\bshall be required to\b", re.IGNORECASE), "must"),
    (re.compile(r"\bshall be deemed\b", re.IGNORECASE), "will be considered"),
    (re.compile(r"\bshall\b", re.IGNORECASE), "must"),
    (re.compile(r"\bin the event that\b", re.IGNORECASE), "if"),
    (re.compile(r"\bin the event of\b", re.IGNORECASE), "in case of"),
    (re.compile(r"\bprior to\b", re.IGNORECASE), "before"),
    (re.compile(r"\bsubsequent to\b", re.IGNORECASE), "after"),
]

# Negation and Condition patterns for strict preservation check
NEGATION_PATTERNS = [
    re.compile(
        r"\b(not|never|no|cannot|neither|nor|prohibit|prohibited|refrain|shall not|must not|may not|without)\b",
        re.IGNORECASE,
    )
]

CONDITION_PATTERNS = [
    re.compile(
        r"\b(unless|except|provided that|provided however|subject to|conditioned upon|in the event|only if)\b",
        re.IGNORECASE,
    )
]


@lru_cache(maxsize=1)
def get_glossary() -> dict[str, dict[str, str]]:
    """Load the legal terms glossary from data/glossary.yaml. Cached singleton."""
    if not os.path.exists(_GLOSSARY_PATH):
        return {}
    with open(_GLOSSARY_PATH, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data.get("terms", {})


@lru_cache(maxsize=1)
def get_sorted_glossary_terms() -> list[tuple[str, str, str, str]]:
    """Return glossary terms sorted by string length descending (term, plain_replacement, definition, category)."""
    glossary = get_glossary()
    items = []
    for term, meta in glossary.items():
        items.append(
            (
                term,
                meta.get("plain_replacement", term),
                meta.get("definition", ""),
                meta.get("category", "General"),
            )
        )
    items.sort(key=lambda x: len(x[0]), reverse=True)
    return items


def extract_clause_glossary(text: str) -> list[dict[str, str]]:
    """Find all glossary terms present in text and return definitions."""
    if not text:
        return []
    terms = get_sorted_glossary_terms()
    found: list[dict[str, str]] = []
    seen: set[str] = set()

    for term, replacement, definition, category in terms:
        pattern = rf"\b{re.escape(term)}\b"
        if re.search(pattern, text, re.IGNORECASE) and term.lower() not in seen:
            seen.add(term.lower())
            found.append(
                {
                    "term": term,
                    "plain_replacement": replacement,
                    "definition": definition,
                    "category": category,
                }
            )
    return found


def detect_traps_and_nuances(text: str) -> list[dict[str, str]]:
    """Detect hidden risks, one-sided terms, and subtle clauses in contractual text."""
    traps: list[dict[str, str]] = []
    if not text:
        return traps

    text_lower = text.lower()

    # 1. Uncapped Indemnity
    if re.search(r"\b(indemnif|hold harmless)\b", text_lower) and not re.search(
        r"\b(liability cap|aggregate liability|capped at|not to exceed|maximum liability)\b",
        text_lower,
    ):
        traps.append(
            {
                "trap": "Uncapped Indemnification",
                "severity": "HIGH",
                "explanation": "This clause obligates defense or payment of damages without an explicit dollar cap, exposing you to unlimited financial liability.",
            }
        )

    # 2. Unilateral Modification
    if re.search(
        r"\b(sole discretion|reserves the right to (?:modify|amend|alter|change)|without (?:prior )?notice)\b",
        text_lower,
    ) and ("modify" in text_lower or "amend" in text_lower or "change" in text_lower):
        traps.append(
            {
                "trap": "Unilateral Modification",
                "severity": "HIGH",
                "explanation": "One party reserves the right to alter contract terms at will without requiring mutual consent or advance notice.",
            }
        )

    # 3. Automatic Renewal / Evergreen
    if re.search(
        r"\b(automatically renew|perpetual|evergreen|automatic extension)\b", text_lower
    ):
        traps.append(
            {
                "trap": "Automatic Renewal / Evergreen Clause",
                "severity": "MEDIUM",
                "explanation": "The agreement renews automatically. You must track the cancellation window carefully to avoid unwanted rollover.",
            }
        )

    # 4. Short Notice / Cure Window (<= 7 days)
    cure_match = re.search(
        r"\b(?:within|prior to)\s+(\d+|three|five|seven)\s+(?:business\s+)?days\b",
        text_lower,
    )
    if cure_match and (
        "cure" in text_lower or "default" in text_lower or "notice" in text_lower
    ):
        traps.append(
            {
                "trap": "Abnormally Short Notice / Cure Window",
                "severity": "MEDIUM",
                "explanation": f"Notice or cure window is restricted to {cure_match.group(0)}, which offers very little time to remedy a disputed breach.",
            }
        )

    # 5. Waiver of Jury Trial or Class Action
    if re.search(
        r"\b(waive(?:s)? (?:any )?right to (?:a )?jury trial|class action waiver|no jury trial)\b",
        text_lower,
    ):
        traps.append(
            {
                "trap": "Waiver of Jury Trial / Class Action",
                "severity": "MEDIUM",
                "explanation": "You forfeit your constitutional right to a jury trial and may be prohibited from joining class-action lawsuits.",
            }
        )

    # 6. Liquidated Damages / Forfeiture
    if re.search(
        r"\b(liquidated damages|forfeited as liquidated damages|penalty amount)\b",
        text_lower,
    ):
        traps.append(
            {
                "trap": "Pre-Agreed Financial Penalties (Liquidated Damages)",
                "severity": "MEDIUM",
                "explanation": "Predetermined penalty amount will be assessed immediately upon breach, even if actual damages are significantly lower.",
            }
        )

    # 7. Broad Restrictive Scope (> 1 year or worldwide)
    if re.search(
        r"\b(non-compete|non-competition|restrictive covenant)\b", text_lower
    ) and (
        re.search(r"\b(two|three|five|2|3|5)\s+years\b", text_lower)
        or "worldwide" in text_lower
    ):
        traps.append(
            {
                "trap": "Extensive Non-Compete Scope",
                "severity": "HIGH",
                "explanation": "The non-compete restricts your post-contract work over an expansive duration or geographic area.",
            }
        )

    # 8. Broad Confidentiality Survival in Perpetuity
    if re.search(r"\b(confidentiality|non-disclosure)\b", text_lower) and re.search(
        r"\b(in perpetuity|indefinitely|without limitation of time|survive forever)\b",
        text_lower,
    ):
        traps.append(
            {
                "trap": "Perpetual Confidentiality Burden",
                "severity": "LOW",
                "explanation": "Secrecy obligations continue forever rather than expiring after a typical 2 to 5 year period.",
            }
        )

    return traps


def lexical_simplify(text: str) -> str:
    """Safe lexical simplification: replaces legalese phrases and glossary terms without altering sentence syntax."""
    if not text:
        return ""

    out = text

    # 1. Apply phrase replacements first (multi-word patterns)
    for pattern, repl in LEGALESE_REPLACEMENTS:
        out = pattern.sub(repl, out)

    # 2. Apply single-word glossary replacements where appropriate
    terms = get_sorted_glossary_terms()
    for term, plain, _, _ in terms:
        # Only substitute if plain replacement is concise (<= 3 words) and different
        if plain.lower() != term.lower() and len(plain.split()) <= 3:
            p = re.compile(rf"\b{re.escape(term)}\b", re.IGNORECASE)
            out = p.sub(plain, out)

    # Clean double spaces
    out = re.sub(r"\s+", " ", out).strip()
    return out


def verify_preservation(original_text: str, candidate_text: str) -> bool:
    """Check that negations and conditions in the original text are preserved in the simplified text.

    If the original had a strict prohibition (e.g. 'shall not disclose'), the simplified version
    must contain a negation ('must not', 'cannot', 'not').
    """
    if not original_text or not candidate_text:
        return True

    # 1. Negation Check
    orig_has_neg = any(p.search(original_text) for p in NEGATION_PATTERNS)
    cand_has_neg = any(p.search(candidate_text) for p in NEGATION_PATTERNS)

    if orig_has_neg and not cand_has_neg:
        return False

    # 2. Condition Check
    orig_has_cond = any(p.search(original_text) for p in CONDITION_PATTERNS)
    cand_has_cond = any(
        re.search(
            r"\b(unless|except|if|provided|subject to|conditioned|when|in case|however)\b",
            candidate_text,
            re.IGNORECASE,
        )
        for _ in [1]
    )

    return not (orig_has_cond and not cand_has_cond)


def split_into_plain_sentences(text: str) -> list[str]:
    """Break legal clauses into short, standalone sentences (10-22 words each)."""
    raw_sentences = legal_sentence_tokenizer.tokenize(text)
    out_sentences: list[str] = []

    for raw in raw_sentences:
        s = raw.strip()
        if not s:
            continue

        # Split condition and coordination markers
        s = re.sub(
            r",\s*provided that\s+",
            ". However, this applies only if ",
            s,
            flags=re.IGNORECASE,
        )
        s = re.sub(
            r",\s*provided however that\s+", ". However, ", s, flags=re.IGNORECASE
        )
        s = re.sub(
            r",\s*subject to\s+", ". This is subject to ", s, flags=re.IGNORECASE
        )
        s = re.sub(
            r",\s*unless\s+", ". This does not apply if ", s, flags=re.IGNORECASE
        )
        s = re.sub(
            r",\s*except that\s+", ". An exception is that ", s, flags=re.IGNORECASE
        )
        s = re.sub(
            r",\s*or from any\s+", ". This also covers any ", s, flags=re.IGNORECASE
        )
        s = re.sub(
            r",\s*and fails to cure\s+",
            ". The breaching party must fix ",
            s,
            flags=re.IGNORECASE,
        )
        s = re.sub(
            r",\s*and (?:shall|must) use such\s+",
            ". The party must use this ",
            s,
            flags=re.IGNORECASE,
        )

        # Split on semicolons or enumerated bullet markers: "; (a) " or "; "
        sub_parts = re.split(r";\s*(?:\([a-z0-9]+\)\s*|\b(?:and|or)\b\s*)?|;\s*", s)
        for part in sub_parts:
            p = part.strip()
            if not p:
                continue

            # If still long (> 28 words), split on coordinating conjunctions with a subject determiner
            words = p.split()
            if len(words) > 28:
                conj_split = re.split(
                    r",\s+(?:and|or|but)\s+(?=(?:the|each|neither|either|all|both|this|such|a|an)\b)",
                    p,
                    maxsplit=2,
                    flags=re.IGNORECASE,
                )
                if len(conj_split) > 1:
                    for c_part in conj_split:
                        cp = c_part.strip()
                        if cp:
                            cp_clean = cp[0].upper() + cp[1:]
                            if not cp_clean.endswith((".", "!", "?")):
                                cp_clean += "."
                            out_sentences.append(cp_clean)
                    continue

            # Format single part
            p_clean = p[0].upper() + p[1:]
            if not p_clean.endswith((".", "!", "?")):
                p_clean += "."
            out_sentences.append(p_clean)

    return out_sentences


def simplify_simple_english(
    original_text: str, category: str = "", affected_party: str = ""
) -> str:
    """Generate a Simple English explanation (6th-8th grade reading level).

    Replaces legalese with plain glossary definitions, simplifies modal verbs,
    and splits run-on sentences into crisp statements.
    """
    if not original_text or not original_text.strip():
        return ""

    # 1. Lexical and phrase substitutions
    simplified = lexical_simplify(original_text)

    # 2. Sentence splitting and restructuring
    sentences = split_into_plain_sentences(simplified)
    result = " ".join(sentences)

    # 3. Clean up spacing and punctuation
    result = re.sub(r"\s+", " ", result)
    result = re.sub(r"\s+([.,;:!?])", r"\1", result)
    result = re.sub(r"\.{2,}", ".", result).strip()

    # 4. Invariant Verification: if preservation failed, return safe lexical simplify
    if not verify_preservation(original_text, result):
        result = lexical_simplify(original_text)

    return result


def simplify_detailed(
    original_text: str, category: str = "", affected_party: str = ""
) -> str:
    """Generate a Detailed contextual explanation of the clause.

    Explains what the clause requires, practical implications, and exceptions.
    """
    if not original_text or not original_text.strip():
        return ""

    cat_upper = category.upper()
    party_str = (
        affected_party
        if affected_party and affected_party != "Unknown"
        else "The responsible party"
    )

    # Extract numbers or deadlines from the clause
    days_match = re.findall(
        r"\b(\d+|thirty|sixty|ninety|ten|fifteen)\s+(?:business\s+)?days\b",
        original_text,
        re.IGNORECASE,
    )
    amounts_match = re.findall(r"[\$₹€£]\s*[\d,]+(?:\.\d{2})?", original_text)

    # Base lexical simplification for readable context
    lex_text = lexical_simplify(original_text)

    # Contextual category narratives
    category_intros: dict[str, str] = {
        "INDEMNITY": f"This indemnification provision defines how legal liabilities and defense costs are allocated. Specifically, {party_str} promises to reimburse and defend the other party against legal claims, damages, and attorney fees arising from contract breaches or operational activities.",
        "CONFIDENTIALITY": f"This confidentiality covenant protects proprietary business information from disclosure. {party_str} is legally bound to keep proprietary disclosures secret and use them exclusively for authorized contract purposes.",
        "TERMINATION": "This clause establishes the formal exit procedures for ending this contract. It specifies the conditions required to cancel the agreement, required advance notice, and whether a cure period is granted to fix contract defaults.",
        "GOVERNING_LAW": "This choice of law clause designates which jurisdiction's courts and statutory laws govern any legal dispute. The parties agree to submit exclusively to these courts, avoiding cross-jurisdictional conflicts.",
        "NON_COMPETE": f"This restrictive covenant limits post-employment or post-business competitive activities for {party_str}. It defines the restricted industry scope, duration, and geographic boundaries to protect trade secrets.",
        "PAYMENT": "This financial clause sets the binding monetary terms. It details the payment schedule, invoicing procedures, acceptable payment methods, and any interest penalties for late payments.",
        "LIABILITY": "This limitation of liability clause restricts monetary damages if a legal breach occurs. It typically excludes consequential or indirect damages and caps total liability to protect against excessive lawsuits.",
        "FORCE_MAJEURE": "This force majeure clause excuses performance failures caused by unforeseeable emergencies beyond human control, such as natural disasters, war, strikes, or governmental restrictions.",
        "SEVERABILITY": "This severability provision ensures contract continuity. If a judge or arbitrator strikes down any single clause as illegal or unenforceable, all remaining clauses continue in full legal force.",
    }

    intro = category_intros.get(
        cat_upper,
        f"This {category or 'contractual'} clause establishes binding terms and requirements that directly apply to {party_str}.",
    )

    details = []
    if days_match:
        unique_days = list(dict.fromkeys(days_match))
        details.append(
            f"Specified timelines include notice or compliance windows of {', '.join(unique_days)} days."
        )
    if amounts_match:
        unique_amounts = list(dict.fromkeys(amounts_match))
        details.append(
            f"Financial commitments or caps noted in the text include {', '.join(unique_amounts)}."
        )

    # Core plain content
    sentences = split_into_plain_sentences(lex_text)
    core_content = " ".join(sentences[:3])

    full_detailed = f"{intro}\n\nCore Terms: {core_content}"
    if details:
        full_detailed += " " + " ".join(details)

    if not verify_preservation(original_text, full_detailed):
        full_detailed = f"{intro}\n\nTerms: {lex_text}"

    return full_detailed


def simplify_professional(
    original_text: str, category: str = "", affected_party: str = ""
) -> str:
    """Generate a structured professional breakdown.

    Suitable for paralegals and contract analysts with structured fields:
    - Obligor / Bound Party
    - Beneficiary
    - Core Obligation
    - Conditions & Triggers
    - Exceptions & Carve-Outs
    - Deadlines & Cure Periods
    - Remedies & Consequence
    """
    if not original_text or not original_text.strip():
        return ""

    party_str = (
        affected_party
        if affected_party and affected_party != "Unknown"
        else "Contracting Party"
    )

    # 1. Detect Obligation Type
    is_prohibition = bool(
        re.search(
            r"\b(shall not|must not|may not|prohibited|refrain)\b",
            original_text,
            re.IGNORECASE,
        )
    )
    is_mandatory = bool(
        re.search(
            r"\b(shall|must|agrees to|obligated|required to)\b",
            original_text,
            re.IGNORECASE,
        )
    )

    if is_prohibition:
        core_type = "Negative Covenant (Strict Prohibition)"
    elif is_mandatory:
        core_type = "Affirmative Covenant (Mandatory Performance)"
    else:
        core_type = "Declaratory Covenant / Procedural Condition"

    # 2. Extract Conditions / Triggers
    cond_match = re.search(
        r"\b(?:in the event(?: that)?|upon|if|subject to|provided that)\s+([^,.;]{10,80})",
        original_text,
        re.IGNORECASE,
    )
    trigger = (
        cond_match.group(0).strip()
        if cond_match
        else "Immediate upon execution / standard operation"
    )

    # 3. Extract Exceptions / Carve-Outs
    exc_match = re.search(
        r"\b(?:except|unless|other than|excluding|provided however that)\s+([^,.;]{10,80})",
        original_text,
        re.IGNORECASE,
    )
    exceptions = (
        exc_match.group(0).strip()
        if exc_match
        else "None explicitly stated in this clause"
    )

    # 4. Extract Deadlines / Timelines
    time_match = re.search(
        r"\b(?:within|prior to|after|on or before)\s+([^,.;]{5,50})",
        original_text,
        re.IGNORECASE,
    )
    timeline = (
        time_match.group(0).strip()
        if time_match
        else "Standard business practice / Not specified"
    )

    # 5. Extract Remedies / Consequences
    rem_match = re.search(
        r"\b(injunction|injunctive relief|liquidated damages|terminate|damages|attorney(?:s')? fees)\b",
        original_text,
        re.IGNORECASE,
    )
    remedy = (
        f"Legal or equitable relief ({rem_match.group(0)})"
        if rem_match
        else "Breach of contract damages and statutory remedies"
    )

    # 6. Concise Summary of Duty
    lex_duty = lexical_simplify(original_text)
    short_duty = lex_duty.split(".")[0].strip()
    if len(short_duty) > 140:
        short_duty = short_duty[:137] + "..."

    breakdown = (
        f"• **Obligor / Bound Party**: {party_str}\n"
        f"• **Covenant Type**: {core_type}\n"
        f"• **Core Duty**: {short_duty}\n"
        f"• **Conditions & Triggers**: {trigger}\n"
        f"• **Exceptions & Carve-Outs**: {exceptions}\n"
        f"• **Timeline / Cure Period**: {timeline}\n"
        f"• **Remedies & Liabilities**: {remedy}"
    )

    return breakdown


def simplify_clause(
    original_text: str,
    category: str = "",
    affected_party: str = "",
) -> dict[str, Any]:
    """Execute complete tri-tier simplification pipeline on a clause with readability scoring."""
    if not original_text or not original_text.strip():
        empty_readability = calculate_readability("")
        return {
            "simple_english": "",
            "detailed": "",
            "professional": "",
            "readability_original": empty_readability,
            "readability_simple": empty_readability,
            "readability_detailed": empty_readability,
            "glossary_terms": [],
            "traps_and_nuances": [],
            "preservation_verified": True,
        }

    simple_eng = simplify_simple_english(original_text, category, affected_party)
    detailed = simplify_detailed(original_text, category, affected_party)
    professional = simplify_professional(original_text, category, affected_party)

    # Calculate readability before and after
    read_orig = calculate_readability(original_text)
    read_simple = calculate_readability(simple_eng)
    read_detailed = calculate_readability(detailed)

    # Detect glossary terms and nuances
    glossary_terms = extract_clause_glossary(original_text)
    traps = detect_traps_and_nuances(original_text)

    is_verified = verify_preservation(
        original_text, simple_eng
    ) and verify_preservation(original_text, detailed)

    return {
        "simple_english": simple_eng,
        "detailed": detailed,
        "professional": professional,
        "readability_original": read_orig,
        "readability_simple": read_simple,
        "readability_detailed": read_detailed,
        "glossary_terms": glossary_terms,
        "traps_and_nuances": traps,
        "preservation_verified": is_verified,
    }
