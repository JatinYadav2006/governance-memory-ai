from __future__ import annotations

from typing import Any, Dict, List

import numpy as np

from backend.services.embedding_service import generate_embedding


# Prototype, in-memory "vector memory" store.
# Each entry contains the raw governance case + its embedding vector.
memory_store: List[Dict[str, Any]] = []


def _to_vector(embedding: Any) -> np.ndarray:
    """
    Normalize different embedding return types into a 1D numpy vector.
    """

    vec = np.asarray(embedding, dtype=np.float32)
    return vec.reshape(-1)


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """
    Compute cosine similarity between two 1D vectors.

    Returns 0.0 for zero-norm vectors to avoid division-by-zero.
    """

    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0.0:
        return 0.0
    return float(np.dot(a, b) / denom)


def add_memory(
    issue_title: str,
    issue_description: str,
    action_taken: str,
    outcome: str,
) -> Dict[str, Any]:
    """
    Add a governance case to the in-memory store.

    Steps:
    - generate embedding for the issue description
    - store the entry along with its embedding
    """

    embedding = _to_vector(generate_embedding(issue_description))
    entry: Dict[str, Any] = {
        "issue_title": issue_title,
        "issue_description": issue_description,
        "embedding": embedding,
        "action_taken": action_taken,
        "outcome": outcome,
    }
    memory_store.append(entry)
    return entry


def find_similar_cases(description: str) -> List[Dict[str, Any]]:
    """
    Retrieve the top 3 most similar stored cases for the given description.

    Steps:
    - generate embedding for the input description
    - compute cosine similarity with stored embeddings
    - rank results
    - return top 3 most similar cases
    """

    if not memory_store:
        return []

    query_vec = _to_vector(generate_embedding(description))

    scored: List[Dict[str, Any]] = []
    for entry in memory_store:
        entry_vec = _to_vector(entry.get("embedding"))
        score = _cosine_similarity(query_vec, entry_vec)

        # Return a copy without the raw embedding to keep payloads light.
        scored.append(
            {
                "issue_title": entry.get("issue_title", ""),
                "issue_description": entry.get("issue_description", ""),
                "action_taken": entry.get("action_taken", ""),
                "outcome": entry.get("outcome", ""),
                "similarity": score,
            }
        )

    scored.sort(key=lambda x: x["similarity"], reverse=True)
    return scored[:3]
