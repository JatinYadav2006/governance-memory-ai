from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from backend.services.embedding_service import generate_embedding as shared_generate_embedding


def _to_vector(value: Any) -> np.ndarray:
    vector = np.asarray(value, dtype=np.float32)
    return vector.reshape(-1)


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    denominator = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denominator == 0.0:
        return 0.0
    return float(np.dot(a, b) / denominator)


def embed_text(text: str) -> list[float]:
    embedding = shared_generate_embedding(text or "")
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
    issue_texts = [
        f"{str(issue.get('title', '')).strip()} {str(issue.get('description', '')).strip()}".strip()
        for issue in resolved_issues
    ]

    try:
        query_vector = _to_vector(embed_text(query_text))
        candidate_vectors = []
        for issue, issue_text in zip(resolved_issues, issue_texts):
            stored_embedding = issue.get("embedding")
            if stored_embedding is None:
                candidate_vectors.append(_to_vector(embed_text(issue_text)))
            else:
                candidate_vectors.append(_to_vector(stored_embedding))
    except Exception:
        vectorizer = TfidfVectorizer(stop_words="english")
        matrix = vectorizer.fit_transform([query_text] + issue_texts)
        query_vector = matrix[0].toarray().reshape(-1).astype(np.float32)
        candidate_vectors = [
            matrix[index + 1].toarray().reshape(-1).astype(np.float32)
            for index in range(len(resolved_issues))
        ]

    best_match: dict[str, Any] | None = None
    best_score = -1.0

    for issue, candidate_vector in zip(resolved_issues, candidate_vectors):
        issue_title = str(issue.get("title", "")).strip()
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
