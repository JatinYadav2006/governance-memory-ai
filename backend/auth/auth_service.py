from __future__ import annotations

import hashlib
from typing import Optional

from sqlalchemy.orm import Session

from backend.db.database import SessionLocal, UserRecord
from backend.models.user_model import User, UserCreate

DEMO_ADMIN_EMAIL = "admin@govai.demo"
DEMO_ADMIN_PASSWORD = "GovAI_Admin#2026!"


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def _to_user(record: UserRecord) -> User:
    return User(
        id=record.id,
        name=record.name,
        email=record.email,
        phone=record.phone,
        location=record.location,
        role=record.role,
    )


def _find_user_record_by_email(session: Session, email: str) -> Optional[UserRecord]:
    normalized_email = email.strip().lower()
    return session.query(UserRecord).filter(UserRecord.email == normalized_email).first()


def _validate_password_strength(password: str) -> None:
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long.")
    if password.lower() == password or password.upper() == password:
        raise ValueError("Password must include both uppercase and lowercase letters.")
    if not any(character.isdigit() for character in password):
        raise ValueError("Password must include at least one number.")
    if not any(not character.isalnum() for character in password):
        raise ValueError("Password must include at least one special character.")


def register_user(user_data: UserCreate) -> User:
    session = SessionLocal()
    try:
        user_dict = user_data.model_dump()
        _validate_password_strength(str(user_dict["password"]))
        existing = _find_user_record_by_email(session, str(user_dict["email"]))
        if existing is not None:
            raise ValueError("An account with this email already exists.")

        user_record = UserRecord(
            name=user_dict["name"],
            email=str(user_dict["email"]).strip().lower(),
            phone=user_dict["phone"],
            location=user_dict["location"],
            password_hash=_hash_password(user_dict["password"]),
            role="user",
        )
        session.add(user_record)
        session.commit()
        session.refresh(user_record)
        return _to_user(user_record)
    finally:
        session.close()


def login_user(email: str, password: str) -> Optional[User]:
    session = SessionLocal()
    try:
        record = (
            session.query(UserRecord)
            .filter(UserRecord.email == email.strip().lower())
            .filter(UserRecord.password_hash == _hash_password(password))
            .first()
        )
        if record is None:
            return None
        return _to_user(record)
    finally:
        session.close()


def create_admin(name: str, email: str, phone: str, location: str, password: str) -> User:
    session = SessionLocal()
    try:
        existing = _find_user_record_by_email(session, email)
        if existing is not None:
            password_hash = _hash_password(password)
            updated = False
            if existing.role != "admin":
                existing.role = "admin"
                updated = True
            if existing.password_hash != password_hash:
                existing.password_hash = password_hash
                updated = True
            if updated:
                session.add(existing)
                session.commit()
                session.refresh(existing)
            return _to_user(existing)

        user_record = UserRecord(
            name=name,
            email=email.strip().lower(),
            phone=phone,
            location=location,
            password_hash=_hash_password(password),
            role="admin",
        )
        session.add(user_record)
        session.commit()
        session.refresh(user_record)
        return _to_user(user_record)
    finally:
        session.close()


def seed_demo_admin() -> User:
    return create_admin(
        name="Demo Admin",
        email=DEMO_ADMIN_EMAIL,
        phone="+971-000-0000",
        location="Central Command",
        password=DEMO_ADMIN_PASSWORD,
    )
