"""LexiLegal AI — Readability Scorer.

Provides pure Python implementation of:
1. Flesch Reading Ease (higher = easier to read, 0-100 scale, legal contracts often < 30)
2. Flesch-Kincaid Grade Level (US school grade level, college = 13-16, post-grad > 16)
3. Syllable counter tailored for legal vocabulary.
"""

import re
from typing import Any

from app.nlp.segmentation import legal_sentence_tokenizer

# Regex for word tokenization (preserves hyphens and contractions)
_WORD_REGEX = re.compile(r"\b[A-Za-z0-9]+(?:'[A-Za-z0-9]+)?\b")


def count_syllables_word(word: str) -> int:
    clean = word.lower().strip()
    clean = re.sub(r"[^a-z]", "", clean)
    if not clean:
        return 0

    if len(clean) <= 3:
        return 1

    # Diphthongs and vowel group matching
    vowels = "aeiouy"
    count = 0
    prev_is_vowel = False
    for char in clean:
        is_vowel = char in vowels
        if is_vowel and not prev_is_vowel:
            count += 1
        prev_is_vowel = is_vowel

    # Specific common legal/Latin vowel pairings that form distinct syllables (excluding -tion / -sion)
    double_vowel_extras = ["ia", "iu", "ea", "eo", "ua", "uo", "oe"]
    for pair in double_vowel_extras:
        if pair in clean:
            count += clean.count(pair)

    # For 'io', only add if not preceded by 't' or 's' (e.g. -tion or -sion are pronounced /ʃən/)
    io_matches = len(re.findall(r"(?<![ts])io", clean))
    count += io_matches

    # Silent 'e' at end of word (e.g. 'make', 'clause', 'here'), unless 'le' preceded by consonant
    if clean.endswith("e") and not clean.endswith("le") and count > 1:
        count -= 1

    # Inactive ending 'es' or 'ed' unless preceded by c/s/x/z/ch/sh or t/d
    if (
        clean.endswith("ed")
        and not clean.endswith(("ted", "ded"))
        and count > 1
        or (
            clean.endswith("es")
            and not clean.endswith(("ses", "zes", "ches", "shes", "xes"))
            and count > 1
        )
    ):
        count -= 1

    return max(1, count)


def count_syllables_text(text: str) -> tuple[int, int]:
    words = _WORD_REGEX.findall(text)
    if not words:
        return 0, 0

    total_syllables = sum(count_syllables_word(w) for w in words)
    return len(words), total_syllables


def get_flesch_interpretation(score: float) -> str:
    if score >= 90.0:
        return "Very Easy (5th Grade)"
    if score >= 80.0:
        return "Easy (6th Grade)"
    if score >= 70.0:
        return "Fairly Easy (7th Grade)"
    if score >= 60.0:
        return "Standard Plain English (8th–9th Grade)"
    if score >= 50.0:
        return "Fairly Difficult (10th–12th Grade)"
    if score >= 30.0:
        return "Difficult (College Level)"
    return "Very Difficult / Complex Legal (Graduate Level)"


def calculate_readability(text: str) -> dict[str, Any]:
    """Calculate Flesch Reading Ease and Flesch-Kincaid Grade Level.

    Formulas:
    - Flesch Reading Ease = 206.835 - 1.015 * (words/sentences) - 84.6 * (syllables/words)
    - Flesch-Kincaid Grade = 0.39 * (words/sentences) + 11.8 * (syllables/words) - 15.59
    """
    if not text or not text.strip():
        return {
            "flesch_reading_ease": 0.0,
            "flesch_kincaid_grade": 0.0,
            "word_count": 0,
            "sentence_count": 0,
            "syllable_count": 0,
            "interpretation": "Empty Text",
        }

    sentences = legal_sentence_tokenizer.tokenize(text)
    sentence_count = max(1, len(sentences))
    word_count, syllable_count = count_syllables_text(text)

    if word_count == 0:
        return {
            "flesch_reading_ease": 0.0,
            "flesch_kincaid_grade": 0.0,
            "word_count": 0,
            "sentence_count": sentence_count,
            "syllable_count": 0,
            "interpretation": "No Words Detected",
        }

    words_per_sentence = word_count / sentence_count
    syllables_per_word = syllable_count / word_count

    # Standard Flesch Reading Ease formula
    fre = 206.835 - (1.015 * words_per_sentence) - (84.6 * syllables_per_word)

    # Standard Flesch-Kincaid Grade Level formula
    fkg = (0.39 * words_per_sentence) + (11.8 * syllables_per_word) - 15.59

    # Round appropriately
    fre_rounded = round(fre, 1)
    fkg_rounded = max(0.0, round(fkg, 1))

    return {
        "flesch_reading_ease": fre_rounded,
        "flesch_kincaid_grade": fkg_rounded,
        "word_count": word_count,
        "sentence_count": sentence_count,
        "syllable_count": syllable_count,
        "interpretation": get_flesch_interpretation(fre_rounded),
    }
