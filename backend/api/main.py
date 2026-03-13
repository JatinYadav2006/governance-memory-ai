from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

from backend.services.prioritization import calculate_priority
from backend.services.vector_memory import add_memory, find_similar_cases


# NOTE:
# This module currently provides a minimal, in-memory implementation
# for accepting and listing citizen issues. It will later be extended
# with proper routing, domain models, business logic, and persistence:
# - `backend/api/routes/` for versioned routers (e.g., /v1/issues, /v1/analytics)
# - `backend/models/` for richer domain models and schemas
# - `backend/logic/` for governance intelligence pipelines
# - `backend/database/` for persistence and governance memory storage layers


class IssueInput(BaseModel):
    """
    Input payload for a citizen-reported issue/complaint.

    This represents the data a client must send when submitting a new issue.
    """

    title: str
    description: str
    location: str
    urgency: str


class Issue(IssueInput):
    """
    Persisted representation of an issue with a server-assigned identifier.

    For now, this is stored in memory only. A proper database-backed model
    will replace this once persistence is introduced.
    """

    id: int
    priority_score: float


# Temporary, in-memory storage for issues. This is deliberately simple and
# not suitable for production use; it will be replaced with a database layer.
issues_db: list[Issue] = []


class MemoryInput(BaseModel):
    """
    Input payload for storing a governance case in vector memory.

    This will later be persisted and augmented with metadata (timestamps,
    jurisdiction, department, verification status, etc.).
    """

    issue_title: str
    issue_description: str
    action_taken: str
    outcome: str


class MemorySuggestionRequest(BaseModel):
    """
    Input payload for requesting memory suggestions based on an issue description.
    """

    issue_description: str


class MemoryCase(BaseModel):
    """
    JSON-safe view of a stored memory entry (embedding excluded).
    """

    issue_title: str
    issue_description: str
    action_taken: str
    outcome: str


app = FastAPI(title="Governance Memory AI API")


@app.get("/", tags=["meta"])
def root() -> dict[str, str]:
    return {"message": "Governance Memory AI API is running."}


@app.get("/health", tags=["meta"])
def health() -> dict[str, str]:
    return {"status": "healthy"}


@app.post("/submit_issue", response_model=Issue, tags=["issues"])
def submit_issue(issue_input: IssueInput) -> Issue:
    """
    Accept a new citizen issue, assign a unique identifier, store it in
    the in-memory collection, and return the stored issue.
    """

    new_id = len(issues_db) + 1

    # Compute priority using the simple prioritization engine.
    priority_score = calculate_priority(issue_input.model_dump())

    issue = Issue(
        id=new_id,
        priority_score=priority_score,
        **issue_input.model_dump(),
    )
    issues_db.append(issue)
    return issue


@app.get("/issues", response_model=list[Issue], tags=["issues"])
def list_issues() -> list[Issue]:
    """
    Return all issues currently stored in the in-memory collection.

    Once a real database is introduced, this endpoint will be updated to
    page, filter, and sort results from the persistence layer.
    """

    # Return issues sorted by priority_score (highest first).
    return sorted(issues_db, key=lambda issue: issue.priority_score, reverse=True)


@app.post("/add_memory", response_model=MemoryCase, tags=["memory"])
def add_memory_case(payload: MemoryInput) -> MemoryCase:
    """
    Store a governance case in the in-memory vector memory store.

    The embedding is generated server-side and stored internally, but omitted
    from the API response to keep payloads JSON-safe and lightweight.
    """

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
    """
    Return the top similar governance cases for a given issue description.

    This is a prototype retrieval endpoint (in-memory + cosine similarity).
    """

    results = find_similar_cases(payload.issue_description)
    return {"results": results}


# Entry-point note:
# Run locally with: `uvicorn backend.api.main:app --reload`
