from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI
from fastapi import File, Form, UploadFile
from fastapi import HTTPException
from pydantic import BaseModel

from backend.ai.crisis_detection import detect_crisis
from backend.ai.governance_memory import find_similar_case
from backend.ai.governance_insights import generate_cluster_insight
from backend.ai.issue_clustering import cluster_issues
from backend.ai.policy_recommendation import generate_policy_recommendation
from backend.ai.war_room import build_war_room
from backend.auth.auth_routes import router as auth_router
from backend.auth.auth_service import seed_demo_admin
from backend.db.database import IssueRecord, SessionLocal, VerificationRecord, init_db
from backend.services.analytics_service import generate_issue_statistics
from backend.services.communication_generator import generate_public_update
from backend.services.demo_seed import seed_demo_data
from backend.services.issue_storage import create_issue, list_issues
from backend.services.prioritization import calculate_priority
from backend.services.sentiment_service import analyze_sentiment
from backend.services.trend_analysis import detect_issue_trends
from backend.services.trust_engine import calculate_trust_score
from backend.services.vector_memory import add_memory, find_similar_cases
from backend.services.work_verification import get_verifications, verify_work


class IssueInput(BaseModel):
    title: str
    description: str
    location: str
    urgency: str
    image_filename: str | None = None


class Issue(IssueInput):
    id: int
    status: str = "Open"
    priority_score: float


class MemoryInput(BaseModel):
    issue_title: str
    issue_description: str
    action_taken: str
    outcome: str


class MemorySuggestionRequest(BaseModel):
    issue_description: str


class MemoryCase(BaseModel):
    issue_title: str
    issue_description: str
    action_taken: str
    outcome: str


app = FastAPI(title="Governance Memory AI API")
app.include_router(auth_router)

UPLOADS_DIR = Path("uploads")
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

init_db()
seed_demo_admin()
seed_demo_data()


def get_issue_dicts() -> list[dict[str, object]]:
    return list_issues()


def get_resolved_issue_dicts() -> list[dict[str, object]]:
    return list_issues(status="Resolved")


def _cluster_input_from_issues(issues: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "id": issue.get("id"),
            "title": issue.get("title", ""),
            "description": issue.get("description", ""),
            "location": issue.get("location", ""),
        }
        for issue in issues
    ]


def _build_clusters_with_issue_details(issues: list[dict[str, object]]) -> list[dict[str, object]]:
    clusters = cluster_issues(_cluster_input_from_issues(issues))
    issues_by_id = {
        int(issue["id"]): issue
        for issue in issues
        if issue.get("id") is not None
    }

    enriched_clusters: list[dict[str, object]] = []
    for cluster in clusters:
        issue_details = [
            issues_by_id[int(issue_id)]
            for issue_id in cluster.get("issue_ids", [])
            if int(issue_id) in issues_by_id
        ]
        enriched_clusters.append({**cluster, "issue_details": issue_details})
    return enriched_clusters


def _get_resolved_issues() -> list[dict[str, object]]:
    session = SessionLocal()
    try:
        verification_records = (
            session.query(VerificationRecord, IssueRecord)
            .join(IssueRecord, VerificationRecord.issue_id == IssueRecord.id)
            .filter(VerificationRecord.action_taken.is_not(None))
            .order_by(VerificationRecord.timestamp.desc())
            .all()
        )

        resolved_by_issue_id: dict[int, dict[str, object]] = {}
        for verification_record, issue_record in verification_records:
            if issue_record.id in resolved_by_issue_id:
                continue
            resolved_by_issue_id[issue_record.id] = {
                "title": issue_record.title,
                "description": issue_record.description,
                "location": issue_record.location,
                "action_taken": verification_record.action_taken,
            }

        return list(resolved_by_issue_id.values())
    finally:
        session.close()


@app.get("/", tags=["meta"])
def root() -> dict[str, str]:
    return {"message": "Governance Memory AI API is running."}


@app.get("/health", tags=["meta"])
def health() -> dict[str, str]:
    return {"status": "healthy"}


@app.post("/submit_issue", response_model=Issue, tags=["issues"])
def submit_issue(issue_input: IssueInput) -> Issue:
    priority_score = calculate_priority(issue_input.model_dump())
    issue_payload = create_issue(issue_input.model_dump(), priority_score)
    return Issue(**issue_payload)


@app.get("/issues", response_model=list[Issue], tags=["issues"])
def list_all_issues() -> list[Issue]:
    return [Issue(**issue) for issue in list_issues()]


@app.get("/issues/history", response_model=list[Issue], tags=["issues"])
def list_resolved_issues() -> list[Issue]:
    return [Issue(**issue) for issue in get_resolved_issue_dicts()]


@app.post("/add_memory", response_model=MemoryCase, tags=["memory"])
def add_memory_case(payload: MemoryInput) -> MemoryCase:
    entry = add_memory(
        issue_title=payload.issue_title,
        issue_description=payload.issue_description,
        action_taken=payload.action_taken,
        outcome=payload.outcome,
    )

    return MemoryCase(
        issue_title=entry.get("issue_title", ""),
        issue_description=entry.get("issue_description", ""),
        action_taken=entry.get("action_taken", ""),
        outcome=entry.get("outcome", ""),
    )


@app.post("/memory_suggestions", tags=["memory"])
def memory_suggestions(payload: MemorySuggestionRequest) -> dict[str, object]:
    return {"results": find_similar_cases(payload.issue_description)}


@app.get("/trust_score", tags=["analytics"])
def trust_score() -> dict[str, int]:
    issue_dicts = get_issue_dicts()
    for issue in issue_dicts:
        _ = analyze_sentiment(str(issue.get("description", "")))

    score = calculate_trust_score(issue_dicts)
    return {"trust_score": score, "total_issues": len(issue_dicts)}


@app.get("/analytics", tags=["analytics"])
def analytics() -> dict[str, object]:
    return generate_issue_statistics(get_issue_dicts())


@app.get("/issue_trends", tags=["analytics"])
def issue_trends() -> dict[str, object]:
    return {"trends": detect_issue_trends(get_issue_dicts())}


@app.get("/issue_clusters", tags=["analytics"])
def issue_clusters() -> list[dict[str, object]]:
    issues = get_issue_dicts()
    return cluster_issues(_cluster_input_from_issues(issues))


@app.get("/ai_insights", tags=["analytics"])
def ai_insights() -> list[dict[str, str]]:
    issues = get_issue_dicts()
    clusters = cluster_issues(_cluster_input_from_issues(issues))
    return [generate_cluster_insight(cluster) for cluster in clusters]


@app.get("/crisis_alerts", tags=["analytics"])
def crisis_alerts() -> list[dict[str, str]]:
    issues = get_issue_dicts()
    clusters = cluster_issues(_cluster_input_from_issues(issues))
    return detect_crisis(clusters)


@app.get("/policy_recommendations", tags=["analytics"])
def policy_recommendations() -> list[dict[str, object]]:
    issues = get_issue_dicts()
    clusters = cluster_issues(_cluster_input_from_issues(issues))
    return [generate_policy_recommendation(cluster) for cluster in clusters]


@app.get("/governance_memory", tags=["analytics"])
def governance_memory() -> list[dict[str, object]]:
    issues = get_issue_dicts()
    clusters = _build_clusters_with_issue_details(issues)
    resolved_issues = _get_resolved_issues()

    memory_results: list[dict[str, object]] = []
    for cluster in clusters:
        cluster_issue_texts: list[str] = []
        for issue in cluster.get("issue_details", []):
            title = str(issue.get("title", "")).strip()
            description = str(issue.get("description", "")).strip()
            combined_text = f"{title} {description}".strip()
            if combined_text:
                cluster_issue_texts.append(combined_text)

        cluster_description = " ".join(cluster_issue_texts)
        similar_case = find_similar_case(
            str(cluster.get("cluster_title", "")),
            cluster_description,
            resolved_issues,
        )
        if similar_case is None:
            continue

        memory_results.append(
            {
                "cluster_title": cluster.get("cluster_title", "General issue cluster"),
                "location": cluster.get("location", "Unknown"),
                "similar_case": similar_case.get("similar_case_title", "Unknown"),
                "action_taken": similar_case.get("action_taken", "No action recorded"),
                "similarity_score": similar_case.get("similarity_score", 0.0),
            }
        )

    return memory_results


@app.get("/war_room", tags=["analytics"])
def war_room(cluster_id: int) -> dict[str, object]:
    issues = get_issue_dicts()
    clusters = _build_clusters_with_issue_details(issues)
    target_cluster = next((cluster for cluster in clusters if int(cluster.get("cluster_id", -1)) == int(cluster_id)), None)
    if target_cluster is None:
        raise HTTPException(status_code=404, detail="Cluster not found.")

    resolved_issues = _get_resolved_issues()
    return build_war_room(
        target_cluster,
        target_cluster.get("issue_details", []),
        resolved_issues,
    )


@app.post("/generate_update", tags=["communication"])
def generate_update(payload: IssueInput) -> dict[str, str]:
    return {"generated_update": generate_public_update(payload.model_dump())}


@app.post("/verify_work", tags=["verification"])
async def verify_work_upload(
    issue_id: int = Form(...),
    location: str = Form(...),
    action_taken: str | None = Form(None),
    image: UploadFile = File(...),
) -> dict[str, object]:
    suffix = Path(image.filename or "").suffix
    saved_filename = f"issue_{issue_id}_{uuid4().hex}{suffix}"
    saved_path = UPLOADS_DIR / saved_filename

    content = await image.read()
    saved_path.write_bytes(content)

    record = verify_work(
        issue_id=issue_id,
        image_filename=saved_filename,
        location=location,
        action_taken=action_taken,
    )
    return {"verification": record}


@app.get("/verifications", tags=["verification"])
def verifications() -> dict[str, object]:
    return {"verifications": get_verifications()}
