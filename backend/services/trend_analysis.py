from __future__ import annotations

from collections import Counter
from typing import Any, Iterable, Mapping


TREND_KEYWORDS = [
    "water",
    "garbage",
    "drainage",
    "road",
    "power",
]
TREND_LABELS = {
    "water": "Water",
    "garbage": "Garbage",
    "drainage": "Drainage",
    "road": "Road",
    "power": "Power",
}
TREND_SYNONYMS = {
    "water": ["water", "pipeline", "supply", "leak"],
    "garbage": ["garbage", "trash", "waste", "overflow"],
    "drainage": ["drainage", "drain", "waterlogged"],
    "road": ["road", "pothole", "traffic", "surface"],
    "power": ["power", "electricity", "electric", "outage"],
}


def detect_issue_trends(issues: Iterable[Mapping[str, Any]]) -> dict[str, int]:
    """
    Detect frequently occurring issue types based on simple keyword counts.

    For each issue, this function inspects the text fields (typically
    description/title) and counts how many times each configured keyword
    appears across all issues (case-insensitive).

    Returns a dictionary of keyword -> count, including only keywords with
    at least one occurrence.
    """

    counter: Counter[str] = Counter()

    for issue in issues:
        # Concatenate potentially relevant text fields for keyword search.
        description = str(issue.get("description", "")).lower()
        title = str(issue.get("title", "")).lower()
        text = f"{title} {description}"

        for kw in TREND_KEYWORDS:
            synonyms = TREND_SYNONYMS.get(kw, [kw])
            if any(synonym in text for synonym in synonyms):
                counter[kw] += 1

    # Filter out keywords that never appeared.
    filtered = {TREND_LABELS.get(kw, kw.title()): count for kw, count in counter.items() if count > 0}

    # Sort by count descending for more useful "top trends" semantics.
    return dict(sorted(filtered.items(), key=lambda item: item[1], reverse=True))

