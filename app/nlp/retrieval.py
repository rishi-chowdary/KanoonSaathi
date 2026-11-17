"""LexiLegal AI — Hybrid Retrieval Engine.

Implements hybrid passage retrieval over page-aware document chunks:
1. Dense semantic search: SBERT cosine similarity (all-MiniLM-L6-v2)
2. Sparse lexical search: BM25 / token matching and MySQL FULLTEXT
3. Reciprocal Rank Fusion (RRF): RRF_score = 1/(60 + dense_rank) + 1/(60 + sparse_rank)
"""

from __future__ import annotations

import math
import re
from typing import Any

import numpy as np

from app.nlp.registry import get_sentence_transformer

# Standard English stop words for lexical token matching
_STOP_WORDS = {
    "a",
    "about",
    "above",
    "after",
    "again",
    "against",
    "all",
    "am",
    "an",
    "and",
    "any",
    "are",
    "aren't",
    "as",
    "at",
    "be",
    "because",
    "been",
    "before",
    "being",
    "below",
    "between",
    "both",
    "but",
    "by",
    "can't",
    "cannot",
    "could",
    "did",
    "do",
    "does",
    "doing",
    "don't",
    "down",
    "during",
    "each",
    "few",
    "for",
    "from",
    "further",
    "had",
    "has",
    "have",
    "having",
    "he",
    "her",
    "here",
    "hers",
    "herself",
    "him",
    "himself",
    "his",
    "how",
    "i",
    "if",
    "in",
    "into",
    "is",
    "isn't",
    "it",
    "its",
    "itself",
    "let's",
    "me",
    "more",
    "most",
    "my",
    "myself",
    "no",
    "nor",
    "not",
    "of",
    "off",
    "on",
    "once",
    "only",
    "or",
    "other",
    "ought",
    "our",
    "ours",
    "ourselves",
    "out",
    "over",
    "own",
    "same",
    "she",
    "should",
    "so",
    "some",
    "such",
    "than",
    "that",
    "the",
    "their",
    "theirs",
    "them",
    "themselves",
    "then",
    "there",
    "these",
    "they",
    "this",
    "those",
    "through",
    "to",
    "too",
    "under",
    "until",
    "up",
    "very",
    "was",
    "wasn't",
    "we",
    "were",
    "what",
    "when",
    "where",
    "which",
    "while",
    "who",
    "whom",
    "why",
    "with",
    "won't",
    "would",
    "you",
    "your",
    "yours",
    "yourself",
    "yourselves",
}


def tokenize_words(text: str) -> list[str]:
    """Tokenize and filter stop words for lexical search."""
    tokens = re.findall(r"\b[A-Za-z0-9'-]+\b", text.lower())
    return [t for t in tokens if t not in _STOP_WORDS and len(t) > 1]


def bm25_score_chunks(query: str, chunks: list[Any]) -> list[tuple[Any, float]]:
    """Compute BM25 / TF-IDF relevance scores for chunks against query."""
    q_tokens = tokenize_words(query)
    if not q_tokens or not chunks:
        return [(c, 0.0) for c in chunks]

    # Precompute document frequencies
    doc_tokens_list = [tokenize_words(getattr(c, "content", "")) for c in chunks]
    total_docs = len(chunks)
    avg_dl = sum(len(dt) for dt in doc_tokens_list) / max(1, total_docs)

    df: dict[str, int] = {}
    for dt in doc_tokens_list:
        seen = set(dt)
        for t in seen:
            df[t] = df.get(t, 0) + 1

    k1 = 1.5
    b = 0.75

    scores: list[tuple[Any, float]] = []
    for idx, chunk in enumerate(chunks):
        doc_tokens = doc_tokens_list[idx]
        dl = len(doc_tokens)
        score = 0.0

        for q in q_tokens:
            if q not in df:
                continue
            # IDF with Robertson-Spärck Jones formula
            doc_freq = df[q]
            idf = math.log((total_docs - doc_freq + 0.5) / (doc_freq + 0.5) + 1.0)

            # Term frequency
            tf = doc_tokens.count(q)
            if tf > 0:
                tf_norm = (tf * (k1 + 1)) / (
                    tf + k1 * (1 - b + b * (dl / max(1, avg_dl)))
                )
                score += idf * tf_norm

        scores.append((chunk, score))

    return scores


def hybrid_retrieve_chunks(
    query: str,
    chunks: list[Any],
    top_k: int = 4,
    rrf_k: int = 60,
) -> list[dict[str, Any]]:
    """Execute hybrid retrieval combining SBERT dense search with BM25 sparse search using RRF.

    Returns top_k retrieved chunks with page numbers, content, and fused scores.
    """
    if not chunks:
        return []

    if len(chunks) <= top_k:
        # If total chunks are fewer than top_k, return all chunks ordered by page
        sorted_chunks = sorted(chunks, key=lambda c: getattr(c, "page_number", 1))
        return [
            {
                "chunk_id": getattr(c, "id", str(idx)),
                "chunk_index": getattr(c, "chunk_index", idx),
                "page_number": getattr(c, "page_number", 1),
                "content": getattr(c, "content", ""),
                "score": 1.0,
            }
            for idx, c in enumerate(sorted_chunks)
        ]

    sbert = get_sentence_transformer()
    q_emb = sbert.encode([query], normalize_embeddings=True)[0]

    chunk_contents = [getattr(c, "content", "") for c in chunks]
    chunk_embs = sbert.encode(chunk_contents, normalize_embeddings=True)

    dense_similarities = np.dot(chunk_embs, q_emb)
    # Dense rank: sort descending (1-indexed rank)
    dense_indices = np.argsort(-dense_similarities)
    dense_ranks = {chunks[idx]: rank + 1 for rank, idx in enumerate(dense_indices)}

    bm25_scores = bm25_score_chunks(query, chunks)
    bm25_scores.sort(key=lambda x: x[1], reverse=True)
    sparse_ranks = {
        chunk_score[0]: rank + 1 for rank, chunk_score in enumerate(bm25_scores)
    }

    # RRF_score(d) = 1/(rrf_k + dense_rank) + 1/(rrf_k + sparse_rank)
    fused_results: list[dict[str, Any]] = []

    for chunk in chunks:
        d_rank = dense_ranks.get(chunk, len(chunks))
        s_rank = sparse_ranks.get(chunk, len(chunks))

        rrf_score = (1.0 / (rrf_k + d_rank)) + (1.0 / (rrf_k + s_rank))

        fused_results.append(
            {
                "chunk_id": getattr(chunk, "id", ""),
                "chunk_index": getattr(chunk, "chunk_index", 0),
                "page_number": getattr(chunk, "page_number", 1),
                "content": getattr(chunk, "content", ""),
                "dense_score": float(dense_similarities[chunks.index(chunk)]),
                "score": round(rrf_score, 6),
            }
        )

    fused_results.sort(key=lambda x: x["score"], reverse=True)
    return fused_results[:top_k]
