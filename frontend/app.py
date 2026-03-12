import streamlit as st
import pandas as pd
import requests


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


def render_citizen_issue_intake() -> None:
    st.markdown("### Citizen Issue Intake")

    api_base = "http://127.0.0.1:8000"

    with st.form("issue_intake_form"):
        title = st.text_input("Title")
        description = st.text_area("Description")
        location = st.text_input("Location")
        urgency = st.selectbox("Urgency", ["Low", "Medium", "High"])

        submitted = st.form_submit_button("Submit Issue")

        if submitted:
            payload = {
                "title": title,
                "description": description,
                "location": location,
                "urgency": urgency,
            }
            try:
                response = requests.post(f"{api_base}/submit_issue", json=payload, timeout=5)
                response.raise_for_status()
            except requests.RequestException as exc:
                st.error(f"Failed to submit issue: {exc}")
            else:
                st.success("Issue submitted successfully.")

    st.markdown("#### Top Priority Issues")

    try:
        issues_response = requests.get(f"{api_base}/issues", timeout=5)
        issues_response.raise_for_status()
        issues = issues_response.json()
    except requests.RequestException as exc:
        st.warning(f"Unable to load issues from backend: {exc}")
        issues = []

    if issues:
        df = pd.DataFrame(issues)

        # Ensure sorting by priority_score (backend already sorts, but keep
        # this here in case the implementation changes).
        if "priority_score" in df.columns:
            df = df.sort_values("priority_score", ascending=False)

        # Display top 3 issues with highest priority.
        top_n = df.head(3)
        if not top_n.empty:
            for _, row in top_n.iterrows():
                st.markdown(
                    f"- **#{int(row.get('id', 0))} - {row.get('title', '')}**  "
                    f"(Location: {row.get('location', 'N/A')}, "
                    f"Urgency: {row.get('urgency', 'N/A')}, "
                    f"Priority: {row.get('priority_score', 'N/A')})"
                )
        else:
            st.info("No issues available to rank.")

        st.markdown("#### Submitted Issues")

        # Restrict columns to the key fields we care about.
        display_columns = ["id", "title", "location", "urgency", "priority_score"]
        existing_columns = [c for c in display_columns if c in df.columns]
        st.dataframe(df[existing_columns], use_container_width=True)
    else:
        st.info("No issues have been submitted yet.")


def main() -> None:
    configure_page()
    render_header()
    render_overview_metrics()
    render_platform_modules()
    st.markdown("---")
    render_citizen_issue_intake()


if __name__ == "__main__":
    main()

