from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List


# Prototype, in-memory storage for work verification records.
# This will later be replaced by a database + object storage for images.
verification_records: List[Dict[str, Any]] = []


def verify_work(issue_id: int, image_filename: str, location: str) -> Dict[str, Any]:
    """
    Create and store a work verification record.

    Steps:
    - generate a timestamp
    - store the record in memory
    - return the stored record
    """

    record: Dict[str, Any] = {
        "issue_id": int(issue_id),
        "image_filename": str(image_filename),
        "location": str(location),
        # ISO 8601 timestamp in UTC for consistency across systems.
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    verification_records.append(record)
    return record


def get_verifications() -> List[Dict[str, Any]]:
    """
    Return all stored verification records (in-memory).
    """

    return verification_records

