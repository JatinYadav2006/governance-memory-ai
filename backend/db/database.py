from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, create_engine, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker


DATABASE_URL = "sqlite:///./governance_ai.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class UserRecord(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    phone: Mapped[str] = mapped_column(String(64), nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(32), nullable=False, default="user")
    auth_provider: Mapped[str | None] = mapped_column(String(64), nullable=True)
    provider_subject: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    issues: Mapped[list["IssueRecord"]] = relationship(back_populates="user")


class IssueClusterRecord(Base):
    __tablename__ = "issue_clusters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    cluster_title: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    issue_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    priority_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    issues: Mapped[list["IssueRecord"]] = relationship(back_populates="cluster")


class IssueRecord(Base):
    __tablename__ = "issues"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    urgency: Mapped[str] = mapped_column(String(32), nullable=False)
    image_filename: Mapped[str | None] = mapped_column(String(512), nullable=True)
    status: Mapped[str] = mapped_column(String(64), nullable=False, default="Open")
    cluster_id: Mapped[int | None] = mapped_column(ForeignKey("issue_clusters.id"), nullable=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    cluster: Mapped[IssueClusterRecord | None] = relationship(back_populates="issues")
    user: Mapped[UserRecord | None] = relationship(back_populates="issues")
    verification_records: Mapped[list["VerificationRecord"]] = relationship(back_populates="issue")


class VerificationRecord(Base):
    __tablename__ = "verification_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    issue_id: Mapped[int] = mapped_column(ForeignKey("issues.id"), nullable=False)
    image_path: Mapped[str] = mapped_column(String(512), nullable=False)
    verified_by: Mapped[str] = mapped_column(String(255), nullable=False)
    action_taken: Mapped[str | None] = mapped_column(String(255), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    issue: Mapped[IssueRecord] = relationship(back_populates="verification_records")


class DispatchAssignmentRecord(Base):
    __tablename__ = "dispatch_assignments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    cluster_key: Mapped[str] = mapped_column(String(512), unique=True, index=True, nullable=False)
    cluster_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cluster_title: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    department: Mapped[str] = mapped_column(String(255), nullable=False)
    team: Mapped[str] = mapped_column(String(255), nullable=False)
    officer: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(64), nullable=False, default="Assigned")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    assigned_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    _ensure_issue_columns()


def _ensure_issue_columns() -> None:
    """
    Lightweight SQLite schema patching for demo use.

    This keeps older local databases compatible when new nullable columns are
    added during rapid iteration, without requiring the user to delete the DB.
    """

    expected_columns = {
        "image_filename": "ALTER TABLE issues ADD COLUMN image_filename VARCHAR(512)",
    }

    with engine.begin() as connection:
        existing_tables = connection.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' AND name='issues'")
        ).fetchall()
        if not existing_tables:
            return

        table_info = connection.execute(text("PRAGMA table_info(issues)")).fetchall()
        existing_columns = {str(row[1]) for row in table_info}

        for column_name, alter_sql in expected_columns.items():
            if column_name not in existing_columns:
                connection.execute(text(alter_sql))

        verification_table_exists = connection.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' AND name='verification_records'")
        ).fetchall()
        if verification_table_exists:
            verification_info = connection.execute(text("PRAGMA table_info(verification_records)")).fetchall()
            verification_columns = {str(row[1]) for row in verification_info}
            if "action_taken" not in verification_columns:
                connection.execute(text("ALTER TABLE verification_records ADD COLUMN action_taken VARCHAR(255)"))

        user_table_exists = connection.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        ).fetchall()
        if user_table_exists:
            user_info = connection.execute(text("PRAGMA table_info(users)")).fetchall()
            user_columns = {str(row[1]) for row in user_info}
            if "auth_provider" not in user_columns:
                connection.execute(text("ALTER TABLE users ADD COLUMN auth_provider VARCHAR(64)"))
            if "provider_subject" not in user_columns:
                connection.execute(text("ALTER TABLE users ADD COLUMN provider_subject VARCHAR(255)"))
