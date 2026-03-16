from __future__ import annotations

from typing import Any

from backend.ai.crisis_detection import detect_crisis
from backend.ai.governance_insights import generate_cluster_insight
from backend.ai.governance_memory import find_similar_case
from backend.ai.policy_recommendation import generate_policy_recommendation
from backend.services.communication_generator import generate_public_update


def _cluster_description(cluster: dict[str, Any], issue_details: list[dict[str, Any]]) -> str:
    descriptions: list[str] = []
    for issue in issue_details:
        title = str(issue.get("title", "")).strip()
        description = str(issue.get("description", "")).strip()
        combined = f"{title} {description}".strip()
        if combined:
            descriptions.append(combined)
    return " ".join(descriptions)


def _operations_actions(recommendations: list[str], issue_count: int) -> list[str]:
    actions = recommendations[:2]
    if issue_count >= 10:
        actions.append("Open a rapid-response command ticket, assign field leads, and set a same-day review checkpoint.")
    else:
        actions.append("Schedule a site inspection in the next operational window and confirm ownership before close of shift.")
    return actions


def _trust_projection(issue_count: int) -> str:
    if issue_count >= 15:
        return "Public trust is at real risk of visible decline if this cluster remains unresolved beyond the next 24 hours."
    if issue_count >= 8:
        return "Public trust will likely soften if residents do not see a visible response and communication update soon."
    return "A prompt, visible response should help stabilize trust in the affected locality."


def _situation_status(issue_count: int, crisis_alert: dict[str, Any] | None) -> str:
    if crisis_alert is not None:
        return str(crisis_alert.get("severity", "High"))
    if issue_count >= 8:
        return "Elevated Watch"
    return "Active Monitoring"


def _final_recommendation(cluster_title: str, location: str, action_plan: list[str], status: str) -> str:
    if action_plan:
        primary_action = action_plan[0].rstrip(".")
        return (
            f"{status} response recommended for {cluster_title} in {location}. "
            f"Immediate focus: {primary_action.lower()}."
        )
    return f"{status} response recommended for {cluster_title} in {location}."


def build_war_room(
    cluster: dict[str, Any],
    issue_details: list[dict[str, Any]],
    resolved_issues: list[dict[str, Any]],
) -> dict[str, Any]:
    cluster_title = str(cluster.get("cluster_title", "Recurring Civic Issue")).strip() or "Recurring Civic Issue"
    location = str(cluster.get("location", "Unknown")).strip() or "Unknown"
    issue_count = int(cluster.get("issue_count", 0))
    cluster_description = _cluster_description(cluster, issue_details)

    insight = generate_cluster_insight(cluster)
    policy = generate_policy_recommendation(cluster)
    crisis = detect_crisis([cluster])
    crisis_alert = crisis[0] if crisis else None
    memory_match = find_similar_case(cluster_title, cluster_description, resolved_issues)

    communication_prompt = {
        "title": cluster_title,
        "description": cluster_description or cluster_title,
        "location": location,
        "urgency": "High" if issue_count >= 10 else "Medium",
        "image_filename": None,
    }

    agents = [
        {
            "agent": "Crisis Analyst",
            "headline": crisis_alert["severity"] if crisis_alert else "Monitor",
            "assessment": (
                f"{crisis_alert['message']} Current cluster load stands at {issue_count} linked complaints."
                if crisis_alert
                else f"{insight['insight']} Current cluster load stands at {issue_count} linked complaints."
            ),
        },
        {
            "agent": "Operations Planner",
            "headline": "Field Response",
            "assessment": (
                "Operational sequence: " + " ".join(_operations_actions(policy["recommendations"], issue_count))
            ),
        },
        {
            "agent": "Policy Advisor",
            "headline": "Recommended Measures",
            "assessment": (
                "Priority interventions: " + " ".join(policy["recommendations"][:3])
            ),
        },
        {
            "agent": "Trust Impact Analyst",
            "headline": "Public Confidence",
            "assessment": _trust_projection(issue_count),
        },
        {
            "agent": "Public Communication Officer",
            "headline": "Citizen Update",
            "assessment": (
                "Recommended public line: " + generate_public_update(communication_prompt)
            ),
        },
    ]

    if memory_match is not None:
        agents.append(
            {
                "agent": "Governance Memory Officer",
                "headline": "Similar Resolved Case",
                "assessment": (
                    f"Closest historical match: {memory_match['similar_case_title']} in "
                    f"{memory_match['location']}. Recorded action: {memory_match['action_taken']}. "
                    f"Similarity score: {memory_match['similarity_score']}."
                ),
            }
        )

    action_plan = policy["recommendations"][:]
    if crisis_alert is not None:
        action_plan.insert(0, "Escalate the cluster to the city response cell for priority monitoring and leadership visibility.")
    if memory_match is not None:
        action_plan.append(f"Reuse the response playbook from {memory_match['similar_case_title']} where appropriate.")

    status = _situation_status(issue_count, crisis_alert)
    final_recommendation = _final_recommendation(cluster_title, location, action_plan, status)

    return {
        "cluster_title": cluster_title,
        "location": location,
        "issue_count": issue_count,
        "status": status,
        "insight": insight["insight"],
        "confidence_score": float(cluster.get("confidence_score", 0.0) or 0.0),
        "evidence_terms": list(cluster.get("evidence_terms", [])),
        "agents": agents,
        "final_recommendation": final_recommendation,
        "action_plan": action_plan,
        "memory_match": memory_match,
    }
