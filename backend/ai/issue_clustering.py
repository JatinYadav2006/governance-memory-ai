from __future__ import annotations

import re
from collections import Counter, defaultdict
from typing import Any

import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.feature_extraction.text import TfidfVectorizer

from backend.services.embedding_service import generate_embedding as shared_generate_embedding


STOPWORDS = {
    "a",
    "an",
    "and",
    "area",
    "at",
    "by",
    "for",
    "from",
    "gate",
    "in",
    "is",
    "issue",
    "main",
    "near",
    "of",
    "on",
    "outside",
    "problem",
    "the",
    "to",
    "with",
}
SYNONYM_MAP = {
    "trash": "garbage",
    "waste": "garbage",
    "overflowing": "overflow",
    "overflowed": "overflow",
    "entrance": "gate",
    "outside": "near",
    "potholes": "pothole",
    "holes": "pothole",
    "roads": "road",
    "electricity": "power",
    "pipeline": "pipe",
}
TITLE_PATTERNS = [
    ({"garbage", "overflow"}, "Garbage Overflow"),
    ({"garbage"}, "Garbage Collection Issue"),
    ({"water", "supply"}, "Water Supply Issue"),
    ({"water", "pipe"}, "Water Pipeline Issue"),
    ({"water"}, "Water Access Issue"),
    ({"drainage"}, "Drainage Blockage"),
    ({"drain"}, "Drainage Issue"),
    ({"road", "pothole"}, "Road Pothole Hazard"),
    ({"road"}, "Road Maintenance Issue"),
    ({"power"}, "Power Supply Issue"),
    ({"electric"}, "Power Supply Issue"),
]


def _to_vector(embedding: Any) -> np.ndarray:
    vector = np.asarray(embedding, dtype=np.float32)
    return vector.reshape(-1)


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    denominator = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denominator == 0.0:
        return 0.0
    return float(np.dot(a, b) / denominator)


def _normalize_text(text: str) -> str:
    words = re.findall(r"[a-zA-Z0-9]+", text.lower())
    normalized_words = [SYNONYM_MAP.get(word, word) for word in words]
    return " ".join(normalized_words)


def _extract_keywords(texts: list[str]) -> list[str]:
    normalized_text = " ".join(_normalize_text(text) for text in texts)
    words = re.findall(r"[a-zA-Z]{3,}", normalized_text.lower())
    filtered = [word for word in words if word not in STOPWORDS]
    return [word for word, _ in Counter(filtered).most_common(5)]


def _extract_cluster_title(texts: list[str]) -> str:
    keywords = _extract_keywords(texts)
    keyword_set = set(keywords)
    for required_words, title in TITLE_PATTERNS:
        if required_words.issubset(keyword_set):
            return title

    if not keywords:
        return "Recurring Civic Issue"

    top_two = keywords[:2]
    if len(top_two) == 1:
        return f"{top_two[0].capitalize()} Service Issue"
    return " ".join(word.capitalize() for word in top_two)


def _cluster_confidence(indices: list[int], similarity_matrix: np.ndarray) -> float:
    if len(indices) <= 1:
        return 0.84

    scores: list[float] = []
    for pos, idx_a in enumerate(indices):
        for idx_b in indices[pos + 1 :]:
            scores.append(float(similarity_matrix[idx_a, idx_b]))

    if not scores:
        return 0.84

    average = sum(scores) / len(scores)
    bounded = min(max(average, 0.0), 1.0)
    return round(bounded, 2)


def _cluster_location(items: list[dict[str, Any]]) -> str:
    locations = [str(item.get("location", "")).strip() for item in items if str(item.get("location", "")).strip()]
    if not locations:
        return "Unknown"
    return Counter(locations).most_common(1)[0][0]


def _build_fallback_embeddings(texts: list[str]) -> list[np.ndarray]:
    normalized_texts = [_normalize_text(text) for text in texts]
    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform(normalized_texts)
    return [matrix[i].toarray().reshape(-1).astype(np.float32) for i in range(matrix.shape[0])]


def _fallback_cluster_by_keywords(issue_list: list[dict[str, Any]], texts: list[str]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    grouped_texts: dict[tuple[str, str], list[str]] = defaultdict(list)

    for issue, text in zip(issue_list, texts):
        keywords = _extract_keywords([text])
        topic = keywords[0] if keywords else "general"
        location = str(issue.get("location", "")).strip() or "Unknown"
        key = (topic, location)
        grouped[key].append(issue)
        grouped_texts[key].append(text)

    clusters: list[dict[str, Any]] = []
    for idx, key in enumerate(sorted(grouped.keys()), start=1):
        items = grouped[key]
        evidence_terms = _extract_keywords(grouped_texts[key])[:3]
        clusters.append(
            {
                "cluster_id": idx,
                "cluster_title": _extract_cluster_title(grouped_texts[key]),
                "location": _cluster_location(items),
                "issue_ids": [int(item["id"]) for item in items if "id" in item],
                "issue_count": len(items),
                "confidence_score": 0.72,
                "evidence_terms": evidence_terms,
            }
        )

    return clusters


def generate_embedding(text: str) -> list[float]:
    embedding = shared_generate_embedding(text or "")
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

        cluster_indices: dict[int, list[int]] = defaultdict(list)
        for index, (issue, label, text) in enumerate(zip(issue_list, labels, combined_texts)):
            grouped[int(label)].append(issue)
            grouped_texts[int(label)].append(text)
            cluster_indices[int(label)].append(index)

        clusters: list[dict[str, Any]] = []
        for cluster_id, items in grouped.items():
            evidence_terms = _extract_keywords(grouped_texts[cluster_id])[:3]
            clusters.append(
                {
                    "cluster_id": int(cluster_id),
                    "cluster_title": _extract_cluster_title(grouped_texts[cluster_id]),
                    "location": _cluster_location(items),
                    "issue_ids": [int(item["id"]) for item in items if "id" in item],
                    "issue_count": len(items),
                    "confidence_score": _cluster_confidence(cluster_indices[cluster_id], similarity_matrix),
                    "evidence_terms": evidence_terms,
                }
            )

        clusters.sort(key=lambda cluster: (-int(cluster["issue_count"]), str(cluster["location"])))
        return clusters
    except Exception:
        return _fallback_cluster_by_keywords(issue_list, combined_texts)
