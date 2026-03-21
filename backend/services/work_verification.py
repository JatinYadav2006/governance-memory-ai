from __future__ import annotations

from collections.abc import Iterable

from backend.db.database import SessionLocal, VerificationRecord
from backend.services.issue_storage import mark_issues_resolved


def verify_work(
    issue_ids: Iterable[int],
    image_filename: str,
    location: str,
    action_taken: str | None = None,
) -> dict[str, object]:
    resolved_issue_ids = [int(issue_id) for issue_id in issue_ids]
    if not resolved_issue_ids:
        raise ValueError("At least one issue id is required for verification.")

    session = SessionLocal()
    try:
        records: list[VerificationRecord] = []
        for issue_id in resolved_issue_ids:
            record = VerificationRecord(
                issue_id=issue_id,
                image_path=str(image_filename),
                # Preserve the existing API's location field without changing the route contract.
                verified_by=str(location),
                action_taken=action_taken.strip() if action_taken else None,
            )
            session.add(record)
            records.append(record)
        session.commit()
        for record in records:
            session.refresh(record)
        mark_issues_resolved(resolved_issue_ids)
        primary_record = records[0]
        return {
            "issue_ids": resolved_issue_ids,
            "issue_count": len(resolved_issue_ids),
            "image_filename": primary_record.image_path,
            "location": primary_record.verified_by,
            "action_taken": primary_record.action_taken,
            "timestamp": primary_record.timestamp.isoformat(),
        }
    finally:
        session.close()


def get_verifications() -> list[dict[str, object]]:
    session = SessionLocal()
    try:
        records = session.query(VerificationRecord).order_by(VerificationRecord.timestamp.desc()).all()
        return [
            {
                "issue_id": record.issue_id,
                "image_filename": record.image_path,
                "location": record.verified_by,
                "action_taken": record.action_taken,
                "timestamp": record.timestamp.isoformat(),
            }
            for record in records
        ]
    finally:
        session.close()
