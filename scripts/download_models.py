#!/usr/bin/env python3
"""Script to download and verify local offline NLP models.

Downloads:
1. spaCy model: en_core_web_md
2. SentenceTransformers: all-MiniLM-L6-v2
3. NLTK data: punkt
"""

import logging
import sys

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("download_models")


def main() -> int:
    logger.info("Verifying and downloading required offline NLP models...")

    # 1. spaCy
    try:
        import spacy

        try:
            spacy.load("en_core_web_md")
            logger.info("[OK] spaCy model en_core_web_md is ready.")
        except Exception:  # noqa: BLE001 - trigger download if not loaded
            logger.info("Downloading spaCy model en_core_web_md...")
            import subprocess

            subprocess.run(
                [sys.executable, "-m", "spacy", "download", "en_core_web_md"],
                check=True,
            )
            logger.info("[OK] spaCy en_core_web_md installed successfully.")
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to verify spaCy: %s", exc)
        return 1

    # 2. SentenceTransformers
    try:
        from sentence_transformers import SentenceTransformer

        logger.info("Verifying SentenceTransformer 'all-MiniLM-L6-v2'...")
        model = SentenceTransformer("all-MiniLM-L6-v2")
        emb = model.encode(["Legal text verification"])
        logger.info("[OK] all-MiniLM-L6-v2 is ready (dim: %s).", emb.shape[1])
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to verify SentenceTransformer: %s", exc)
        return 1

    # 3. NLTK punkt
    try:
        import nltk

        nltk.download("punkt", quiet=True)
        logger.info("[OK] NLTK punkt tokenizer is ready.")
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to verify NLTK: %s", exc)
        return 1

    logger.info("All offline NLP models verified successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
