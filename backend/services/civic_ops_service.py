from __future__ import annotations

from collections import Counter, defaultdict
from datetime import UTC, datetime
from typing import Any

from backend.ai.issue_clustering import cluster_issues
from backend.db.database import IssueRecord, SessionLocal, VerificationRecord
from backend.services.trust_engine import calculate_trust_score


MANUAL_REVIEW_MINUTES_PER_ISSUE = 6
CLUSTER_REVIEW_MINUTES = 12


DEPARTMENT_RULES = {
    "garbage": {
        "department": "Sanitation Department",
        "team": "Waste Response Unit",
        "officer": "Sanitation Operations Lead",
        "sla_hours": 18,
        "reason": "Waste overflow and sanitation complaints are handled by civic sanitation teams.",
    },
    "water": {
        "department": "Water Supply Department",
        "team": "Pipeline Response Cell",
        "officer": "Water Infrastructure Lead",
        "sla_hours": 12,
        "reason": "Water disruption and pipe-related complaints need infrastructure inspection and rapid supply restoration.",
    },
    "drain": {
        "department": "Drainage Department",
        "team": "Drain Clearance Unit",
        "officer": "Drainage Response Lead",
        "sla_hours": 10,
        "reason": "Drainage and waterlogging issues require drain cleaning and runoff restoration teams.",
    },
    "road": {
        "department": "Roads and Civil Works",
        "team": "Road Maintenance Crew",
        "officer": "Civil Maintenance Lead",
        "sla_hours": 36,
        "reason": "Road damage and pothole complaints are routed to civil maintenance and resurfacing teams.",
    },
    "power": {
        "department": "Electric Utility Coordination",
        "team": "Grid Stability Unit",
        "officer": "Utility Response Lead",
        "sla_hours": 8,
        "reason": "Power and electrical complaints require utility coordination and outage response.",
    },
}


def _now() -> datetime:
    return datetime.now(UTC)


def _normalize_timestamp(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def _hours_between(start: datetime | None, end: datetime | None) -> float:
    normalized_start = _normalize_timestamp(start)
    normalized_end = _normalize_timestamp(end)
    if normalized_start is None or normalized_end is None:
        return 0.0
    return round((normalized_end - normalized_start).total_seconds() / 3600, 1)


def _category_for_text(text: str) -> str:
    lowered = text.lower()
    if any(keyword in lowered for keyword in ["garbage", "waste", "trash", "sanitation", "overflow"]):
        return "garbage"
    if any(keyword in lowered for keyword in ["drainage", "drain", "waterlogged"]):
        return "drain"
    if any(keyword in lowered for keyword in ["water", "supply", "pipeline", "pipe", "leak"]):
        return "water"
    if any(keyword in lowered for keyword in ["road", "pothole", "traffic", "surface"]):
        return "road"
    if any(keyword in lowered for keyword in ["power", "electric", "outage", "grid"]):
        return "power"
    return "general"


def _assignment_profile(text: str, urgency: str, location: str) -> dict[str, Any]:
    category = _category_for_text(text)
    rule = DEPARTMENT_RULES.get(
        category,
        {
            "department": "City Operations Desk",
            "team": "General Civic Response Unit",
            "officer": "Ward Coordination Lead",
            "sla_hours": 24,
            "reason": "General civic complaints are routed through the city operations desk for local assignment.",
        },
    )

    sla_hours = int(rule["sla_hours"])
    urgency_lower = urgency.lower()
    if urgency_lower == "high":
        sla_hours = max(6, int(sla_hours * 0.65))
    elif urgency_lower == "medium":
        sla_hours = sla_hours
    else:
        sla_hours = int(sla_hours * 1.25)

    return {
        "category": category.title(),
        "department": rule["department"],
        "team": rule["team"],
        "officer": f"{location} {rule['officer']}",
        "sla_hours": sla_hours,
        "reason": rule["reason"],
    }


def _stage_for_issue(status: str, age_hours: float, sla_hours: int) -> str:
    status_lower = status.lower()
    if status_lower == "resolved":
        return "Resolved"
    if age_hours >= sla_hours:
        return "Escalation Needed"
    if age_hours >= max(2.0, sla_hours * 0.5):
        return "Field Response In Progress"
    return "Intake and Triage"


def _load_issue_context() -> tuple[list[IssueRecord], dict[int, VerificationRecord]]:
    session = SessionLocal()
    try:
        issues = session.query(IssueRecord).order_by(IssueRecord.created_at.desc()).all()
        verifications = (
            session.query(VerificationRecord)
            .order_by(VerificationRecord.timestamp.desc())
            .all()
        )
        latest_by_issue: dict[int, VerificationRecord] = {}
        for record in verifications:
            latest_by_issue.setdefault(record.issue_id, record)
        return issues, latest_by_issue
    finally:
        session.close()


def _serialize_issue(issue: IssueRecord, verification: VerificationRecord | None) -> dict[str, Any]:
    assignment = _assignment_profile(
        f"{issue.title} {issue.description}",
        issue.urgency,
        issue.location,
    )
    age_hours = _hours_between(issue.created_at, _now())
    resolution_hours = _hours_between(issue.created_at, verification.timestamp if verification else None)
    stage = _stage_for_issue(issue.status, age_hours, int(assignment["sla_hours"]))

    return {
        "id": issue.id,
        "title": issue.title,
        "description": issue.description,
        "location": issue.location,
        "urgency": issue.urgency,
        "status": issue.status,
        "created_at": _normalize_timestamp(issue.created_at).isoformat() if issue.created_at else None,
        "age_hours": age_hours,
        "department": assignment["department"],
        "team": assignment["team"],
        "officer": assignment["officer"],
        "category": assignment["category"],
        "sla_hours": int(assignment["sla_hours"]),
        "overdue": issue.status != "Resolved" and age_hours > float(assignment["sla_hours"]),
        "stage": stage,
        "assignment_reason": assignment["reason"],
        "verification": (
            {
                "verified_by": verification.verified_by,
                "action_taken": verification.action_taken,
                "timestamp": _normalize_timestamp(verification.timestamp).isoformat() if verification.timestamp else None,
                "image_path": verification.image_path,
            }
            if verification
            else None
        ),
        "resolution_hours": resolution_hours if verification else None,
    }


def load_issue_records() -> list[dict[str, Any]]:
    issues, latest_by_issue = _load_issue_context()
    return [_serialize_issue(issue, latest_by_issue.get(issue.id)) for issue in issues]


def _active_cluster_input(active_issues: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "id": issue["id"],
            "title": issue["title"],
            "description": issue["description"],
            "location": issue["location"],
        }
        for issue in active_issues
    ]


def _build_department_assignments_from_records(
    issue_records: list[dict[str, Any]],
    active_clusters: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    active_issues = [issue for issue in issue_records if issue["status"] != "Resolved"]
    cluster_input = [
        item for item in _active_cluster_input(active_issues)
    ]
    clusters = active_clusters if active_clusters is not None else cluster_issues(cluster_input)
    issues_by_id = {int(issue["id"]): issue for issue in active_issues}
    assignments: list[dict[str, Any]] = []

    for cluster in clusters:
        issue_ids = [int(issue_id) for issue_id in cluster.get("issue_ids", [])]
        related_issues = [issues_by_id[issue_id] for issue_id in issue_ids if issue_id in issues_by_id]
        dominant_issue = related_issues[0] if related_issues else {
            "title": str(cluster.get("cluster_title", "")),
            "description": str(cluster.get("cluster_title", "")),
            "urgency": "Medium",
            "location": str(cluster.get("location", "Unknown")),
        }
        assignment = _assignment_profile(
            f"{dominant_issue.get('title', '')} {dominant_issue.get('description', '')}",
            str(dominant_issue.get("urgency", "Medium")),
            str(cluster.get("location", "Unknown")),
        )
        assignments.append(
            {
                "cluster_id": cluster.get("cluster_id"),
                "cluster_title": cluster.get("cluster_title"),
                "location": cluster.get("location"),
                "issue_count": cluster.get("issue_count"),
                "department": assignment["department"],
                "team": assignment["team"],
                "officer": assignment["officer"],
                "sla_hours": assignment["sla_hours"],
                "assignment_reason": assignment["reason"],
                "confidence_score": cluster.get("confidence_score", 0.0),
            }
        )

    return assignments


def build_department_assignments() -> list[dict[str, Any]]:
    issue_records = load_issue_records()
    return _build_department_assignments_from_records(issue_records)


def _build_sla_overview_from_records(issue_records: list[dict[str, Any]]) -> dict[str, Any]:
    active_issues = [issue for issue in issue_records if issue["status"] != "Resolved"]
    overdue = [issue for issue in active_issues if issue["overdue"]]
    on_track = [issue for issue in active_issues if not issue["overdue"]]
    avg_age = round(
        sum(float(issue["age_hours"]) for issue in active_issues) / len(active_issues),
        1,
    ) if active_issues else 0.0

    return {
        "summary": {
            "active_issues": len(active_issues),
            "overdue_issues": len(overdue),
            "on_track_issues": len(on_track),
            "average_open_age_hours": avg_age,
        },
        "issues": active_issues,
    }


def build_sla_overview() -> dict[str, Any]:
    issue_records = load_issue_records()
    return _build_sla_overview_from_records(issue_records)


def _build_zone_performance_from_records(issue_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_location: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for issue in issue_records:
        by_location[str(issue["location"])].append(issue)

    performance: list[dict[str, Any]] = []
    for location, issues in by_location.items():
        active = [issue for issue in issues if issue["status"] != "Resolved"]
        resolved = [issue for issue in issues if issue["status"] == "Resolved"]
        avg_resolution_hours = round(
            sum(float(issue["resolution_hours"] or 0.0) for issue in resolved) / len(resolved),
            1,
        ) if resolved else None
        trust_score = calculate_trust_score(active) if active else 100
        performance.append(
            {
                "location": location,
                "total_issues": len(issues),
                "active_issues": len(active),
                "resolved_issues": len(resolved),
                "resolution_rate": round((len(resolved) / len(issues)) * 100, 1) if issues else 0.0,
                "avg_resolution_hours": avg_resolution_hours,
                "trust_score": trust_score,
                "high_urgency_issues": sum(1 for issue in active if str(issue["urgency"]).lower() == "high"),
            }
        )

    performance.sort(key=lambda item: (-int(item["active_issues"]), item["location"]))
    return performance


def build_zone_performance() -> list[dict[str, Any]]:
    issue_records = load_issue_records()
    return _build_zone_performance_from_records(issue_records)


def _build_impact_metrics_from_records(
    issue_records: list[dict[str, Any]],
    active_clusters: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    total_issues = len(issue_records)
    active = [issue for issue in issue_records if issue["status"] != "Resolved"]
    resolved = [issue for issue in issue_records if issue["status"] == "Resolved"]

    avg_resolution_hours = round(
        sum(float(issue["resolution_hours"] or 0.0) for issue in resolved) / len(resolved),
        1,
    ) if resolved else 0.0
    resolution_rate = round((len(resolved) / total_issues) * 100, 1) if total_issues else 0.0
    recovered_trust_points = min(
        30,
        sum(5 if str(issue["urgency"]).lower() == "high" else 3 for issue in resolved),
    )

    repeat_counter: Counter[tuple[str, str]] = Counter(
        (
            str(issue["location"]).lower(),
            str(issue["category"]).lower(),
        )
        for issue in issue_records
    )
    repeat_complaint_pressure = round(
        (sum(count for count in repeat_counter.values() if count > 1) / total_issues) * 100,
        1,
    ) if total_issues else 0.0

    active_clusters = active_clusters if active_clusters is not None else cluster_issues(_active_cluster_input(active))
    manual_review_hours_saved = round(
        max(
            0,
            ((len(active) * MANUAL_REVIEW_MINUTES_PER_ISSUE) - (len(active_clusters) * CLUSTER_REVIEW_MINUTES)) / 60,
        ),
        1,
    )

    return {
        "total_issues": total_issues,
        "active_issues": len(active),
        "resolved_issues": len(resolved),
        "resolution_rate": resolution_rate,
        "average_resolution_hours": avg_resolution_hours,
        "repeat_complaint_pressure": repeat_complaint_pressure,
        "trust_recovery_points": recovered_trust_points,
        "estimated_manual_review_hours_saved": manual_review_hours_saved,
    }


def build_impact_metrics() -> dict[str, Any]:
    issue_records = load_issue_records()
    return _build_impact_metrics_from_records(issue_records)


def _build_executive_summary_from_parts(
    impact: dict[str, Any],
    assignments: list[dict[str, Any]],
    zones: list[dict[str, Any]],
    sla_summary: dict[str, Any],
) -> dict[str, Any]:
    sla = sla_summary

    critical_assignments = [
        item for item in assignments if int(item.get("issue_count", 0)) >= 10
    ]
    if critical_assignments:
        city_risk = "High"
    elif sla["overdue_issues"] > 0:
        city_risk = "Elevated"
    else:
        city_risk = "Stable"

    return {
        "city_risk_level": city_risk,
        "active_issues": impact["active_issues"],
        "resolution_rate": impact["resolution_rate"],
        "estimated_manual_review_hours_saved": impact["estimated_manual_review_hours_saved"],
        "departments_engaged": len({item["department"] for item in assignments}),
        "zones_covered": len(zones),
        "overdue_issues": sla["overdue_issues"],
        "top_operational_message": (
            "AI clustering is reducing manual review overhead while highlighting the highest-risk service clusters."
        ),
    }


def build_executive_summary() -> dict[str, Any]:
    bundle = build_civic_ops_bundle()
    return dict(bundle["executive_summary"])


def build_civic_ops_bundle() -> dict[str, Any]:
    issue_records = load_issue_records()
    active_issues = [issue for issue in issue_records if issue["status"] != "Resolved"]
    active_clusters = cluster_issues(_active_cluster_input(active_issues))
    impact = _build_impact_metrics_from_records(issue_records, active_clusters)
    assignments = _build_department_assignments_from_records(issue_records, active_clusters)
    sla = _build_sla_overview_from_records(issue_records)
    zones = _build_zone_performance_from_records(issue_records)
    executive = _build_executive_summary_from_parts(impact, assignments, zones, sla["summary"])

    return {
        "impact_metrics": impact,
        "department_assignments": assignments,
        "sla_overview": sla,
        "zone_performance": zones,
        "executive_summary": executive,
    }


def build_citizen_transparency(location: str) -> dict[str, Any]:
    issue_records = load_issue_records()
    normalized_location = location.strip().lower()
    nearby = [
        issue for issue in issue_records
        if normalized_location in str(issue["location"]).lower()
    ] if normalized_location else issue_records

    active = [issue for issue in nearby if issue["status"] != "Resolved"]
    resolved = [issue for issue in nearby if issue["status"] == "Resolved"]
    trust_score = calculate_trust_score(active) if active else 100
    recent_proofs = [
        {
            "issue_id": issue["id"],
            "title": issue["title"],
            "action_taken": issue["verification"]["action_taken"],
            "verified_by": issue["verification"]["verified_by"],
            "verified_at": issue["verification"]["timestamp"],
            "proof_available": bool(issue["verification"]["image_path"]),
        }
        for issue in resolved
        if issue.get("verification")
    ][:5]

    return {
        "location": location,
        "stats": {
            "nearby_active": len(active),
            "nearby_resolved": len(resolved),
            "verification_proofs": len(recent_proofs),
            "local_trust_score": trust_score,
        },
        "active_reports": active[:10],
        "resolved_reports": resolved[:10],
        "recent_proofs": recent_proofs,
    }
