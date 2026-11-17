import numpy as np

from app.nlp.registry import get_sentence_transformer
from app.nlp.segmentation import legal_sentence_tokenizer

OBLIGATION_PATTERNS = [
    "shall",
    "must",
    "agrees to",
    "hereby assigns",
    "covenants",
    "warrants",
    "governed by",
    "indemnify",
    "in no event",
    "terminate",
    "will pay",
    "monthly rent",
    "effective date",
]


def extract_evidence_quote(
    original_text: str,
    category: str = "",
    title: str = "",
) -> tuple[str, bool]:
    """Select the most representative, high-impact sentence as the evidence quote.

    Guarantees:
    - Evidence quote is 100% an exact substring slice of original_text
    - Verified against source text
    """
    if not original_text.strip():
        return "", True

    sentences = legal_sentence_tokenizer.tokenize(original_text)
    clean_sentences = [s.strip() for s in sentences if len(s.strip()) >= 15]

    if not clean_sentences:
        # Fallback to original text if very short
        return original_text.strip(), True

    # If only one sentence exists, return it directly
    if len(clean_sentences) == 1:
        quote = clean_sentences[0]
        return quote, (quote in original_text)

    # Score candidates using obligation signals and semantic similarity
    scored: list[tuple[float, str]] = []
    model = get_sentence_transformer()

    target_prompt = f"{title}. {category} obligation."
    target_vec = model.encode([target_prompt], convert_to_numpy=True)[0]
    target_norm = np.linalg.norm(target_vec)
    if target_norm > 0:
        target_vec = target_vec / target_norm

    candidate_vecs = model.encode(clean_sentences, convert_to_numpy=True)
    if candidate_vecs.ndim == 1:
        candidate_vecs = candidate_vecs.reshape(1, -1)

    for idx, sentence in enumerate(clean_sentences):
        # Semantic score
        s_vec = candidate_vecs[idx]
        s_norm = np.linalg.norm(s_vec)
        cos_sim = float(np.dot(s_vec / s_norm, target_vec)) if s_norm > 0 else 0.0

        # Lexical bonus for legal obligation markers
        s_lower = sentence.lower()
        bonus = 0.0
        for pat in OBLIGATION_PATTERNS:
            if pat in s_lower:
                bonus += 0.15

        total_score = cos_sim + bonus
        scored.append((total_score, sentence))

    scored.sort(key=lambda x: x[0], reverse=True)
    best_quote = scored[0][1]

    # Verification: Confirm quote is an exact substring of original_text
    is_verified = best_quote in original_text
    return best_quote, is_verified
