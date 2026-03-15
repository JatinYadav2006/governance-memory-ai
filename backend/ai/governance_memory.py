from __future__ import annotations

from functools import lru_cache
from typing import Any

import numpy as np
from sentence_transformers import SentenceTransformer


MODEL_NAME = "all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def _get_model() -> SentenceTransformer:
    return SentenceTransformer(MODEL_NAME)


def _to_vector(value: Any) -> np.ndarray:
    vector = np.asarray(value, dtype=np.float32)
    return vector.reshape(-1)


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    denominator = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denominator == 0.0:
        return 0.0
    return float(np.dot(a, b) / denominator)


def embed_text(text: str) -> list[float]:
    model = _get_model()
    embedding = model.encode(text or "", normalize_embeddings=False)
    if isinstance(embedding, np.ndarray):
        return embedding.tolist()
    return list(embedding)


def find_similar_case(
    cluster_title: str,
    cluster_description: str,
    resolved_issues: list[dict[str, Any]],
) -> dict[str, Any] | None:
    if not resolved_issues:
        return None

    query_text = f"{cluster_title.strip()} {cluster_description.strip()}".strip()
    query_vector = _to_vector(embed_text(query_text))

    best_match: dict[str, Any] | None = None
    best_score = -1.0

    for issue in resolved_issues:
        issue_title = str(issue.get("title", "")).strip()
        issue_description = str(issue.get("description", "")).strip()
        issue_text = f"{issue_title} {issue_description}".strip()

        stored_embedding = issue.get("embedding")
        if stored_embedding is None:
            candidate_vector = _to_vector(embed_text(issue_text))
        else:
            candidate_vector = _to_vector(stored_embedding)

        score = _cosine_similarity(query_vector, candidate_vector)
        if score > best_score:
            best_score = score
            best_match = {
                "similar_case_title": issue_title or "Untitled resolved issue",
                "location": str(issue.get("location", "Unknown")).strip() or "Unknown",
                "action_taken": str(issue.get("action_taken", "No action recorded")).strip() or "No action recorded",
                "similarity_score": round(score, 2),
            }

    return best_match
