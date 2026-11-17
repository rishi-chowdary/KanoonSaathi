import difflib
import re
from app.schemas.extraction import PageExtraction
from app.schemas.summary import DocumentSummaryResponse, GroundedItem, PartyItem


def normalize_text(text: str) -> str:
    if not text:
        return ""
    # Lowercase and normalize all whitespace (tabs, newlines, multiple spaces) to single space
    cleaned = re.sub(r"\s+", " ", text.lower()).strip()
    return cleaned


def verify_quote(
    quote: str,
    pages: list[PageExtraction],
    claimed_page: int | None = None,
    threshold: float = 0.90,
) -> tuple[bool, int]:
    if not quote:
        return False, claimed_page or 1

    cleaned_quote = quote.strip()
    if cleaned_quote.lower() in ("not specified", "none", "n/a", ""):
        return False, claimed_page or 1

    norm_quote = normalize_text(cleaned_quote)
    if len(norm_quote) < 4:
        return False, claimed_page or 1

    # 1. Check claimed page first for exact substring match
    if claimed_page is not None:
        claimed_p = next((p for p in pages if p.page_number == claimed_page), None)
        if claimed_p:
            norm_claimed = normalize_text(claimed_p.text)
            if norm_quote in norm_claimed:
                return True, claimed_page

    # 2. Check all pages for exact substring match
    for p in pages:
        norm_page = normalize_text(p.text)
        if norm_quote in norm_page:
            return True, p.page_number

    # 3. Fuzzy matching with threshold >= 0.90
    quote_words = norm_quote.split()
    quote_word_count = len(quote_words)

    for p in pages:
        norm_page = normalize_text(p.text)
        page_words = norm_page.split()
        if not page_words:
            continue

        # If page has fewer words than quote, compare entire page
        if len(page_words) <= quote_word_count:
            ratio = difflib.SequenceMatcher(None, norm_quote, norm_page).ratio()
            if ratio >= threshold:
                return True, p.page_number
            continue

        # Sliding window over words
        window_size = quote_word_count
        step = max(1, quote_word_count // 3)
        for i in range(0, len(page_words) - window_size + 1, step):
            window_str = " ".join(page_words[i : i + window_size])
            ratio = difflib.SequenceMatcher(None, norm_quote, window_str).ratio()
            if ratio >= threshold:
                return True, p.page_number

        # Check with slightly expanded window (for minor omitted filler words)
        expanded_size = min(len(page_words), quote_word_count + 3)
        for i in range(0, len(page_words) - expanded_size + 1, step):
            window_str = " ".join(page_words[i : i + expanded_size])
            ratio = difflib.SequenceMatcher(None, norm_quote, window_str).ratio()
            if ratio >= threshold:
                return True, p.page_number

    return False, claimed_page or 1


def verify_summary_quotes(
    summary: DocumentSummaryResponse,
    pages: list[PageExtraction],
) -> DocumentSummaryResponse:
    total_verifiable = 0
    verified_count = 0

    def verify_item(item: GroundedItem | PartyItem):
        nonlocal total_verifiable, verified_count
        quote = item.evidence_quote
        if quote and quote.lower() not in ("not specified", "none", ""):
            total_verifiable += 1
            is_valid, matched_page = verify_quote(quote, pages, item.source_page)
            item.quote_verified = is_valid
            if is_valid:
                item.source_page = matched_page
                verified_count += 1
        else:
            item.quote_verified = False

    for party in summary.parties:
        verify_item(party)

    for cond in summary.main_conditions:
        verify_item(cond)

    for ob in summary.obligations:
        verify_item(ob)

    for term in summary.financial_terms:
        verify_item(term)

    if total_verifiable > 0:
        rate = (verified_count / total_verifiable) * 100.0
    else:
        rate = 100.0

    summary.verification_rate = round(rate, 2)
    return summary
