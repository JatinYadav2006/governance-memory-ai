import pandas as pd
import plotly.express as px
import requests
import streamlit as st


API_BASE = "http://127.0.0.1:8000"
DEMO_ADMIN_EMAIL = "admin@govai.demo"
DEMO_ADMIN_PASSWORD = "admin123"


def init_state() -> None:
    st.session_state.setdefault("admin_user", None)
    st.session_state.setdefault("generated_update", "")


def api_get(path: str) -> dict | list:
    response = requests.get(f"{API_BASE}{path}", timeout=15)
    response.raise_for_status()
    return response.json()


def api_post(path: str, json: dict) -> dict:
    response = requests.post(f"{API_BASE}{path}", json=json, timeout=15)
    response.raise_for_status()
    return response.json() or {}


def apply_page_style() -> None:
    st.set_page_config(page_title="Admin Dashboard - Governance Memory AI", layout="wide")
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(30,64,175,0.22), transparent 28%),
                radial-gradient(circle at top right, rgba(22,163,74,0.14), transparent 24%),
                linear-gradient(180deg, #0b1020 0%, #111827 48%, #0b1220 100%);
        }
        .gm-panel {
            border: 1px solid rgba(255,255,255,0.09);
            border-radius: 22px;
            padding: 18px 20px;
            background: linear-gradient(180deg, rgba(255,255,255,0.05), rgba(255,255,255,0.025));
            box-shadow: 0 18px 50px rgba(0,0,0,0.20);
            position: relative;
            overflow: hidden;
        }
        .gm-hero {
            border: 1px solid rgba(255,255,255,0.10);
            border-radius: 28px;
            padding: 26px 28px;
            background:
                linear-gradient(135deg, rgba(37,99,235,0.22), rgba(15,23,42,0.15)),
                linear-gradient(180deg, rgba(255,255,255,0.05), rgba(255,255,255,0.025));
            box-shadow: 0 24px 60px rgba(0,0,0,0.28);
            position: relative;
            overflow: hidden;
        }
        .gm-metric {
            border: 1px solid rgba(255,255,255,0.10);
            border-radius: 20px;
            padding: 18px;
            min-height: 140px;
            background: linear-gradient(180deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02));
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
        .gm-panel::before,
        .gm-hero::before,
        .gm-metric::before,
        .gm-card::before {
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
        .gm-panel:hover::before,
        .gm-hero:hover::before,
        .gm-metric:hover::before,
        .gm-card:hover::before {
            transform: rotate(18deg) translateX(430%);
        }
        .gm-section-title {
            font-size: 1.35rem;
            font-weight: 800;
            margin-bottom: 0.35rem;
        }
        .gm-section-subtitle {
            color: rgba(255,255,255,0.60);
            margin-bottom: 1rem;
            max-width: 640px;
        }
        .gm-alert-empty {
            border: 1px dashed rgba(96,165,250,0.30);
            border-radius: 18px;
            padding: 18px;
            background: rgba(59,130,246,0.08);
            color: rgba(191,219,254,0.95);
        }
        .gm-mini {
            font-size: 0.82rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: rgba(255,255,255,0.58);
        }
        .gm-big {
            font-size: 2.4rem;
            line-height: 1;
            font-weight: 800;
            margin-top: 10px;
            margin-bottom: 14px;
        }
        .gm-tabs [data-baseweb="tab-list"] {
            gap: 10px;
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


def render_header() -> None:
    st.markdown(
        """
        <div class="gm-hero">
            <div class="gm-mini">Governance Command Center</div>
            <h1 style="margin:0.35rem 0 0.25rem 0;">Admin Dashboard</h1>
            <p style="margin:0;max-width:760px;font-size:1.05rem;color:rgba(255,255,255,0.78);">
                Monitor public trust, detect pressure zones early, and move from complaint intake
                to verified action with a cleaner command-center workflow.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("Demo admin credentials: `admin@govai.demo` / `admin123`")


def render_login() -> dict | None:
    user = st.session_state.get("admin_user")
    if user is not None:
        cols = st.columns([4, 1])
        with cols[0]:
            st.markdown(
                f"**Logged in as:** {user.get('name')} | {user.get('email')} | role: {user.get('role', 'admin')}"
            )
        with cols[1]:
            if st.button("Logout", use_container_width=True):
                st.session_state["admin_user"] = None
                st.session_state["generated_update"] = ""
                st.rerun()
        return user

    st.markdown("### Admin Access")
    col1, col2, col3 = st.columns([1.2, 1.2, 0.8])
    with col1:
        email = st.text_input("Admin Email", value=DEMO_ADMIN_EMAIL)
    with col2:
        password = st.text_input("Admin Password", type="password", value=DEMO_ADMIN_PASSWORD)
    with col3:
        st.write("")
        st.write("")
        if st.button("Login", type="primary", use_container_width=True):
            try:
                user = api_post("/auth/admin_login", {"email": email, "password": password})
            except requests.HTTPError as exc:
                detail = exc.response.text if exc.response is not None else str(exc)
                st.error(f"Admin login failed: {detail}")
            except requests.RequestException as exc:
                st.error(f"Admin login failed: {exc}")
            else:
                st.session_state["admin_user"] = user
                st.success("Admin access granted.")
                st.rerun()
    return None


def fetch_crisis_alerts() -> list[dict]:
    alerts_payload = api_get("/crisis_alerts")
    return alerts_payload if isinstance(alerts_payload, list) else []


def render_metric_strip(
    issues: list[dict],
    analytics: dict,
    trust: dict,
    clusters: list[dict],
    alerts: list[dict],
) -> None:
    cards = [
        ("Total Issues", str(analytics.get("total_issues", len(issues))), "[]", "#38bdf8"),
        ("Active Clusters", str(len(clusters)), "{}", "#818cf8"),
        ("Crisis Alerts", str(len(alerts)), "!!", "#f87171"),
        ("Public Trust Score", str(trust.get("trust_score", "N/A")), "::", "#4ade80"),
    ]
    cols = st.columns(4)
    for col, (label, value, icon, accent) in zip(cols, cards):
        with col:
            st.markdown(
                f"""
                <div class="gm-metric">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <div class="gm-mini">{label}</div>
                        <div style="font-weight:800;color:{accent};">{icon}</div>
                    </div>
                    <div class="gm-big">{value}</div>
                    <div style="height:8px;border-radius:999px;background:rgba(255,255,255,0.06);overflow:hidden;">
                        <div style="width:68%;height:100%;background:{accent};opacity:0.9;"></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_charts(analytics: dict, trends: dict) -> None:
    st.markdown('<div class="gm-section-title">Situation Overview</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="gm-section-subtitle">Track where complaints are concentrating, how urgency is distributed, and which topics are emerging fastest.</div>',
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1.05, 0.95, 0.9])
    by_category = analytics.get("by_category", {})
    by_urgency = analytics.get("by_urgency", {})
    trend_items = trends.get("trends", {})

    with col1:
        st.markdown('<div class="gm-panel">', unsafe_allow_html=True)
        st.markdown("#### Issue Categories")
        if by_category:
            df = pd.DataFrame({"Category": list(by_category.keys()), "Count": list(by_category.values())})
            chart = px.bar(
                df,
                x="Category",
                y="Count",
                color="Category",
                text="Count",
                color_discrete_sequence=["#38bdf8", "#4ade80", "#f59e0b", "#f87171", "#a78bfa", "#22c55e"],
            )
            chart.update_layout(showlegend=False, margin=dict(l=10, r=10, t=10, b=10), height=300)
            chart.update_traces(textposition="outside")
            st.plotly_chart(chart, use_container_width=True)
        else:
            st.info("No category data yet.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="gm-panel">', unsafe_allow_html=True)
        st.markdown("#### Pressure Signals")
        if by_urgency:
            df = pd.DataFrame({"Urgency": list(by_urgency.keys()), "Count": list(by_urgency.values())})
            chart = px.pie(
                df,
                names="Urgency",
                values="Count",
                color="Urgency",
                color_discrete_map={"High": "#f87171", "Medium": "#f59e0b", "Low": "#4ade80"},
            )
            chart.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=300)
            st.plotly_chart(chart, use_container_width=True)
        else:
            st.info("No urgency data yet.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="gm-panel">', unsafe_allow_html=True)
        st.markdown("#### Emerging Trends")
        if trend_items:
            trend_df = pd.DataFrame({"Trend": list(trend_items.keys()), "Count": list(trend_items.values())})
            trend_df["Signal"] = trend_df["Count"].apply(lambda value: "High" if value >= 4 else "Watch")
            st.dataframe(
                trend_df,
                use_container_width=True,
                hide_index=True,
                height=300,
            )
        else:
            st.info("No trends detected yet.")
        st.markdown("</div>", unsafe_allow_html=True)


def render_crisis_alerts(alerts: list[dict]) -> None:
    st.markdown('<div class="gm-section-title">Crisis Monitor</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="gm-section-subtitle">Surface clusters that may require immediate escalation or rapid field response.</div>',
        unsafe_allow_html=True,
    )
    if not alerts:
        st.markdown(
            """
            <div class="gm-alert-empty">
                No crisis alerts detected right now. The city is currently operating below the configured crisis thresholds.
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    severity_colors = {"high": "#dc2626", "severe": "#dc2626", "medium": "#f97316", "low": "#eab308"}
    for alert in alerts[:6]:
        severity = str(alert.get("severity", "Low"))
        color = severity_colors.get(severity.lower(), "#eab308")
        st.markdown(
            f"""
            <div class="gm-card" style="border-left:6px solid {color};">
                <div style="display:flex;justify-content:space-between;gap:12px;">
                    <div>
                        <div style="font-weight:800;font-size:1.02rem;">{alert.get("cluster_title", "General issue cluster")}</div>
                        <div style="color:rgba(255,255,255,0.68);margin-top:4px;">{alert.get("location", "Unknown")}</div>
                    </div>
                    <div style="font-weight:800;color:{color};white-space:nowrap;">{severity}</div>
                </div>
                <div style="margin-top:10px;color:rgba(255,255,255,0.82);">
                    {alert.get("message", "No alert message available.")}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_cluster_console(
    clusters: list[dict],
    insights: list[dict],
    recommendations: list[dict],
    memory_items: list[dict],
) -> None:
    st.markdown("#### Cluster Intelligence")
    if not clusters:
        st.info("No issue clusters available yet.")
        return

    insights_by_cluster = {
        (str(item.get("cluster_title", "")).strip().lower(), str(item.get("location", "")).strip().lower()): item
        for item in insights
    }
    recommendations_by_cluster = {
        (str(item.get("cluster_title", "")).strip().lower(), str(item.get("location", "")).strip().lower()): item
        for item in recommendations
    }
    memory_by_cluster = {
        (str(item.get("cluster_title", "")).strip().lower(), str(item.get("location", "")).strip().lower()): item
        for item in memory_items
    }

    search = st.text_input("Search clusters", placeholder="Filter by title or location")
    display_count = st.selectbox("Show", [4, 8, 12, len(clusters)], index=1)
    normalized_search = search.strip().lower()

    filtered_clusters = [
        cluster
        for cluster in clusters
        if not normalized_search
        or normalized_search in str(cluster.get("cluster_title", "")).lower()
        or normalized_search in str(cluster.get("location", "")).lower()
    ]
    filtered_clusters = sorted(filtered_clusters, key=lambda item: int(item.get("issue_count", 0)), reverse=True)

    for index, cluster in enumerate(filtered_clusters[:display_count], start=1):
        cluster_title = cluster.get("cluster_title", "General cluster")
        location = cluster.get("location", "Unknown")
        issue_count = cluster.get("issue_count", 0)
        issue_ids = cluster.get("issue_ids", [])
        cluster_key = (str(cluster_title).strip().lower(), str(location).strip().lower())
        insight = insights_by_cluster.get(cluster_key, {})
        recommendation = recommendations_by_cluster.get(cluster_key, {})
        memory_item = memory_by_cluster.get(cluster_key, {})

        with st.container(border=True):
            top_cols = st.columns([2, 1, 1])
            with top_cols[0]:
                st.markdown(f"#### {index}. {cluster_title}")
                st.caption(location)
            with top_cols[1]:
                st.metric("Complaints", issue_count)
            with top_cols[2]:
                st.metric("Issue IDs", len(issue_ids))

            with st.expander("View Details"):
                info_cols = st.columns(3)
                with info_cols[0]:
                    st.markdown("**Issue IDs**")
                    if issue_ids:
                        st.code(", ".join(str(issue_id) for issue_id in issue_ids), language="text")
                    else:
                        st.caption("No complaint IDs available.")
                with info_cols[1]:
                    st.markdown("**AI Insight**")
                    st.write(insight.get("insight", "No AI insight available yet."))
                with info_cols[2]:
                    st.markdown("**Governance Memory**")
                    similar_case = memory_item.get("similar_case")
                    if similar_case:
                        st.write(similar_case)
                        st.caption(memory_item.get("action_taken", "No action recorded"))
                        st.caption(f"Similarity: {memory_item.get('similarity_score', 0.0)}")
                    else:
                        st.caption("No similar resolved case found yet.")

                st.markdown("**AI Recommendations**")
                items = recommendation.get("recommendations", [])
                if items:
                    for item in items:
                        st.markdown(f"- {item}")
                else:
                    st.caption("No AI recommendations available yet.")


def render_public_update_generator(issues: list[dict]) -> None:
    st.markdown("#### Public Update Generator")
    if not issues:
        st.info("Submit an issue first to generate an update.")
        return

    issue_limit = min(len(issues), 25)
    usable_issues = issues[:issue_limit]

    def format_issue(issue: dict) -> str:
        return f"#{issue.get('id', 'N/A')} | {issue.get('title', 'Untitled')} | {issue.get('location', 'Unknown')}"

    selected_issue = st.selectbox("Select issue for communication draft", usable_issues, format_func=format_issue)
    if st.button("Generate Update", type="primary"):
        try:
            payload = {
                "title": selected_issue.get("title", ""),
                "description": selected_issue.get("description", ""),
                "location": selected_issue.get("location", ""),
                "urgency": selected_issue.get("urgency", ""),
                "image_filename": selected_issue.get("image_filename"),
            }
            response = api_post("/generate_update", payload)
        except requests.RequestException as exc:
            st.error(f"Unable to generate update: {exc}")
        else:
            st.session_state["generated_update"] = response.get("generated_update", "")

    if st.session_state.get("generated_update"):
        st.text_area("Generated public statement", st.session_state["generated_update"], height=180)


def render_work_verification_upload(issues: list[dict]) -> None:
    st.markdown("#### Work Verification Upload")
    if not issues:
        st.info("No issues available yet for verification.")
        return

    def format_issue(issue: dict) -> str:
        return (
            f"#{issue.get('id', 'N/A')} | "
            f"{issue.get('title', 'Untitled')} | "
            f"{issue.get('location', 'Unknown')} | "
            f"{issue.get('urgency', 'Unknown')}"
        )

    usable_issues = issues[: min(len(issues), 25)]
    with st.form("admin_verification_form"):
        selected_issue = st.selectbox("Select resolved issue", usable_issues, format_func=format_issue)
        verified_by = st.text_input("Verified By / Location", placeholder="e.g. Field Officer A or Ward 7")
        action_taken = st.text_input("Action Taken", placeholder="e.g. Pipeline repair completed")
        image_file = st.file_uploader(
            "Upload verification image",
            type=["png", "jpg", "jpeg", "webp"],
            key="admin_verification_image",
        )
        submitted = st.form_submit_button("Submit Verification")

        if submitted:
            if image_file is None:
                st.error("Please upload a verification image.")
            elif not verified_by.strip():
                st.error("Please enter who verified the work or the verification location.")
            else:
                data = {
                    "issue_id": str(selected_issue.get("id")),
                    "location": verified_by.strip(),
                    "action_taken": action_taken.strip() or "",
                }
                files = {
                    "image": (
                        image_file.name,
                        image_file.getvalue(),
                        image_file.type or "application/octet-stream",
                    )
                }
                try:
                    response = requests.post(f"{API_BASE}/verify_work", data=data, files=files, timeout=20)
                    response.raise_for_status()
                except requests.RequestException as exc:
                    st.error(f"Unable to submit verification: {exc}")
                else:
                    st.success("Verification uploaded successfully.")


def render_record_tables(issues: list[dict], resolved_issues: list[dict]) -> None:
    issue_col, verification_col = st.columns(2)

    with issue_col:
        active_tab, history_tab = st.tabs(["Active Complaints", "Resolved History"])

        with active_tab:
            st.markdown("#### Active Complaints")
            search = st.text_input("Filter active issues", placeholder="Search title or location", key="issue_table_search")
            show_count = st.selectbox("Show active", [10, 25, 50, len(issues) if issues else 10], key="issue_table_count")
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
                st.dataframe(df[cols], use_container_width=True, hide_index=True, height=370)
            else:
                st.info("No matching active complaints.")

        with history_tab:
            st.markdown("#### Resolved History")
            search = st.text_input(
                "Filter resolved issues",
                placeholder="Search title or location",
                key="resolved_issue_table_search",
            )
            show_count = st.selectbox(
                "Show resolved",
                [10, 25, 50, len(resolved_issues) if resolved_issues else 10],
                key="resolved_issue_table_count",
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
                st.dataframe(df[cols], use_container_width=True, hide_index=True, height=370)
            else:
                st.info("No resolved complaints yet.")

    with verification_col:
        st.markdown("#### Verification Records")
        try:
            payload = api_get("/verifications")
            records = payload.get("verifications", []) if isinstance(payload, dict) else []
        except requests.RequestException as exc:
            st.warning(f"Unable to load verification records: {exc}")
            return

        search = st.text_input(
            "Filter verifications",
            placeholder="Search location or action taken",
            key="verification_table_search",
        )
        show_count = st.selectbox(
            "Show verifications",
            [10, 25, 50, len(records) if records else 10],
            key="verification_table_count",
        )
        filtered_records = records
        if search.strip():
            term = search.strip().lower()
            filtered_records = [
                record
                for record in records
                if term in str(record.get("location", "")).lower()
                or term in str(record.get("action_taken", "")).lower()
            ]
        if filtered_records:
            df = pd.DataFrame(filtered_records[:show_count])
            cols = [
                col
                for col in ["issue_id", "location", "action_taken", "timestamp", "image_filename"]
                if col in df.columns
            ]
            st.dataframe(df[cols], use_container_width=True, hide_index=True, height=430)
        else:
            st.info("No matching verification records.")


def main() -> None:
    init_state()
    apply_page_style()
    render_header()
    user = render_login()
    if user is None:
        return

    try:
        issues_payload = api_get("/issues")
        resolved_issues_payload = api_get("/issues/history")
        analytics_payload = api_get("/analytics")
        trust_payload = api_get("/trust_score")
        trends_payload = api_get("/issue_trends")
        clusters_payload = api_get("/issue_clusters")
        insights_payload = api_get("/ai_insights")
        policy_recommendations_payload = api_get("/policy_recommendations")
        governance_memory_payload = api_get("/governance_memory")
        crisis_alerts_payload = fetch_crisis_alerts()
    except requests.RequestException as exc:
        st.error(f"Dashboard data could not be loaded: {exc}")
        return

    issues = issues_payload if isinstance(issues_payload, list) else []
    resolved_issues = resolved_issues_payload if isinstance(resolved_issues_payload, list) else []
    analytics = analytics_payload if isinstance(analytics_payload, dict) else {}
    trust = trust_payload if isinstance(trust_payload, dict) else {}
    trends = trends_payload if isinstance(trends_payload, dict) else {}
    clusters = clusters_payload if isinstance(clusters_payload, list) else []
    insights = insights_payload if isinstance(insights_payload, list) else []
    policy_recommendations = (
        policy_recommendations_payload if isinstance(policy_recommendations_payload, list) else []
    )
    governance_memory = governance_memory_payload if isinstance(governance_memory_payload, list) else []

    render_metric_strip(issues, analytics, trust, clusters, crisis_alerts_payload)
    st.markdown('<div class="gm-tabs">', unsafe_allow_html=True)
    tab_overview, tab_clusters, tab_operations = st.tabs(
        ["Command Center", "Cluster Intelligence", "Operations Desk"]
    )
    st.markdown("</div>", unsafe_allow_html=True)

    with tab_overview:
        render_charts(analytics, trends)
        st.markdown("")
        render_crisis_alerts(crisis_alerts_payload)

    with tab_clusters:
        render_cluster_console(clusters, insights, policy_recommendations, governance_memory)

    with tab_operations:
        ops_left, ops_right = st.columns([1, 1])
        with ops_left:
            st.markdown('<div class="gm-panel">', unsafe_allow_html=True)
            render_public_update_generator(issues)
            st.markdown("</div>", unsafe_allow_html=True)
        with ops_right:
            st.markdown('<div class="gm-panel">', unsafe_allow_html=True)
            render_work_verification_upload(issues)
            st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("")
        render_record_tables(issues, resolved_issues)


if __name__ == "__main__":
    main()
