from __future__ import annotations

from typing import Any


def generate_policy_recommendation(cluster: dict[str, Any]) -> dict[str, object]:
    cluster_title = str(cluster.get("cluster_title", "General issue cluster")).strip() or "General issue cluster"
    location = str(cluster.get("location", "Unknown")).strip() or "Unknown"
    title_lower = cluster_title.lower()
    issue_count = int(cluster.get("issue_count", 0) or 0)
    confidence_score = float(cluster.get("confidence_score", 0.0) or 0.0)

    if "garbage" in title_lower or "waste" in title_lower or "trash" in title_lower:
        recommendations = [
            f"Increase garbage pickup frequency across {location}",
            "Deploy a sanitation inspection team to audit missed routes and overflow points",
            "Install temporary waste bins or overflow support units in the affected pocket",
        ]
    elif "water" in title_lower or "drain" in title_lower or "drainage" in title_lower:
        recommendations = [
            "Inspect water supply and drainage infrastructure for blockages, leaks, or pressure loss",
            "Dispatch a rapid-response maintenance team with a same-day inspection target",
            "Monitor the affected zone for repeat complaints after intervention",
        ]
    elif "road" in title_lower or "traffic" in title_lower:
        recommendations = [
            "Deploy the road maintenance team for an on-ground condition check",
            "Schedule a civil inspection to scope damage and traffic risk",
            "Prioritize the area in the next repair and resurfacing cycle",
        ]
    elif "electric" in title_lower or "power" in title_lower:
        recommendations = [
            "Conduct an electrical grid inspection on the affected service segment",
            "Coordinate with utility response teams for rapid fault isolation and repair",
            "Prepare a backup support response for impacted residents if restoration slips",
        ]
    else:
        recommendations = [
            "Assign the responsible department for immediate field inspection",
            "Review the complaint pattern for recurring service gaps in the locality",
            "Prepare a local action plan with a visible response timeline",
        ]

    if issue_count >= 12:
        recommendations.append("Escalate the cluster to zonal leadership for monitored execution until complaint volume stabilizes.")

    return {
        "cluster_title": cluster_title,
        "location": location,
        "recommendations": recommendations,
        "rationale": (
            f"Recommendations are based on the detected service category, {issue_count} linked complaints, "
            f"and a cluster confidence of {confidence_score:.2f}."
        ),
    }
