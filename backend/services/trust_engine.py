from __future__ import annotations

from typing import Any, Iterable, Mapping

from backend.services.sentiment_service import analyze_sentiment


def calculate_trust_score(issues: Iterable[Mapping[str, Any]]) -> int:
    """
    Calculate a public trust score based on issue volume, urgency, and sentiment.

    Prototype logic:
    - Start from 100
    - For each issue:
      - High urgency  -> -5
      - Medium urgency -> -3
      - Negative sentiment (description) -> -4
    - Clamp final score to the range [0, 100]

    Notes:
    - This function intentionally stays simple for the MVP.
    - It can later be extended with weighting by time, resolution rate,
      department performance, and verified outcomes.
    """

    score = 100

    for issue in issues:
        urgency = str(issue.get("urgency", "")).strip().lower()
        description = str(issue.get("description", "")).strip()

        # Urgency-based impact.
        if urgency == "high":
            score -= 5
        elif urgency == "medium":
            score -= 3

        # Sentiment-based impact.
        if description and analyze_sentiment(description) == "negative":
            score -= 4

    # Clamp score to [0, 100].
    if score < 0:
        return 0
    if score > 100:
        return 100
    return int(score)

