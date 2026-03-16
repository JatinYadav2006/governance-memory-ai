from __future__ import annotations

from typing import Any, Mapping


def generate_public_update(issue: Mapping[str, Any]) -> str:
    """
    Generate an official public-facing update message for a reported issue.

    This is a lightweight template-based generator for the MVP. It can later be
    upgraded to support multiple languages, tone control, and richer context
    (timestamps, department, ETA, verification status, and contact channels).
    """

    title = str(issue.get("title", "")).strip() or "a reported issue"
    location = str(issue.get("location", "")).strip() or "the affected area"
    urgency = str(issue.get("urgency", "")).strip().lower()
    description = str(issue.get("description", "")).strip().lower()

    if any(keyword in description for keyword in ["water", "pipeline", "supply", "drain"]):
        service_label = "water and drainage service issue"
    elif any(keyword in description for keyword in ["garbage", "trash", "waste", "overflow"]):
        service_label = "sanitation issue"
    elif any(keyword in description for keyword in ["road", "pothole", "traffic"]):
        service_label = "road safety issue"
    elif any(keyword in description for keyword in ["power", "electric", "outage"]):
        service_label = "power service issue"
    else:
        service_label = "civic service issue"

    lines: list[str] = [f"Municipal authorities are actively responding to the reported {service_label} in {location}."]

    if urgency == "high":
        lines.append("Field teams have been placed on priority response due to the urgency of the complaint.")
    else:
        lines.append("The responsible department has been assigned to inspect the situation and begin response steps.")

    lines.append(f"The current complaint cluster includes reports linked to {title.lower()}.")
    lines.append("A further public update will be shared once on-ground verification and response progress are confirmed.")

    return " ".join(lines)

