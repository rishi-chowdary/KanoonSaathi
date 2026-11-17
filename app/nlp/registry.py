import logging
import threading
from pathlib import Path
from typing import Any

logger = logging.getLogger("lexilegal.nlp.registry")

_lock = threading.Lock()
_spacy_nlp: Any | None = None
_sentence_model: Any | None = None
_clause_hf_model: Any | None = None
_clause_hf_tokenizer: Any | None = None


def get_spacy():
    """Retrieve the shared spaCy NLP pipeline instance.

    Uses en_core_web_md for syntactic parsing and legal NER;
    falls back gracefully to en_core_web_sm if medium model is not installed.
    """
    global _spacy_nlp
    if _spacy_nlp is not None:
        return _spacy_nlp

    with _lock:
        if _spacy_nlp is None:
            import spacy

            try:
                _spacy_nlp = spacy.load("en_core_web_md")
                logger.info("Loaded spaCy model: en_core_web_md")
            except Exception as e:  # noqa: BLE001 - graceful fallback to small model
                logger.warning(
                    "en_core_web_md not found (%s). Falling back to en_core_web_sm", e
                )
                _spacy_nlp = spacy.load("en_core_web_sm")
    return _spacy_nlp


def get_sentence_transformer():
    """Retrieve the shared SentenceTransformer instance.

    Uses all-MiniLM-L6-v2 (~90MB) for lightweight, high-speed dense embeddings
    on CPU without requiring GPU acceleration.
    """
    global _sentence_model
    if _sentence_model is not None:
        return _sentence_model

    with _lock:
        if _sentence_model is None:
            from sentence_transformers import SentenceTransformer

            logger.info("Loading SentenceTransformer: all-MiniLM-L6-v2")
            _sentence_model = SentenceTransformer("all-MiniLM-L6-v2")
            logger.info("SentenceTransformer loaded successfully.")
    return _sentence_model


def get_clause_hf_classifier() -> tuple[Any | None, Any | None]:
    """Retrieve fine-tuned Hugging Face clause classification model and tokenizer if present.

    Returns (model, tokenizer) if weights exist in models/clause_classifier,
    otherwise returns (None, None) so the ensemble gracefully uses SBERT + Rules.
    """
    global _clause_hf_model, _clause_hf_tokenizer
    if _clause_hf_model is not None and _clause_hf_tokenizer is not None:
        return _clause_hf_model, _clause_hf_tokenizer

    model_dir = Path("models/clause_classifier")
    if not (model_dir.exists() and (model_dir / "config.json").exists()):
        return None, None

    with _lock:
        if _clause_hf_model is None:
            try:
                from transformers import (
                    AutoModelForSequenceClassification,
                    AutoTokenizer,
                )

                logger.info("Loading fine-tuned clause classifier from %s", model_dir)
                _clause_hf_tokenizer = AutoTokenizer.from_pretrained(str(model_dir))
                _clause_hf_model = AutoModelForSequenceClassification.from_pretrained(
                    str(model_dir)
                )
                _clause_hf_model.eval()
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "Failed to load fine-tuned clause classifier (%s). Using SBERT fallback.",
                    exc,
                )
                return None, None

    return _clause_hf_model, _clause_hf_tokenizer
