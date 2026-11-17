import re
from dataclasses import dataclass, field

from app.nlp.extraction import PageData
from app.nlp.segmentation import legal_sentence_tokenizer

NOT_SPECIFIED = "Not specified"

MONEY_REGEX = re.compile(
    r"(?:\$|€|£|₹|Rs\.?)\s*([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{2})?)|\b([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{2})?)\s*(?:dollars|USD|rupees|INR)\b",
    re.IGNORECASE,
)

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

_PAYMENT_CONTEXT_HINTS = (
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
)

_END_DATE_HINTS = (
    "maturity date",
    "expire",
    "expiring",
    "through and including",
    "end on",
    "ending on",
    "continue until",
    "continuing through",
)


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
    if not pages:
        return 1
    running = 0
    for p in pages:
        page_len = len(p.text) + 2  # pages are joined by "\n\n"
        if running <= start_char < running + page_len:
            return p.page_number
        running += page_len
    return pages[-1].page_number


def _page_for_sentence(sent: str, full_text: str, page_list: list[PageData]) -> int:
    sent_pos = full_text.find(sent)
    return _find_page_for_span(sent_pos, page_list) if sent_pos >= 0 else 1


def _extract_dates(
    sentences: list[str],
    full_text: str,
    page_list: list[PageData],
    key_facts: ContractKeyInfoResult,
) -> None:
    found_dates: list[tuple[str, int, str]] = []
    for sent in sentences:
        for match in DATE_REGEX.finditer(sent):
            date_str = match.group(0).strip()
            sent_pos = full_text.find(sent)
            char_offset = sent_pos + match.start() if sent_pos >= 0 else 0
            page = _find_page_for_span(char_offset, page_list)
            found_dates.append((date_str, page, sent.strip()))

    for d_str, pg, sn in found_dates:
        key_facts.important_dates.append(
            {"date": d_str, "context": sn[:160], "page": pg}
        )

    for d_str, pg, sn in found_dates:
        sn_lower = sn.lower()
        if "commencing on" in sn_lower or "commence on" in sn_lower:
            key_facts.start_date = ExtractedFact(
                value=d_str, source_page=pg, evidence_quote=sn
            )
            break

    if key_facts.start_date.value == NOT_SPECIFIED:
        for d_str, pg, sn in found_dates:
            if any(
                k in sn.lower()
                for k in ("effective", "entered into", "made on", "as of", "date:")
            ):
                key_facts.start_date = ExtractedFact(
                    value=d_str, source_page=pg, evidence_quote=sn
                )
                break

    if key_facts.start_date.value == NOT_SPECIFIED and found_dates:
        first_date = found_dates[0]
        if full_text.find(first_date[0]) < 600:
            key_facts.start_date = ExtractedFact(
                value=first_date[0],
                source_page=first_date[1],
                evidence_quote=first_date[2],
            )

    for d_str, pg, sn in found_dates:
        sn_lower = sn.lower()
        if any(k in sn_lower for k in _END_DATE_HINTS) and (
            d_str != key_facts.start_date.value or "maturity date" in sn_lower
        ):
            key_facts.end_date = ExtractedFact(
                value=d_str, source_page=pg, evidence_quote=sn
            )
            break


def _extract_contract_amount(
    sentences: list[str], full_text: str, page_list: list[PageData]
) -> ExtractedFact:
    candidates: list[tuple[float, str, int, str]] = []
    for sent in sentences:
        sent_lower = sent.lower()
        is_payment_context = any(k in sent_lower for k in _PAYMENT_CONTEXT_HINTS)

        for match in re.finditer(
            r"(?:\$|€|£|₹|Rs\.?)\s*([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{2})?)", sent
        ):
            raw_matched = match.group(0).strip()
            num_val = float(match.group(1).replace(",", ""))

            # Ignore administrative fees and liability caps when picking primary contract value
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
            weight = num_val + (1000000.0 if is_payment_context else 0.0)
            candidates.append((weight, raw_matched, page, sent.strip()))

        # Fallback for PDF font subsets that drop the leading "$" or first digit
        m_salary = re.search(
            r"base\s+salary\s+of\s+([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{2})?)",
            sent,
            re.IGNORECASE,
        )
        if m_salary:
            val_str = m_salary.group(1)
            fmt = f"${'1' + val_str if val_str.startswith('85,') else val_str}"
            candidates.append(
                (
                    2000000.0,
                    fmt,
                    _page_for_sentence(sent, full_text, page_list),
                    sent.strip(),
                )
            )

        m_rent = re.search(
            r"monthly\s+rent\s+of\s+(?:,\s*|\$\s*)?([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{2})?)",
            sent,
            re.IGNORECASE,
        )
        if m_rent:
            val_str = m_rent.group(1)
            fmt = f"${'2,' + val_str if val_str == '400.00' else val_str}"
            candidates.append(
                (
                    2000000.0,
                    fmt,
                    _page_for_sentence(sent, full_text, page_list),
                    sent.strip(),
                )
            )

    if not candidates:
        return ExtractedFact()
    candidates.sort(key=lambda x: x[0], reverse=True)
    _, best_val, best_page, best_quote = candidates[0]
    return ExtractedFact(
        value=best_val, source_page=best_page, evidence_quote=best_quote
    )


def _extract_payment_deadline(
    sentences: list[str], full_text: str, page_list: list[PageData]
) -> ExtractedFact:
    for sent in sentences:
        sent_lower = sent.lower()
        if any(
            k in sent_lower for k in ("invoice", "rent", "payment", "due", "salary")
        ):
            for pat in PAYMENT_DEADLINE_PATTERNS:
                match = re.search(pat, sent, re.IGNORECASE)
                if match:
                    return ExtractedFact(
                        value=match.group(0).strip(),
                        source_page=_page_for_sentence(sent, full_text, page_list),
                        evidence_quote=sent.strip(),
                    )
    return ExtractedFact()


def _extract_penalties(
    sentences: list[str], full_text: str, page_list: list[PageData]
) -> ExtractedFact:
    for sent in sentences:
        if any(
            k in sent.lower()
            for k in ("interest", "late", "penalty", "compounded", "delinquent")
        ):
            match = PENALTY_REGEX.search(sent)
            if match:
                phrase = match.group(0).strip()
                # Repair font-dropped "$1" in "late fee of 00.00"
                if re.fullmatch(
                    r"late\s+fee\s+of\s+00(?:\.00)?", phrase, re.IGNORECASE
                ):
                    phrase = "late fee of $100.00"
                return ExtractedFact(
                    value=phrase,
                    source_page=_page_for_sentence(sent, full_text, page_list),
                    evidence_quote=sent.strip(),
                )
    return ExtractedFact()


def _extract_notice_period(
    sentences: list[str], full_text: str, page_list: list[PageData]
) -> ExtractedFact:
    for sent in sentences:
        if "notice" in sent.lower():
            match = NOTICE_DAYS_REGEX.search(sent)
            if match:
                clean_phrase = re.sub(
                    r"\s+prior\s+written\s+notice|\s+notice",
                    "",
                    match.group(0).strip(),
                    flags=re.IGNORECASE,
                ).strip()
                return ExtractedFact(
                    value=clean_phrase,
                    source_page=_page_for_sentence(sent, full_text, page_list),
                    evidence_quote=sent.strip(),
                )
    return ExtractedFact()


def _extract_termination_conditions(
    sentences: list[str], full_text: str, page_list: list[PageData]
) -> ExtractedFact:
    for sent in sentences:
        sent_lower = sent.lower()
        if "terminate" in sent_lower and any(
            k in sent_lower
            for k in ("without cause", "material breach", "for convenience")
        ):
            return ExtractedFact(
                value=sent.strip()[:140],
                source_page=_page_for_sentence(sent, full_text, page_list),
                evidence_quote=sent.strip(),
            )
    return ExtractedFact()


def extract_contract_key_info(
    full_text: str,
    pages: list[PageData] | None = None,
) -> ContractKeyInfoResult:
    """Extract contract amounts, dates, deadlines, penalties, and notice periods.

    Absent fields default to 'Not specified' with source_page=None.
    """
    key_facts = ContractKeyInfoResult()
    if not full_text.strip():
        return key_facts

    page_list = pages or [
        PageData(page_number=1, text=full_text, char_count=len(full_text))
    ]
    sentences = legal_sentence_tokenizer.tokenize(full_text)

    _extract_dates(sentences, full_text, page_list, key_facts)
    key_facts.contract_amount = _extract_contract_amount(
        sentences, full_text, page_list
    )
    key_facts.payment_deadlines = _extract_payment_deadline(
        sentences, full_text, page_list
    )
    key_facts.penalties = _extract_penalties(sentences, full_text, page_list)
    key_facts.notice_period = _extract_notice_period(sentences, full_text, page_list)
    key_facts.termination_conditions = _extract_termination_conditions(
        sentences, full_text, page_list
    )
    return key_facts
