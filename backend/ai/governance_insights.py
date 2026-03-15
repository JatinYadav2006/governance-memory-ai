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
        return "This may indicate missed waste pickup cycles."
    if "water" in title_lower or "drain" in title_lower or "drainage" in title_lower:
        return "This may indicate drainage blockage or uneven water supply management."
    if "road" in title_lower or "traffic" in title_lower:
        return "This may indicate delayed road maintenance or traffic control gaps."
    if "electric" in title_lower or "power" in title_lower:
        return "This may indicate unstable utility service or delayed repair response."
    return "This may indicate a recurring service delivery gap in the area."


def _recommendation(cluster_title: str) -> str:
    title_lower = cluster_title.lower()
    if "garbage" in title_lower or "waste" in title_lower or "trash" in title_lower:
        return "Inspect sanitation schedule and deploy additional collection units."
    if "water" in title_lower or "drain" in title_lower or "drainage" in title_lower:
        return "Inspect pipelines and drainage routes, then assign a rapid-response field team."
    if "road" in title_lower or "traffic" in title_lower:
        return "Schedule a site inspection and prioritize the location for civil maintenance."
    if "electric" in title_lower or "power" in title_lower:
        return "Coordinate with utility teams to inspect infrastructure and restore service reliability."
    return "Assign the issue to the responsible department for immediate field verification and follow-up."


def generate_cluster_insight(cluster: dict[str, Any]) -> dict[str, str]:
    cluster_title = str(cluster.get("cluster_title", "General issue cluster")).strip() or "General issue cluster"
    location = str(cluster.get("location", "Unknown area")).strip() or "Unknown area"
    issue_count = _to_int(cluster.get("issue_count"))
    previous_issue_count = _to_int(cluster.get("previous_issue_count"))

    widespread = issue_count >= HIGH_VOLUME_THRESHOLD
    rising_trend = previous_issue_count > 0 and issue_count > previous_issue_count

    opening = f"Complaints about {cluster_title.lower()} are being reported in {location}."
    if widespread and rising_trend:
        opening = f"Complaints about {cluster_title.lower()} are increasing in {location} and appear to be widespread."
    elif widespread:
        opening = f"Complaints about {cluster_title.lower()} appear to be widespread in {location}."
    elif rising_trend:
        opening = f"Complaints about {cluster_title.lower()} are increasing in {location}."

    insight = f"{opening} {_problem_summary(cluster_title)}"

    return {
        "cluster_title": cluster_title,
        "location": location,
        "insight": insight,
        "recommendation": _recommendation(cluster_title),
    }
