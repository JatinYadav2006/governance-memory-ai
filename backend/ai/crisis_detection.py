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
            return "Water supply complaints have surged and may indicate a major infrastructure failure."
        return "Water supply complaints have increased significantly and may indicate infrastructure failure."

    if "garbage" in title_lower or "waste" in title_lower or "trash" in title_lower:
        if severity == "Severe":
            return "Sanitation complaints are at severe levels and may indicate a breakdown in waste collection operations."
        return "Sanitation complaints have increased significantly and may indicate missed waste management cycles."

    if "electric" in title_lower or "power" in title_lower:
        if severity == "Severe":
            return "Power-related complaints have surged and may indicate widespread utility disruption."
        return "Power-related complaints have increased significantly and may indicate utility instability."

    if severity == "Severe":
        return "Complaint volume has reached a severe level and may indicate a major civic service disruption."
    return "Complaint volume has increased significantly and may indicate an emerging civic crisis."


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
            }
        )

    return alerts
