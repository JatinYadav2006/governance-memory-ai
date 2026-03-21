from __future__ import annotations

from functools import lru_cache
from typing import Any, Union

import numpy as np


MODEL_NAME = "all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def _get_model() -> Any:
    """
    Load the Sentence Transformers model once and cache it.

    This prevents reloading the model for every embedding request.
    """

    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(MODEL_NAME)


def generate_embedding(text: str) -> Union[list[float], np.ndarray]:
    """
    Generate an embedding vector for the given text.

    This is a small, reusable building block that will later be used for
    semantic similarity search inside the Governance Memory system.
    """

    model = _get_model()

    # `encode` returns a numpy array for a single input string by default.
    embedding = model.encode(text, normalize_embeddings=False)

    # Return a python list for easy JSON-serialization when needed.
    if isinstance(embedding, np.ndarray):
        return embedding.tolist()

    return embedding
