from __future__ import annotations

from backend.db.database import SessionLocal, VerificationRecord
from backend.services.issue_storage import mark_issue_resolved


def verify_work(issue_id: int, image_filename: str, location: str, action_taken: str | None = None) -> dict[str, object]:
    session = SessionLocal()
    try:
        record = VerificationRecord(
            issue_id=int(issue_id),
            image_path=str(image_filename),
            # Preserve the existing API's location field without changing the route contract.
            verified_by=str(location),
            action_taken=action_taken.strip() if action_taken else None,
        )
        session.add(record)
        session.commit()
        session.refresh(record)
        mark_issue_resolved(int(issue_id))
        return {
            "issue_id": record.issue_id,
            "image_filename": record.image_path,
            "location": record.verified_by,
            "action_taken": record.action_taken,
            "timestamp": record.timestamp.isoformat(),
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
