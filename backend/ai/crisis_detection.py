from __future__ import annotations

from typing import Any


POTENTIAL_CRISIS_THRESHOLD = 10
SEVERE_CRISIS_THRESHOLD = 30


def _to_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _message_for_cluster(cluster_title: str, severity: str) -> str:
    title_lower = cluster_title.lower()

    if "water" in title_lower:
        if severity == "Severe":
            return "Water complaints have surged to a severe level and may indicate a major distribution or infrastructure failure."
        return "Water complaints are rising sharply and may indicate infrastructure stress that now needs fast intervention."

    if "garbage" in title_lower or "waste" in title_lower or "trash" in title_lower:
        if severity == "Severe":
            return "Sanitation complaints are now at a severe level and may indicate a breakdown in waste collection operations."
        return "Sanitation complaints are climbing quickly and may indicate missed collection cycles or overloaded disposal points."

    if "electric" in title_lower or "power" in title_lower:
        if severity == "Severe":
            return "Power complaints have surged and may indicate widespread utility disruption or unstable restoration."
        return "Power complaints are increasing rapidly and may indicate utility instability in the affected zone."

    if severity == "Severe":
        return "Complaint volume has reached a severe level and may indicate a major civic service disruption requiring command-level attention."
    return "Complaint volume is rising fast enough to suggest an emerging civic disruption that should be monitored closely."


def detect_crisis(clusters: list[dict[str, Any]]) -> list[dict[str, str]]:
    alerts: list[dict[str, str]] = []

    for cluster in clusters:
        cluster_title = str(cluster.get("cluster_title", "General issue cluster")).strip() or "General issue cluster"
        location = str(cluster.get("location", "Unknown")).strip() or "Unknown"
        issue_count = _to_int(cluster.get("issue_count"))

        if issue_count > SEVERE_CRISIS_THRESHOLD:
            severity = "Severe"
        elif issue_count > POTENTIAL_CRISIS_THRESHOLD:
            severity = "High"
        else:
            continue

        alerts.append(
            {
                "cluster_title": cluster_title,
                "location": location,
                "severity": severity,
                "message": _message_for_cluster(cluster_title, severity),
                "reason": f"{issue_count} linked complaints crossed the configured alert threshold.",
            }
        )

    return alerts
