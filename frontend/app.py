import streamlit as st


def configure_page() -> None:
    st.set_page_config(
        page_title="Governance Memory AI",
        layout="wide",
    )


def render_header() -> None:
    st.title("Governance Memory AI")
    st.subheader("AI Platform for Local Governance Intelligence")
    st.markdown("---")


def render_overview_metrics() -> None:
    st.markdown("### Overview")

    col_open, col_resolved, col_trust = st.columns(3)

    # NOTE: Static placeholder values for the initial skeleton.
    # These will be wired to backend analytics and governance memory
    # metrics in later iterations.
    with col_open:
        st.metric(label="Open Issues", value="0")

    with col_resolved:
        st.metric(label="Resolved Issues", value="0")

    with col_trust:
        st.metric(label="Public Trust Score", value="N/A")

    st.markdown("---")


def render_platform_modules() -> None:
    st.markdown("### Platform Modules")

    # Simple bullet list for now; this can evolve into
    # cards, tabs, or navigable sections as functionality grows.
    st.markdown(
        """
        - **Citizen Issue Intake**
        - **AI Issue Prioritization**
        - **Governance Memory**
        - **Work Verification**
        - **Social Sentiment Monitoring**
        - **Communication Generator**
        """
    )


def main() -> None:
    configure_page()
    render_header()
    render_overview_metrics()
    render_platform_modules()


if __name__ == "__main__":
    main()

