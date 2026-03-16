import streamlit as st


def configure_page() -> None:
    st.set_page_config(page_title="Governance Memory AI", layout="wide")
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(56,189,248,0.18), transparent 24%),
                radial-gradient(circle at top right, rgba(96,165,250,0.12), transparent 22%),
                linear-gradient(180deg, #09111f 0%, #0f172a 48%, #0b1220 100%);
        }
        .hero {
            border: 1px solid rgba(255,255,255,0.10);
            border-radius: 30px;
            padding: 28px 30px;
            background:
                radial-gradient(circle at top right, rgba(14,165,233,0.28), transparent 24%),
                linear-gradient(135deg, rgba(37,99,235,0.18), rgba(15,23,42,0.10));
            box-shadow: 0 28px 70px rgba(0,0,0,0.30);
            position: relative;
            overflow: hidden;
        }
        .feature {
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 22px;
            padding: 18px;
            background: rgba(255,255,255,0.025);
            min-height: 180px;
            position: relative;
            overflow: hidden;
        }
        .hero::before,
        .feature::before {
            content: "";
            position: absolute;
            top: -120%;
            left: -35%;
            width: 42%;
            height: 340%;
            background: linear-gradient(
                90deg,
                rgba(255,255,255,0) 0%,
                rgba(125,211,252,0.00) 24%,
                rgba(191,219,254,0.18) 50%,
                rgba(34,211,238,0.09) 68%,
                rgba(255,255,255,0) 100%
            );
            transform: rotate(18deg) translateX(-180%);
            transition: transform 720ms ease;
            pointer-events: none;
        }
        .hero:hover::before,
        .feature:hover::before {
            transform: rotate(18deg) translateX(430%);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero() -> None:
    st.markdown(
        """
        <div class="hero">
            <div style="font-size:0.82rem;text-transform:uppercase;letter-spacing:0.08em;color:rgba(255,255,255,0.58);">
                Governance Intelligence Platform
            </div>
            <h1 style="margin:0.45rem 0 0.35rem 0;font-size:3rem;">Governance Memory AI</h1>
            <p style="max-width:860px;font-size:1.08rem;color:rgba(255,255,255,0.78);margin:0;">
                An AI-assisted governance command system that turns citizen complaints into
                clustered signals, crisis detection, coordinated response plans, and verified action history.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_demo_flow() -> None:
    st.markdown("### Demo Flow")
    cols = st.columns(5)
    steps = [
        ("1. Citizen Intake", "Residents submit complaints with text, voice, and image evidence."),
        ("2. AI Triage", "The platform prioritizes, clusters, and interprets emerging complaint pressure."),
        ("3. War Room", "Specialized AI agents build a coordinated response plan for the most urgent cluster."),
        ("4. Action + Memory", "Admins review policy guidance, historical matches, and public communication support."),
        ("5. Verified Closure", "Field action is logged with proof-of-work and preserved in resolved history."),
    ]
    for col, (title, text) in zip(cols, steps):
        with col:
            st.markdown(f"**{title}**")
            st.caption(text)


def render_value_props() -> None:
    st.markdown("### Why This Stands Out")
    cols = st.columns(3)
    cards = [
        ("Decision Intelligence", "Complaint clustering, crisis alerts, governance memory, and multi-agent response in one operational loop."),
        ("Public Accountability", "Tracks issues from citizen intake to verified field action and resolved history."),
        ("Hackathon Demo Ready", "Role-based navigation, deliberate storytelling, and a clear command-center showcase for judges."),
    ]
    for col, (title, text) in zip(cols, cards):
        with col:
            st.markdown(
                f"""
                <div class="feature">
                    <div style="font-size:1.1rem;font-weight:800;margin-bottom:10px;">{title}</div>
                    <div style="color:rgba(255,255,255,0.76);line-height:1.6;">{text}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_portal_guide() -> None:
    st.markdown("### Recommended Demo Path")
    left, right = st.columns([1, 1])
    with left:
        st.markdown(
            """
            - Start in `Home` to frame the problem and workflow
            - Move to `Citizen Portal` to submit or review complaints
            - Finish in `Admin Dashboard` for command-center analysis and War Room response
            """
        )
    with right:
        st.markdown(
            """
            - Demo admin: `admin@govai.demo`
            - Password: `admin123`
            - Citizens can create their own accounts directly in the portal
            """
        )


def main() -> None:
    configure_page()
    render_hero()
    st.divider()
    render_demo_flow()
    st.divider()
    render_value_props()
    st.divider()
    render_portal_guide()


if __name__ == "__main__":
    main()
