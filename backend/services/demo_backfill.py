from __future__ import annotations

from collections.abc import Iterable

from backend.db.database import IssueRecord, SessionLocal
from backend.services.dispatch_service import save_dispatch_assignment
from backend.services.issue_storage import create_issue
from backend.services.prioritization import calculate_priority
from backend.services.work_verification import verify_work


ACTIVE_BACKFILL_ISSUES = [
    {
        "title": "Water tanker demand rising in Ward 9",
        "description": "Families in Ward 9 say low supply has continued for two days and tanker support is now urgently needed.",
        "location": "Prayagraj",
        "urgency": "High",
    },
    {
        "title": "Uneven water pressure near station colony",
        "description": "Station colony residents report weak water flow in the morning and no stable supply by evening.",
        "location": "Prayagraj",
        "urgency": "High",
    },
    {
        "title": "No municipal water on doctors lane",
        "description": "Doctors lane residents say the municipal water line has been dry since the previous evening and pressure has not returned.",
        "location": "Prayagraj",
        "urgency": "High",
    },
    {
        "title": "Water shortage near court campus",
        "description": "Homes near the court campus are facing a prolonged water shortage and residents now depend on private supply.",
        "location": "Prayagraj",
        "urgency": "High",
    },
    {
        "title": "Dry taps reported in police colony",
        "description": "Police colony households report dry taps through the morning cycle and suspect a distribution failure in the local network.",
        "location": "Prayagraj",
        "urgency": "High",
    },
    {
        "title": "Water flow stopped near district hospital road",
        "description": "Supply on district hospital road has become unreliable and several homes report no usable water for hours.",
        "location": "Prayagraj",
        "urgency": "High",
    },
    {
        "title": "Garbage pickup missed near medical crossing",
        "description": "Bins near the medical crossing have not been cleared and trash is spilling onto the footpath.",
        "location": "Lucknow",
        "urgency": "Medium",
    },
    {
        "title": "Overflowing waste bins near hostel block",
        "description": "Students report foul smell and overflowing garbage bins near the hostel block entrance.",
        "location": "Lucknow",
        "urgency": "Medium",
    },
    {
        "title": "Streetlights not working on service road",
        "description": "Several streetlights on the service road are out, creating unsafe conditions for commuters after dark.",
        "location": "Kanpur",
        "urgency": "Medium",
    },
    {
        "title": "Electricity fluctuation in residential pocket",
        "description": "Frequent power fluctuation in the residential pocket is damaging appliances and disrupting evening routines.",
        "location": "Kanpur",
        "urgency": "High",
    },
    {
        "title": "Broken road shoulder near flyover turn",
        "description": "The road shoulder has broken near the flyover turn, increasing accident risk for two-wheelers.",
        "location": "Kanpur",
        "urgency": "Medium",
    },
    {
        "title": "Sewage overflow in lane behind temple road",
        "description": "Dirty water is backing up from the drain behind temple road and creating hygiene concerns for nearby homes.",
        "location": "Varanasi",
        "urgency": "High",
    },
]


RESOLVED_BACKFILL_ISSUES = [
    {
        "issue": {
            "title": "Emergency tanker deployment in Ward 11",
            "description": "A short-term supply collapse in Ward 11 led to complaints and demand for tanker support.",
            "location": "Prayagraj",
            "urgency": "High",
        },
        "verification": {
            "location": "Water Response Team Alpha",
            "action_taken": "Emergency tanker deployment completed and supply normalized",
        },
    },
    {
        "issue": {
            "title": "Night sanitation clearance near metro market",
            "description": "Missed waste collection caused garbage overflow and odor around the metro market zone.",
            "location": "Lucknow",
            "urgency": "Medium",
        },
        "verification": {
            "location": "Sanitation Zone C",
            "action_taken": "Night sanitation clearance completed and waste pickup frequency increased",
        },
    },
    {
        "issue": {
            "title": "Streetlight repair on school corridor",
            "description": "Dark stretches on the school corridor triggered repeated safety complaints from residents.",
            "location": "Kanpur",
            "urgency": "Medium",
        },
        "verification": {
            "location": "Electrical Maintenance Crew 2",
            "action_taken": "Streetlight repair completed and corridor lighting restored",
        },
    },
    {
        "issue": {
            "title": "Drain desilting near river lane",
            "description": "Waterlogging and slow runoff near river lane pointed to blocked drainage and silt buildup.",
            "location": "Varanasi",
            "urgency": "High",
        },
        "verification": {
            "location": "Drainage Rapid Unit",
            "action_taken": "Drain desilting completed and runoff cleared",
        },
    },
    {
        "issue": {
            "title": "Pressure restoration near station road",
            "description": "Low water pressure around station road triggered multiple complaints over two supply cycles.",
            "location": "Prayagraj",
            "urgency": "High",
        },
        "verification": {
            "location": "Water Maintenance South",
            "action_taken": "Valve calibration completed and water pressure restored",
        },
    },
    {
        "issue": {
            "title": "Leak isolation beside college gate",
            "description": "A pipeline leak beside the college gate caused repeated supply loss in nearby homes.",
            "location": "Prayagraj",
            "urgency": "High",
        },
        "verification": {
            "location": "Pipeline Repair Crew 4",
            "action_taken": "Pipeline leak isolated and section repair completed",
        },
    },
    {
        "issue": {
            "title": "Cluster cleanup near transport nagar",
            "description": "Uncollected garbage near transport nagar built up across two pickup cycles and caused odor complaints.",
            "location": "Lucknow",
            "urgency": "Medium",
        },
        "verification": {
            "location": "Sanitation Response Team East",
            "action_taken": "Cluster cleanup completed and overflow waste cleared",
        },
    },
    {
        "issue": {
            "title": "Road patch repair near depot turn",
            "description": "Damaged surface near depot turn created repeat pothole complaints and traffic slowdown.",
            "location": "Kanpur",
            "urgency": "Medium",
        },
        "verification": {
            "location": "Road Works Unit B",
            "action_taken": "Road patch repair completed and traffic movement stabilized",
        },
    },
    {
        "issue": {
            "title": "Power restoration in market extension",
            "description": "Market extension residents reported repeated outage and unstable evening supply.",
            "location": "Kanpur",
            "urgency": "High",
        },
        "verification": {
            "location": "Grid Stabilization Cell",
            "action_taken": "Power restoration completed and feeder stability improved",
        },
    },
    {
        "issue": {
            "title": "Drain flushing in riverside ward",
            "description": "Drain blockage in the riverside ward caused repeated waterlogging after moderate rainfall.",
            "location": "Varanasi",
            "urgency": "High",
        },
        "verification": {
            "location": "Drainage Maintenance Team 1",
            "action_taken": "Drain flushing completed and waterlogging risk reduced",
        },
    },
]


DISPATCH_BACKFILL_ASSIGNMENTS = [
    {
        "cluster_title": "Water Supply Issue",
        "location": "Prayagraj",
        "department": "Water Department",
        "team": "Hydraulic Response Cell",
        "officer": "A. Sharma",
        "status": "In Progress",
        "notes": "Field inspection and pressure-line diagnosis scheduled for the morning cycle.",
        "assigned_by": "Demo Admin",
    },
    {
        "cluster_title": "Garbage Overflow",
        "location": "Lucknow",
        "department": "Sanitation Department",
        "team": "Urban Cleanliness Unit",
        "officer": "N. Khan",
        "status": "Assigned",
        "notes": "Additional pickup round requested for hotspot bins and market lanes.",
        "assigned_by": "Demo Admin",
    },
]


def _existing_titles() -> set[str]:
    session = SessionLocal()
    try:
        titles = session.query(IssueRecord.title).all()
        return {str(title).strip().lower() for (title,) in titles if str(title).strip()}
    finally:
        session.close()


def _create_if_missing(payloads: Iterable[dict[str, str]], existing_titles: set[str]) -> int:
    created_count = 0
    for payload in payloads:
        normalized_title = str(payload.get("title", "")).strip().lower()
        if not normalized_title or normalized_title in existing_titles:
            continue
        priority_score = calculate_priority(payload)
        create_issue(payload, priority_score)
        existing_titles.add(normalized_title)
        created_count += 1
    return created_count


def _create_resolved_if_missing(payloads: Iterable[dict[str, object]], existing_titles: set[str]) -> int:
    created_count = 0
    for item in payloads:
        issue_payload = dict(item["issue"])
        normalized_title = str(issue_payload.get("title", "")).strip().lower()
        if not normalized_title or normalized_title in existing_titles:
            continue

        priority_score = calculate_priority(issue_payload)
        created = create_issue(issue_payload, priority_score)
        verify_work(
            issue_ids=[int(created["id"])],
            image_filename="demo-backfill-verification.png",
            location=str(item["verification"]["location"]),
            action_taken=str(item["verification"]["action_taken"]),
        )
        existing_titles.add(normalized_title)
        created_count += 1
    return created_count


def _backfill_dispatch_assignments() -> int:
    saved_count = 0
    for assignment in DISPATCH_BACKFILL_ASSIGNMENTS:
        save_dispatch_assignment(
            cluster_title=str(assignment["cluster_title"]),
            location=str(assignment["location"]),
            department=str(assignment["department"]),
            team=str(assignment["team"]),
            officer=str(assignment["officer"]),
            status=str(assignment["status"]),
            notes=str(assignment["notes"]),
            assigned_by=str(assignment["assigned_by"]),
        )
        saved_count += 1
    return saved_count


def backfill_demo_data() -> dict[str, int]:
    """
    Enrich a non-empty local demo database without resetting any existing data.

    The backfill is idempotent for issues, using issue titles as a lightweight
    duplicate guard. Dispatch assignments are safely upserted by cluster key.
    """

    existing_titles = _existing_titles()
    created_active = _create_if_missing(ACTIVE_BACKFILL_ISSUES, existing_titles)
    created_resolved = _create_resolved_if_missing(RESOLVED_BACKFILL_ISSUES, existing_titles)
    saved_dispatch = _backfill_dispatch_assignments()

    return {
        "active_issues_added": created_active,
        "resolved_issues_added": created_resolved,
        "dispatch_assignments_upserted": saved_dispatch,
    }
