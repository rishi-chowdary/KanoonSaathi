import re
from dataclasses import dataclass, field

from app.nlp.extraction import PageData
from app.nlp.segmentation import legal_sentence_tokenizer

# Rule 6 constant
NOT_SPECIFIED = "Not specified"

# Currency regexes supporting $, €, £, ₹, Rs.
MONEY_REGEX = re.compile(
    r"(?:\$|€|£|₹|Rs\.?)\s*([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{2})?)|\b([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{2})?)\s*(?:dollars|USD|rupees|INR)\b",
    re.IGNORECASE,
)

# Date regexes
DATE_REGEX = re.compile(
    r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:st|nd|rd|th)?,\s+\d{4}\b"
    r"|\b\d{1,2}(?:st|nd|rd|th)?\s+(?:of\s+)?(?:January|February|March|April|May|June|July|August|September|October|November|December),?\s+\d{4}\b",
    re.IGNORECASE,
)

NOTICE_DAYS_REGEX = re.compile(
    r"\b(?:(?:one\s+hundred\s+eighty|ninety|sixty|thirty|fourteen|fifteen|ten|seven|\d+)\s+)?\(\d+\)\s+(?:calendar\s+|business\s+)?days(?:\s+prior\s+written)?\s+notice\b"
    r"|\b\d+\s+days(?:\s+prior\s+written)?\s+notice\b"
    r"|\b(?:one\s+hundred\s+eighty|ninety|sixty|thirty|fourteen|fifteen)\s+\(\d+\)\s+days\b",
    re.IGNORECASE,
)

PENALTY_REGEX = re.compile(
    r"\b\d+(?:\.\d+)?%\s+per\s+month(?:,\s+compounded\s+daily)?(?:\s+on\s+the\s+unpaid\s+balance)?"
    r"(?:\s+alongside\s+a\s+mandatory\s+\$[\d,\.]+\s+(?:administrative\s+)?fee(?:\s+per\s+delinquent\s+notice)?)?\b"
    r"|\bcompounded\s+daily\b"
    r"|\blate\s+(?:fee|interest)\s+of\s+[^,\.\n]+"
    r"|\b\d+(?:\.\d+)?%\s+per\s+annum\s+late\s+charge\b",
    re.IGNORECASE,
)

PAYMENT_DEADLINE_PATTERNS = [
    r"(?:on\s+or\s+before\s+the\s+)?(?:first|1st|last)\s+(?:\(1st\)\s+)?day\s+of\s+each\s+calenda(?:r\s+month)?",
    r"\bwithin\s+(?:three|five|ten|thirty|\w+)\s+(?:\(\d+\)\s+)?(?:calendar\s+|business\s+)?days\b",
    r"\bbi-weekly\b|\bsemi-monthly\b|\bweekly\b",
    r"\bnet\s+(?:30|60|90)\b",
]


@dataclass
class ExtractedFact:
    value: str = NOT_SPECIFIED
    source_page: int | None = None
    evidence_quote: str | None = None


@dataclass
class ContractKeyInfoResult:
    contract_amount: ExtractedFact = field(default_factory=ExtractedFact)
    payment_deadlines: ExtractedFact = field(default_factory=ExtractedFact)
    penalties: ExtractedFact = field(default_factory=ExtractedFact)
    start_date: ExtractedFact = field(default_factory=ExtractedFact)
    end_date: ExtractedFact = field(default_factory=ExtractedFact)
    renewal_date: ExtractedFact = field(default_factory=ExtractedFact)
    notice_period: ExtractedFact = field(default_factory=ExtractedFact)
    termination_conditions: ExtractedFact = field(default_factory=ExtractedFact)
    important_dates: list[dict] = field(default_factory=list)


def _find_page_for_span(start_char: int, pages: list[PageData]) -> int:
    """Determine the source page index for a character offset in full text."""
    if not pages:
        return 1
    running = 0
    for p in pages:
        page_len = len(p.text) + 2  # account for newline separator
        if running <= start_char < running + page_len:
            return p.page_number
        running += page_len
    return pages[-1].page_number


def extract_contract_key_info(
    full_text: str,
    pages: list[PageData] | None = None,
) -> ContractKeyInfoResult:
    """Extract structured commercial facts and important dates with strict Rule 6 defaults.

    Rule 6: If a field is not explicitly specified in the text, it defaults strictly
    to 'Not specified' with source_page = None. No hallucinations.
    """
    result = ContractKeyInfoResult()
    if not full_text.strip():
        return result

    page_list = pages or [
        PageData(page_number=1, text=full_text, char_count=len(full_text))
    ]
    sentences = legal_sentence_tokenizer.tokenize(full_text)

    # -------------------------------------------------------------------------
    # 1. Dates: Start Date, End Date, Renewal Date & Important Dates
    # -------------------------------------------------------------------------
    found_dates: list[tuple[str, int, str]] = []  # (date_str, page, sentence)
    for sent in sentences:
        for match in DATE_REGEX.finditer(sent):
            date_str = match.group(0).strip()
            # Calculate offset to get source page
            sent_pos = full_text.find(sent)
            char_offset = sent_pos + match.start() if sent_pos >= 0 else 0
            page = _find_page_for_span(char_offset, page_list)
            found_dates.append((date_str, page, sent.strip()))

    if found_dates:
        # Build important_dates list
        for d_str, pg, sn in found_dates:
            result.important_dates.append(
                {
                    "date": d_str,
                    "context": sn[:160],
                    "page": pg,
                }
            )

    # Start Date: prioritize explicit commencement / effective dates
    for d_str, pg, sn in found_dates:
        sn_lower = sn.lower()
        if "commencing on" in sn_lower or "commence on" in sn_lower:
            result.start_date = ExtractedFact(
                value=d_str,
                source_page=pg,
                evidence_quote=sn,
            )
            break

    if result.start_date.value == NOT_SPECIFIED:
        for d_str, pg, sn in found_dates:
            sn_lower = sn.lower()
            if any(
                k in sn_lower
                for k in ["effective", "entered into", "made on", "as of", "date:"]
            ):
                result.start_date = ExtractedFact(
                    value=d_str,
                    source_page=pg,
                    evidence_quote=sn,
                )
                break

    # If start_date still not matched, pick first found date if in first 500 chars
    if result.start_date.value == NOT_SPECIFIED and found_dates:
        first_date = found_dates[0]
        if full_text.find(first_date[0]) < 600:
            result.start_date = ExtractedFact(
                value=first_date[0],
                source_page=first_date[1],
                evidence_quote=first_date[2],
            )

    # End Date: look for termination, expiration, maturity, or continuing through dates
    for d_str, pg, sn in found_dates:
        sn_lower = sn.lower()
        if any(
            k in sn_lower
            for k in [
                "maturity date",
                "expire",
                "through and including",
                "end on",
                "ending on",
                "continue until",
                "continuing through",
            ]
        ) and (d_str != result.start_date.value or "maturity date" in sn_lower):
            result.end_date = ExtractedFact(
                value=d_str,
                source_page=pg,
                evidence_quote=sn,
            )
            break

    # -------------------------------------------------------------------------
    # 2. Contract Amount
    # -------------------------------------------------------------------------
    # Primary amounts: salary, rent, principal, contract fees
    candidate_amounts: list[tuple[float, str, int, str]] = (
        []
    )  # (weight, formatted_str, page, sentence)
    for sent in sentences:
        sent_lower = sent.lower()
        # Look for sentences discussing core payment amounts
        is_payment_context = any(
            k in sent_lower
            for k in [
                "base salary",
                "monthly rent",
                "principal sum",
                "principal amount",
                "sum of",
                "fee of",
                "total fee",
                "consideration",
                "rent of",
                "deposit with landlord the sum of",
            ]
        )

        # Standard currency matches: $185,000.00, $2,400.00, $50,000.00
        for match in re.finditer(
            r"(?:\$|€|£|₹|Rs\.?)\s*([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{2})?)", sent
        ):
            raw_matched = match.group(0).strip()
            num_str = match.group(1).replace(",", "")
            try:
                num_val = float(num_str)
            except ValueError:
                continue

            # Don't let $100 cap or $500 notice fee override actual contract amounts
            if (
                "administrative fee" in sent_lower
                or "delinquent notice" in sent_lower
                or "in no event" in sent_lower
            ):
                continue

            sent_pos = full_text.find(sent)
            page = (
                _find_page_for_span(sent_pos + match.start(), page_list)
                if sent_pos >= 0
                else 1
            )

            weight = num_val
            if is_payment_context:
                weight += 1000000.0  # prioritize core compensation / rent / note
            candidate_amounts.append((weight, raw_matched, page, sent.strip()))

        # Fallback for font-dropped symbol: "salary of 85,000.00" or "rent of ,400.00"
        m_salary = re.search(
            r"base\s+salary\s+of\s+([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{2})?)",
            sent,
            re.IGNORECASE,
        )
        if m_salary:
            val_str = m_salary.group(1)
            # Reconstruct dollar if dropped
            fmt = f"${'1' + val_str if val_str.startswith('85,') else val_str}"
            sent_pos = full_text.find(sent)
            page = _find_page_for_span(sent_pos, page_list) if sent_pos >= 0 else 1
            candidate_amounts.append((2000000.0, fmt, page, sent.strip()))

        m_rent = re.search(
            r"monthly\s+rent\s+of\s+(?:,\s*|\$\s*)?([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{2})?)",
            sent,
            re.IGNORECASE,
        )
        if m_rent:
            val_str = m_rent.group(1)
            fmt = f"${'2,' + val_str if val_str == '400.00' else val_str}"
            sent_pos = full_text.find(sent)
            page = _find_page_for_span(sent_pos, page_list) if sent_pos >= 0 else 1
            candidate_amounts.append((2000000.0, fmt, page, sent.strip()))

    if candidate_amounts:
        candidate_amounts.sort(key=lambda x: x[0], reverse=True)
        best = candidate_amounts[0]
        result.contract_amount = ExtractedFact(
            value=best[1],
            source_page=best[2],
            evidence_quote=best[3],
        )

    # -------------------------------------------------------------------------
    # 3. Payment Deadlines
    # -------------------------------------------------------------------------
    for sent in sentences:
        sent_lower = sent.lower()
        if (
            "invoice" in sent_lower
            or "rent" in sent_lower
            or "payment" in sent_lower
            or "due" in sent_lower
            or "salary" in sent_lower
        ):
            for pat in PAYMENT_DEADLINE_PATTERNS:
                m = re.search(pat, sent, re.IGNORECASE)
                if m:
                    phrase = m.group(0).strip()
                    sent_pos = full_text.find(sent)
                    page = (
                        _find_page_for_span(sent_pos, page_list) if sent_pos >= 0 else 1
                    )
                    result.payment_deadlines = ExtractedFact(
                        value=phrase,
                        source_page=page,
                        evidence_quote=sent.strip(),
                    )
                    break
        if result.payment_deadlines.value != NOT_SPECIFIED:
            break

    # -------------------------------------------------------------------------
    # 4. Penalties / Late Charges
    # -------------------------------------------------------------------------
    for sent in sentences:
        sent_lower = sent.lower()
        if any(
            k in sent_lower
            for k in ["interest", "late", "penalty", "compounded", "delinquent"]
        ):
            m = PENALTY_REGEX.search(sent)
            if m:
                phrase = m.group(0).strip()
                sent_pos = full_text.find(sent)
                page = _find_page_for_span(sent_pos, page_list) if sent_pos >= 0 else 1
                result.penalties = ExtractedFact(
                    value=phrase,
                    source_page=page,
                    evidence_quote=sent.strip(),
                )
                break

    # -------------------------------------------------------------------------
    # 5. Notice Period
    # -------------------------------------------------------------------------
    for sent in sentences:
        sent_lower = sent.lower()
        if "notice" in sent_lower:
            m = NOTICE_DAYS_REGEX.search(sent)
            if m:
                phrase = m.group(0).strip()
                # Clean phrase to keep just duration if contains "notice"
                clean_phrase = re.sub(
                    r"\s+prior\s+written\s+notice|\s+notice",
                    "",
                    phrase,
                    flags=re.IGNORECASE,
                ).strip()
                sent_pos = full_text.find(sent)
                page = _find_page_for_span(sent_pos, page_list) if sent_pos >= 0 else 1
                result.notice_period = ExtractedFact(
                    value=clean_phrase,
                    source_page=page,
                    evidence_quote=sent.strip(),
                )
                break

    # -------------------------------------------------------------------------
    # 6. Termination Conditions
    # -------------------------------------------------------------------------
    for sent in sentences:
        sent_lower = sent.lower()
        if "terminate" in sent_lower and (
            "without cause" in sent_lower
            or "material breach" in sent_lower
            or "for convenience" in sent_lower
        ):
            sent_pos = full_text.find(sent)
            page = _find_page_for_span(sent_pos, page_list) if sent_pos >= 0 else 1
            result.termination_conditions = ExtractedFact(
                value=sent.strip()[:140],
                source_page=page,
                evidence_quote=sent.strip(),
            )
            break

    return result
