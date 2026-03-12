from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel


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


# Temporary, in-memory storage for issues. This is deliberately simple and
# not suitable for production use; it will be replaced with a database layer.
issues_db: list[Issue] = []


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
    issue = Issue(id=new_id, **issue_input.model_dump())
    issues_db.append(issue)
    return issue


@app.get("/issues", response_model=list[Issue], tags=["issues"])
def list_issues() -> list[Issue]:
    """
    Return all issues currently stored in the in-memory collection.

    Once a real database is introduced, this endpoint will be updated to
    page, filter, and sort results from the persistence layer.
    """

    return issues_db


# Entry-point note:
# Run locally with: `uvicorn backend.api.main:app --reload`
