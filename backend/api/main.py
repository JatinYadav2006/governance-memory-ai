from __future__ import annotations

from pathlib import Path
from threading import Lock
from uuid import uuid4

from fastapi import FastAPI
from fastapi import File, Form, UploadFile
from fastapi import HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import shutil

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
from backend.services.civic_ops_service import (
    build_citizen_transparency,
    build_civic_ops_bundle,
    build_department_assignments,
    build_executive_summary,
    build_impact_metrics,
    build_sla_overview,
    build_zone_performance,
)
from backend.services.demo_seed import seed_demo_data
from backend.services.issue_storage import create_issue, list_issues
from backend.services.prioritization import calculate_priority
from backend.services.sentiment_service import analyze_sentiment
from backend.services.social_feed_service import build_social_pulse
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

POLICY_DIR = Path(__file__).resolve().parents[2] / "assets" / "policies"
POLICY_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/policies", StaticFiles(directory=str(POLICY_DIR)), name="policies")

init_db()
seed_demo_admin()
seed_demo_data()

_ANALYTICS_CACHE_LOCK = Lock()
_ANALYTICS_CACHE: dict[str, object] = {
    "signature": None,
    "bundle": None,
}


def get_issue_dicts() -> list[dict[str, object]]:
    return list_issues()


def get_resolved_issue_dicts() -> list[dict[str, object]]:
    return list_issues(status="Resolved")


def _scan_policy_files(query: str, date_from: str | None = None, date_to: str | None = None) -> list[dict[str, str]]:
    from datetime import datetime
    normalized = str(query or "").strip().lower()
    if not normalized:
        return []

    matches = []
    for pdf_file in POLICY_DIR.glob("*.pdf"):
        filename = pdf_file.name
        stat = pdf_file.stat()
        upload_date = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d")

        # Filter by date if provided
        if date_from and upload_date < date_from:
            continue
        if date_to and upload_date > date_to:
            continue

        if normalized in filename.lower():
            matches.append({"filename": filename, "match_source": "filename", "snippet": "", "upload_date": upload_date})
            continue

        try:
            from pypdf import PdfReader
        except ImportError:
            continue

        try:
            text_chunks = []
            reader = PdfReader(str(pdf_file))
            for page in reader.pages:
                page_text = page.extract_text() or ""
                text_chunks.append(page_text)
            full_text = "\n".join(text_chunks)
            if normalized in full_text.lower():
                pos = full_text.lower().find(normalized)
                start = max(0, pos - 120)
                end = min(len(full_text), pos + 120)
                snippet = full_text[start:end].replace("\n", " ")
                matches.append({"filename": filename, "match_source": "content", "snippet": snippet, "upload_date": upload_date})
        except Exception:
            continue

    # Sort by relevance: filename matches first, then content matches
    matches.sort(key=lambda x: (0 if x["match_source"] == "filename" else 1, x["filename"]))

    # Limit to top 10
    return matches[:10]


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


def _issues_signature(issues: list[dict[str, object]]) -> tuple[tuple[object, ...], ...]:
    return tuple(
        (
            issue.get("id"),
            issue.get("status"),
            issue.get("title"),
            issue.get("description"),
            issue.get("location"),
            issue.get("urgency"),
            issue.get("priority_score"),
        )
        for issue in issues
    )


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


def _get_analysis_bundle() -> dict[str, object]:
    issues = get_issue_dicts()
    resolved_issues = _get_resolved_issues()
    signature = (
        _issues_signature(issues),
        tuple(
            (
                issue.get("title"),
                issue.get("description"),
                issue.get("location"),
                issue.get("action_taken"),
            )
            for issue in resolved_issues
        ),
    )

    with _ANALYTICS_CACHE_LOCK:
        cached_signature = _ANALYTICS_CACHE.get("signature")
        cached_bundle = _ANALYTICS_CACHE.get("bundle")
        if cached_signature == signature and isinstance(cached_bundle, dict):
            return cached_bundle

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

        bundle = {
            "issues": issues,
            "resolved_issues": resolved_issues,
            "clusters": clusters,
            "enriched_clusters": enriched_clusters,
        }
        _ANALYTICS_CACHE["signature"] = signature
        _ANALYTICS_CACHE["bundle"] = bundle
        return bundle


@app.get("/", tags=["meta"])
def root() -> dict[str, str]:
    return {"message": "Governance Memory AI API is running."}


@app.get("/health", tags=["meta"])
def health() -> dict[str, str]:
    return {"status": "healthy"}


@app.get("/policy_search", tags=["policy"])
def policy_search(query: str, date_from: str | None = None, date_to: str | None = None) -> list[dict[str, object]]:
    """Search stored policy PDF documents by keyword (filename + optional PDF content via pypdf). Returns top 10 results sorted by relevance. Optional date filters in YYYY-MM-DD format."""
    return _scan_policy_files(query, date_from, date_to)


@app.post("/upload_policy", tags=["policy"])
async def upload_policy(file: UploadFile = File(...)) -> dict[str, str]:
    """Upload a PDF policy document to the assets/policies folder."""
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
    file_path = POLICY_DIR / file.filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"message": f"Policy '{file.filename}' uploaded successfully."}


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
    bundle = _get_analysis_bundle()
    return list(bundle["clusters"])


@app.get("/ai_insights", tags=["analytics"])
def ai_insights() -> list[dict[str, str]]:
    bundle = _get_analysis_bundle()
    clusters = list(bundle["clusters"])
    return [generate_cluster_insight(cluster) for cluster in clusters]


@app.get("/crisis_alerts", tags=["analytics"])
def crisis_alerts() -> list[dict[str, str]]:
    bundle = _get_analysis_bundle()
    clusters = list(bundle["clusters"])
    return detect_crisis(clusters)


@app.get("/policy_recommendations", tags=["analytics"])
def policy_recommendations() -> list[dict[str, object]]:
    bundle = _get_analysis_bundle()
    clusters = list(bundle["clusters"])
    return [generate_policy_recommendation(cluster) for cluster in clusters]


@app.get("/governance_memory", tags=["analytics"])
def governance_memory() -> list[dict[str, object]]:
    bundle = _get_analysis_bundle()
    clusters = list(bundle["enriched_clusters"])
    resolved_issues = list(bundle["resolved_issues"])

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
    bundle = _get_analysis_bundle()
    clusters = list(bundle["enriched_clusters"])
    target_cluster = next((cluster for cluster in clusters if int(cluster.get("cluster_id", -1)) == int(cluster_id)), None)
    if target_cluster is None:
        raise HTTPException(status_code=404, detail="Cluster not found.")

    resolved_issues = list(bundle["resolved_issues"])
    return build_war_room(
        target_cluster,
        target_cluster.get("issue_details", []),
        resolved_issues,
    )


@app.get("/impact_metrics", tags=["analytics"])
def impact_metrics() -> dict[str, object]:
    return build_impact_metrics()


@app.get("/department_assignments", tags=["analytics"])
def department_assignments() -> list[dict[str, object]]:
    return build_department_assignments()


@app.get("/sla_overview", tags=["analytics"])
def sla_overview() -> dict[str, object]:
    return build_sla_overview()


@app.get("/zone_performance", tags=["analytics"])
def zone_performance() -> list[dict[str, object]]:
    return build_zone_performance()


@app.get("/executive_summary", tags=["analytics"])
def executive_summary() -> dict[str, object]:
    return build_executive_summary()


@app.get("/social_pulse", tags=["analytics"])
def social_pulse() -> dict[str, object]:
    analysis = _get_analysis_bundle()
    return build_social_pulse(list(analysis["clusters"]))


@app.get("/admin_dashboard_bundle", tags=["analytics"])
def admin_dashboard_bundle() -> dict[str, object]:
    analysis = _get_analysis_bundle()
    civic_ops = build_civic_ops_bundle()

    issues = list(analysis["issues"])
    resolved_issues = get_resolved_issue_dicts()
    analytics_payload = generate_issue_statistics(issues)
    trust_payload = {
        "trust_score": calculate_trust_score(issues),
        "total_issues": len(issues),
    }
    trends_payload = {"trends": detect_issue_trends(issues)}
    clusters = list(analysis["clusters"])
    enriched_clusters = list(analysis["enriched_clusters"])
    crisis = detect_crisis(clusters)
    insights = [generate_cluster_insight(cluster) for cluster in clusters]
    policy = [generate_policy_recommendation(cluster) for cluster in clusters]
    social = build_social_pulse(clusters)

    memory_results: list[dict[str, object]] = []
    resolved_issues_memory = list(analysis["resolved_issues"])
    for cluster in enriched_clusters:
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
            resolved_issues_memory,
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

    return {
        "issues": issues,
        "resolved_issues": resolved_issues,
        "analytics": analytics_payload,
        "trust": trust_payload,
        "trends": trends_payload,
        "clusters": clusters,
        "insights": insights,
        "policy_recommendations": policy,
        "governance_memory": memory_results,
        "crisis_alerts": crisis,
        "social_pulse": social,
        "impact_metrics": civic_ops["impact_metrics"],
        "department_assignments": civic_ops["department_assignments"],
        "sla_overview": civic_ops["sla_overview"],
        "zone_performance": civic_ops["zone_performance"],
        "executive_summary": civic_ops["executive_summary"],
    }


@app.get("/citizen_transparency", tags=["analytics"])
def citizen_transparency(location: str = "") -> dict[str, object]:
    return build_citizen_transparency(location)


@app.post("/generate_update", tags=["communication"])
def generate_update(payload: IssueInput) -> dict[str, str]:
    return {"generated_update": generate_public_update(payload.model_dump())}


@app.post("/verify_work", tags=["verification"])
async def verify_work_upload(
    issue_id: int | None = Form(None),
    issue_ids: str | None = Form(None),
    location: str = Form(...),
    action_taken: str | None = Form(None),
    image: UploadFile = File(...),
) -> dict[str, object]:
    resolved_issue_ids: list[int] = []
    if issue_ids:
        resolved_issue_ids = [
            int(value.strip())
            for value in issue_ids.split(",")
            if value.strip()
        ]
    elif issue_id is not None:
        resolved_issue_ids = [int(issue_id)]

    if not resolved_issue_ids:
        raise HTTPException(status_code=400, detail="Provide issue_id or issue_ids for verification.")

    suffix = Path(image.filename or "").suffix
    saved_filename = f"issue_batch_{resolved_issue_ids[0]}_{uuid4().hex}{suffix}"
    saved_path = UPLOADS_DIR / saved_filename

    content = await image.read()
    saved_path.write_bytes(content)

    record = verify_work(
        issue_ids=resolved_issue_ids,
        image_filename=saved_filename,
        location=location,
        action_taken=action_taken,
    )
    return {"verification": record}


@app.get("/verifications", tags=["verification"])
def verifications() -> dict[str, object]:
    return {"verifications": get_verifications()}
