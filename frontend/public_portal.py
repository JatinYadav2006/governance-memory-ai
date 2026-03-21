import tempfile
import re
from pathlib import Path
from typing import Any

import pandas as pd
import requests
import speech_recognition as sr
import streamlit as st


API_BASE = "http://127.0.0.1:8000"
VOICE_LANGUAGE_OPTIONS = {
    "English": "en-IN",
    "Hindi": "hi-IN",
    "Bengali": "bn-IN",
    "Tamil": "ta-IN",
    "Telugu": "te-IN",
    "Marathi": "mr-IN",
    "Gujarati": "gu-IN",
    "Kannada": "kn-IN",
    "Malayalam": "ml-IN",
    "Punjabi": "pa-IN",
    "Urdu": "ur-IN",
}
ISSUE_CATEGORY_ALIASES = {
    "Water Pipeline Issue": [
        "water pipe",
        "pipeline",
        "pipe leak",
        "जल पाइप",
        "पाइप लाइन",
        "पाइपलाइन",
        "পাইপলাইন",
        "குழாய்",
        "పైప్",
        "पाइप",
    ],
    "Water Supply Issue": [
        "no water",
        "water supply",
        "low pressure",
        "dry tap",
        "जल",
        "पानी",
        "जल आपूर्ति",
        "पानी नहीं",
        "জল",
        "পানি",
        "தண்ணீர்",
        "నీరు",
        "પાણી",
        "पाणी",
        "ਪਾਣੀ",
        "پانی",
    ],
    "Garbage Collection Issue": [
        "garbage",
        "trash",
        "waste",
        "overflow bin",
        "कचरा",
        "गंदगी",
        "আবর্জনা",
        "குப்பை",
        "చెత్త",
        "કચરો",
        "कचरा",
        "ਕੂੜਾ",
        "کوڑا",
    ],
    "Drainage Issue": [
        "drain",
        "drainage",
        "waterlogged",
        "sewage",
        "नाली",
        "जलभराव",
        "ড্রেন",
        "জল জমা",
        "வடிகால்",
        "కాలువ",
        "ગટર",
        "पाणी साचले",
        "ਨਾਲੀ",
        "نالہ",
    ],
    "Road Pothole Issue": [
        "pothole",
        "road broken",
        "damaged road",
        "road surface",
        "गड्ढा",
        "सड़क टूटी",
        "রাস্তা ভাঙা",
        "குழி",
        "రోడ్డు గుంత",
        "ખાડો",
        "खड्डा",
        "ਟੁੱਟੀ ਸੜਕ",
        "گڑھا",
    ],
    "Road Maintenance Issue": [
        "road",
        "street",
        "सड़क",
        "রাস্তা",
        "சாலை",
        "రోడ్డు",
        "રસ્તો",
        "रस्ता",
        "ਸੜਕ",
        "سڑک",
    ],
    "Power Supply Issue": [
        "power",
        "electricity",
        "outage",
        "streetlight",
        "बिजली",
        "करंट",
        "বিদ্যুৎ",
        "மின்சாரம்",
        "కరెంట్",
        "વીજળી",
        "वीज",
        "ਬਿਜਲੀ",
        "بجلی",
    ],
    "Streetlight Issue": [
        "streetlight",
        "street light",
        "लाइट",
        "स्ट्रीट लाइट",
        "রাস্তার আলো",
        "தெரு விளக்கு",
        "వీధి దీపం",
        "સ્ટ્રીટ લાઇટ",
        "रस्त्यावरील दिवा",
        "اسٹریٹ لائٹ",
    ],
    "Sewage Issue": [
        "sewage",
        "sewer",
        "सीवर",
        "গটার",
        "கழிவுநீர்",
        "కాలుష్య నీరు",
        "ગંદુ પાણી",
        "सांडपाणी",
        "سیوریج",
    ],
}
HIGH_URGENCY_ALIASES = {
    "emergency",
    "urgent",
    "danger",
    "serious",
    "severe",
    "immediately",
    "accident",
    "injury",
    "burst",
    "flood",
    "outage",
    "no water",
    "blocked road",
    "आपातकाल",
    "तुरंत",
    "खतरा",
    "गंभीर",
    "अभी",
    "दुर्घटना",
    "बाढ़",
    "অতি জরুরি",
    "বিপদ",
    "জরুরি",
    "அவசரம்",
    "ஆபத்து",
    "తక్షణం",
    "ప్రమాదం",
    "ઇમરજન્સી",
    "જોખમ",
    "तात्काळ",
    "धोका",
    "ਹਾਦਸਾ",
    "خطرہ",
}
MEDIUM_URGENCY_ALIASES = {
    "overflow",
    "pothole",
    "delay",
    "leak",
    "garbage",
    "unclean",
    "broken",
    "issue",
    "problem",
    "कचरा",
    "लीक",
    "देरी",
    "गड्ढा",
    "সমস্যা",
    "আবর্জনা",
    "கசிவு",
    "குப்பை",
    "సమస్య",
    "చెత్త",
    "લીક",
    "કચરો",
    "गळती",
    "समस्या",
    "مسئلہ",
}
KNOWN_LOCATION_ALIASES = {
    "Prayagraj": ["prayagraj", "इलाहाबाद", "allahabad", "प्रयागराज"],
    "Lucknow": ["lucknow", "लखनऊ"],
    "Kanpur": ["kanpur", "कानपुर"],
    "Varanasi": ["varanasi", "वाराणसी", "banaras", "काशी"],
    "Civil Lines": ["civil lines", "सिविल लाइंस"],
    "Ward 7": ["ward 7", "वार्ड 7", "वॉर्ड 7"],
    "Ward 5": ["ward 5", "वार्ड 5", "वॉर्ड 5"],
    "Ward 3": ["ward 3", "वार्ड 3", "वॉर्ड 3"],
    "Sector 4": ["sector 4", "सेक्टर 4"],
    "Teacher Colony": ["teacher colony", "टीचर कॉलोनी"],
    "University Road": ["university road", "यूनिवर्सिटी रोड"],
    "University Gate": ["university gate", "यूनिवर्सिटी गेट"],
    "Market Chowk": ["market chowk", "मार्केट चौक"],
    "Railway Lane": ["railway lane", "रेलवे लेन"],
    "Ring Road": ["ring road", "रिंग रोड"],
    "Bus Stand": ["bus stand", "बस स्टैंड"],
    "School Lane": ["school lane", "स्कूल लेन"],
    "Temple Road": ["temple road", "टेंपल रोड", "मंदिर रोड"],
}


def init_state() -> None:
    st.session_state.setdefault("current_user", None)
    st.session_state.setdefault("voice_transcript", "")
    st.session_state.setdefault("voice_status", "")
    st.session_state.setdefault("issue_title_draft", "")
    st.session_state.setdefault("issue_description_draft", "")
    st.session_state.setdefault("issue_location_draft", "")
    st.session_state.setdefault("issue_urgency_draft", "Medium")
    st.session_state.setdefault("reset_issue_form", False)
    st.session_state.setdefault("memory_suggestions", [])
    st.session_state.setdefault("last_submitted_issue", None)
    st.session_state.setdefault("voice_language_label", "English")


def apply_page_style() -> None:
    if not st.session_state.get("use_unified_access"):
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


def api_get(path: str, params: dict[str, Any] | None = None) -> Any:
    response = requests.get(f"{API_BASE}{path}", params=params, timeout=15)
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
                st.rerun()
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
                st.rerun()
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
            st.session_state["voice_status"] = ""
            st.session_state["issue_title_draft"] = ""
            st.session_state["issue_description_draft"] = ""
            st.session_state["issue_location_draft"] = ""
            st.session_state["issue_urgency_draft"] = "Medium"
            st.session_state["reset_issue_form"] = False
            st.session_state["memory_suggestions"] = []
            st.session_state["last_submitted_issue"] = None
            st.session_state["voice_language_label"] = "English"
            st.rerun()
    return user


def _suggest_issue_title(transcript: str) -> str:
    cleaned = re.sub(r"\s+", " ", transcript).strip()
    lowered = cleaned.lower()
    for title, aliases in ISSUE_CATEGORY_ALIASES.items():
        if any(alias in lowered for alias in aliases):
            return title

    words = re.findall(r"\w+", cleaned, re.UNICODE)
    if not words:
        return "Civic Issue Report"
    summary = " ".join(words[:5]).strip()
    return summary.title()


def _suggest_urgency(transcript: str) -> str:
    lowered = transcript.lower()
    if any(term in lowered for term in HIGH_URGENCY_ALIASES):
        return "High"
    if any(term in lowered for term in MEDIUM_URGENCY_ALIASES):
        return "Medium"
    return "Low"


def _extract_location(transcript: str, fallback_location: str) -> str:
    lowered = transcript.lower()
    for location, aliases in KNOWN_LOCATION_ALIASES.items():
        if any(alias in lowered for alias in aliases):
            return location

    ward_match = re.search(r"(ward|वार्ड|वॉर्ड)\s*[-:]?\s*(\d+)", lowered, re.IGNORECASE)
    if ward_match:
        return f"Ward {ward_match.group(2)}"

    sector_match = re.search(r"(sector|सेक्टर)\s*[-:]?\s*(\d+)", lowered, re.IGNORECASE)
    if sector_match:
        return f"Sector {sector_match.group(2)}"

    locality_match = re.search(
        r"(?:in|near|at|from|around|beside)\s+([A-Za-z][A-Za-z\s]{2,30})",
        transcript,
        re.IGNORECASE,
    )
    if locality_match:
        return locality_match.group(1).strip().title()

    return fallback_location


def _apply_voice_draft(transcript: str) -> None:
    cleaned_transcript = transcript.strip()
    if not cleaned_transcript:
        return

    if not str(st.session_state.get("issue_title_draft", "")).strip():
        st.session_state["issue_title_draft"] = _suggest_issue_title(cleaned_transcript)

    existing_description = str(st.session_state.get("issue_description_draft", "")).strip()
    if not existing_description:
        st.session_state["issue_description_draft"] = cleaned_transcript
    elif cleaned_transcript.lower() not in existing_description.lower():
        st.session_state["issue_description_draft"] = f"{existing_description}\n\nVoice note:\n{cleaned_transcript}"

    current_urgency = str(st.session_state.get("issue_urgency_draft", "Medium"))
    suggested_urgency = _suggest_urgency(cleaned_transcript)
    if current_urgency in {"", "Low", "Medium"} or suggested_urgency == "High":
        st.session_state["issue_urgency_draft"] = suggested_urgency

    fallback_location = str(
        st.session_state.get("issue_location_draft")
        or st.session_state.get("current_user", {}).get("location", "")
    ).strip()
    detected_location = _extract_location(cleaned_transcript, fallback_location)
    if detected_location:
        st.session_state["issue_location_draft"] = detected_location


def _sync_transcript_into_description(transcript: str) -> None:
    _apply_voice_draft(transcript)


def _transcribe_audio_upload(audio_file: Any, language_code: str) -> str:
    recognizer = sr.Recognizer()
    recognizer.dynamic_energy_threshold = True

    filename = getattr(audio_file, "name", "voice-note.wav")
    suffix = Path(filename).suffix.lower() or ".wav"
    supported_suffixes = {".wav", ".flac", ".aiff", ".aif", ".aifc"}
    if suffix not in supported_suffixes:
        raise ValueError("Please record with the built-in recorder or upload a WAV/FLAC audio file.")

    raw_bytes = audio_file.getvalue() if hasattr(audio_file, "getvalue") else audio_file.read()
    if not raw_bytes:
        raise ValueError("The selected audio file is empty.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_audio:
        temp_audio.write(raw_bytes)
        temp_path = temp_audio.name

    try:
        with sr.AudioFile(temp_path) as source:
            audio = recognizer.record(source)
        return recognizer.recognize_google(audio, language=language_code)
    finally:
        try:
            Path(temp_path).unlink(missing_ok=True)
        except OSError:
            pass


def render_voice_input() -> None:
    st.markdown("#### Voice Complaint")
    st.caption(
        "Record or upload a complaint in English or major Indian languages. "
        "Use the language selector so speech recognition matches the speaker."
    )
    language_label = st.selectbox(
        "Complaint Language",
        list(VOICE_LANGUAGE_OPTIONS.keys()),
        key="voice_language_label",
        help="Pick the language being spoken in the voice note for better transcription accuracy.",
    )
    language_code = VOICE_LANGUAGE_OPTIONS.get(language_label, "en-IN")
    st.caption(f"Recognition mode: `{language_label}` (`{language_code}`)")
    audio_file = st.audio_input("Record a complaint") if hasattr(st, "audio_input") else None
    if audio_file is None and not hasattr(st, "audio_input"):
        audio_file = st.file_uploader("Upload audio", type=["wav", "flac"], key="voice_upload")

    if audio_file is not None:
        audio_name = getattr(audio_file, "name", "Recorded voice note")
        st.caption(f"Selected audio: {audio_name}")

    if st.button("Transcribe Voice", disabled=audio_file is None):
        try:
            transcript = _transcribe_audio_upload(audio_file, language_code)
        except sr.UnknownValueError:
            st.session_state["voice_status"] = (
                f"No usable speech was detected for {language_label}. "
                "Try again with clearer audio or switch to the correct complaint language."
            )
            st.error("The audio was unclear. Please try again.")
        except sr.RequestError as exc:
            st.session_state["voice_status"] = "Speech recognition service could not be reached."
            st.error(f"Speech recognition service error: {exc}")
        except ValueError as exc:
            st.session_state["voice_status"] = str(exc)
            st.error(str(exc))
        except Exception as exc:
            st.session_state["voice_status"] = "Unexpected transcription error."
            st.error(f"Unexpected transcription error: {exc}")
        else:
            st.session_state["voice_transcript"] = transcript
            st.session_state["voice_status"] = (
                f"Voice complaint transcribed successfully in {language_label} and added to the issue description."
            )
            _sync_transcript_into_description(transcript)
            st.success("Voice complaint transcribed.")

    transcript = st.session_state.get("voice_transcript")
    if st.session_state.get("voice_status"):
        st.caption(st.session_state["voice_status"])
    if transcript:
        draft_cols = st.columns(3)
        with draft_cols[0]:
            st.caption(f"Suggested title: **{_suggest_issue_title(transcript)}**")
        with draft_cols[1]:
            st.caption(f"Suggested urgency: **{_suggest_urgency(transcript)}**")
        with draft_cols[2]:
            preview_location = _extract_location(
                transcript,
                str(st.session_state.get("issue_location_draft", "")).strip() or "Current account location",
            )
            st.caption(f"Suggested location: **{preview_location}**")
        st.text_area("Transcribed text", transcript, height=90, disabled=True)
        if st.button("Clear Voice Transcript"):
            st.session_state["voice_transcript"] = ""
            st.session_state["voice_status"] = ""
            st.rerun()


def render_issue_submission(user: dict[str, Any]) -> None:
    if st.session_state.get("reset_issue_form"):
        st.session_state["issue_title_draft"] = ""
        st.session_state["issue_description_draft"] = ""
        st.session_state["issue_location_draft"] = str(user.get("location", "")).strip()
        st.session_state["issue_urgency_draft"] = "Medium"
        st.session_state["voice_transcript"] = ""
        st.session_state["voice_status"] = ""
        st.session_state["reset_issue_form"] = False

    left, right = st.columns([1.15, 0.85])

    with left:
        st.markdown("### Submit a New Issue")
        st.caption("Record or type the complaint, review the drafted details, and submit it into the civic response pipeline.")
        st.info(
            "Voice mode can draft the title, description, location, and urgency automatically. "
            "You only need to review the details before submission."
        )
        if not str(st.session_state.get("issue_location_draft", "")).strip():
            st.session_state["issue_location_draft"] = str(user.get("location", "")).strip()
        render_voice_input()
        with st.form("citizen_issue_form"):
            title = st.text_input("Issue Title", key="issue_title_draft")
            description = st.text_area("Issue Description", key="issue_description_draft")
            location = st.text_input("Location", key="issue_location_draft")
            urgency = st.selectbox("Urgency", ["Low", "Medium", "High"], key="issue_urgency_draft")
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
                    st.session_state["reset_issue_form"] = True
                    st.success("Issue submitted successfully.")
                    st.rerun()

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
            st.caption("Priority is a decision-support score based on urgency, recurrence, and complaint context. It is not a final administrative order.")
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


def render_transparency_panel(user: dict[str, Any]) -> None:
    st.markdown("### Local Transparency")
    st.caption("See how complaints in your area are progressing, which department is responsible, and whether proof-of-work has been recorded.")
    try:
        transparency_payload = api_get("/citizen_transparency", {"location": user.get("location", "")})
    except requests.RequestException as exc:
        st.warning(f"Unable to load transparency data: {exc}")
        return

    transparency = transparency_payload if isinstance(transparency_payload, dict) else {}
    stats = transparency.get("stats", {})
    top = st.columns(4)
    summary_items = [
        ("Nearby Active", stats.get("nearby_active", 0)),
        ("Nearby Resolved", stats.get("nearby_resolved", 0)),
        ("Proof Records", stats.get("verification_proofs", 0)),
        ("Local Trust Score", stats.get("local_trust_score", 0)),
    ]
    for col, (label, value) in zip(top, summary_items):
        with col:
            st.metric(label, value)

    active_tab, resolved_tab, proof_tab = st.tabs(["Active Status", "Resolved with Proof", "Recent Proof Log"])

    with active_tab:
        active_reports = transparency.get("active_reports", [])
        if not active_reports:
            st.info("No active reports in your area right now.")
        else:
            for report in active_reports[:6]:
                st.markdown(
                    f"""
                    <div class="gm-card">
                        <div style="display:flex;justify-content:space-between;gap:12px;align-items:flex-start;">
                            <div>
                                <div style="font-weight:800;">#{report.get('id', 'N/A')} | {report.get('title', 'Untitled issue')}</div>
                                <div style="color:rgba(255,255,255,0.70);margin-top:4px;">{report.get('location', 'Unknown')}</div>
                            </div>
                            <div style="font-weight:800;color:#7dd3fc;">{report.get('stage', 'Intake')}</div>
                        </div>
                        <div style="margin-top:10px;"><strong>Assigned Department:</strong> {report.get('department', 'City Operations Desk')}</div>
                        <div style="margin-top:6px;"><strong>Officer:</strong> {report.get('officer', 'Pending')}</div>
                        <div style="margin-top:6px;"><strong>SLA Window:</strong> {report.get('sla_hours', 0)} hours</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    with resolved_tab:
        resolved_reports = transparency.get("resolved_reports", [])
        if not resolved_reports:
            st.info("No resolved reports in your area yet.")
        else:
            df = pd.DataFrame(resolved_reports)
            cols = [
                col for col in [
                    "id",
                    "title",
                    "location",
                    "department",
                    "stage",
                    "resolution_hours",
                ] if col in df.columns
            ]
            st.dataframe(df[cols], use_container_width=True, hide_index=True, height=320)

    with proof_tab:
        proof_rows = transparency.get("recent_proofs", [])
        if not proof_rows:
            st.info("No recent proof-of-work records available.")
        else:
            df = pd.DataFrame(proof_rows)
            cols = [
                col for col in [
                    "issue_id",
                    "title",
                    "action_taken",
                    "verified_by",
                    "verified_at",
                    "proof_available",
                ] if col in df.columns
            ]
            st.dataframe(df[cols], use_container_width=True, hide_index=True, height=320)


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
    tab_submit, tab_feed, tab_transparency = st.tabs(["Report Issue", "Track Reports", "Local Transparency"])
    st.markdown("</div>", unsafe_allow_html=True)

    with tab_submit:
        render_issue_submission(user)
    with tab_feed:
        render_issue_tables(user)
    with tab_transparency:
        render_transparency_panel(user)


if __name__ == "__main__":
    main()
