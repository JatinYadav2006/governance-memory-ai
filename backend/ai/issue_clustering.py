from __future__ import annotations

import re
from collections import Counter, defaultdict
from functools import lru_cache
from typing import Any

import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.feature_extraction.text import TfidfVectorizer


MODEL_NAME = "all-MiniLM-L6-v2"
STOPWORDS = {
    "a",
    "an",
    "and",
    "at",
    "by",
    "for",
    "from",
    "in",
    "is",
    "near",
    "of",
    "on",
    "outside",
    "the",
    "to",
    "with",
}
SYNONYM_MAP = {
    "trash": "garbage",
    "waste": "garbage",
    "entrance": "gate",
    "overflowing": "overflow",
    "overflowed": "overflow",
    "outside": "near",
}


@lru_cache(maxsize=1)
def _get_model() -> Any:
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(MODEL_NAME)


def _to_vector(embedding: Any) -> np.ndarray:
    vector = np.asarray(embedding, dtype=np.float32)
    return vector.reshape(-1)


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    denominator = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denominator == 0.0:
        return 0.0
    return float(np.dot(a, b) / denominator)


def _extract_cluster_title(texts: list[str]) -> str:
    normalized_text = " ".join(_normalize_text(text) for text in texts)
    words = re.findall(r"[a-zA-Z]{3,}", normalized_text.lower())
    filtered = [word for word in words if word not in STOPWORDS]
    if not filtered:
        return "General issue cluster"

    most_common = [word for word, _ in Counter(filtered).most_common(3)]
    return " ".join(word.capitalize() for word in most_common)


def _cluster_location(items: list[dict[str, Any]]) -> str:
    locations = [str(item.get("location", "")).strip() for item in items if str(item.get("location", "")).strip()]
    if not locations:
        return "Unknown"
    return Counter(locations).most_common(1)[0][0]


def _normalize_text(text: str) -> str:
    words = re.findall(r"[a-zA-Z0-9]+", text.lower())
    normalized_words = [SYNONYM_MAP.get(word, word) for word in words]
    return " ".join(normalized_words)


def _build_fallback_embeddings(texts: list[str]) -> list[np.ndarray]:
    normalized_texts = [_normalize_text(text) for text in texts]
    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform(normalized_texts)
    return [matrix[i].toarray().reshape(-1).astype(np.float32) for i in range(matrix.shape[0])]


def _fallback_cluster_by_keywords(issue_list: list[dict[str, Any]], texts: list[str]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    grouped_texts: dict[tuple[str, str], list[str]] = defaultdict(list)

    for issue, text in zip(issue_list, texts):
        normalized = _normalize_text(text)
        tokens = [token for token in normalized.split() if token not in STOPWORDS]
        topic = tokens[0] if tokens else "general"
        location = str(issue.get("location", "")).strip() or "Unknown"
        key = (topic, location)
        grouped[key].append(issue)
        grouped_texts[key].append(text)

    clusters: list[dict[str, Any]] = []
    for idx, key in enumerate(sorted(grouped.keys()), start=1):
        items = grouped[key]
        clusters.append(
            {
                "cluster_id": idx,
                "cluster_title": _extract_cluster_title(grouped_texts[key]),
                "location": _cluster_location(items),
                "issue_ids": [int(item["id"]) for item in items if "id" in item],
                "issue_count": len(items),
            }
        )

    return clusters


def generate_embedding(text: str) -> list[float]:
    model = _get_model()
    embedding = model.encode(text or "", normalize_embeddings=False)
    if isinstance(embedding, np.ndarray):
        return embedding.tolist()
    return list(embedding)


def cluster_issues(issue_list: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not issue_list:
        return []

    combined_texts = [
        f"{str(issue.get('title', '')).strip()} {str(issue.get('description', '')).strip()}".strip()
        for issue in issue_list
    ]
    try:
        try:
            embeddings = [_to_vector(generate_embedding(text)) for text in combined_texts]
        except Exception:
            embeddings = _build_fallback_embeddings(combined_texts)

        similarity_matrix = np.zeros((len(embeddings), len(embeddings)), dtype=np.float32)
        for i, emb_a in enumerate(embeddings):
            for j, emb_b in enumerate(embeddings):
                similarity_matrix[i, j] = _cosine_similarity(emb_a, emb_b)

        distance_matrix = 1.0 - similarity_matrix
        clustering = DBSCAN(eps=0.35, min_samples=1, metric="precomputed")
        labels = clustering.fit_predict(distance_matrix)

        grouped: dict[int, list[dict[str, Any]]] = defaultdict(list)
        grouped_texts: dict[int, list[str]] = defaultdict(list)

        for issue, label, text in zip(issue_list, labels, combined_texts):
            grouped[int(label)].append(issue)
            grouped_texts[int(label)].append(text)

        clusters: list[dict[str, Any]] = []
        for cluster_id, items in grouped.items():
            clusters.append(
                {
                    "cluster_id": int(cluster_id),
                    "cluster_title": _extract_cluster_title(grouped_texts[cluster_id]),
                    "location": _cluster_location(items),
                    "issue_ids": [int(item["id"]) for item in items if "id" in item],
                    "issue_count": len(items),
                }
            )

        clusters.sort(key=lambda cluster: (cluster["cluster_id"], cluster["location"]))
        return clusters
    except Exception:
        return _fallback_cluster_by_keywords(issue_list, combined_texts)
