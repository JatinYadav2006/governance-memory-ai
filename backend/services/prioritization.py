from __future__ import annotations

from collections import defaultdict
from typing import Dict, Mapping


# Simple, in-memory tracker for recurrence by location.
# Each call to `calculate_priority` is treated as a new issue event.
_location_counts: Dict[str, int] = defaultdict(int)

_URGENCY_SCORES: Dict[str, int] = {
    "low": 1,
    "medium": 2,
    "high": 3,
}

_SEVERITY_KEYWORDS = {
    "water",
    "electricity",
    "road",
    "hospital",
    "flood",
}


def calculate_priority(issue: Mapping[str, str]) -> float:
    """
    Compute a simple priority score for a citizen issue.

    The score combines:
    - urgency (1–3)
    - recurrence (number of issues seen for the same location)
    - severity (count of severity-related keywords in the description)

    priority_score = 0.5 * urgency_score
                      + 0.3 * recurrence_score
                      + 0.2 * severity_score
    """

    title = (issue.get("title") or "").strip()
    description = (issue.get("description") or "").strip()
    location = (issue.get("location") or "").strip()
    urgency_raw = (issue.get("urgency") or "").strip().lower()

    # Urgency mapping: Low=1, Medium=2, High=3 (default to 1 if unknown).
    urgency_score = _URGENCY_SCORES.get(urgency_raw, 1)

    # Recurrence score: increment for each issue seen at the same location.
    if location:
        _location_counts[location] += 1
        recurrence_score = _location_counts[location]
    else:
        recurrence_score = 1

    # Severity score: count of distinct severity keywords in the description.
    text_blob = f"{title} {description}".lower()
    severity_score = sum(1 for kw in _SEVERITY_KEYWORDS if kw in text_blob)

    priority_score = (
        0.5 * urgency_score
        + 0.3 * recurrence_score
        + 0.2 * severity_score
    )

    return float(priority_score)

