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
    st.session_state.setdefault("selected_war_room_cluster", None)


def api_get(path: str) -> dict | list:
    response = requests.get(f"{API_BASE}{path}", timeout=15)
    response.raise_for_status()
    return response.json()


def api_post(path: str, json: dict) -> dict:
    response = requests.post(f"{API_BASE}{path}", json=json, timeout=15)
    response.raise_for_status()
    return response.json() or {}


def _count_options(total: int, base: list[int]) -> list[int]:
    options = [value for value in base if value < total]
    options.append(total if total > 0 else base[0])
    return sorted(set(options))


def _confidence_label(score: float) -> str:
    if score >= 0.82:
        return "High confidence"
    if score >= 0.68:
        return "Medium confidence"
    return "Low confidence"


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
        .gm-summary-strip {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 14px;
            margin-bottom: 18px;
        }
        .gm-summary-card {
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 18px;
            padding: 16px 18px;
            background: rgba(255,255,255,0.03);
        }
        .gm-console-grid {
            display: grid;
            grid-template-columns: 1.1fr 0.9fr;
            gap: 16px;
            align-items: start;
        }
        .gm-ops-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
            align-items: start;
        }
        .gm-war-room {
            border: 1px solid rgba(56,189,248,0.22);
            border-radius: 24px;
            padding: 20px 22px;
            background:
                radial-gradient(circle at top right, rgba(56,189,248,0.12), transparent 20%),
                linear-gradient(180deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02));
            box-shadow: 0 24px 54px rgba(0,0,0,0.24);
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


def severity_tone(severity: str) -> tuple[str, str]:
    normalized = severity.lower()
    if normalized in {"high", "severe"}:
        return "#fecaca", "rgba(220,38,38,0.16)"
    if normalized == "medium":
        return "#fdba74", "rgba(249,115,22,0.16)"
    return "#fde68a", "rgba(234,179,8,0.16)"


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
    high_alerts = sum(1 for alert in alerts if str(alert.get("severity", "")).lower() in {"high", "severe"})
    monitored_zones = len({str(alert.get("location", "")).strip() for alert in alerts if str(alert.get("location", "")).strip()})
    st.markdown(
        f"""
        <div class="gm-summary-strip">
            <div class="gm-summary-card">
                <div class="gm-mini">Active Alerts</div>
                <div style="font-size:1.7rem;font-weight:800;margin-top:6px;">{len(alerts)}</div>
            </div>
            <div class="gm-summary-card">
                <div class="gm-mini">High Severity</div>
                <div style="font-size:1.7rem;font-weight:800;margin-top:6px;">{high_alerts}</div>
            </div>
            <div class="gm-summary-card">
                <div class="gm-mini">Watched Locations</div>
                <div style="font-size:1.7rem;font-weight:800;margin-top:6px;">{monitored_zones}</div>
            </div>
        </div>
        """,
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


def render_command_center(analytics: dict, trends: dict, alerts: list[dict]) -> None:
    st.markdown(
        '<div class="gm-section-subtitle">Use the signal boards below to move from a fast citywide scan into focused crisis review without one long scroll.</div>',
        unsafe_allow_html=True,
    )
    signals_tab, crisis_tab = st.tabs(["Signals Board", "Crisis Monitor"])

    with signals_tab:
        render_charts(analytics, trends)

    with crisis_tab:
        render_crisis_alerts(alerts)


def render_cluster_console(
    clusters: list[dict],
    insights: list[dict],
    recommendations: list[dict],
    memory_items: list[dict],
) -> None:
    st.markdown("#### Cluster Intelligence Console")
    st.caption("Review each cluster with issue IDs, AI interpretation, policy recommendations, and historical memory in one place.")
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

    controls_left, controls_right = st.columns([2, 1])
    with controls_left:
        search = st.text_input("Search clusters", placeholder="Filter by title or location")
    with controls_right:
        options = _count_options(len(clusters), [4, 8, 12])
        display_count = st.selectbox("Show", options, index=min(1, len(options) - 1))
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
        confidence_score = float(cluster.get("confidence_score", 0.0) or 0.0)
        evidence_terms = cluster.get("evidence_terms", [])
        cluster_key = (str(cluster_title).strip().lower(), str(location).strip().lower())
        insight = insights_by_cluster.get(cluster_key, {})
        recommendation = recommendations_by_cluster.get(cluster_key, {})
        memory_item = memory_by_cluster.get(cluster_key, {})
        top_recommendation = next(iter(recommendation.get("recommendations", [])), "Awaiting recommended action set.")
        memory_summary = memory_item.get("similar_case", "No historical match found yet.")

        with st.container():
            st.markdown('<div class="gm-panel">', unsafe_allow_html=True)
            top_cols = st.columns([2, 1, 1])
            with top_cols[0]:
                st.markdown(f"#### {index}. {cluster_title}")
                st.caption(location)
            with top_cols[1]:
                st.metric("Complaints", issue_count)
            with top_cols[2]:
                st.metric("Confidence", _confidence_label(confidence_score))

            preview_left, preview_right = st.columns([1.2, 0.8])
            with preview_left:
                st.markdown("**Live Insight**")
                st.write(insight.get("insight", "No AI insight available yet."))
            with preview_right:
                st.markdown("**Immediate Focus**")
                st.write(top_recommendation)
                st.caption(memory_summary)
                if evidence_terms:
                    st.caption(f"Evidence terms: {', '.join(str(term) for term in evidence_terms)}")

            with st.expander("View Details"):
                info_cols = st.columns(4)
                with info_cols[0]:
                    st.markdown("**Issue IDs**")
                    if issue_ids:
                        st.code(", ".join(str(issue_id) for issue_id in issue_ids), language="text")
                    else:
                        st.caption("No complaint IDs available.")
                with info_cols[1]:
                    st.markdown("**Cluster Confidence**")
                    st.write(f"{confidence_score:.2f} | {_confidence_label(confidence_score)}")
                    if evidence_terms:
                        st.caption(", ".join(str(term) for term in evidence_terms))
                    else:
                        st.caption("No evidence terms available.")
                with info_cols[2]:
                    st.markdown("**AI Insight**")
                    st.write(insight.get("insight", "No AI insight available yet."))
                with info_cols[3]:
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
            st.markdown("</div>", unsafe_allow_html=True)


def render_war_room(clusters: list[dict]) -> None:
    st.markdown("### AI Multi-Agent Emergency War Room")
    st.caption("Launch a coordinated response room where specialized AI agents analyze one cluster together.")
    if not clusters:
        st.info("Create some issue clusters first to launch the War Room.")
        return

    sorted_clusters = sorted(clusters, key=lambda item: int(item.get("issue_count", 0)), reverse=True)
    default_cluster_id = st.session_state.get("selected_war_room_cluster")
    default_index = 0
    if default_cluster_id is not None:
        for idx, cluster in enumerate(sorted_clusters):
            if int(cluster.get("cluster_id", -1)) == int(default_cluster_id):
                default_index = idx
                break

    def format_cluster(cluster: dict) -> str:
        return (
            f"#{cluster.get('cluster_id', 'N/A')} | "
            f"{cluster.get('cluster_title', 'Recurring Civic Issue')} | "
            f"{cluster.get('location', 'Unknown')} | "
            f"{cluster.get('issue_count', 0)} complaints"
        )

    picker_col, context_col = st.columns([1.4, 0.9])
    with picker_col:
        selected_cluster = st.selectbox(
            "Choose cluster for War Room",
            sorted_clusters,
            index=default_index,
            format_func=format_cluster,
            key="war_room_cluster_picker",
        )
    with context_col:
        st.markdown(
            """
            <div class="gm-card" style="margin-top:28px;">
                <div class="gm-mini">Why This Matters</div>
                <div style="margin-top:8px;line-height:1.55;color:rgba(255,255,255,0.82);">
                    This room synthesizes crisis risk, policy response, historical memory, trust impact,
                    and citizen communications into one decision-ready response flow.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.session_state["selected_war_room_cluster"] = int(selected_cluster.get("cluster_id", 0))

    try:
        war_room_payload = api_get(f"/war_room?cluster_id={int(selected_cluster.get('cluster_id', 0))}")
        war_room = war_room_payload if isinstance(war_room_payload, dict) else {}
    except requests.RequestException as exc:
        st.warning(f"Unable to load War Room analysis: {exc}")
        return

    if not war_room:
        st.info("No War Room analysis available for this cluster.")
        return

    badge_text, badge_background = severity_tone(str(war_room.get("status", "Active Monitoring")))

    st.markdown(
        f"""
        <div class="gm-war-room">
            <div style="display:flex;justify-content:space-between;gap:18px;align-items:flex-start;">
                <div>
                    <div class="gm-mini">Live Coordination Room</div>
                    <h3 style="margin:0.45rem 0 0.2rem 0;">{war_room.get("cluster_title", "Recurring Civic Issue")}</h3>
                    <div style="color:rgba(255,255,255,0.72);">{war_room.get("location", "Unknown")} | {war_room.get("issue_count", 0)} complaints</div>
                </div>
                <div style="padding:8px 14px;border-radius:999px;background:{badge_background};font-weight:800;color:{badge_text};">
                    {war_room.get("status", "Active Monitoring")}
                </div>
            </div>
            <div style="margin-top:16px;font-size:1.02rem;color:rgba(255,255,255,0.86);">
                {war_room.get("final_recommendation", "No final recommendation generated.")}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    summary_items = [
        ("Situation Read", war_room.get("insight", "No situational insight available.")),
        ("Recommended First Move", (war_room.get("action_plan") or ["No immediate action plan available."])[0]),
        (
            "Historical Anchor",
            (war_room.get("memory_match") or {}).get("similar_case_title", "No resolved analogue available yet."),
        ),
        (
            "Model Confidence",
            f"{float(war_room.get('confidence_score', 0.0) or 0.0):.2f} | {_confidence_label(float(war_room.get('confidence_score', 0.0) or 0.0))}",
        ),
    ]
    summary_cols = st.columns(len(summary_items))
    for col, (label, value) in zip(summary_cols, summary_items):
        with col:
            st.markdown(
                f"""
                <div class="gm-card">
                    <div class="gm-mini">{label}</div>
                    <div style="margin-top:8px;line-height:1.55;font-weight:600;">{value}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    evidence_terms = war_room.get("evidence_terms") or []
    if evidence_terms:
        st.caption(f"Cluster evidence terms: {', '.join(str(term) for term in evidence_terms)}")

    left, right = st.columns([1.2, 0.8])
    with left:
        st.markdown("#### Agent Deliberation")
        for agent in war_room.get("agents", []):
            st.markdown(
                f"""
                <div class="gm-card">
                    <div style="display:flex;justify-content:space-between;gap:10px;align-items:flex-start;">
                        <div style="font-weight:800;">{agent.get("agent", "AI Agent")}</div>
                        <div style="font-size:0.8rem;text-transform:uppercase;letter-spacing:0.08em;color:#7dd3fc;">
                            {agent.get("headline", "Assessment")}
                        </div>
                    </div>
                    <div style="margin-top:10px;color:rgba(255,255,255,0.84);line-height:1.6;">
                        {agent.get("assessment", "No assessment available.")}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with right:
        st.markdown("#### Action Stack")
        action_plan = war_room.get("action_plan", [])
        if action_plan:
            for idx, action in enumerate(action_plan, start=1):
                st.markdown(
                    f"""
                    <div class="gm-card">
                        <div class="gm-mini">Action {idx:02d}</div>
                        <div style="margin-top:8px;font-weight:700;line-height:1.55;">{action}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.info("No action plan available yet.")

        memory_match = war_room.get("memory_match") or {}
        if memory_match:
            st.markdown("#### Historical Anchor")
            st.markdown(
                f"""
                <div class="gm-card">
                    <div style="font-weight:800;">{memory_match.get("similar_case_title", "Resolved Case")}</div>
                    <div style="margin-top:8px;color:rgba(255,255,255,0.76);">{memory_match.get("location", "Unknown")}</div>
                    <div style="margin-top:10px;"><strong>Action Taken:</strong> {memory_match.get("action_taken", "No action recorded")}</div>
                    <div style="margin-top:8px;"><strong>Similarity:</strong> {memory_match.get("similarity_score", 0.0)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_public_update_generator(issues: list[dict]) -> None:
    st.markdown("#### Public Update Generator")
    st.caption("Create a public-facing update from the current complaint queue without leaving the operations desk.")
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
    st.caption("Close the loop by attaching proof-of-work and pushing the complaint into resolved history.")
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
    st.markdown("#### Operations Records")
    st.caption("Search active complaints, resolved history, and verification evidence without letting long lists overwhelm the page.")
    issue_col, verification_col = st.columns(2)

    with issue_col:
        active_tab, history_tab = st.tabs(["Active Complaints", "Resolved History"])

        with active_tab:
            st.markdown("#### Active Complaints")
            search = st.text_input("Filter active issues", placeholder="Search title or location", key="issue_table_search")
            show_count = st.selectbox(
                "Show active",
                _count_options(len(issues), [10, 25, 50]),
                key="issue_table_count",
            )
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
                _count_options(len(resolved_issues), [10, 25, 50]),
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
            _count_options(len(records), [10, 25, 50]),
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


def render_operations_desk(issues: list[dict], resolved_issues: list[dict]) -> None:
    st.markdown('<div class="gm-section-title">Operations Desk</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="gm-section-subtitle">Run public communication, submit work verification, and inspect operational records from one tighter workspace.</div>',
        unsafe_allow_html=True,
    )

    action_tab, records_tab = st.tabs(["Response Actions", "Records Console"])

    with action_tab:
        ops_left, ops_right = st.columns([1, 1])
        with ops_left:
            st.markdown('<div class="gm-panel">', unsafe_allow_html=True)
            render_public_update_generator(issues)
            st.markdown("</div>", unsafe_allow_html=True)
        with ops_right:
            st.markdown('<div class="gm-panel">', unsafe_allow_html=True)
            render_work_verification_upload(issues)
            st.markdown("</div>", unsafe_allow_html=True)

    with records_tab:
        render_record_tables(issues, resolved_issues)


def render_cluster_intelligence(
    clusters: list[dict],
    insights: list[dict],
    recommendations: list[dict],
    memory_items: list[dict],
) -> None:
    st.markdown(
        '<div class="gm-section-subtitle">Switch between the high-impact War Room and the wider cluster review console without stacking both views into one long page.</div>',
        unsafe_allow_html=True,
    )
    war_room_tab, console_tab = st.tabs(["War Room", "Cluster Console"])

    with war_room_tab:
        render_war_room(clusters)

    with console_tab:
        render_cluster_console(clusters, insights, recommendations, memory_items)


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
        render_command_center(analytics, trends, crisis_alerts_payload)

    with tab_clusters:
        render_cluster_intelligence(clusters, insights, policy_recommendations, governance_memory)

    with tab_operations:
        render_operations_desk(issues, resolved_issues)


if __name__ == "__main__":
    main()
