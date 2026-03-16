from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any, Iterable, Mapping


CATEGORY_KEYWORDS = {
    "Water": ["water", "pipeline", "supply", "drain", "drainage", "leak"],
    "Road": ["road", "pothole", "traffic", "street", "surface"],
    "Garbage": ["garbage", "trash", "waste", "overflow", "sanitation"],
    "Electricity": ["electricity", "electric", "power", "outage", "grid"],
    "Health": ["hospital", "clinic", "ambulance", "medical"],
}


def _detect_category(text: str) -> str:
    """
    Detect a coarse category for an issue based on description keywords.
    Returns one of the keys in CATEGORY_KEYWORDS or "Other" if none match.
    """

    text = text.lower()
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
        title = str(issue.get("title", "")).strip()
        combined_text = f"{title} {description}".strip()
        category = _detect_category(combined_text) if combined_text else "Other"
        category_counter[category] += 1

    return {
        "total_issues": total_issues,
        "by_urgency": dict(urgency_counter),
        "by_category": dict(category_counter),
    }

