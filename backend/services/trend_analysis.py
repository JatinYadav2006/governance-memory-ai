from __future__ import annotations

from collections import Counter
from typing import Any, Iterable, Mapping


TREND_KEYWORDS = [
    "water",
    "garbage",
    "road",
    "electricity",
    "drainage",
]


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
            if kw in text:
                counter[kw] += 1

    # Filter out keywords that never appeared.
    filtered = {kw: count for kw, count in counter.items() if count > 0}

    # Sort by count descending for more useful "top trends" semantics.
    return dict(sorted(filtered.items(), key=lambda item: item[1], reverse=True))

