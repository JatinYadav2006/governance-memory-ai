import streamlit as st

import admin_dashboard
import homepage
import public_portal


PAGES = {
    "Home": {
        "label": "01  Home",
        "subtitle": "Product story and demo framing",
        "render": homepage.main,
    },
    "Citizen Portal": {
        "label": "02  Citizen Portal",
        "subtitle": "Complaint intake and public reporting",
        "render": public_portal.main,
    },
    "Admin Dashboard": {
        "label": "03  Admin Dashboard",
        "subtitle": "AI operations and command center",
        "render": admin_dashboard.main,
    },
}


def apply_shell_style() -> None:
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] {
            background:
                radial-gradient(circle at top left, rgba(56,189,248,0.16), transparent 24%),
                linear-gradient(180deg, #09111f 0%, #0f172a 46%, #0b1220 100%);
            border-right: 1px solid rgba(255,255,255,0.08);
        }
        [data-testid="stSidebar"] .block-container {
            padding-top: 1.35rem;
            padding-bottom: 1.2rem;
        }
        .nav-shell {
            display: flex;
            flex-direction: column;
            gap: 14px;
        }
        .nav-brand {
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 22px;
            padding: 18px 18px 16px 18px;
            background: linear-gradient(180deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02));
            box-shadow: 0 18px 40px rgba(0,0,0,0.18);
            position: relative;
            overflow: hidden;
        }
        .nav-brand-title {
            font-size: 1.65rem;
            font-weight: 800;
            line-height: 1.15;
            margin-bottom: 10px;
        }
        .nav-brand-meta {
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: rgba(255,255,255,0.55);
            margin-bottom: 12px;
        }
        .nav-credentials {
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 20px;
            padding: 16px 16px 14px 16px;
            background: linear-gradient(180deg, rgba(255,255,255,0.045), rgba(255,255,255,0.018));
            position: relative;
            overflow: hidden;
        }
        .nav-brand::before,
        .nav-credentials::before,
        div[role="radiogroup"] > label::before {
            content: "";
            position: absolute;
            top: -120%;
            left: -38%;
            width: 46%;
            height: 340%;
            background: linear-gradient(
                90deg,
                rgba(255,255,255,0) 0%,
                rgba(125,211,252,0.00) 24%,
                rgba(191,219,254,0.16) 50%,
                rgba(96,165,250,0.09) 68%,
                rgba(255,255,255,0) 100%
            );
            transform: rotate(18deg) translateX(-180%);
            transition: transform 680ms ease;
            pointer-events: none;
        }
        .nav-brand:hover::before,
        .nav-credentials:hover::before,
        div[role="radiogroup"] > label:hover::before {
            transform: rotate(18deg) translateX(420%);
        }
        .nav-cred-row {
            display: flex;
            justify-content: space-between;
            gap: 12px;
            margin-bottom: 8px;
            font-size: 0.92rem;
        }
        .nav-cred-label {
            color: rgba(255,255,255,0.56);
            text-transform: uppercase;
            letter-spacing: 0.08em;
            font-size: 0.72rem;
        }
        div[role="radiogroup"] > label {
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 18px;
            background: rgba(255,255,255,0.025);
            margin-bottom: 10px;
            padding: 6px 8px 6px 6px;
            transition: all 160ms ease;
            position: relative;
            overflow: hidden;
        }
        div[role="radiogroup"] > label:hover {
            border-color: rgba(56,189,248,0.30);
            background: rgba(56,189,248,0.06);
        }
        div[role="radiogroup"] > label[data-selected="true"] {
            border-color: rgba(56,189,248,0.55);
            background: linear-gradient(90deg, rgba(56,189,248,0.14), rgba(255,255,255,0.02));
            box-shadow: inset 0 0 0 1px rgba(56,189,248,0.12);
        }
        div[role="radiogroup"] > label > div:first-child {
            display: none;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def format_nav_option(option: str) -> str:
    item = PAGES[option]
    return item["label"]


def render_sidebar() -> str:
    with st.sidebar:
        st.markdown(
            """
            <div class="nav-shell">
                <div class="nav-brand">
                    <div class="nav-brand-meta">Hackathon Demo Navigation</div>
                    <div class="nav-brand-title">Governance Memory AI</div>
                    <div style="color:rgba(255,255,255,0.70);line-height:1.55;">
                        Move from the product story to citizen intake and then into the AI-driven
                        command center without losing the demo narrative.
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        page = st.radio(
            "Choose view",
            list(PAGES.keys()),
            format_func=format_nav_option,
            label_visibility="visible",
        )
        st.caption(PAGES[page]["subtitle"])
        st.caption("Suggested order: `Home -> Citizen Portal -> Admin Dashboard`")
        st.markdown(
            """
            <div class="nav-credentials">
                <div class="nav-brand-meta" style="margin-bottom:14px;">Command Access</div>
                <div class="nav-cred-row">
                    <div class="nav-cred-label">Admin Email</div>
                    <div style="font-weight:700;">admin@govai.demo</div>
                </div>
                <div class="nav-cred-row" style="margin-bottom:0;">
                    <div class="nav-cred-label">Password</div>
                    <div style="font-weight:700;">admin123</div>
                </div>
                <div style="margin-top:14px;color:rgba(255,255,255,0.62);line-height:1.55;font-size:0.88rem;">
                    Citizens create their own accounts directly from the portal.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    return page


def main() -> None:
    apply_shell_style()
    selected_page = render_sidebar()
    PAGES[selected_page]["render"]()


if __name__ == "__main__":
    main()
