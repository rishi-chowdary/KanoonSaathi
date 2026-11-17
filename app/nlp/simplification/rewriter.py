from __future__ import annotations

import re

from app.nlp.segmentation import legal_sentence_tokenizer
from app.nlp.simplification.glossary import get_sorted_glossary_terms

# Ordered from specific multi-word phrases to shorter terms so longer matches win
LEGALESE_REPLACEMENTS: list[tuple[re.Pattern, str]] = [
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

_SENTENCE_SPLIT_SUBSTITUTIONS = [
    (r",\s*provided that\s+", ". However, this applies only if "),
    (r",\s*provided however that\s+", ". However, "),
    (r",\s*subject to\s+", ". This is subject to "),
    (r",\s*unless\s+", ". This does not apply if "),
    (r",\s*except that\s+", ". An exception is that "),
    (r",\s*or from any\s+", ". This also covers any "),
    (r",\s*and fails to cure\s+", ". The breaching party must fix "),
    (r",\s*and (?:shall|must) use such\s+", ". The party must use this "),
]


def lexical_simplify(text: str) -> str:
    """Replace legalese phrases and concise glossary terms without restructuring syntax."""
    if not text:
        return ""
    out = text
    for pattern, repl in LEGALESE_REPLACEMENTS:
        out = pattern.sub(repl, out)

    for term, plain, _, _ in get_sorted_glossary_terms():
        if plain.lower() != term.lower() and len(plain.split()) <= 3:
            out = re.sub(rf"\b{re.escape(term)}\b", plain, out, flags=re.IGNORECASE)

    return re.sub(r"\s+", " ", out).strip()


def verify_preservation(original_text: str, candidate_text: str) -> bool:
    """Ensure negations and conditions in original_text survive simplification."""
    if not original_text or not candidate_text:
        return True

    orig_has_neg = any(p.search(original_text) for p in NEGATION_PATTERNS)
    cand_has_neg = any(p.search(candidate_text) for p in NEGATION_PATTERNS)
    if orig_has_neg and not cand_has_neg:
        return False

    orig_has_cond = any(p.search(original_text) for p in CONDITION_PATTERNS)
    cand_has_cond = bool(
        re.search(
            r"\b(unless|except|if|provided|subject to|conditioned|when|in case|however)\b",
            candidate_text,
            re.IGNORECASE,
        )
    )
    return not (orig_has_cond and not cand_has_cond)


def _format_plain_sentence(part: str) -> str:
    clean = part[0].upper() + part[1:]
    if not clean.endswith((".", "!", "?")):
        clean += "."
    return clean


def split_into_plain_sentences(text: str) -> list[str]:
    """Break long legal sentences into shorter standalone sentences."""
    out_sentences: list[str] = []
    for raw in legal_sentence_tokenizer.tokenize(text):
        sent = raw.strip()
        if not sent:
            continue
        for pat, repl in _SENTENCE_SPLIT_SUBSTITUTIONS:
            sent = re.sub(pat, repl, sent, flags=re.IGNORECASE)

        for part in re.split(r";\s*(?:\([a-z0-9]+\)\s*|\b(?:and|or)\b\s*)?|;\s*", sent):
            cleaned = part.strip()
            if not cleaned:
                continue
            if len(cleaned.split()) > 28:
                conj_split = re.split(
                    r",\s+(?:and|or|but)\s+(?=(?:the|each|neither|either|all|both|this|such|a|an)\b)",
                    cleaned,
                    maxsplit=2,
                    flags=re.IGNORECASE,
                )
                if len(conj_split) > 1:
                    out_sentences.extend(
                        _format_plain_sentence(c.strip())
                        for c in conj_split
                        if c.strip()
                    )
                    continue
            out_sentences.append(_format_plain_sentence(cleaned))
    return out_sentences


def simplify_simple_english(
    original_text: str, category: str = "", affected_party: str = ""
) -> str:
    """Produce a plain-language rewrite using glossary substitutions and sentence splitting."""
    if not original_text or not original_text.strip():
        return ""

    simplified = lexical_simplify(original_text)
    simplified_text = " ".join(split_into_plain_sentences(simplified))
    simplified_text = re.sub(r"\s+", " ", simplified_text)
    simplified_text = re.sub(r"\s+([.,;:!?])", r"\1", simplified_text)
    simplified_text = re.sub(r"\.{2,}", ".", simplified_text).strip()

    if not verify_preservation(original_text, simplified_text):
        simplified_text = lexical_simplify(original_text)
    return simplified_text
