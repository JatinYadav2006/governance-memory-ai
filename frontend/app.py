import requests
import streamlit as st

import admin_dashboard
import public_portal


API_BASE = "http://127.0.0.1:8000"
DEMO_ADMIN_EMAIL = "admin@govai.demo"
DEMO_ADMIN_PASSWORD = "GovAI_Admin#2026!"


def init_state() -> None:
    st.session_state.setdefault("current_user", None)
    st.session_state.setdefault("admin_user", None)
    st.session_state["use_unified_access"] = True


def api_post(path: str, payload: dict) -> dict:
    response = requests.post(f"{API_BASE}{path}", json=payload, timeout=20)
    response.raise_for_status()
    return response.json() or {}


def apply_shell_style() -> None:
    st.set_page_config(
        page_title="Governance Memory AI",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"],
        [data-testid="stSidebarCollapsedControl"] {
            display: none;
        }
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(37,99,235,0.20), transparent 22%),
                radial-gradient(circle at top right, rgba(34,197,94,0.10), transparent 18%),
                linear-gradient(180deg, #0a1020 0%, #101827 48%, #0b1220 100%);
        }
        .access-hero,
        .access-card {
            position: relative;
            overflow: hidden;
        }
        .access-hero {
            border: 1px solid rgba(255,255,255,0.10);
            border-radius: 28px;
            padding: 30px 32px;
            background:
                linear-gradient(135deg, rgba(37,99,235,0.22), rgba(15,23,42,0.16)),
                linear-gradient(180deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02));
            box-shadow: 0 26px 60px rgba(0,0,0,0.26);
        }
        .access-card {
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 22px;
            padding: 22px 22px 18px 22px;
            background: linear-gradient(180deg, rgba(255,255,255,0.045), rgba(255,255,255,0.02));
            box-shadow: 0 18px 42px rgba(0,0,0,0.18);
            min-height: 100%;
        }
        .access-hero::before,
        .access-card::before {
            content: "";
            position: absolute;
            top: -120%;
            left: -35%;
            width: 42%;
            height: 340%;
            background: linear-gradient(
                90deg,
                rgba(255,255,255,0) 0%,
                rgba(125,211,252,0.00) 25%,
                rgba(186,230,253,0.18) 50%,
                rgba(96,165,250,0.10) 65%,
                rgba(255,255,255,0) 100%
            );
            transform: rotate(18deg) translateX(-180%);
            transition: transform 700ms ease;
            pointer-events: none;
        }
        .access-hero:hover::before,
        .access-card:hover::before {
            transform: rotate(18deg) translateX(430%);
        }
        .access-mini {
            font-size: 0.82rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: rgba(255,255,255,0.58);
            margin-bottom: 12px;
        }
        .access-caption {
            color: rgba(255,255,255,0.70);
            line-height: 1.6;
            margin-top: 8px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def reset_citizen_view() -> None:
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


def reset_admin_view() -> None:
    st.session_state["admin_user"] = None
    st.session_state["generated_update"] = ""
    st.session_state["selected_war_room_cluster"] = None
    st.session_state["admin_dashboard_bundle"] = None


def render_access_shell() -> None:
    st.markdown(
        """
        <div class="access-hero">
            <div class="access-mini">Unified Access</div>
            <h1 style="margin:0 0 0.4rem 0;">Governance Memory AI</h1>
            <p style="margin:0;max-width:820px;font-size:1.02rem;color:rgba(255,255,255,0.78);">
                Sign in once and move directly into the right workspace. Citizen accounts open the
                complaint portal, while admin credentials open the command center.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("")
    mode = st.radio(
        "Access mode",
        ["Login", "Create Account"],
        horizontal=True,
        label_visibility="collapsed",
        key="unified_access_mode",
    )

    if mode == "Login":
        login_col, info_col = st.columns([1.25, 0.95], gap="large")
        with login_col:
            st.markdown('<div class="access-card">', unsafe_allow_html=True)
            st.markdown('<div class="access-mini">Login</div>', unsafe_allow_html=True)
            email = st.text_input("Email", value="", key="unified_login_email", placeholder="Enter citizen or admin email")
            password = st.text_input("Password", type="password", key="unified_login_password")
            if st.button("Continue", type="primary", use_container_width=True, key="unified_login_submit"):
                try:
                    user = api_post("/auth/admin_login", {"email": email, "password": password})
                except requests.HTTPError:
                    try:
                        user = api_post("/auth/login", {"email": email, "password": password})
                    except requests.HTTPError as exc:
                        detail = exc.response.text if exc.response is not None else str(exc)
                        st.error(f"Login failed: {detail}")
                    except requests.RequestException as exc:
                        st.error(f"Login failed: {exc}")
                    else:
                        reset_admin_view()
                        st.session_state["current_user"] = user
                        st.rerun()
                except requests.RequestException as exc:
                    st.error(f"Login failed: {exc}")
                else:
                    reset_citizen_view()
                    st.session_state["admin_user"] = user
                    st.session_state["admin_dashboard_bundle"] = None
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        with info_col:
            st.markdown('<div class="access-card">', unsafe_allow_html=True)
            st.markdown('<div class="access-mini">Access Routing</div>', unsafe_allow_html=True)
            st.markdown(
                """
                <div class="access-caption">
                    Use one login form for both roles.
                    If the credentials belong to an admin account, the app opens the command center.
                    If they belong to a citizen account, the app opens the citizen portal.
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown(
                f"""
                <div style="margin-top:18px;padding:14px 16px;border:1px solid rgba(255,255,255,0.08);border-radius:16px;background:rgba(255,255,255,0.025);">
                    <div class="access-mini" style="margin-bottom:10px;">Admin Demo Access</div>
                    <div style="font-weight:700;">{DEMO_ADMIN_EMAIL}</div>
                    <div style="margin-top:6px;font-weight:700;">{DEMO_ADMIN_PASSWORD}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)

    else:
        signup_col, info_col = st.columns([1.25, 0.95], gap="large")
        with signup_col:
            st.markdown('<div class="access-card">', unsafe_allow_html=True)
            st.markdown('<div class="access-mini">Create Account</div>', unsafe_allow_html=True)
            name = st.text_input("Full Name", key="citizen_signup_name")
            sign_email = st.text_input("Email", key="citizen_signup_email")
            phone = st.text_input("Phone", key="citizen_signup_phone")
            location = st.text_input("Location", key="citizen_signup_location")
            password = st.text_input("Password", type="password", key="citizen_signup_password")
            if st.button("Create Account", type="primary", use_container_width=True, key="citizen_signup_submit"):
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
                    st.error(f"Account creation failed: {detail}")
                except requests.RequestException as exc:
                    st.error(f"Account creation failed: {exc}")
                else:
                    reset_admin_view()
                    st.session_state["current_user"] = user
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        with info_col:
            st.markdown('<div class="access-card">', unsafe_allow_html=True)
            st.markdown('<div class="access-mini">New Citizen Account</div>', unsafe_allow_html=True)
            st.markdown(
                """
                <div class="access-caption">
                    Create a citizen account once and the app will take you directly into complaint reporting,
                    issue tracking, and local transparency after sign-up is complete.
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)


def main() -> None:
    init_state()
    apply_shell_style()
    if st.session_state.get("admin_user") is not None:
        admin_dashboard.main()
        return
    if st.session_state.get("current_user") is not None:
        public_portal.main()
        return
    render_access_shell()


if __name__ == "__main__":
    main()
