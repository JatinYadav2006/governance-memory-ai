import pandas as pd
import plotly.express as px
import requests
import streamlit as st


API_BASE = "http://127.0.0.1:8000"
DEMO_ADMIN_EMAIL = "admin@govai.demo"
DEMO_ADMIN_PASSWORD = "GovAI_Admin#2026!"


def init_state() -> None:
    st.session_state.setdefault("admin_user", None)
    st.session_state.setdefault("generated_update", "")
    st.session_state.setdefault("selected_war_room_cluster", None)
    st.session_state.setdefault("admin_dashboard_bundle", None)


def api_get(path: str) -> dict | list:
    response = requests.get(f"{API_BASE}{path}", timeout=30)
    response.raise_for_status()
    return response.json()


def api_post(path: str, json: dict) -> dict:
    response = requests.post(f"{API_BASE}{path}", json=json, timeout=20)
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
    if not st.session_state.get("use_unified_access"):
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
        .gm-switch-shell {
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 22px;
            padding: 16px 18px 12px 18px;
            background: linear-gradient(180deg, rgba(255,255,255,0.045), rgba(255,255,255,0.02));
            box-shadow: 0 18px 44px rgba(0,0,0,0.16);
            margin: 18px 0 24px 0;
        }
        .gm-switch-title {
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: rgba(255,255,255,0.54);
            margin-bottom: 12px;
        }
        .gm-subswitch-shell {
            border-top: 1px solid rgba(255,255,255,0.08);
            margin-top: 18px;
            padding-top: 18px;
            margin-bottom: 18px;
        }
        div[role="radiogroup"] {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }
        div[role="radiogroup"] > label {
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 14px;
            padding: 10px 14px 10px 12px;
            background: rgba(255,255,255,0.025);
            min-height: 48px;
            transition: all 160ms ease;
            position: relative;
            overflow: hidden;
        }
        div[role="radiogroup"] > label:hover {
            border-color: rgba(56,189,248,0.28);
            background: rgba(56,189,248,0.06);
            transform: translateY(-1px);
        }
        div[role="radiogroup"] > label[data-selected="true"],
        div[role="radiogroup"] > label:has(input:checked) {
            border-color: rgba(96,165,250,0.46);
            background: linear-gradient(90deg, rgba(37,99,235,0.30), rgba(14,165,233,0.12));
            box-shadow:
                inset 0 0 0 1px rgba(147,197,253,0.18),
                0 10px 24px rgba(15,23,42,0.24);
            transform: translateY(-1px);
        }
        div[role="radiogroup"] > label > div:first-child {
            display: none;
        }
        div[role="radiogroup"] > label > div:last-child {
            font-weight: 700;
        }
        div[role="radiogroup"] > label[data-selected="true"] > div:last-child,
        div[role="radiogroup"] > label:has(input:checked) > div:last-child {
            color: #eff6ff;
        }
        .gm-content-shell {
            border-top: 1px solid rgba(255,255,255,0.08);
            padding-top: 26px;
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
    if not st.session_state.get("use_unified_access"):
        st.caption("Demo admin credentials: `admin@govai.demo` / `GovAI_Admin#2026!`")


def render_workspace_switch(title: str, options: list[str], key: str) -> str:
    st.markdown(
        f"""
        <div class="gm-switch-shell">
            <div class="gm-switch-title">{title}</div>
        """,
        unsafe_allow_html=True,
    )
    selection = st.radio(
        title,
        options,
        horizontal=True,
        label_visibility="collapsed",
        key=key,
    )
    st.markdown("</div>", unsafe_allow_html=True)
    return selection


def render_subworkspace_switch(title: str, options: list[str], key: str) -> str:
    st.markdown(
        f"""
        <div class="gm-subswitch-shell">
            <div class="gm-switch-title">{title}</div>
        """,
        unsafe_allow_html=True,
    )
    selection = st.radio(
        title,
        options,
        horizontal=True,
        label_visibility="collapsed",
        key=key,
    )
    st.markdown("</div>", unsafe_allow_html=True)
    return selection


def render_login() -> dict | None:
    user = st.session_state.get("admin_user")
    if user is not None:
        cols = st.columns([4, 1, 1])
        with cols[0]:
            st.markdown(
                f"**Logged in as:** {user.get('name')} | {user.get('email')} | role: {user.get('role', 'admin')}"
            )
        with cols[1]:
            if st.button("Refresh", use_container_width=True):
                st.session_state["admin_dashboard_bundle"] = None
                st.rerun()
        with cols[2]:
            if st.button("Logout", use_container_width=True):
                st.session_state["admin_user"] = None
                st.session_state["generated_update"] = ""
                st.session_state["admin_dashboard_bundle"] = None
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
                st.session_state["admin_dashboard_bundle"] = None
                st.success("Admin access granted.")
                st.rerun()
    return None


def fetch_crisis_alerts() -> list[dict]:
    alerts_payload = api_get("/crisis_alerts")
    return alerts_payload if isinstance(alerts_payload, list) else []


def fetch_admin_dashboard_bundle(force_refresh: bool = False) -> dict:
    cached = st.session_state.get("admin_dashboard_bundle")
    if cached is not None and not force_refresh:
        return cached

    payload = api_get("/admin_dashboard_bundle")
    bundle = payload if isinstance(payload, dict) else {}
    st.session_state["admin_dashboard_bundle"] = bundle
    return bundle


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


def render_executive_mode(
    executive: dict,
    impact: dict,
    assignments: list[dict],
    sla_overview: dict,
    zones: list[dict],
) -> None:
    st.markdown('<div class="gm-section-title">Operational Performance</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="gm-section-subtitle">Track service pressure, delivery speed, and department response from one clean performance view.</div>',
        unsafe_allow_html=True,
    )
    st.caption("Operational metrics are platform-derived indicators based on complaint, resolution, verification, and assignment data.")

    summary_cards = [
        ("City Risk Level", executive.get("city_risk_level", "Stable"), "#f87171"),
        ("Resolution Rate", f"{impact.get('resolution_rate', 0)}%", "#4ade80"),
        ("Review Hours Saved", f"{impact.get('estimated_manual_review_hours_saved', 0)}h", "#38bdf8"),
        ("Trust Recovery", f"+{impact.get('trust_recovery_points', 0)}", "#a78bfa"),
        ("Departments Engaged", str(executive.get("departments_engaged", 0)), "#f59e0b"),
    ]
    cards = st.columns(len(summary_cards))
    for col, (label, value, accent) in zip(cards, summary_cards):
        with col:
            st.markdown(
                f"""
                <div class="gm-metric">
                    <div class="gm-mini">{label}</div>
                    <div class="gm-big">{value}</div>
                    <div style="height:8px;border-radius:999px;background:rgba(255,255,255,0.06);overflow:hidden;">
                        <div style="width:70%;height:100%;background:{accent};"></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    if executive.get("top_operational_message"):
        st.caption(str(executive.get("top_operational_message")))

    exec_view = render_subworkspace_switch(
        "Performance workspace",
        ["Impact Metrics", "Department Dispatch", "Zone Performance"],
        "performance_workspace",
    )

    if exec_view == "Impact Metrics":
        left, right = st.columns([1.1, 0.9])
        with left:
            st.markdown('<div class="gm-panel">', unsafe_allow_html=True)
            st.markdown("#### Civic Impact Scorecard")
            impact_rows = [
                ("Active Issues", impact.get("active_issues", 0)),
                ("Resolved Issues", impact.get("resolved_issues", 0)),
                ("Average Resolution Time", f"{impact.get('average_resolution_hours', 0)} hours"),
                ("Repeat Complaint Pressure", f"{impact.get('repeat_complaint_pressure', 0)}%"),
            ]
            for label, value in impact_rows:
                st.markdown(
                    f"""
                    <div class="gm-card">
                        <div class="gm-mini">{label}</div>
                        <div style="margin-top:8px;font-size:1.25rem;font-weight:800;">{value}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            st.markdown("</div>", unsafe_allow_html=True)
        with right:
            st.markdown('<div class="gm-panel">', unsafe_allow_html=True)
            st.markdown("#### Operational Notes")
            st.markdown(
                """
                - Impact indicators are calculated from complaint, assignment, SLA, verification, and resolution records.
                - Response pressure reflects currently open complaints and active issue clusters.
                - Trust recovery is a platform signal that rises when verified resolutions increase.
                - Repeat complaint pressure shows where the same civic category continues to reappear.
                """
            )
            st.markdown("#### Leadership Focus")
            st.markdown(
                """
                - Prioritize locations with high active issue concentration
                - Watch overdue SLA windows before they become crisis signals
                - Use resolved-history trends to compare field response quality by zone
                """
            )
            st.markdown("</div>", unsafe_allow_html=True)
    elif exec_view == "Department Dispatch":
        render_department_assignment_board(assignments, sla_overview)
        st.markdown("")
        render_sla_table(sla_overview)
    else:
        render_zone_performance_board(zones)


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
                <div style="margin-top:8px;color:rgba(255,255,255,0.62);">
                    {alert.get("reason", "")}
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


def render_department_assignment_board(assignments: list[dict], sla_overview: dict) -> None:
    st.markdown("#### Department and Officer Assignment")
    st.caption("Each cluster is routed to the right civic department, assigned to an operational lead, and tracked against a response window.")
    top = st.columns(3)
    with top[0]:
        st.metric("Clusters Assigned", len(assignments))
    with top[1]:
        st.metric("Overdue Issues", sla_overview.get("summary", {}).get("overdue_issues", 0))
    with top[2]:
        st.metric("Average Open Age", f"{sla_overview.get('summary', {}).get('average_open_age_hours', 0)}h")

    search_col, count_col = st.columns([2, 1])
    with search_col:
        search = st.text_input("Search assignments", placeholder="Search cluster, department, or location", key="assignment_search")
    with count_col:
        show_count = st.selectbox("Show assignments", _count_options(len(assignments), [5, 10, 20]), key="assignment_count")

    filtered = assignments
    if search.strip():
        term = search.strip().lower()
        filtered = [
            item
            for item in assignments
            if term in str(item.get("cluster_title", "")).lower()
            or term in str(item.get("department", "")).lower()
            or term in str(item.get("location", "")).lower()
        ]

    if filtered:
        df = pd.DataFrame(filtered[:show_count])
        cols = [
            col for col in [
                "cluster_title",
                "location",
                "issue_count",
                "department",
                "team",
                "officer",
                "sla_hours",
            ] if col in df.columns
        ]
        st.dataframe(df[cols], use_container_width=True, hide_index=True, height=360)
    else:
        st.info("No assignments match the current filter.")


def render_zone_performance_board(zones: list[dict]) -> None:
    st.markdown("#### Ward and Zone Performance")
    st.caption("Compare which locations carry the highest complaint load, which are resolving fastest, and where trust is weakest.")
    if not zones:
        st.info("No zone data available yet.")
        return

    left, right = st.columns([1, 1])
    with left:
        zone_df = pd.DataFrame(zones)
        chart = px.bar(
            zone_df,
            x="location",
            y=["active_issues", "resolved_issues"],
            barmode="group",
            color_discrete_sequence=["#f87171", "#4ade80"],
            height=320,
        )
        chart.update_layout(margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(chart, use_container_width=True)
    with right:
        trust_chart = px.scatter(
            pd.DataFrame(zones),
            x="resolution_rate",
            y="trust_score",
            size="total_issues",
            color="active_issues",
            hover_name="location",
            color_continuous_scale="Blues",
            height=320,
        )
        trust_chart.update_layout(margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(trust_chart, use_container_width=True)

    df = pd.DataFrame(zones)
    cols = [
        col for col in [
            "location",
            "total_issues",
            "active_issues",
            "resolved_issues",
            "resolution_rate",
            "avg_resolution_hours",
            "trust_score",
        ] if col in df.columns
    ]
    st.dataframe(df[cols], use_container_width=True, hide_index=True, height=320)


def render_sla_table(sla_overview: dict) -> None:
    st.markdown("#### SLA and Response Tracking")
    st.caption("Track time since complaint intake, assigned department, stage, and whether the complaint has moved beyond its response window.")
    summary = sla_overview.get("summary", {})
    cards = st.columns(4)
    items = [
        ("Active Issues", summary.get("active_issues", 0)),
        ("On Track", summary.get("on_track_issues", 0)),
        ("Overdue", summary.get("overdue_issues", 0)),
        ("Avg Open Age", f"{summary.get('average_open_age_hours', 0)}h"),
    ]
    for col, (label, value) in zip(cards, items):
        with col:
            st.markdown(
                f"""
                <div class="gm-card">
                    <div class="gm-mini">{label}</div>
                    <div style="margin-top:8px;font-size:1.2rem;font-weight:800;">{value}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    issues = sla_overview.get("issues", [])
    if not issues:
        st.info("No active SLA items right now.")
        return
    df = pd.DataFrame(issues)
    cols = [
        col for col in [
            "id",
            "title",
            "location",
            "department",
            "officer",
            "stage",
            "age_hours",
            "sla_hours",
            "overdue",
        ] if col in df.columns
    ]
    st.dataframe(df[cols], use_container_width=True, hide_index=True, height=360)


def render_cluster_console(
    clusters: list[dict],
    insights: list[dict],
    recommendations: list[dict],
    memory_items: list[dict],
) -> None:
    st.markdown("#### Cluster Intelligence Console")
    st.caption("Review each cluster with issue IDs, AI interpretation, policy recommendations, and historical memory in one place.")
    st.caption("Confidence and evidence terms explain why complaints were grouped together; they are meant to support human review, not replace it.")
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
                    st.caption(insight.get("evidence_note", ""))
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
                    rationale = recommendation.get("rationale")
                    if rationale:
                        st.caption(rationale)
                else:
                    st.caption("No AI recommendations available yet.")
            st.markdown("</div>", unsafe_allow_html=True)


def render_war_room(clusters: list[dict]) -> None:
    st.markdown("### AI Multi-Agent Emergency War Room")
    st.caption("Launch a coordinated response room where specialized AI agents analyze one cluster together.")
    st.caption("The war room synthesizes evidence and recommendations for human decision-makers; it does not auto-execute administrative action.")
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
                <div class="gm-mini">Room Summary</div>
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
    if war_room.get("evidence_summary"):
        st.caption(str(war_room.get("evidence_summary")))

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


def render_social_pulse(social_pulse: dict) -> None:
    st.markdown('<div class="gm-section-title">Social Pulse Intelligence</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="gm-section-subtitle">Track citizen sentiment, early civic buzz, and potentially harmful misinformation before it turns into a formal crisis.</div>',
        unsafe_allow_html=True,
    )

    if not isinstance(social_pulse, dict):
        social_pulse = {}

    sentiment = social_pulse.get("sentiment_summary", {}) if isinstance(social_pulse.get("sentiment_summary", {}), dict) else {}
    emerging = social_pulse.get("emerging_issues", []) if isinstance(social_pulse.get("emerging_issues", []), list) else []
    misinformation = social_pulse.get("misinformation_alerts", []) if isinstance(social_pulse.get("misinformation_alerts", []), list) else []
    mismatch = social_pulse.get("mismatch_alerts", []) if isinstance(social_pulse.get("mismatch_alerts", []), list) else []
    recent_posts = social_pulse.get("recent_posts", []) if isinstance(social_pulse.get("recent_posts", []), list) else []

    top = st.columns(4)
    summary_items = [
        ("Tracked Posts", sentiment.get("total_posts", 0), "#38bdf8"),
        ("Negative Share", f"{sentiment.get('negative_share', 0)}%", "#f87171"),
        ("Top Topic", sentiment.get("top_topic", "No social activity"), "#a78bfa"),
        ("Narrative Alerts", len(misinformation), "#f59e0b"),
    ]
    for col, (label, value, accent) in zip(top, summary_items):
        with col:
            st.markdown(
                f"""
                <div class="gm-metric">
                    <div class="gm-mini">{label}</div>
                    <div style="margin-top:10px;font-size:1.6rem;font-weight:800;color:{accent};">{value}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    pulse_tab, misinformation_tab, live_tab = st.tabs(["Sentiment Pulse", "Narrative Watch", "Recent Posts"])

    with pulse_tab:
        left, right = st.columns([0.95, 1.05])
        with left:
            st.markdown('<div class="gm-panel">', unsafe_allow_html=True)
            st.markdown("#### Sentiment Split")
            sentiment_df = pd.DataFrame(
                {
                    "Sentiment": ["Negative", "Neutral", "Positive"],
                    "Count": [
                        sentiment.get("negative_posts", 0),
                        sentiment.get("neutral_posts", 0),
                        sentiment.get("positive_posts", 0),
                    ],
                }
            )
            chart = px.pie(
                sentiment_df,
                names="Sentiment",
                values="Count",
                color="Sentiment",
                color_discrete_map={
                    "Negative": "#f87171",
                    "Neutral": "#94a3b8",
                    "Positive": "#4ade80",
                },
            )
            chart.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=290)
            st.plotly_chart(chart, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with right:
            st.markdown('<div class="gm-panel">', unsafe_allow_html=True)
            st.markdown("#### Emerging Social Issues")
            if emerging:
                emerging_df = pd.DataFrame(emerging[:6])
                chart = px.bar(
                    emerging_df,
                    x="topic",
                    y="post_count",
                    color="signal",
                    hover_data=["location", "negative_posts", "average_engagement"],
                    color_discrete_map={"High": "#f87171", "Watch": "#f59e0b"},
                )
                chart.update_layout(showlegend=True, margin=dict(l=10, r=10, t=10, b=10), height=290)
                st.plotly_chart(chart, use_container_width=True)
            else:
                st.info("No emerging social issue clusters detected.")
            st.markdown("</div>", unsafe_allow_html=True)

        if mismatch:
            st.markdown("#### Complaint vs Social Buzz Gap")
            for item in mismatch:
                st.markdown(
                    f"""
                    <div class="gm-card">
                        <div style="font-weight:800;">{item.get('topic', 'Civic Issue')} | {item.get('location', 'Unknown')}</div>
                        <div style="margin-top:8px;color:rgba(255,255,255,0.78);">
                            {item.get('signal', 'Social buzz is ahead of formal complaints.')}
                        </div>
                        <div style="margin-top:10px;"><strong>Social Posts:</strong> {item.get('social_posts', 0)} | <strong>Formal Complaints:</strong> {item.get('complaint_count', 0)}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    with misinformation_tab:
        if not misinformation:
            st.markdown(
                """
                <div class="gm-alert-empty">
                    No misinformation alerts are active right now. Social narratives are currently aligned with complaint evidence.
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            for alert in misinformation:
                color, background = severity_tone(str(alert.get("severity", "Medium")))
                st.markdown(
                    f"""
                    <div class="gm-card" style="border-left:6px solid {color};background:{background};">
                        <div style="display:flex;justify-content:space-between;gap:12px;align-items:flex-start;">
                            <div style="font-weight:800;">{alert.get('alert_title', 'Narrative Alert')}</div>
                            <div style="font-weight:800;color:{color};">{alert.get('severity', 'Medium')}</div>
                        </div>
                        <div style="margin-top:10px;color:rgba(255,255,255,0.84);line-height:1.55;">{alert.get('message', '')}</div>
                        <div style="margin-top:10px;"><strong>Location:</strong> {alert.get('location', 'Unknown')} | <strong>Posts:</strong> {alert.get('post_count', 0)}</div>
                        <div style="margin-top:8px;"><strong>Status:</strong> {alert.get('status', 'Needs verification')}</div>
                        <div style="margin-top:8px;"><strong>Evidence Terms:</strong> {', '.join(str(term) for term in alert.get('evidence_terms', []))}</div>
                        <div style="margin-top:8px;"><strong>Recommended Response:</strong> {alert.get('recommended_response', '')}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    with live_tab:
        if not recent_posts:
            st.info("No recent social posts are available.")
        else:
            for post in recent_posts:
                sentiment_color = {
                    "negative": "#f87171",
                    "neutral": "#94a3b8",
                    "positive": "#4ade80",
                }.get(str(post.get("sentiment", "neutral")).lower(), "#94a3b8")
                st.markdown(
                    f"""
                    <div class="gm-card">
                        <div style="display:flex;justify-content:space-between;gap:12px;align-items:flex-start;">
                            <div>
                                <div style="font-weight:800;">{post.get('author', 'Citizen')}</div>
                                <div style="color:rgba(255,255,255,0.62);margin-top:4px;">{post.get('platform', 'Social')} | {post.get('location', 'Unknown')}</div>
                            </div>
                            <div style="font-weight:800;color:{sentiment_color};text-transform:capitalize;">
                                {post.get('sentiment', 'neutral')}
                            </div>
                        </div>
                        <div style="margin-top:10px;line-height:1.6;color:rgba(255,255,255,0.84);">{post.get('text', '')}</div>
                        <div style="margin-top:10px;"><strong>Topic:</strong> {post.get('topic', 'General Civic Concern')} | <strong>Engagement:</strong> {post.get('engagement', 0)}</div>
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


def render_work_verification_upload(clusters: list[dict]) -> None:
    st.markdown("#### Work Verification Upload")
    st.caption("Close an entire complaint cluster with one proof-of-work submission so the linked active issues move together into resolved history.")
    if not clusters:
        st.info("No active clusters available yet for verification.")
        return

    resolvable_clusters = [cluster for cluster in clusters if cluster.get("issue_ids")]
    if not resolvable_clusters:
        st.info("No active clusters are ready for verification.")
        return

    def format_cluster(cluster: dict) -> str:
        return (
            f"#{cluster.get('cluster_id', 'N/A')} | "
            f"{cluster.get('cluster_title', 'Recurring Civic Issue')} | "
            f"{cluster.get('location', 'Unknown')} | "
            f"{cluster.get('issue_count', 0)} issues"
        )

    with st.form("admin_verification_form"):
        selected_cluster = st.selectbox(
            "Select resolved cluster",
            resolvable_clusters[: min(len(resolvable_clusters), 25)],
            format_func=format_cluster,
        )
        issue_ids = [int(issue_id) for issue_id in selected_cluster.get("issue_ids", [])]
        st.caption(
            f"This verification will resolve {len(issue_ids)} linked complaints: "
            + ", ".join(f"#{issue_id}" for issue_id in issue_ids[:8])
            + (" ..." if len(issue_ids) > 8 else "")
        )
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
                    "issue_ids": ",".join(str(issue_id) for issue_id in issue_ids),
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
                    st.session_state["admin_dashboard_bundle"] = None
                    st.success(f"Verification uploaded successfully for {len(issue_ids)} complaints in the selected cluster.")
                    st.rerun()


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
        grouped_records: list[dict] = []
        grouped_index: dict[tuple[str, str, str, str], dict] = {}
        for record in records:
            key = (
                str(record.get("location", "")),
                str(record.get("action_taken", "")),
                str(record.get("timestamp", "")),
                str(record.get("image_filename", "")),
            )
            existing = grouped_index.get(key)
            if existing is None:
                existing = {
                    "location": record.get("location", ""),
                    "action_taken": record.get("action_taken", ""),
                    "timestamp": record.get("timestamp", ""),
                    "image_filename": record.get("image_filename", ""),
                    "issue_count": 0,
                    "issue_ids": [],
                }
                grouped_index[key] = existing
                grouped_records.append(existing)

            existing["issue_count"] += 1
            existing["issue_ids"].append(record.get("issue_id"))

        filtered_records = grouped_records
        if search.strip():
            term = search.strip().lower()
            filtered_records = [
                record
                for record in grouped_records
                if term in str(record.get("location", "")).lower()
                or term in str(record.get("action_taken", "")).lower()
                or term in ", ".join(str(issue_id) for issue_id in record.get("issue_ids", [])).lower()
            ]
        if filtered_records:
            df = pd.DataFrame(filtered_records[:show_count])
            if "issue_ids" in df.columns:
                df["issue_ids"] = df["issue_ids"].apply(
                    lambda issue_ids: ", ".join(f"#{issue_id}" for issue_id in issue_ids[:8])
                    + (" ..." if len(issue_ids) > 8 else "")
                )
            cols = [
                col
                for col in ["issue_count", "issue_ids", "location", "action_taken", "timestamp", "image_filename"]
                if col in df.columns
            ]
            st.dataframe(df[cols], use_container_width=True, hide_index=True, height=430)
        else:
            st.info("No matching verification records.")


def render_operations_desk(issues: list[dict], resolved_issues: list[dict], clusters: list[dict]) -> None:
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
            render_work_verification_upload(clusters)
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
    intelligence_view = render_subworkspace_switch(
        "Cluster workspace",
        ["War Room", "Cluster Console"],
        "cluster_workspace",
    )

    if intelligence_view == "War Room":
        render_war_room(clusters)
    else:
        render_cluster_console(clusters, insights, recommendations, memory_items)


def render_policy_management() -> None:
    st.markdown("### Policy Document Management")
    st.caption("Upload new policy PDFs for citizen access. Citizens can search and view these documents in the Policy Lookup tab.")

    uploaded_file = st.file_uploader("Select a PDF policy document", type=["pdf"], key="policy_upload")
    if uploaded_file is not None:
        st.write(f"Selected: {uploaded_file.name}")
        if st.button("Upload Policy", key="upload_policy_button"):
            try:
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                response = requests.post(f"{API_BASE}/upload_policy", files=files, timeout=30)
                response.raise_for_status()
                result = response.json()
                st.success(result.get("message", "Upload successful."))
            except requests.RequestException as exc:
                st.error(f"Upload failed: {exc}")

    st.markdown("---")
    st.markdown("#### Existing Policies")
    st.info("Policies are stored in assets/policies. Citizens can search by keyword in the Policy Lookup tab.")


def main() -> None:
    init_state()
    apply_page_style()
    render_header()
    user = render_login()
    if user is None:
        return

    try:
        dashboard_bundle = fetch_admin_dashboard_bundle()
    except requests.RequestException as exc:
        st.error(f"Dashboard data could not be loaded: {exc}")
        return

    issues = dashboard_bundle.get("issues", []) if isinstance(dashboard_bundle.get("issues", []), list) else []
    resolved_issues = (
        dashboard_bundle.get("resolved_issues", [])
        if isinstance(dashboard_bundle.get("resolved_issues", []), list)
        else []
    )
    analytics = dashboard_bundle.get("analytics", {}) if isinstance(dashboard_bundle.get("analytics", {}), dict) else {}
    trust = dashboard_bundle.get("trust", {}) if isinstance(dashboard_bundle.get("trust", {}), dict) else {}
    trends = dashboard_bundle.get("trends", {}) if isinstance(dashboard_bundle.get("trends", {}), dict) else {}
    clusters = dashboard_bundle.get("clusters", []) if isinstance(dashboard_bundle.get("clusters", []), list) else []
    insights = dashboard_bundle.get("insights", []) if isinstance(dashboard_bundle.get("insights", []), list) else []
    policy_recommendations = (
        dashboard_bundle.get("policy_recommendations", [])
        if isinstance(dashboard_bundle.get("policy_recommendations", []), list)
        else []
    )
    governance_memory = (
        dashboard_bundle.get("governance_memory", [])
        if isinstance(dashboard_bundle.get("governance_memory", []), list)
        else []
    )
    social_pulse = (
        dashboard_bundle.get("social_pulse", {})
        if isinstance(dashboard_bundle.get("social_pulse", {}), dict)
        else {}
    )
    crisis_alerts_payload = (
        dashboard_bundle.get("crisis_alerts", [])
        if isinstance(dashboard_bundle.get("crisis_alerts", []), list)
        else []
    )
    impact_metrics = (
        dashboard_bundle.get("impact_metrics", {})
        if isinstance(dashboard_bundle.get("impact_metrics", {}), dict)
        else {}
    )
    department_assignments = (
        dashboard_bundle.get("department_assignments", [])
        if isinstance(dashboard_bundle.get("department_assignments", []), list)
        else []
    )
    sla_overview = (
        dashboard_bundle.get("sla_overview", {})
        if isinstance(dashboard_bundle.get("sla_overview", {}), dict)
        else {}
    )
    zone_performance = (
        dashboard_bundle.get("zone_performance", [])
        if isinstance(dashboard_bundle.get("zone_performance", []), list)
        else []
    )
    executive_summary = (
        dashboard_bundle.get("executive_summary", {})
        if isinstance(dashboard_bundle.get("executive_summary", {}), dict)
        else {}
    )

    render_metric_strip(issues, analytics, trust, clusters, crisis_alerts_payload)
    workspace = render_workspace_switch(
        "Admin workspace",
        ["Performance", "Command Center", "Social Pulse", "Cluster Intelligence", "Operations Desk", "Policy Management"],
        "admin_workspace",
    )

    st.markdown('<div class="gm-content-shell">', unsafe_allow_html=True)
    if workspace == "Performance":
        render_executive_mode(
            executive_summary,
            impact_metrics,
            department_assignments,
            sla_overview,
            zone_performance,
        )
    elif workspace == "Command Center":
        render_command_center(analytics, trends, crisis_alerts_payload)
    elif workspace == "Social Pulse":
        render_social_pulse(social_pulse)
    elif workspace == "Cluster Intelligence":
        render_cluster_intelligence(clusters, insights, policy_recommendations, governance_memory)
    elif workspace == "Policy Management":
        render_policy_management()
    else:
        render_operations_desk(issues, resolved_issues, clusters)
    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
