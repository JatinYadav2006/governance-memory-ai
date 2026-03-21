from __future__ import annotations

import re
from typing import Mapping

from backend.db.database import IssueRecord, SessionLocal


_URGENCY_SCORES = {
    "low": 1.0,
    "medium": 2.0,
    "high": 3.0,
}

_CATEGORY_PATTERNS = {
    "water": ["water", "pipeline", "pipe", "leak", "tap", "supply", "drain", "drainage"],
    "power": ["power", "electric", "electricity", "outage", "grid", "streetlight"],
    "road": ["road", "pothole", "traffic", "surface", "street"],
    "garbage": ["garbage", "trash", "waste", "sanitation", "overflow", "bin"],
    "health": ["hospital", "ambulance", "medical", "clinic"],
}

_CATEGORY_BASE_IMPACT = {
    "water": 2.4,
    "power": 2.2,
    "road": 1.8,
    "garbage": 1.6,
    "health": 2.5,
    "general": 1.2,
}

_HIGH_RISK_TERMS = {
    "flood",
    "burst",
    "danger",
    "accident",
    "injury",
    "blocked",
    "outage",
    "collapsed",
    "sewage",
    "emergency",
    "unsafe",
}

_MEDIUM_RISK_TERMS = {
    "overflow",
    "broken",
    "delay",
    "leak",
    "dirty",
    "waterlogged",
    "smell",
    "damage",
}

_MAX_RECURRENCE_SCORE = 2.0
_MAX_RISK_SCORE = 2.0
_MAX_DESCRIPTION_LENGTH = 600


def _normalize_text(text: str) -> str:
    lowered = text.lower()
    lowered = re.sub(r"\s+", " ", lowered).strip()
    return lowered[:_MAX_DESCRIPTION_LENGTH]


def _tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-zA-Z]+", text.lower()))


def _detect_category(text: str) -> str:
    lowered = text.lower()
    for category, patterns in _CATEGORY_PATTERNS.items():
        if any(pattern in lowered for pattern in patterns):
            return category
    return "general"


def _risk_signal_score(text: str) -> float:
    tokens = _tokenize(text)
    high_matches = len(tokens & _HIGH_RISK_TERMS)
    medium_matches = len(tokens & _MEDIUM_RISK_TERMS)
    score = (high_matches * 0.8) + (medium_matches * 0.35)
    return min(score, _MAX_RISK_SCORE)


def _recurrence_score(location: str, category: str) -> float:
    if not location:
        return 0.4

    session = SessionLocal()
    try:
        open_issues = (
            session.query(IssueRecord)
            .filter(IssueRecord.status == "Open")
            .filter(IssueRecord.location.ilike(location.strip()))
            .all()
        )
    finally:
        session.close()

    similar_open_count = 0
    for issue in open_issues:
        issue_category = _detect_category(f"{issue.title} {issue.description}")
        if issue_category == category:
            similar_open_count += 1

    return min(0.4 + (similar_open_count * 0.4), _MAX_RECURRENCE_SCORE)


def calculate_priority(issue: Mapping[str, str]) -> float:
    """
    Compute a more defensible priority score for a citizen issue.

    Design goals:
    - repeated words should not inflate the score
    - recurrence should come from actual stored open complaints, not an in-memory counter
    - essential services and visible risk signals should matter
    - the final score should stay in a readable range for the UI
    """

    title = _normalize_text(str(issue.get("title") or ""))
    description = _normalize_text(str(issue.get("description") or ""))
    location = str(issue.get("location") or "").strip()
    urgency_raw = str(issue.get("urgency") or "").strip().lower()

    combined_text = f"{title} {description}".strip()
    category = _detect_category(combined_text)

    urgency_score = _URGENCY_SCORES.get(urgency_raw, 1.0)
    category_score = _CATEGORY_BASE_IMPACT.get(category, _CATEGORY_BASE_IMPACT["general"])
    recurrence_score = _recurrence_score(location, category)
    risk_score = _risk_signal_score(combined_text)

    priority_score = (
        (urgency_score * 0.9)
        + (category_score * 0.45)
        + (recurrence_score * 0.55)
        + (risk_score * 0.5)
    )

    return round(float(priority_score), 2)
