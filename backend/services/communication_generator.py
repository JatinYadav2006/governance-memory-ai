from __future__ import annotations

from typing import Any, Mapping


def generate_public_update(issue: Mapping[str, Any]) -> str:
    """
    Generate an official public-facing update message for a reported issue.

    This is a lightweight template-based generator for the MVP. It can later be
    upgraded to support multiple languages, tone control, and richer context
    (timestamps, department, ETA, verification status, and contact channels).
    """

    title = str(issue.get("title", "")).strip() or "a reported issue"
    location = str(issue.get("location", "")).strip() or "the affected area"
    urgency = str(issue.get("urgency", "")).strip().lower()

    lines: list[str] = [
        f"Municipal authorities are aware of the issue regarding {title} in {location}.",
        "Teams have been assigned to investigate and resolve the situation.",
    ]

    if urgency == "high":
        lines.append("Immediate attention is being given to this matter.")

    lines.append("Citizens will be informed once the issue is addressed.")

    return " ".join(lines)

