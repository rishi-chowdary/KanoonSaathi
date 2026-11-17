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
_qa_model: Any | None = None
_qa_tokenizer: Any | None = None


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
                logger.info("loaded spacy model: en_core_web_md")
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "en_core_web_md not found (%s); falling back to en_core_web_sm",
                    exc,
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

            logger.info("loading sentence-transformer: all-MiniLM-L6-v2")
            _sentence_model = SentenceTransformer("all-MiniLM-L6-v2")
            logger.info("sentence-transformer ready")
    return _sentence_model


get_sbert = get_sentence_transformer


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

                logger.info("loading clause classifier from %s", model_dir)
                _clause_hf_tokenizer = AutoTokenizer.from_pretrained(str(model_dir))
                _clause_hf_model = AutoModelForSequenceClassification.from_pretrained(
                    str(model_dir)
                )
                _clause_hf_model.eval()
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "could not load clause classifier (%s); using sbert + rules fallback",
                    exc,
                )
                return None, None

    return _clause_hf_model, _clause_hf_tokenizer


def get_qa_model() -> tuple[Any, Any]:
    """Retrieve the shared Hugging Face extractive question answering model and tokenizer.

    Uses deepset/minilm-uncased-squad2 for fast, CPU-friendly extractive QA with
    SQuAD 2.0 unanswerable thresholding.
    """
    global _qa_model, _qa_tokenizer
    if _qa_model is not None and _qa_tokenizer is not None:
        return _qa_model, _qa_tokenizer

    with _lock:
        if _qa_model is None:
            from transformers import AutoModelForQuestionAnswering, AutoTokenizer

            model_name = "deepset/minilm-uncased-squad2"
            logger.info("loading qa model: %s", model_name)
            _qa_tokenizer = AutoTokenizer.from_pretrained(model_name)
            _qa_model = AutoModelForQuestionAnswering.from_pretrained(model_name)
            _qa_model.eval()
            logger.info("qa model ready")

    return _qa_model, _qa_tokenizer
