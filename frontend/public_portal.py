import io
from typing import Any

import pandas as pd
import requests
import speech_recognition as sr
import streamlit as st


API_BASE = "http://127.0.0.1:8000"


def init_state() -> None:
    st.session_state.setdefault("current_user", None)
    st.session_state.setdefault("voice_transcript", "")
    st.session_state.setdefault("memory_suggestions", [])
    st.session_state.setdefault("last_submitted_issue", None)


def apply_page_style() -> None:
    st.set_page_config(page_title="Citizen Portal - Governance Memory AI", layout="wide")
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(56,189,248,0.18), transparent 24%),
                radial-gradient(circle at top right, rgba(74,222,128,0.12), transparent 22%),
                linear-gradient(180deg, #0d1322 0%, #111827 45%, #0f172a 100%);
        }
        .gm-hero {
            border: 1px solid rgba(255,255,255,0.10);
            border-radius: 24px;
            padding: 24px 26px;
            background:
                linear-gradient(135deg, rgba(14,165,233,0.18), rgba(15,23,42,0.10)),
                linear-gradient(180deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02));
            position: relative;
            overflow: hidden;
        }
        .gm-card {
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 18px;
            padding: 16px 18px;
            background: rgba(255,255,255,0.025);
            margin-bottom: 12px;
            position: relative;
            overflow: hidden;
        }
        .gm-hero::before,
        .gm-card::before {
            content: "";
            position: absolute;
            top: -110%;
            left: -35%;
            width: 42%;
            height: 320%;
            background: linear-gradient(
                90deg,
                rgba(255,255,255,0) 0%,
                rgba(125,211,252,0.00) 22%,
                rgba(186,230,253,0.16) 50%,
                rgba(45,212,191,0.08) 68%,
                rgba(255,255,255,0) 100%
            );
            transform: rotate(18deg) translateX(-180%);
            transition: transform 680ms ease;
            pointer-events: none;
        }
        .gm-hero:hover::before,
        .gm-card:hover::before {
            transform: rotate(18deg) translateX(430%);
        }
        .gm-tabs [data-baseweb="tab"] {
            background: rgba(255,255,255,0.04);
            border-radius: 999px;
            padding-left: 18px;
            padding-right: 18px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _count_options(total: int, base: list[int]) -> list[int]:
    options = [value for value in base if value < total]
    options.append(total if total > 0 else base[0])
    return sorted(set(options))


def render_header() -> None:
    st.markdown(
        """
        <div class="gm-hero">
            <div style="font-size:0.82rem;text-transform:uppercase;letter-spacing:0.08em;color:rgba(255,255,255,0.58);">
                Citizen Experience
            </div>
            <h1 style="margin:0.35rem 0 0.25rem 0;">Citizen Portal</h1>
            <p style="margin:0;max-width:760px;font-size:1.02rem;color:rgba(255,255,255,0.78);">
                Report local issues, attach supporting evidence, and see how the platform
                prioritizes your complaint and connects it to similar past civic cases.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def api_post(path: str, json: dict[str, Any]) -> dict[str, Any]:
    response = requests.post(f"{API_BASE}{path}", json=json, timeout=15)
    response.raise_for_status()
    return response.json() or {}


def api_get(path: str) -> Any:
    response = requests.get(f"{API_BASE}{path}", timeout=15)
    response.raise_for_status()
    return response.json()


def render_auth_section() -> None:
    st.markdown("### Account Access")
    st.caption("Use the citizen portal to submit a complaint, review nearby active reports, and track resolved history.")
    col_login, col_signup = st.columns(2)

    with col_login:
        st.markdown('<div class="gm-card">', unsafe_allow_html=True)
        st.markdown("#### Login")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login", use_container_width=True):
            try:
                user = api_post("/auth/login", {"email": email, "password": password})
            except requests.HTTPError as exc:
                detail = exc.response.text if exc.response is not None else str(exc)
                st.error(f"Login failed: {detail}")
            except requests.RequestException as exc:
                st.error(f"Login failed: {exc}")
            else:
                st.session_state["current_user"] = user
                st.success(f"Welcome back, {user.get('name')}.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_signup:
        st.markdown('<div class="gm-card">', unsafe_allow_html=True)
        st.markdown("#### Sign Up")
        name = st.text_input("Full Name", key="signup_name")
        sign_email = st.text_input("Email", key="signup_email")
        phone = st.text_input("Phone", key="signup_phone")
        location = st.text_input("Location", key="signup_location")
        password = st.text_input("Password", type="password", key="signup_password")
        if st.button("Create Account", use_container_width=True):
            payload = {
                "name": name,
                "email": sign_email,
                "phone": phone,
                "location": location,
                "password": password,
            }
            try:
                user = api_post("/auth/signup", payload)
            except requests.HTTPError as exc:
                detail = exc.response.text if exc.response is not None else str(exc)
                st.error(f"Sign up failed: {detail}")
            except requests.RequestException as exc:
                st.error(f"Sign up failed: {exc}")
            else:
                st.session_state["current_user"] = user
                st.success(f"Account created for {user.get('name')}.")
        st.markdown("</div>", unsafe_allow_html=True)


def require_login() -> dict[str, Any] | None:
    user = st.session_state.get("current_user")
    if user is None:
        st.info("Log in or sign up to submit an issue and track reports near your area.")
        return None

    cols = st.columns([4, 1])
    with cols[0]:
        st.markdown(
            f"**Logged in as:** {user.get('name')} | {user.get('email')} | {user.get('location')}"
        )
    with cols[1]:
        if st.button("Logout", use_container_width=True):
            st.session_state["current_user"] = None
            st.session_state["voice_transcript"] = ""
            st.session_state["memory_suggestions"] = []
            st.session_state["last_submitted_issue"] = None
            st.rerun()
    return user


def render_voice_input() -> None:
    st.markdown("#### Voice Complaint")
    audio_file = st.audio_input("Record a complaint") if hasattr(st, "audio_input") else None
    if audio_file is None and not hasattr(st, "audio_input"):
        audio_file = st.file_uploader("Upload audio", type=["wav", "flac", "mp3", "m4a"], key="voice_upload")

    if st.button("Transcribe Voice", disabled=audio_file is None):
        recognizer = sr.Recognizer()
        raw_bytes = audio_file.getvalue() if hasattr(audio_file, "getvalue") else audio_file.read()
        try:
            with sr.AudioFile(io.BytesIO(raw_bytes)) as source:
                audio = recognizer.record(source)
            transcript = recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            st.error("The audio was unclear. Please try again.")
        except sr.RequestError as exc:
            st.error(f"Speech recognition service error: {exc}")
        except Exception as exc:
            st.error(f"Unexpected transcription error: {exc}")
        else:
            st.session_state["voice_transcript"] = transcript
            st.success("Voice complaint transcribed.")

    transcript = st.session_state.get("voice_transcript")
    if transcript:
        st.text_area("Transcribed text", transcript, height=90, disabled=True)


def render_issue_submission(user: dict[str, Any]) -> None:
    left, right = st.columns([1.15, 0.85])

    with left:
        st.markdown("### Submit a New Issue")
        st.caption("The fastest demo flow is: record or type the complaint, submit it, then watch the AI triage panel update on the right.")
        render_voice_input()
        with st.form("citizen_issue_form"):
            title = st.text_input("Issue Title")
            description = st.text_area("Issue Description", value=st.session_state.get("voice_transcript", ""))
            location = st.text_input("Location", value=user.get("location", ""))
            urgency = st.selectbox("Urgency", ["Low", "Medium", "High"])
            issue_image = st.file_uploader(
                "Upload issue image",
                type=["png", "jpg", "jpeg", "webp"],
                key="issue_image",
            )
            submitted = st.form_submit_button("Submit Issue", type="primary")
            if submitted:
                payload = {
                    "title": title,
                    "description": description,
                    "location": location,
                    "urgency": urgency,
                    "image_filename": issue_image.name if issue_image is not None else None,
                }
                try:
                    issue = api_post("/submit_issue", payload)
                    suggestions_response = api_post("/memory_suggestions", {"issue_description": description})
                except requests.RequestException as exc:
                    st.error(f"Issue submission failed: {exc}")
                else:
                    st.session_state["last_submitted_issue"] = issue
                    st.session_state["memory_suggestions"] = suggestions_response.get("results", [])[:3]
                    st.session_state["voice_transcript"] = ""
                    st.success("Issue submitted successfully.")

    with right:
        st.markdown("### AI Triage Snapshot")
        last_issue = st.session_state.get("last_submitted_issue")
        if last_issue:
            top = st.columns(3)
            with top[0]:
                st.metric("Issue ID", last_issue.get("id", "N/A"))
            with top[1]:
                st.metric("Priority", f"{float(last_issue.get('priority_score', 0.0)):.1f}")
            with top[2]:
                st.metric("Urgency", last_issue.get("urgency", "N/A"))
            st.caption("This snapshot shows how the complaint entered the triage pipeline before it reaches the admin command center.")
        else:
            st.info("Submit an issue to see the AI triage result here.")

        suggestions = st.session_state.get("memory_suggestions") or []
        if suggestions:
            for suggestion in suggestions:
                st.markdown(
                    f"""
                    <div class="gm-card">
                        <div style="font-weight:800;margin-bottom:8px;">{suggestion.get("issue_title", "Untitled case")}</div>
                        <div style="margin-bottom:8px;"><strong>Action Taken:</strong> {suggestion.get("action_taken", "N/A")}</div>
                        <div><strong>Outcome:</strong> {suggestion.get("outcome", "N/A")}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.caption("Governance memory insights will appear here after submission.")


def filter_issues_by_location(issues: list[dict[str, Any]], location: str) -> list[dict[str, Any]]:
    if not location:
        return issues
    normalized = location.strip().lower()
    return [issue for issue in issues if normalized in str(issue.get("location", "")).lower()]


def render_issue_tables(user: dict[str, Any]) -> None:
    try:
        issues_payload = api_get("/issues")
        issues = issues_payload if isinstance(issues_payload, list) else []
        resolved_payload = api_get("/issues/history")
        resolved_issues = resolved_payload if isinstance(resolved_payload, list) else []
    except requests.RequestException as exc:
        st.warning(f"Unable to load issues: {exc}")
        return

    nearby = filter_issues_by_location(issues, user.get("location", ""))
    st.caption("Track the live complaint queue, the nearby active feed, and the resolved history without scrolling through long lists.")
    metrics = st.columns(3)
    with metrics[0]:
        st.metric("Total Reports", len(issues))
    with metrics[1]:
        st.metric("Nearby Reports", len(nearby))
    with metrics[2]:
        st.metric("Resolved History", len(resolved_issues))

    feed_tab, all_tab, history_tab = st.tabs(["Nearby Feed", "Active Reports", "Resolved History"])

    with feed_tab:
        search = st.text_input("Search nearby issues", placeholder="Search title or location", key="nearby_search")
        show_count = st.selectbox("Show nearby", _count_options(len(nearby), [10, 20, 50]), key="nearby_count")
        filtered = nearby
        if search.strip():
            term = search.strip().lower()
            filtered = [
                issue
                for issue in nearby
                if term in str(issue.get("title", "")).lower() or term in str(issue.get("location", "")).lower()
            ]
        if filtered:
            df = pd.DataFrame(filtered[:show_count])
            cols = [col for col in ["id", "title", "location", "urgency", "priority_score"] if col in df.columns]
            st.dataframe(df[cols], use_container_width=True, hide_index=True, height=420)
        else:
            st.info("No nearby issues found.")

    with all_tab:
        search = st.text_input("Search active reports", placeholder="Search title or location", key="all_reports_search")
        show_count = st.selectbox("Show reports", _count_options(len(issues), [10, 25, 50]), key="all_reports_count")
        filtered = issues
        if search.strip():
            term = search.strip().lower()
            filtered = [
                issue
                for issue in issues
                if term in str(issue.get("title", "")).lower() or term in str(issue.get("location", "")).lower()
            ]
        if filtered:
            df = pd.DataFrame(filtered[:show_count])
            cols = [col for col in ["id", "title", "location", "urgency", "priority_score"] if col in df.columns]
            st.dataframe(df[cols], use_container_width=True, hide_index=True, height=420)
        else:
            st.info("No submitted reports yet.")

    with history_tab:
        search = st.text_input(
            "Search resolved reports",
            placeholder="Search title or location",
            key="resolved_reports_search",
        )
        show_count = st.selectbox(
            "Show resolved",
            _count_options(len(resolved_issues), [10, 25, 50]),
            key="resolved_reports_count",
        )
        filtered = resolved_issues
        if search.strip():
            term = search.strip().lower()
            filtered = [
                issue
                for issue in resolved_issues
                if term in str(issue.get("title", "")).lower() or term in str(issue.get("location", "")).lower()
            ]
        if filtered:
            df = pd.DataFrame(filtered[:show_count])
            cols = [col for col in ["id", "title", "location", "urgency", "status", "priority_score"] if col in df.columns]
            st.dataframe(df[cols], use_container_width=True, hide_index=True, height=420)
        else:
            st.info("No resolved reports yet.")


def main() -> None:
    init_state()
    apply_page_style()
    render_header()
    if st.session_state.get("current_user") is None:
        render_auth_section()
    user = require_login()
    if user is None:
        return

    st.markdown('<div class="gm-tabs">', unsafe_allow_html=True)
    tab_submit, tab_feed = st.tabs(["Report Issue", "Track Reports"])
    st.markdown("</div>", unsafe_allow_html=True)

    with tab_submit:
        render_issue_submission(user)
    with tab_feed:
        render_issue_tables(user)


if __name__ == "__main__":
    main()
