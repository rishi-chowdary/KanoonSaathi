#!/usr/bin/env python3
"""Script to download, verify, and report sizes of all offline NLP models.

Models:
1. spaCy model: en_core_web_md (NER & dependency parsing)
2. SentenceTransformers: all-MiniLM-L6-v2 (semantic similarity & hybrid search)
3. Hugging Face QA: deepset/minilm-uncased-squad2 (extractive QA with unanswerable support)
4. NLTK data: punkt tokenizer
5. Fine-tuned LEDGAR classifier check: models/clause_classifier (with SBERT fallback note)
"""

import logging
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("download_models")


def _dir_size_mb(path: Path) -> float:
    """Calculate recursive directory size in Megabytes."""
    if not path.exists():
        return 0.0
    return sum(f.stat().st_size for f in path.glob("**/*") if f.is_file()) / (
        1024 * 1024
    )


def _hf_model_size_mb(repo_id: str) -> float:
    """Estimate cached size of Hugging Face repository in hub cache."""
    cache_dir = Path.home() / ".cache" / "huggingface" / "hub"
    normalized_name = "models--" + repo_id.replace("/", "--")
    target_dir = cache_dir / normalized_name
    return _dir_size_mb(target_dir)


def main() -> int:
    logger.info("=" * 60)
    logger.info("KanoonSaathi — Offline NLP Model Verification & Download")
    logger.info("=" * 60)

    # 1. spaCy (en_core_web_md)
    try:
        import spacy
        import spacy.util

        try:
            spacy.load("en_core_web_md")
        except Exception:  # noqa: BLE001
            logger.info("Downloading spaCy model en_core_web_md...")
            import subprocess

            subprocess.run(
                [sys.executable, "-m", "spacy", "download", "en_core_web_md"],
                check=True,
            )

        spacy_path = spacy.util.get_package_path("en_core_web_md")
        size = _dir_size_mb(Path(spacy_path))
        logger.info("[OK] spaCy en_core_web_md loaded (disk size: %.1f MB).", size)
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to verify spaCy: %s", exc)
        return 1

    # 2. SentenceTransformers (all-MiniLM-L6-v2)
    try:
        from sentence_transformers import SentenceTransformer

        logger.info("Verifying SentenceTransformer 'all-MiniLM-L6-v2'...")
        model = SentenceTransformer("all-MiniLM-L6-v2")
        emb = model.encode(["Legal text verification"])
        size = _hf_model_size_mb("sentence-transformers/all-MiniLM-L6-v2")
        logger.info(
            "[OK] all-MiniLM-L6-v2 is ready (dim: %d, disk size: %.1f MB).",
            emb.shape[1],
            size,
        )
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to verify SentenceTransformer: %s", exc)
        return 1

    # 3. Extractive QA (deepset/minilm-uncased-squad2)
    try:
        from transformers import AutoModelForQuestionAnswering, AutoTokenizer

        qa_model_name = "deepset/minilm-uncased-squad2"
        logger.info("Verifying Extractive QA model '%s'...", qa_model_name)
        AutoTokenizer.from_pretrained(qa_model_name)
        AutoModelForQuestionAnswering.from_pretrained(qa_model_name)
        size = _hf_model_size_mb(qa_model_name)
        logger.info(
            "[OK] Extractive QA model '%s' is ready (disk size: %.1f MB).",
            qa_model_name,
            size,
        )
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to verify QA model: %s", exc)
        return 1

    # 4. NLTK punkt tokenizer
    try:
        import nltk

        nltk.download("punkt", quiet=True)
        logger.info("[OK] NLTK punkt tokenizer is ready.")
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to verify NLTK: %s", exc)
        return 1

    # 5. Fine-tuned Classifier Check
    classifier_dir = Path("models/clause_classifier")
    if classifier_dir.exists() and (classifier_dir / "config.json").exists():
        size = _dir_size_mb(classifier_dir)
        logger.info(
            "[OK] Fine-tuned LEDGAR classifier found in %s (disk size: %.1f MB).",
            classifier_dir,
            size,
        )
    else:
        logger.info(
            "[NOTE] Fine-tuned LEDGAR classifier not found in %s. "
            "Pipeline will gracefully use SBERT zero-shot + keyword rules ensemble.",
            classifier_dir,
        )

    logger.info("=" * 60)
    logger.info(
        "All offline NLP models verified successfully. Total cloud cost: $0.00."
    )
    logger.info("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
