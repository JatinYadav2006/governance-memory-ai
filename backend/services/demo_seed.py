from __future__ import annotations

from backend.db.database import IssueRecord, SessionLocal
from backend.services.issue_storage import create_issue
from backend.services.prioritization import calculate_priority
from backend.services.work_verification import verify_work


ACTIVE_ISSUES = [
    {
        "title": "Water supply disruption near Sector 4",
        "description": "Residents report low pressure and repeated water cuts across the Sector 4 blocks since morning.",
        "location": "Prayagraj",
        "urgency": "High",
    },
    {
        "title": "No water in Ward 7 apartments",
        "description": "Multiple apartment buildings in Ward 7 have not received regular water supply since last night.",
        "location": "Prayagraj",
        "urgency": "High",
    },
    {
        "title": "Water pipeline leak near civil lines",
        "description": "A pipeline leak is reducing pressure and leaving homes without stable water in Civil Lines.",
        "location": "Prayagraj",
        "urgency": "High",
    },
    {
        "title": "Irregular water supply in teacher colony",
        "description": "Teacher colony residents say the water supply is dropping for long stretches during the day.",
        "location": "Prayagraj",
        "urgency": "High",
    },
    {
        "title": "Morning water cuts in old quarter",
        "description": "The old quarter is facing repeated morning water cuts and residents are depending on stored supply.",
        "location": "Prayagraj",
        "urgency": "High",
    },
    {
        "title": "Water pressure collapse near railway lane",
        "description": "Very low water pressure near railway lane suggests a supply issue or local pipeline fault.",
        "location": "Prayagraj",
        "urgency": "High",
    },
    {
        "title": "Pipe damage affecting north block",
        "description": "Pipe damage may be affecting the north block where residents report no usable water for several hours.",
        "location": "Prayagraj",
        "urgency": "High",
    },
    {
        "title": "Water access complaint from hostel road",
        "description": "Hostel road residents report delayed water access and inconsistent pressure since last evening.",
        "location": "Prayagraj",
        "urgency": "High",
    },
    {
        "title": "Supply interruption near university road",
        "description": "University road households report intermittent supply interruption and dry taps in the morning cycle.",
        "location": "Prayagraj",
        "urgency": "High",
    },
    {
        "title": "Water line issue beside market chowk",
        "description": "A suspected water line issue beside market chowk is affecting distribution to nearby homes.",
        "location": "Prayagraj",
        "urgency": "High",
    },
    {
        "title": "Low-pressure water issue in Ward 5",
        "description": "Ward 5 residents are seeing weak water flow that may indicate a larger supply failure.",
        "location": "Prayagraj",
        "urgency": "High",
    },
    {
        "title": "Garbage piling up near university gate",
        "description": "Overflowing waste bins and uncollected trash near the main university entrance are causing foul smell.",
        "location": "Lucknow",
        "urgency": "Medium",
    },
    {
        "title": "Trash overflow beside market lane",
        "description": "Garbage bags and waste overflow are spreading beside the evening market lane.",
        "location": "Lucknow",
        "urgency": "Medium",
    },
    {
        "title": "Sanitation delay near old bus stop",
        "description": "Sanitation crews may have missed pickup near the old bus stop because trash is collecting again.",
        "location": "Lucknow",
        "urgency": "Medium",
    },
    {
        "title": "Waste bins overflowing near shopping block",
        "description": "Overflowing waste bins near the shopping block are creating smell and attracting stray animals.",
        "location": "Lucknow",
        "urgency": "Medium",
    },
    {
        "title": "Potholes on ring road stretch",
        "description": "Deep potholes on the ring road are slowing traffic and causing near misses for two-wheelers.",
        "location": "Kanpur",
        "urgency": "Medium",
    },
    {
        "title": "Road surface broken near bus stand",
        "description": "Damaged road surface near the central bus stand is causing congestion and safety concerns.",
        "location": "Kanpur",
        "urgency": "Medium",
    },
    {
        "title": "Pothole hazard beside school lane",
        "description": "Large potholes beside the school lane are worsening and creating safety issues for parents and buses.",
        "location": "Kanpur",
        "urgency": "Medium",
    },
    {
        "title": "Drainage blockage after rainfall",
        "description": "Water is not clearing from the side drains after rainfall and the lane remains waterlogged.",
        "location": "Varanasi",
        "urgency": "High",
    },
    {
        "title": "Drain overflow in residential pocket",
        "description": "Blocked drainage line is pushing dirty water back into the residential lane.",
        "location": "Varanasi",
        "urgency": "High",
    },
    {
        "title": "Waterlogged lane due to blocked drain",
        "description": "A blocked drain is leaving the lane waterlogged and residents cannot move safely after rain.",
        "location": "Varanasi",
        "urgency": "High",
    },
]


RESOLVED_ISSUES = [
    {
        "issue": {
            "title": "Pipeline leak affecting Ward 3",
            "description": "A damaged pipeline caused repeated low-pressure complaints across Ward 3.",
            "location": "Prayagraj",
            "urgency": "High",
        },
        "verification": {
            "location": "Ward 3 Field Team",
            "action_taken": "Pipeline repair completed and pressure restored",
        },
    },
    {
        "issue": {
            "title": "Garbage overflow near old market",
            "description": "Missed pickup cycles led to overflow around the old market cluster.",
            "location": "Lucknow",
            "urgency": "Medium",
        },
        "verification": {
            "location": "Sanitation Zone B",
            "action_taken": "Garbage collection completed and overflow bins cleared",
        },
    },
    {
        "issue": {
            "title": "Power outage in residential block",
            "description": "Repeated electricity complaints were reported after feeder instability in the residential block.",
            "location": "Kanpur",
            "urgency": "High",
        },
        "verification": {
            "location": "Utility Response Unit",
            "action_taken": "Electrical fault isolated and feeder service restored",
        },
    },
    {
        "issue": {
            "title": "Drain cleanup near temple road",
            "description": "Blocked drainage near temple road caused waterlogging and foul runoff after rainfall.",
            "location": "Varanasi",
            "urgency": "High",
        },
        "verification": {
            "location": "Drainage Response Cell",
            "action_taken": "Drainage blockage cleared and water flow restored",
        },
    },
]


def seed_demo_data() -> None:
    session = SessionLocal()
    try:
        issue_count = session.query(IssueRecord).count()
    finally:
        session.close()

    if issue_count > 0:
        return

    for payload in ACTIVE_ISSUES:
        priority_score = calculate_priority(payload)
        create_issue(payload, priority_score)

    for item in RESOLVED_ISSUES:
        payload = item["issue"]
        priority_score = calculate_priority(payload)
        created = create_issue(payload, priority_score)
        verify_work(
            issue_ids=[int(created["id"])],
            image_filename="seed-verification.png",
            location=str(item["verification"]["location"]),
            action_taken=str(item["verification"]["action_taken"]),
        )
