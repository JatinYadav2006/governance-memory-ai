from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from backend.db.database import DispatchAssignmentRecord, SessionLocal


def build_cluster_key(cluster_title: str, location: str) -> str:
    return f"{str(cluster_title).strip().lower()}::{str(location).strip().lower()}"


def save_dispatch_assignment(
    *,
    cluster_id: int | None = None,
    cluster_title: str,
    location: str,
    department: str,
    team: str,
    officer: str,
    status: str,
    notes: str | None,
    assigned_by: str | None,
) -> dict[str, Any]:
    session = SessionLocal()
    try:
        cluster_key = build_cluster_key(cluster_title, location)
        record = (
            session.query(DispatchAssignmentRecord)
            .filter(DispatchAssignmentRecord.cluster_key == cluster_key)
            .first()
        )
        now = datetime.now(UTC)

        if record is None:
            record = DispatchAssignmentRecord(
                cluster_key=cluster_key,
                cluster_id=cluster_id,
                cluster_title=cluster_title,
                location=location,
                department=department,
                team=team,
                officer=officer,
                status=status,
                notes=notes,
                assigned_by=assigned_by,
                created_at=now,
                updated_at=now,
            )
            session.add(record)
        else:
            record.cluster_id = cluster_id
            record.cluster_title = cluster_title
            record.location = location
            record.department = department
            record.team = team
            record.officer = officer
            record.status = status
            record.notes = notes
            record.assigned_by = assigned_by
            record.updated_at = now
            session.add(record)

        session.commit()
        session.refresh(record)
        return serialize_dispatch_assignment(record)
    finally:
        session.close()


def list_dispatch_assignments() -> list[dict[str, Any]]:
    session = SessionLocal()
    try:
        records = (
            session.query(DispatchAssignmentRecord)
            .order_by(DispatchAssignmentRecord.updated_at.desc())
            .all()
        )
        return [serialize_dispatch_assignment(record) for record in records]
    finally:
        session.close()


def serialize_dispatch_assignment(record: DispatchAssignmentRecord) -> dict[str, Any]:
    return {
        "id": record.id,
        "cluster_key": record.cluster_key,
        "cluster_id": record.cluster_id,
        "cluster_title": record.cluster_title,
        "location": record.location,
        "department": record.department,
        "team": record.team,
        "officer": record.officer,
        "status": record.status,
        "notes": record.notes,
        "assigned_by": record.assigned_by,
        "created_at": record.created_at.isoformat() if record.created_at else None,
        "updated_at": record.updated_at.isoformat() if record.updated_at else None,
    }
