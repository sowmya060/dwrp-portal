"""
Domestic Worker Registration Portal — Government Admin Panel
Run: streamlit run admin.py --server.port 8502
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from data import SEED_WORKERS, compute_trust, trust_color, build_verification

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DWRP Admin Panel — Government",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&family=DM+Serif+Display&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1rem !important; }

.admin-navbar {
    background: #223355;
    color: white;
    padding: 14px 24px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 24px;
}
.admin-title { font-size: 17px; font-weight: 600; }
.admin-sub   { font-size: 12px; opacity: 0.65; margin-top: 2px; }

.stat-card {
    background: white;
    border: 1px solid #c8d3e8;
    border-radius: 12px;
    padding: 18px 20px;
    text-align: center;
}
.stat-num   { font-size: 36px; font-weight: 700; line-height: 1; margin-bottom: 4px; }
.stat-label { font-size: 12px; color: #8899bb; }

.section-title {
    font-family: 'DM Serif Display', serif;
    font-size: 18px;
    color: #223355;
    border-bottom: 2px solid #ddeeff;
    padding-bottom: 8px;
    margin-bottom: 16px;
}

.badge { display: inline-block; padding: 3px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; }
.badge-blue   { background: #ddeeff; color: #1a5fb4; }
.badge-green  { background: #e8f5ec; color: #2d8a4e; }
.badge-amber  { background: #fef3c7; color: #b45309; }
.badge-red    { background: #fee2e2; color: #b91c1c; }
.badge-gray   { background: #e8edf5; color: #445577; }

.info-box    { background: #ddeeff; color: #1a5fb4; border-radius: 8px; padding: 10px 14px; font-size: 13px; margin: 8px 0; }
.success-box { background: #e8f5ec; color: #2d8a4e; border-radius: 8px; padding: 10px 14px; font-size: 13px; margin: 8px 0; }
.warn-box    { background: #fef3c7; color: #b45309; border-radius: 8px; padding: 10px 14px; font-size: 13px; margin: 8px 0; }

.bar-label { font-size: 12px; color: #445577; text-align: right; }
.bar-bg    { background: #e8edf5; border-radius: 4px; height: 18px; overflow: hidden; }
.bar-fill  { height: 100%; border-radius: 4px; }
</style>
""", unsafe_allow_html=True)


# ── Session state ─────────────────────────────────────────────────────────────
if "workers" not in st.session_state:
    st.session_state.workers = {w["worker_id"]: w for w in SEED_WORKERS}
if "complaints" not in st.session_state:
    st.session_state.complaints = []

# ── Navbar ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="admin-navbar">
  <div style="font-size:28px">🏛️</div>
  <div>
    <div class="admin-title">Domestic Worker Registration Portal — Government Admin Panel</div>
    <div class="admin-sub">Ministry of Labour &amp; Employment · Restricted Access</div>
  </div>
  <div style="margin-left:auto">
    <span class="badge badge-green">● Live</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Sidebar filters ───────────────────────────────────────────────────────────
st.sidebar.title("🔎 Filters")

all_workers = list(st.session_state.workers.values())

f_nationality = st.sidebar.multiselect(
    "Nationality",
    ["Indian", "Nepal / Bhutan", "Foreign"],
    default=["Indian", "Nepal / Bhutan", "Foreign"],
)
f_police = st.sidebar.multiselect(
    "Police Status",
    ["Verified", "Pending", "Not Verified"],
    default=["Verified", "Pending", "Not Verified"],
)
f_flagged = st.sidebar.selectbox("Flagged Status", ["All", "Flagged only", "Not flagged"])
f_trust = st.sidebar.slider("Min Trust Score", 0, 100, 0)
f_search = st.sidebar.text_input("Search by name / ID", placeholder="e.g. Sunita or DW-4821")

# Apply filters
filtered = [
    w for w in all_workers
    if w.get("nationality") in f_nationality
    and w.get("police_status", "Not Verified") in f_police
    and (f_flagged == "All"
         or (f_flagged == "Flagged only" and w.get("flagged"))
         or (f_flagged == "Not flagged" and not w.get("flagged")))
    and w.get("trust_score", 0) >= f_trust
    and (
        not f_search
        or f_search.lower() in w.get("name", "").lower()
        or f_search.upper() in w.get("worker_id", "")
    )
]

st.sidebar.markdown("---")
st.sidebar.markdown(f"**{len(filtered)}** workers shown out of **{len(all_workers)}**")


# ── Admin tabs ────────────────────────────────────────────────────────────────
tab_dash, tab_workers, tab_verify, tab_complaints = st.tabs([
    "📊 Dashboard", "👥 All Workers", "✅ Verify Worker", "🚨 Complaints"
])


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
with tab_dash:
    st.markdown('<div class="section-title">National Overview</div>', unsafe_allow_html=True)

    total   = len(all_workers)
    verified_count = sum(1 for w in all_workers if w.get("trust_score", 0) >= 70)
    partial_count  = sum(1 for w in all_workers if 40 <= w.get("trust_score", 0) < 70)
    low_count      = sum(1 for w in all_workers if w.get("trust_score", 0) < 40)
    police_v       = sum(1 for w in all_workers if w.get("police_status") == "Verified")
    police_p       = sum(1 for w in all_workers if w.get("police_status") == "Pending")
    flagged_count  = sum(1 for w in all_workers if w.get("flagged"))

    c1, c2, c3, c4, c5 = st.columns(5)
    stats = [
        (c1, total,          "#1a5fb4", "Total Registered"),
        (c2, verified_count, "#2d8a4e", "High Trust (≥70)"),
        (c3, partial_count,  "#f59e0b", "Moderate Trust"),
        (c4, low_count,      "#b91c1c", "Low Trust (<40)"),
        (c5, police_v,       "#1a5fb4", "Police Verified"),
    ]
    for col, num, color, label in stats:
        with col:
            st.markdown(f"""
            <div class="stat-card">
              <div class="stat-num" style="color:{color}">{num}</div>
              <div class="stat-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_left, col_right = st.columns(2)

    # ── Nationality breakdown ──────────────────────────────────────────────
    with col_left:
        st.markdown('<div class="section-title">Workers by Nationality</div>', unsafe_allow_html=True)
        nat_counts = {}
        for w in all_workers:
            n = w.get("nationality", "Unknown")
            nat_counts[n] = nat_counts.get(n, 0) + 1

        nat_colors = {"Indian": "#1a5fb4", "Nepal / Bhutan": "#3584e4", "Foreign": "#85b7eb"}
        for nat, count in sorted(nat_counts.items(), key=lambda x: -x[1]):
            pct = (count / total * 100) if total else 0
            color = nat_colors.get(nat, "#8899bb")
            flag  = "🇮🇳" if nat == "Indian" else "🇳🇵" if nat == "Nepal / Bhutan" else "🌐"
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px">
              <div style="width:130px;font-size:12px;color:#445577;text-align:right">
                {flag} {nat}
              </div>
              <div class="bar-bg" style="flex:1">
                <div class="bar-fill" style="width:{pct:.0f}%;background:{color}"></div>
              </div>
              <div style="width:36px;font-size:12px;font-weight:500;color:#445577">{count}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── Skill breakdown ────────────────────────────────────────────────────
    with col_right:
        st.markdown('<div class="section-title">Workers by Skill</div>', unsafe_allow_html=True)
        skill_counts = {}
        for w in all_workers:
            s = w.get("skill", "Other")
            skill_counts[s] = skill_counts.get(s, 0) + 1

        skill_colors = ["#2d8a4e", "#3d9b5e", "#52b06f", "#6fc482", "#9ed4a8"]
        for i, (skill, count) in enumerate(sorted(skill_counts.items(), key=lambda x: -x[1])[:8]):
            pct   = (count / total * 100) if total else 0
            color = skill_colors[i % len(skill_colors)]
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px">
              <div style="width:130px;font-size:12px;color:#445577;text-align:right">{skill}</div>
              <div class="bar-bg" style="flex:1">
                <div class="bar-fill" style="width:{pct:.0f}%;background:{color}"></div>
              </div>
              <div style="width:36px;font-size:12px;font-weight:500;color:#445577">{count}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── State breakdown (Indian only) ──────────────────────────────────────
    st.markdown('<div class="section-title" style="margin-top:24px">Indian Workers by State</div>',
                unsafe_allow_html=True)
    state_counts = {}
    for w in all_workers:
        if w.get("nationality") == "Indian" and w.get("state"):
            s = w["state"]
            state_counts[s] = state_counts.get(s, 0) + 1

    if state_counts:
        df_state = pd.DataFrame(
            sorted(state_counts.items(), key=lambda x: -x[1]),
            columns=["State", "Count"]
        )
        st.bar_chart(df_state.set_index("State"))
    else:
        st.caption("No state data available.")

    # ── Trust distribution ─────────────────────────────────────────────────
    st.markdown('<div class="section-title" style="margin-top:24px">Trust Score Distribution</div>',
                unsafe_allow_html=True)
    bins = {"0–19": 0, "20–39": 0, "40–59": 0, "60–79": 0, "80–100": 0}
    for w in all_workers:
        ts = w.get("trust_score", 0)
        if ts < 20:    bins["0–19"]   += 1
        elif ts < 40:  bins["20–39"]  += 1
        elif ts < 60:  bins["40–59"]  += 1
        elif ts < 80:  bins["60–79"]  += 1
        else:          bins["80–100"] += 1

    df_trust = pd.DataFrame({"Range": list(bins.keys()), "Count": list(bins.values())})
    st.bar_chart(df_trust.set_index("Range"))


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — ALL WORKERS TABLE
# ═══════════════════════════════════════════════════════════════════════════════
with tab_workers:
    st.markdown(f'<div class="section-title">Worker Registry — {len(filtered)} workers</div>',
                unsafe_allow_html=True)

    if not filtered:
        st.warning("No workers match your current filters.")
    else:
        # Build display dataframe
        rows = []
        for w in filtered:
            ts = w.get("trust_score", 0)
            rows.append({
                "Worker ID":   w["worker_id"],
                "Name":        w["name"],
                "Nationality": w.get("nationality", "—"),
                "Skill":       w.get("skill", "—"),
                "State":       w.get("state") or "—",
                "Trust Score": ts,
                "Identity":    w.get("verification", {}).get("Identity", "—"),
                "Police":      w.get("verification", {}).get("Police", "—"),
                "Registered":  w.get("registered_at", "—"),
                "Flagged":     "⚠️ Yes" if w.get("flagged") else "—",
            })

        df = pd.DataFrame(rows)

        # Colour-code trust score column
        def colour_trust(val):
            if val >= 70:   return "color: #2d8a4e; font-weight: 600"
            if val >= 40:   return "color: #f59e0b; font-weight: 600"
            return "color: #b91c1c; font-weight: 600"

        styled = df.style.applymap(colour_trust, subset=["Trust Score"])
        st.dataframe(styled, use_container_width=True, hide_index=True)

        # CSV export
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Export to CSV",
            data=csv,
            file_name=f"workers_export_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
        )


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — VERIFY / MANAGE INDIVIDUAL WORKER
# ═══════════════════════════════════════════════════════════════════════════════
with tab_verify:
    st.markdown('<div class="section-title">Verify / Manage Worker</div>', unsafe_allow_html=True)

    search_id = st.text_input("Enter Worker ID", placeholder="e.g. DW-4821").strip().upper()

    if search_id:
        w = st.session_state.workers.get(search_id)
        if not w:
            st.error("Worker not found.")
        else:
            ts = w.get("trust_score", 0)
            tc_col = {"green": "#2d8a4e", "orange": "#f59e0b", "red": "#b91c1c"}[trust_color(ts)]

            # Summary row
            ci, cn, cs, ct = st.columns(4)
            ci.metric("Worker ID",    w["worker_id"])
            cn.metric("Name",         w["name"])
            cs.metric("Skill",        w.get("skill", "—"))
            ct.metric("Trust Score",  ts)

            st.markdown("---")

            col_actions, col_info = st.columns([1, 1])

            with col_actions:
                st.markdown("**🔧 Admin Actions**")

                # Approve identity
                if st.button("✅ Approve Identity", use_container_width=True):
                    st.session_state.workers[search_id]["verification"]["Identity"] = "✅ Verified"
                    st.session_state.workers[search_id]["flagged"] = False
                    new_ts = min(ts + 10, 100)
                    st.session_state.workers[search_id]["trust_score"] = new_ts
                    st.success(f"Identity approved. Trust score → {new_ts}")
                    st.rerun()

                # Mark police verified
                if st.button("🔵 Mark Police Verified", use_container_width=True):
                    st.session_state.workers[search_id]["police_status"] = "Verified"
                    st.session_state.workers[search_id]["verification"]["Police"] = "✅ Verified"
                    new_ts = compute_trust(st.session_state.workers[search_id])
                    st.session_state.workers[search_id]["trust_score"] = new_ts
                    st.success(f"Police verification confirmed. Trust score → {new_ts}")
                    st.rerun()

                # Flag worker
                if st.button("⚠️ Flag Worker", use_container_width=True):
                    st.session_state.workers[search_id]["flagged"] = True
                    new_ts = max(ts - 15, 0)
                    st.session_state.workers[search_id]["trust_score"] = new_ts
                    st.warning(f"Worker flagged. Trust score reduced to {new_ts}.")
                    st.rerun()

                # Unflag
                if w.get("flagged") and st.button("✔️ Remove Flag", use_container_width=True):
                    st.session_state.workers[search_id]["flagged"] = False
                    st.success("Flag removed.")
                    st.rerun()

                st.markdown("---")
                st.markdown("**Manual Trust Score Override**")
                new_score = st.number_input("Set Trust Score", 0, 100, value=ts, key="manual_trust")
                if st.button("Update Trust Score", use_container_width=True):
                    st.session_state.workers[search_id]["trust_score"] = new_score
                    st.success(f"Trust score updated to {new_score}.")
                    st.rerun()

            with col_info:
                st.markdown("**📋 Current Verification Status**")
                for k, v in w.get("verification", {}).items():
                    st.markdown(f"**{k}:** {v}")

                st.markdown("---")
                st.markdown("**📄 Documents Submitted**")
                docs = w.get("docs", [])
                if docs:
                    for d in docs:
                        st.markdown(f"- {d}")
                else:
                    st.caption("No documents submitted.")

                st.markdown("---")
                st.markdown("**🔗 Full Worker Record**")
                st.json({
                    k: v for k, v in w.items()
                    if k not in ("feedbacks", "complaints")
                }, expanded=False)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — COMPLAINTS
# ═══════════════════════════════════════════════════════════════════════════════
with tab_complaints:
    st.markdown('<div class="section-title">Complaints Registry</div>', unsafe_allow_html=True)

    complaints = st.session_state.complaints
    if not complaints:
        st.info("No complaints filed yet.")
    else:
        st.markdown(f"**{len(complaints)} complaint(s) on record.**")

        # Status filter
        cstatus_filter = st.selectbox("Filter by status", ["All", "Open", "In Review", "Resolved"])

        for c in reversed(complaints):
            if cstatus_filter != "All" and c.get("status") != cstatus_filter:
                continue

            with st.expander(f"{c['id']} — {c['type']} ({c['status']})"):
                st.markdown(f"**Worker ID:** {c['worker_id']}")
                st.markdown(f"**Type:** {c['type']}")
                st.markdown(f"**Description:** {c['description']}")
                st.markdown(f"**Filed:** {c['created_at']}")

                col_s1, col_s2, col_s3 = st.columns(3)
                with col_s1:
                    if st.button("Mark In Review", key=f"review_{c['id']}"):
                        c["status"] = "In Review"
                        st.rerun()
                with col_s2:
                    if st.button("Mark Resolved", key=f"resolve_{c['id']}"):
                        c["status"] = "Resolved"
                        st.rerun()
                with col_s3:
                    st.markdown(
                        f'<span class="badge {"badge-amber" if c["status"]=="Open" else "badge-green" if c["status"]=="Resolved" else "badge-blue"}">'
                        f'{c["status"]}</span>',
                        unsafe_allow_html=True
                    )
