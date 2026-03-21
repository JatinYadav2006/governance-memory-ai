from __future__ import annotations

from typing import Any


HIGH_VOLUME_THRESHOLD = 5


def _to_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _problem_summary(cluster_title: str) -> str:
    title_lower = cluster_title.lower()
    if "garbage" in title_lower or "waste" in title_lower or "trash" in title_lower:
        return "The pattern suggests missed pickup cycles, overloaded collection points, or weak sanitation coverage."
    if "water" in title_lower or "drain" in title_lower or "drainage" in title_lower:
        return "The signal points to blocked drainage, inconsistent water delivery, or infrastructure stress in the service network."
    if "road" in title_lower or "traffic" in title_lower:
        return "The signal points to delayed maintenance, deteriorating surface conditions, or weak traffic management at the site."
    if "electric" in title_lower or "power" in title_lower:
        return "The complaint pattern suggests unstable utility service, localized outages, or slow fault response."
    return "The complaint pattern suggests a recurring service delivery gap that now needs coordinated field attention."


def _recommendation(cluster_title: str) -> str:
    title_lower = cluster_title.lower()
    if "garbage" in title_lower or "waste" in title_lower or "trash" in title_lower:
        return "Audit the sanitation route, clear overflow points, and place additional collection support in the affected pocket."
    if "water" in title_lower or "drain" in title_lower or "drainage" in title_lower:
        return "Inspect pipelines and drainage corridors, then dispatch a rapid-response field crew to the affected zone."
    if "road" in title_lower or "traffic" in title_lower:
        return "Run a field inspection quickly and move the location into the next high-priority civil maintenance cycle."
    if "electric" in title_lower or "power" in title_lower:
        return "Coordinate with utility teams to inspect the grid segment and restore service reliability with a visible response window."
    return "Assign the cluster to the responsible department for rapid field verification, containment, and a public-facing response plan."


def generate_cluster_insight(cluster: dict[str, Any]) -> dict[str, str]:
    cluster_title = str(cluster.get("cluster_title", "General issue cluster")).strip() or "General issue cluster"
    location = str(cluster.get("location", "Unknown area")).strip() or "Unknown area"
    issue_count = _to_int(cluster.get("issue_count"))
    previous_issue_count = _to_int(cluster.get("previous_issue_count"))
    evidence_terms = [str(term) for term in cluster.get("evidence_terms", []) if str(term).strip()]

    widespread = issue_count >= HIGH_VOLUME_THRESHOLD
    rising_trend = previous_issue_count > 0 and issue_count > previous_issue_count

    opening = f"{cluster_title} complaints are being reported across {location}."
    if widespread and rising_trend:
        opening = f"{cluster_title} complaints are accelerating in {location} and already show signs of wider civic pressure."
    elif widespread:
        opening = f"{cluster_title} complaints appear widespread across {location}."
    elif rising_trend:
        opening = f"{cluster_title} complaints are increasing in {location}."

    evidence_line = (
        f" The cluster is being grouped around terms like {', '.join(evidence_terms[:3])}."
        if evidence_terms
        else ""
    )
    operating_note = (
        " This is a local decision-support inference based on complaint concentration and complaint language."
    )
    insight = f"{opening} {_problem_summary(cluster_title)}{evidence_line}{operating_note}"

    return {
        "cluster_title": cluster_title,
        "location": location,
        "insight": insight,
        "recommendation": _recommendation(cluster_title),
        "evidence_note": evidence_line.strip() if evidence_line else "Grouped from repeated complaint language and location overlap.",
    }
