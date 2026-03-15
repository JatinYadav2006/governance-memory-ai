from __future__ import annotations

from typing import Any

from backend.db.database import IssueClusterRecord, IssueRecord, SessionLocal


def _to_issue_payload(record: IssueRecord, priority_score: float | None = None) -> dict[str, Any]:
    if priority_score is not None:
        resolved_priority = priority_score
    else:
        cluster_priority = record.cluster.priority_score if record.cluster is not None else 0.0
        resolved_priority = cluster_priority
    return {
        "id": record.id,
        "title": record.title,
        "description": record.description,
        "location": record.location,
        "urgency": record.urgency,
        "image_filename": record.image_filename,
        "status": record.status,
        "priority_score": float(resolved_priority),
    }


def _find_or_create_cluster(
    *,
    title: str,
    location: str,
    priority_score: float,
) -> IssueClusterRecord:
    session = SessionLocal()
    try:
        cluster = (
            session.query(IssueClusterRecord)
            .filter(IssueClusterRecord.cluster_title == title.strip())
            .filter(IssueClusterRecord.location == location.strip())
            .first()
        )
        if cluster is None:
            cluster = IssueClusterRecord(
                cluster_title=title.strip(),
                location=location.strip(),
                issue_count=1,
                priority_score=priority_score,
            )
            session.add(cluster)
            session.commit()
            session.refresh(cluster)
            session.expunge(cluster)
            return cluster

        cluster.issue_count += 1
        if priority_score > float(cluster.priority_score):
            cluster.priority_score = priority_score
        session.commit()
        session.refresh(cluster)
        session.expunge(cluster)
        return cluster
    finally:
        session.close()


def create_issue(payload: dict[str, Any], priority_score: float) -> dict[str, Any]:
    cluster = _find_or_create_cluster(
        title=str(payload.get("title", "")),
        location=str(payload.get("location", "")),
        priority_score=priority_score,
    )

    session = SessionLocal()
    try:
        issue = IssueRecord(
            title=str(payload.get("title", "")),
            description=str(payload.get("description", "")),
            location=str(payload.get("location", "")),
            urgency=str(payload.get("urgency", "")),
            image_filename=payload.get("image_filename"),
            status="Open",
            cluster_id=cluster.id,
            user_id=None,
        )
        session.add(issue)
        session.commit()
        session.refresh(issue)
        session.expunge(issue)
        return _to_issue_payload(issue, priority_score=priority_score)
    finally:
        session.close()


def list_issues(status: str | None = "Open") -> list[dict[str, Any]]:
    session = SessionLocal()
    try:
        query = (
            session.query(IssueRecord)
            .outerjoin(IssueClusterRecord, IssueRecord.cluster_id == IssueClusterRecord.id)
        )
        if status is not None:
            query = query.filter(IssueRecord.status == status)
        issues = query.order_by(IssueClusterRecord.priority_score.desc(), IssueRecord.created_at.desc()).all()
        for issue in issues:
            if issue.cluster is not None:
                _ = issue.cluster.priority_score
        return [_to_issue_payload(issue) for issue in issues]
    finally:
        session.close()


def mark_issue_resolved(issue_id: int) -> None:
    session = SessionLocal()
    try:
        issue = session.query(IssueRecord).filter(IssueRecord.id == int(issue_id)).first()
        if issue is None:
            return
        issue.status = "Resolved"
        session.commit()
    finally:
        session.close()
