from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any, Iterable, Mapping


CATEGORY_KEYWORDS = {
    "Water": ["water"],
    "Road": ["road"],
    "Garbage": ["garbage"],
    "Electricity": ["electricity"],
    "Hospital": ["hospital"],
}


def _detect_category(description: str) -> str:
    """
    Detect a coarse category for an issue based on description keywords.
    Returns one of the keys in CATEGORY_KEYWORDS or "Other" if none match.
    """

    text = description.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            return category
    return "Other"


def generate_issue_statistics(issues: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    """
    Generate basic governance statistics over a collection of issues.

    Computes:
    - total number of issues
    - count of issues by urgency (case-insensitive)
    - count of issues by detected category (based on description keywords)
    """

    total_issues = 0
    urgency_counter: Counter[str] = Counter()
    category_counter: Counter[str] = Counter()

    for issue in issues:
        total_issues += 1

        urgency_raw = str(issue.get("urgency", "")).strip().lower()
        urgency_label = urgency_raw.capitalize() if urgency_raw else "Unknown"
        urgency_counter[urgency_label] += 1

        description = str(issue.get("description", "")).strip()
        category = _detect_category(description) if description else "Other"
        category_counter[category] += 1

    return {
        "total_issues": total_issues,
        "by_urgency": dict(urgency_counter),
        "by_category": dict(category_counter),
    }

