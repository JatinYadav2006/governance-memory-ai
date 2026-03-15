from __future__ import annotations

from typing import Any


def generate_policy_recommendation(cluster: dict[str, Any]) -> dict[str, object]:
    cluster_title = str(cluster.get("cluster_title", "General issue cluster")).strip() or "General issue cluster"
    location = str(cluster.get("location", "Unknown")).strip() or "Unknown"
    title_lower = cluster_title.lower()

    if "garbage" in title_lower or "waste" in title_lower or "trash" in title_lower:
        recommendations = [
            "Increase garbage pickup frequency",
            "Deploy sanitation inspection team",
            "Install temporary waste bins",
        ]
    elif "water" in title_lower or "drain" in title_lower or "drainage" in title_lower:
        recommendations = [
            "Inspect water supply and drainage infrastructure",
            "Dispatch rapid-response maintenance team",
            "Monitor affected zone for repeat complaints",
        ]
    elif "road" in title_lower or "traffic" in title_lower:
        recommendations = [
            "Deploy road maintenance team",
            "Schedule site inspection for civil damage",
            "Prioritize the area in the next repair cycle",
        ]
    elif "electric" in title_lower or "power" in title_lower:
        recommendations = [
            "Conduct electrical grid inspection",
            "Coordinate with utility response teams",
            "Prepare backup response for affected residents",
        ]
    else:
        recommendations = [
            "Assign responsible department for field inspection",
            "Review complaint pattern for recurring service gaps",
            "Prepare a local action plan with response timeline",
        ]

    return {
        "cluster_title": cluster_title,
        "location": location,
        "recommendations": recommendations,
    }
