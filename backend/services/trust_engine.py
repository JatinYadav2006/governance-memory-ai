from __future__ import annotations

from collections import Counter
from typing import Any, Iterable, Mapping

from backend.services.sentiment_service import analyze_sentiment


def _clamp(value: float, minimum: int = 0, maximum: int = 100) -> int:
    return int(max(minimum, min(maximum, round(value))))


def calculate_trust_score(issues: Iterable[Mapping[str, Any]]) -> int:
    """
    Calculate a public trust score using aggregate service-health signals.

    Why this version is softer than the old one:
    - Trust should not collapse by a large fixed amount for every single complaint.
    - Citizens usually react to backlog pressure, overdue response, repeated failures,
      and concentration of high-severity issues more than raw complaint count alone.
    - Verified resolution and resolved-history presence should help stabilize trust.

    Inputs expected on each issue when available:
    - urgency
    - description
    - status
    - overdue
    - age_hours
    - location
    - category
    """

    issue_list = list(issues)
    if not issue_list:
        return 100

    active_issues = [
        issue for issue in issue_list
        if str(issue.get("status", "Open")).strip().lower() != "resolved"
    ]
    resolved_issues = [
        issue for issue in issue_list
        if str(issue.get("status", "")).strip().lower() == "resolved"
    ]

    if not active_issues:
        resolved_ratio = len(resolved_issues) / max(len(issue_list), 1)
        return _clamp(92 + min(8, resolved_ratio * 12), minimum=70, maximum=100)

    total_active = len(active_issues)
    high_urgency = sum(1 for issue in active_issues if str(issue.get("urgency", "")).strip().lower() == "high")
    medium_urgency = sum(1 for issue in active_issues if str(issue.get("urgency", "")).strip().lower() == "medium")
    overdue_count = sum(1 for issue in active_issues if bool(issue.get("overdue", False)))
    long_open_count = sum(1 for issue in active_issues if float(issue.get("age_hours", 0.0) or 0.0) >= 24.0)
    negative_sentiment = sum(
        1
        for issue in active_issues
        if str(issue.get("description", "")).strip()
        and analyze_sentiment(str(issue.get("description", "")).strip()) == "negative"
    )

    concentration_counter = Counter(
        (
            str(issue.get("location", "")).strip().lower(),
            str(issue.get("category", "")).strip().lower(),
        )
        for issue in active_issues
    )
    repeat_pressure = sum(max(0, count - 1) for count in concentration_counter.values())

    resolved_ratio = len(resolved_issues) / max(len(issue_list), 1)
    negative_ratio = negative_sentiment / max(total_active, 1)

    score = 92.0

    # Backlog pressure should matter, but gradually.
    score -= min(14.0, total_active * 1.1)

    # Urgency mix should influence trust more than raw issue count.
    score -= min(12.0, (high_urgency * 1.8) + (medium_urgency * 0.7))

    # Overdue and long-open complaints hurt confidence in responsiveness.
    score -= min(12.0, overdue_count * 2.4)
    score -= min(6.0, long_open_count * 0.8)

    # Repeated failures in the same location/category are worse than isolated complaints.
    score -= min(8.0, repeat_pressure * 1.2)

    # Sentiment matters, but as a concentration signal rather than a fixed heavy deduction.
    score -= min(7.0, negative_ratio * 8.0)

    # Resolved history should stabilize trust and reflect visible action.
    score += min(10.0, resolved_ratio * 14.0)

    # Keep the metric realistic for a prototype: trust should be pressured, not collapse instantly.
    return _clamp(score, minimum=28, maximum=100)
