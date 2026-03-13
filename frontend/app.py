import streamlit as st
import pandas as pd
import requests


API_BASE = "http://127.0.0.1:8000"


def fetch_trust_score(api_base: str = API_BASE) -> tuple[int | None, int | None, str | None]:
    """
    Fetch the current trust score from the backend.

    Returns: (trust_score, total_issues, error_message)
    """

    try:
        resp = requests.get(f"{api_base}/trust_score", timeout=5)
        resp.raise_for_status()
        payload = resp.json()
        return int(payload.get("trust_score")), int(payload.get("total_issues")), None
    except Exception as exc:  # keep UI resilient in early prototype
        return None, None, str(exc)


def trust_indicator(trust_score: int) -> tuple[str, str]:
    """
    Return (color, label) for a trust score threshold.
    """

    if trust_score > 80:
        return "#16a34a", "High"
    if trust_score >= 50:
        return "#ca8a04", "Moderate"
    return "#dc2626", "Low"


def configure_page() -> None:
    st.set_page_config(
        page_title="Governance Memory AI",
        layout="wide",
    )


def render_header() -> None:
    st.title("Governance Memory AI")
    st.subheader("AI Platform for Local Governance Intelligence")
    st.markdown("---")


def render_public_trust_analytics(trust_score: int | None, total_issues: int | None, error: str | None) -> None:
    st.markdown("### Public Trust Analytics")

    if error or trust_score is None or total_issues is None:
        st.warning(f"Unable to load trust analytics from backend: {error or 'unknown error'}")
        st.markdown("---")
        return

    color, label = trust_indicator(trust_score)

    col_score, col_total, col_indicator = st.columns([1, 1, 1])
    with col_score:
        st.metric(label="Trust Score", value=str(trust_score))
    with col_total:
        st.metric(label="Total Issues", value=str(total_issues))
    with col_indicator:
        st.markdown("**Indicator**")
        st.markdown(
            f"<div style='display:flex;align-items:center;gap:8px;'>"
            f"<span style='width:10px;height:10px;border-radius:999px;background:{color};display:inline-block;'></span>"
            f"<span style='font-weight:600;color:{color};'>{label}</span>"
            f"</div>",
            unsafe_allow_html=True,
        )

    st.progress(trust_score / 100.0)
    st.markdown("---")


def render_overview_metrics(public_trust_score: int | None) -> None:
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
        st.metric(label="Public Trust Score", value=str(public_trust_score) if public_trust_score is not None else "N/A")

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

    api_base = API_BASE

    if "memory_suggestions" not in st.session_state:
        st.session_state["memory_suggestions"] = []

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
                try:
                    suggestions_response = requests.post(
                        f"{api_base}/memory_suggestions",
                        json={"issue_description": description},
                        timeout=10,
                    )
                    suggestions_response.raise_for_status()
                    st.session_state["memory_suggestions"] = suggestions_response.json().get("results", [])[:3]
                except requests.RequestException as exc:
                    st.session_state["memory_suggestions"] = []
                    st.warning(f"Unable to fetch governance memory insights: {exc}")

    suggestions = st.session_state.get("memory_suggestions") or []
    if suggestions:
        st.markdown("#### Governance Memory Insights")
        st.caption("Similar past cases based on semantic similarity (prototype).")

        for idx, suggestion in enumerate(suggestions, start=1):
            st.markdown(
                f"**Suggestion {idx}**\n\n"
                f"- **Past Issue Title**: {suggestion.get('issue_title', 'N/A')}\n"
                f"- **Action Taken**: {suggestion.get('action_taken', 'N/A')}\n"
                f"- **Outcome**: {suggestion.get('outcome', 'N/A')}"
            )
            st.divider()

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


def render_ai_communication_generator() -> None:
    st.markdown("### AI Communication Generator")
    st.caption("Generate a public-facing update for a submitted issue.")

    try:
        issues_response = requests.get(f"{API_BASE}/issues", timeout=5)
        issues_response.raise_for_status()
        issues = issues_response.json()
    except requests.RequestException as exc:
        st.warning(f"Unable to load issues from backend: {exc}")
        return

    if not issues:
        st.info("Submit an issue first to generate a public update.")
        return

    def issue_label(issue: dict) -> str:
        issue_id = issue.get("id", "N/A")
        title = issue.get("title", "Untitled")
        location = issue.get("location", "N/A")
        urgency = issue.get("urgency", "N/A")
        return f"#{issue_id} • {title} • {location} • {urgency}"

    selected = st.selectbox(
        "Select an issue",
        options=issues,
        format_func=issue_label,
    )

    if st.button("Generate Public Update", type="primary"):
        try:
            resp = requests.post(f"{API_BASE}/generate_update", json=selected, timeout=10)
            resp.raise_for_status()
            update_text = resp.json().get("generated_update", "")
        except requests.RequestException as exc:
            st.error(f"Failed to generate public update: {exc}")
            return

        if not update_text:
            st.warning("No update text returned by the backend.")
            return

        st.markdown("#### Generated Public Update")
        st.markdown(
            f"""
            <div style="
                padding: 14px 16px;
                border: 1px solid rgba(120,120,120,0.35);
                border-radius: 10px;
                background: rgba(240,240,240,0.35);
                line-height: 1.55;
                white-space: pre-wrap;
            ">{update_text}</div>
            """,
            unsafe_allow_html=True,
        )


def render_work_verification() -> None:
    st.markdown("### Work Verification")
    st.caption("Upload proof-of-work for a selected issue (prototype).")

    try:
        issues_response = requests.get(f"{API_BASE}/issues", timeout=5)
        issues_response.raise_for_status()
        issues = issues_response.json()
    except requests.RequestException as exc:
        st.warning(f"Unable to load issues from backend: {exc}")
        issues = []

    if issues:
        def issue_label(issue: dict) -> str:
            issue_id = issue.get("id", "N/A")
            title = issue.get("title", "Untitled")
            location = issue.get("location", "N/A")
            return f"#{issue_id} • {title} • {location}"

        with st.form("work_verification_form"):
            selected_issue = st.selectbox(
                "Select issue",
                options=issues,
                format_func=issue_label,
            )
            location = st.text_input("Location")
            image_file = st.file_uploader("Upload verification image", type=["png", "jpg", "jpeg", "webp"])

            submitted = st.form_submit_button("Submit Verification")
            if submitted:
                if image_file is None:
                    st.error("Please upload an image to submit verification.")
                else:
                    data = {
                        "issue_id": str(selected_issue.get("id")),
                        "location": location,
                    }
                    files = {
                        "image": (image_file.name, image_file.getvalue(), image_file.type or "application/octet-stream"),
                    }
                    try:
                        resp = requests.post(f"{API_BASE}/verify_work", data=data, files=files, timeout=20)
                        resp.raise_for_status()
                    except requests.RequestException as exc:
                        st.error(f"Failed to submit verification: {exc}")
                    else:
                        st.success("Verification submitted successfully.")
    else:
        st.info("Submit an issue first to upload a work verification.")

    st.markdown("#### Verification Records")

    try:
        resp = requests.get(f"{API_BASE}/verifications", timeout=5)
        resp.raise_for_status()
        records = (resp.json() or {}).get("verifications", [])
    except requests.RequestException as exc:
        st.warning(f"Unable to load verification records: {exc}")
        records = []

    if records:
        df = pd.DataFrame(records)
        rename_map = {
            "issue_id": "Issue ID",
            "location": "Location",
            "timestamp": "Timestamp",
            "image_filename": "Image filename",
        }
        df = df.rename(columns=rename_map)
        display_cols = ["Issue ID", "Location", "Timestamp", "Image filename"]
        existing_cols = [c for c in display_cols if c in df.columns]
        st.dataframe(df[existing_cols], use_container_width=True)
    else:
        st.info("No verification records yet.")


def main() -> None:
    configure_page()
    render_header()

    trust_score, total_issues, trust_error = fetch_trust_score()
    render_public_trust_analytics(trust_score, total_issues, trust_error)
    render_overview_metrics(trust_score)

    render_platform_modules()
    st.markdown("---")
    render_citizen_issue_intake()
    st.markdown("---")
    render_ai_communication_generator()
    st.markdown("---")
    render_work_verification()


if __name__ == "__main__":
    main()

