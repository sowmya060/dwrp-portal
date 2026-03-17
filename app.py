"""
Domestic Worker Registration Portal — Public App
Run: streamlit run app.py
"""

import streamlit as st
from datetime import datetime
from data import (
    SEED_WORKERS, STATES,
    REQUIRED_DOCS, OPTIONAL_BOOST_DOCS,
    compute_trust, trust_color, trust_label,
    generate_id, build_verification,
)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Domestic Worker Registration Portal",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&family=DM+Serif+Display&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

/* Hide default Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1rem !important; }

/* Navbar */
.navbar {
    background: #1a5fb4;
    color: white;
    padding: 14px 28px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 24px;
}
.navbar-title { font-size: 17px; font-weight: 600; }
.navbar-sub { font-size: 12px; opacity: 0.75; margin-top: 2px; }

/* Hero */
.hero {
    background: linear-gradient(135deg, #1a5fb4 0%, #2771c9 60%, #3584e4 100%);
    color: white;
    padding: 48px 32px;
    border-radius: 16px;
    text-align: center;
    margin-bottom: 28px;
}
.hero h1 { font-family: 'DM Serif Display', serif; font-size: 32px; margin-bottom: 12px; }
.hero p  { font-size: 15px; opacity: 0.88; max-width: 520px; margin: 0 auto 24px; line-height: 1.6; }
.hero-badges { display: flex; justify-content: center; gap: 20px; font-size: 12px; opacity: 0.78; flex-wrap: wrap; }

/* Benefit card */
.benefit-card {
    background: white;
    border: 1px solid #c8d3e8;
    border-radius: 12px;
    padding: 18px;
    height: 100%;
    transition: border-color 0.15s;
}
.benefit-card:hover { border-color: #3584e4; }
.benefit-icon { font-size: 22px; margin-bottom: 8px; }
.benefit-title { font-size: 13px; font-weight: 600; color: #1a5fb4; margin-bottom: 5px; }
.benefit-desc  { font-size: 12px; color: #445577; line-height: 1.55; }

/* FAQ */
.faq-answer { font-size: 13px; color: #445577; line-height: 1.65; padding: 4px 0 8px; }

/* Trust bar */
.trust-bar-wrap { background: #e8edf5; border-radius: 6px; height: 12px; overflow: hidden; margin: 6px 0; }
.trust-bar-fill  { height: 100%; border-radius: 6px; transition: width 0.4s; }

/* Section title */
.section-title {
    font-family: 'DM Serif Display', serif;
    font-size: 20px;
    color: #223355;
    border-bottom: 2px solid #ddeeff;
    padding-bottom: 8px;
    margin-bottom: 18px;
}

/* Profile header */
.profile-header {
    background: #1a5fb4;
    color: white;
    padding: 20px 24px;
    border-radius: 12px 12px 0 0;
    display: flex;
    align-items: center;
    gap: 16px;
}
.profile-avatar {
    width: 52px; height: 52px;
    background: rgba(255,255,255,0.2);
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 20px; font-weight: 600;
}
.profile-name { font-size: 18px; font-weight: 600; }
.profile-sub  { font-size: 12px; opacity: 0.8; }

/* Badges */
.badge { display: inline-block; padding: 3px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; }
.badge-blue   { background: #ddeeff; color: #1a5fb4; }
.badge-green  { background: #e8f5ec; color: #2d8a4e; }
.badge-amber  { background: #fef3c7; color: #b45309; }
.badge-red    { background: #fee2e2; color: #b91c1c; }
.badge-gray   { background: #e8edf5; color: #445577; }

/* Info boxes */
.info-box  { background: #ddeeff; color: #1a5fb4; border-radius: 8px; padding: 10px 14px; font-size: 13px; margin: 8px 0; }
.warn-box  { background: #fef3c7; color: #b45309; border-radius: 8px; padding: 10px 14px; font-size: 13px; margin: 8px 0; }
.error-box { background: #fee2e2; color: #b91c1c; border-radius: 8px; padding: 10px 14px; font-size: 13px; margin: 8px 0; }
.success-box { background: #e8f5ec; color: #2d8a4e; border-radius: 8px; padding: 10px 14px; font-size: 13px; margin: 8px 0; }

/* Worker ID display */
.worker-id-box {
    background: #1a5fb4; color: white;
    border-radius: 12px; padding: 24px;
    text-align: center; margin: 20px 0;
}
.worker-id-code { font-size: 36px; font-weight: 700; letter-spacing: 3px; font-family: monospace; }
.worker-id-label { font-size: 12px; opacity: 0.75; margin-bottom: 6px; }

/* Station card */
.station-card {
    background: white; border: 1px solid #c8d3e8;
    border-radius: 10px; padding: 14px 16px; margin-top: 10px;
}
</style>
""", unsafe_allow_html=True)


# ── Session state ─────────────────────────────────────────────────────────────
if "workers" not in st.session_state:
    st.session_state.workers = {w["worker_id"]: w for w in SEED_WORKERS}
if "complaints" not in st.session_state:
    st.session_state.complaints = []
if "reg_step" not in st.session_state:
    st.session_state.reg_step = 1
if "reg_data" not in st.session_state:
    st.session_state.reg_data = {}
if "last_registered" not in st.session_state:
    st.session_state.last_registered = None


# ── Navbar ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="navbar">
  <div style="font-size:26px">🇮🇳</div>
  <div>
    <div class="navbar-title">Domestic Worker Registration Portal</div>
    <div class="navbar-sub">Government of India — Ministry of Labour & Employment</div>
  </div>
</div>
""", unsafe_allow_html=True)


# ── Tab navigation ────────────────────────────────────────────────────────────
tab_home, tab_reg, tab_lookup, tab_complaint = st.tabs([
    "Home", "Register", "Worker Lookup", "File Complaint"
])


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — HOME
# ═══════════════════════════════════════════════════════════════════════════════
with tab_home:
    st.markdown("""
    <div class="hero">
      <h1>Protect Your Rights. Build Your Future.</h1>
      <p>A government initiative to register, verify, and protect domestic workers across India.
         Free, safe, and confidential.</p>
      <div class="hero-badges">
        <span>Government Protected</span>
        <span>100% Free</span>
        <span>Mobile Friendly</span>
        <span>Multi-language Coming Soon</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">Benefits of Registration</div>', unsafe_allow_html=True)

    benefits = [
        ("", "Accident Insurance",
         "₹2 lakh coverage under PMSBY for accidental death or permanent disability. ₹1 lakh for partial disability."),
        ("", "Healthcare Coverage",
         "Access Ayushman Bharat (AB-PMJAY) for free hospitalisation up to ₹5 lakh/year."),
        ("", "Pension Scheme",
         "₹3,000/month pension after age 60 via PM-SYM. Government matches your contribution every month."),
        ("", "Emergency Assistance",
         "Government can reach you during national crises like COVID-19 for direct monetary relief."),
        ("", "Skill Training",
         "Free access to Skill India Digital portal for courses, certifications and apprenticeships."),
        ("", "Portability of Benefits",
         "Your welfare benefits follow you even if you move cities or states. No need to re-register."),
        ("", "Report Underpayment",
         "Being paid below minimum wage? File a complaint directly. We investigate every case."),
        ("", "Harassment Protection",
         "Report workplace harassment or abuse. Your identity is protected during the entire inquiry."),
    ]

    cols = st.columns(4)
    for i, (icon, title, desc) in enumerate(benefits):
        with cols[i % 4]:
            st.markdown(f"""
            <div class="benefit-card">
              <div class="benefit-icon">{icon}</div>
              <div class="benefit-title">{title}</div>
              <div class="benefit-desc">{desc}</div>
            </div><br>
            """, unsafe_allow_html=True)

    st.markdown('<div class="section-title" style="margin-top:32px">Frequently Asked Questions</div>',
                unsafe_allow_html=True)

    faqs = [
        ("Is my data safe with the government?",
         "Yes. All data is encrypted and stored under India's Personal Data Protection framework. "
         "Your information is not shared with private parties without your consent."),
        ("What if I don't have an Aadhaar card?",
         "You can still register with alternative documents. You'll receive a lower initial trust score, "
         "but the portal provides links to apply for Aadhaar. Benefits unlock once Aadhaar is linked."),
        ("Can my employer force me to register?",
         "No. Registration must be done with your consent. If registering via employer, "
         "you will receive an OTP on your phone which only you can confirm."),
        ("What happens if I change employers?",
         "Your Worker ID stays with you permanently. Your profile can be updated. "
         "Previous work history is preserved with your consent."),
        ("Do I need to pay anything?",
         "Registration is completely free. Any person charging a fee is acting illegally and should be reported."),
        ("What if I have no phone number?",
         "You can register through a government agent or your employer who will act as a verified intermediary."),
        ("What is police verification? Is it mandatory?",
         "Police verification is a background check that increases your trust score by +25 points and adds a "
         "verified badge. It is voluntary but strongly recommended as employers prefer verified workers."),
        ("What is a Trust Score?",
         "A Trust Score (0–100) reflects how complete and verified your registration is. "
         "Higher scores unlock more benefits and make you more attractive to employers."),
    ]

    for q, a in faqs:
        with st.expander(q):
            st.markdown(f'<div class="faq-answer">{a}</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — REGISTER
# ═══════════════════════════════════════════════════════════════════════════════
with tab_reg:
    st.markdown("###  Worker Registration")
    st.caption("Complete all required fields. Your information is protected under Government of India data privacy laws.")

    # ── Live trust meter ──────────────────────────────────────────────────────
    rd = st.session_state.reg_data
    # Police bonus only applies once user reaches step 3
    # Docs only count if actually uploaded (uploaded_docs key)
    _include_police = st.session_state.reg_step >= 3
    live_score = compute_trust(rd, include_police=_include_police) if rd else 0
    tc = trust_color(live_score)
    color_map = {"green": "#2d8a4e", "orange": "#f59e0b", "red": "#b91c1c"}
    fill_color = color_map[tc]

    st.markdown(f"""
    <div style="background:white;border:1px solid #c8d3e8;border-radius:12px;padding:16px;margin-bottom:20px">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
        <span style="font-size:13px;color:#445577;font-weight:500">Live Trust Score</span>
        <span style="font-size:28px;font-weight:700;color:{fill_color};line-height:1">{live_score}</span>
      </div>
      <div class="trust-bar-wrap">
        <div class="trust-bar-fill" style="width:{live_score}%;background:{fill_color}"></div>
      </div>
      <div style="font-size:11px;color:#8899bb;margin-top:4px">{trust_label(live_score)}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Step indicator ────────────────────────────────────────────────────────
    step = st.session_state.reg_step
    step_cols = st.columns(3)
    for i, label in enumerate(["1 · Identity", "2 · Documents", "3 · Verification"]):
        with step_cols[i]:
            if step > i + 1:
                st.success(f"✓ {label}")
            elif step == i + 1:
                st.info(f"▶ {label}")
            else:
                st.markdown(f"<div style='color:#8899bb;font-size:13px;text-align:center'>{label}</div>",
                            unsafe_allow_html=True)

    st.markdown("---")

    # ══════════════════════════════════════════════════════════════════════════
    # STEP 1 — Identity
    # ══════════════════════════════════════════════════════════════════════════
    if step == 1:
        # Section A
        st.markdown("**Section A — Basic Information**")
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Full Name *", placeholder="As per ID document",
                                 value=rd.get("name", ""))
            gender = st.selectbox("Gender *", ["", "Male", "Female", "Other"],
                                  index=["", "Male", "Female", "Other"].index(rd.get("gender", "")))
        with c2:
            age = st.number_input("Age *", min_value=0, max_value=100, value=int(rd.get("age", 0)) or 0)
            skill = st.text_input("Skill / Occupation *", placeholder="e.g. Cook, Driver, Caretaker",
                                  value=rd.get("skill", ""))

        if age and 0 < age < 18:
            st.markdown('<div class="warn-box">⚠️ Registrant appears to be under 18. '
                        'A guardian must be present and this registration will be flagged for review.</div>',
                        unsafe_allow_html=True)

        # Phone
        st.markdown("**Phone Number**")
        phone_type = st.radio(
            "Phone type",
            ["Personal (Aadhaar-linked)", "Family / Shared", "No Phone"],
            horizontal=True,
            index=["Personal (Aadhaar-linked)", "Family / Shared", "No Phone"]
                  .index(rd.get("phone_type", "Personal (Aadhaar-linked)")),
            label_visibility="collapsed",
        )
        if phone_type == "No Phone":
            st.markdown('<div class="warn-box">No phone requires registration by an Agent or Employer. '
                        'You cannot self-register.</div>', unsafe_allow_html=True)
            phone = None
        elif phone_type == "Family / Shared":
            st.markdown('<div class="info-box">This number will be marked as indirect contact. '
                        'Verification may take longer.</div>', unsafe_allow_html=True)
            phone = st.text_input("Phone Number", placeholder="10-digit mobile", value=rd.get("phone", "") or "")
        else:
            phone = st.text_input("Phone Number", placeholder="10-digit Aadhaar-linked number",
                                  value=rd.get("phone", "") or "")

        st.markdown("---")

        # Section B — Nationality
        st.markdown("**Nationality**")
        nationality = st.selectbox(
            "Nationality *",
            ["", "Indian", "Nepal / Bhutan", "Foreign"],
            index=["", "Indian", "Nepal / Bhutan", "Foreign"].index(rd.get("nationality", "")),
        )
        country = None
        state   = None
        if nationality == "Foreign":
            st.markdown('<div class="info-box">Foreign nationals with valid work permits must be registered '
                        'with FRRO. Ensure you have Form C if live-in.</div>', unsafe_allow_html=True)
            country = st.text_input("Country Name *", value=rd.get("country", "") or "")
        if nationality == "Indian":
            state = st.selectbox("Home State *", [""] + STATES,
                                 index=([""] + STATES).index(rd.get("state", "") or ""))

        st.markdown("---")

        # Section C — Registration Mode
        st.markdown("**Registration Mode**")
        reg_mode = st.selectbox(
            "Registering as *",
            ["", "Self", "Employer", "Agent"],
            index=["", "Self", "Employer", "Agent"].index(rd.get("reg_mode", "")),
        )
        employer_aadhaar = None
        agent_id         = None

        if reg_mode == "Employer":
            st.markdown('<div class="info-box">Employer Aadhaar is used instead of name for verification. '
                        'It will be masked in public records. Worker consent via OTP is required.</div>',
                        unsafe_allow_html=True)
            employer_aadhaar = st.text_input("Employer Aadhaar (masked) *",
                                             placeholder="XXXX-XXXX-1234",
                                             value=rd.get("employer_aadhaar", "") or "")
            st.text_input("Worker Consent OTP *",
                          placeholder="Worker must confirm on their phone — enter OTP here")

        if reg_mode == "Agent":
            st.markdown('<div class="info-box">Agent photo and ID are mandatory for fraud prevention.</div>',
                        unsafe_allow_html=True)
            agent_id = st.text_input("Government Agent ID *", placeholder="e.g. AGT-2024-MH-0012",
                                     value=rd.get("agent_id", "") or "")
            st.file_uploader("Agent Photograph (mandatory) *", type=["jpg", "jpeg", "png"])

        # Duplicate check hint
        if phone and phone_type != "No Phone":
            dup = [w for w in st.session_state.workers.values() if w.get("phone") == phone]
            if dup:
                st.markdown(f'<div class="warn-box">A worker with this phone is already registered: '
                            f'<strong>{dup[0]["worker_id"]}</strong>. '
                            f'Please verify or update the existing record.</div>',
                            unsafe_allow_html=True)

        # Next button
        if st.button("Continue to Documents →", type="primary", use_container_width=True):
            errors = []
            if not name:       errors.append("Full Name is required.")
            if not age:        errors.append("Age is required.")
            if not gender:     errors.append("Gender is required.")
            if not skill:      errors.append("Skill / Occupation is required.")
            if not nationality: errors.append("Nationality is required.")
            if not reg_mode:   errors.append("Registration mode is required.")
            if phone_type == "No Phone" and reg_mode == "Self":
                errors.append("Workers without a phone must register via an Agent or Employer.")
            if errors:
                for e in errors:
                    st.error(e)
            else:
                st.session_state.reg_data = {
                    **rd,
                    "name": name, "age": age, "gender": gender, "skill": skill,
                    "phone": phone, "phone_type": phone_type,
                    "nationality": nationality, "country": country, "state": state,
                    "reg_mode": reg_mode, "employer_aadhaar": employer_aadhaar, "agent_id": agent_id,
                    "docs": rd.get("docs", []),
                    "references": rd.get("references", [{"name": "", "phone": ""},
                                                         {"name": "", "phone": ""}]),
                }
                st.session_state.reg_step = 2
                st.rerun()

    # ══════════════════════════════════════════════════════════════════════════
    # STEP 2 — Documents
    # ══════════════════════════════════════════════════════════════════════════
    elif step == 2:
        nat = rd.get("nationality", "Indian")

        st.markdown(f"**Document Verification ({nat})**")

        # Build doc lists per nationality
        if nat == "Indian":
            req_docs = [
                "Photograph", "Aadhaar Card", "Address Proof",
            ]
            opt_docs = [
                "Bank Details", "PAN Card", "Ration Card",
                "Permanent Address Proof", "Educational Certificates", "Skill Certification",
            ]
        elif nat == "Nepal / Bhutan":
            req_docs = ["Citizenship Card", "Address Proof"]
            opt_docs = ["Indian Aadhaar (if issued)", "Police Clearance (home country)"]
        else:  # Foreign
            req_docs = [
                "Passport", "Visa", "Work Permit",
                "FRRO Registration", "Police Clearance Certificate",
            ]
            opt_docs = ["Form C (for live-in staff)"]

        # Driving licence is mandatory if skill is Driver
        skill_lower = rd.get("skill", "").strip().lower()
        is_driver = any(w in skill_lower for w in ["driver", "driving", "chauffeur"])
        if is_driver and "Driving Licence" not in req_docs:
            req_docs.insert(0, "Driving Licence")
            st.markdown("""
            <div class="warn-box">
            🚗 <strong>Driver skill detected.</strong> A valid Driving Licence is required as a mandatory document.
            </div>
            """, unsafe_allow_html=True)

        # current_docs = what the user has SELECTED (checkbox ticked)
        # uploaded_docs = subset that have an actual file attached → counts toward trust score
        current_docs  = list(rd.get("docs", []))
        uploaded_docs = list(rd.get("uploaded_docs", []))

        st.markdown("**Required documents** — tick the box, then upload the file to earn trust points:")
        for doc in req_docs:
            checked = st.checkbox(doc, value=(doc in current_docs), key=f"doc_req_{doc}")
            if checked and doc not in current_docs:
                current_docs.append(doc)
            elif not checked and doc in current_docs:
                current_docs = [d for d in current_docs if d != doc]
                uploaded_docs = [d for d in uploaded_docs if d != doc]

        st.markdown("**Optional documents** — each uploaded file to increase your trust score:")
        for doc in opt_docs:
            checked = st.checkbox(f"{doc} ", value=(doc in current_docs), key=f"doc_opt_{doc}")
            if checked and doc not in current_docs:
                current_docs.append(doc)
            elif not checked and doc in current_docs:
                current_docs = [d for d in current_docs if d != doc]
                uploaded_docs = [d for d in uploaded_docs if d != doc]

        # File uploaders — trust score increases ONLY when file is actually attached
        if current_docs:
            st.markdown("---")
            st.info("Upload each document below. Trust score increases only when a file is attached.")
            for doc in current_docs:
                f = st.file_uploader(
                    f"Upload: {doc}",
                    type=["jpg", "jpeg", "png", "pdf"],
                    key=f"upload_{doc}",
                )
                if f is not None:
                    if doc not in uploaded_docs:
                        uploaded_docs.append(doc)
                else:
                    uploaded_docs = [d for d in uploaded_docs if d != doc]

        # References (Indian only)
        refs = list(rd.get("references", [{"name": "", "phone": ""}, {"name": "", "phone": ""}]))
        if nat == "Indian":
            st.markdown("---")
            st.markdown("**👥 References (2 contacts required)**")
            st.caption("Each valid reference adds +3 to your trust score.")
            for i in range(2):
                rc1, rc2 = st.columns(2)
                with rc1:
                    rname = st.text_input(f"Reference {i+1} — Name",
                                          value=refs[i].get("name", "") if i < len(refs) else "",
                                          key=f"ref_name_{i}")
                with rc2:
                    rphone = st.text_input(f"Reference {i+1} — Phone",
                                           value=refs[i].get("phone", "") if i < len(refs) else "",
                                           key=f"ref_phone_{i}")
                if i < len(refs):
                    refs[i] = {"name": rname, "phone": rphone}
                else:
                    refs.append({"name": rname, "phone": rphone})

        # Write back — uploaded_docs drives the trust score, docs drives verification map
        st.session_state.reg_data = {
            **rd,
            "docs": current_docs,
            "uploaded_docs": uploaded_docs,
            "references": refs,
        }

        col_back, col_next = st.columns([1, 3])
        with col_back:
            if st.button("← Back"):
                st.session_state.reg_step = 1
                st.rerun()
        with col_next:
            if st.button("Continue to Verification →", type="primary", use_container_width=True):
                st.session_state.reg_data = {
                    **rd,
                    "docs": current_docs,
                    "uploaded_docs": uploaded_docs,
                    "references": refs,
                }
                st.session_state.reg_step = 3
                st.rerun()

    # ══════════════════════════════════════════════════════════════════════════
    # STEP 3 — Police Verification & Submit
    # ══════════════════════════════════════════════════════════════════════════
    elif step == 3:
        st.markdown("**Police Verification**")
        st.markdown("""
        <div class="info-box">
        Police verification is <strong>optional</strong> but adds <strong>+25 trust score</strong>
        and unlocks a verified badge on your profile. Verified workers are preferred by employers —
        it works entirely in your favour.
        </div>
        """, unsafe_allow_html=True)

        police_status = rd.get("police_status", "Not Verified")
        police_area   = None  # no station picker; kept for data schema

        pv_option = st.radio(
            "Police Verification",
            ["Upload existing Police Verification Certificate (PVC)", "Apply for Police Verification", "Skip for Now"],
            horizontal=False,
            label_visibility="collapsed",
        )

        if "Upload" in pv_option:
            st.markdown("""
            <div class="success-box">
            If you already have a Police Verification Certificate, upload it here.
            It will be reviewed by an admin and your profile will be marked <strong>Police Verified</strong>.
            </div>
            """, unsafe_allow_html=True)
            pvc_file = st.file_uploader("Upload Police Verification Certificate (PDF / Image)", type=["jpg","jpeg","png","pdf"], key="pvc_upload")
            if pvc_file:
                police_status = "Pending"
                st.markdown('<span class="badge badge-amber">PVC uploaded — pending admin review</span>', unsafe_allow_html=True)
            else:
                st.markdown('<span class="badge badge-gray">— Waiting for file upload</span>', unsafe_allow_html=True)

        elif "Apply" in pv_option:
            st.markdown("""
            <div style="background:white;border:1px solid #c8d3e8;border-radius:12px;padding:20px;margin-bottom:12px">
              <div style="font-size:14px;font-weight:600;color:#223355;margin-bottom:8px">🔵 Apply for Police Verification</div>
              <div style="font-size:13px;color:#445577;line-height:1.6;margin-bottom:12px">
                A verification request will be sent to the local police authority.
                A police officer will be <strong>randomly assigned</strong> by the system and will
                contact you directly. No station visit required.
                This ensures a fair, corruption-free process.
              </div>
              <div style="display:flex;gap:8px;flex-wrap:wrap">
                <span class="badge badge-green">✓ No station visit required</span>
                <span class="badge badge-blue">✓ Officer randomly assigned</span>
                <span class="badge badge-blue">✓ Adds +25 to trust score once verified</span>
              </div>
            </div>
            """, unsafe_allow_html=True)
            police_status = "Pending"
            st.markdown('<span class="badge badge-amber">Request will be submitted on registration</span>', unsafe_allow_html=True)

        else:
            st.markdown('<span class="badge badge-gray">— Skipped. You can apply later from your profile.</span>', unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("**Duplicate Check**")
        st.markdown("""
        <div class="info-box">
        On submission, the system checks for existing registrations using your phone number
        and Name + Age combination. If a match is found, you will be asked to verify
        or update your existing record.
        </div>
        """, unsafe_allow_html=True)

        col_back, col_sub = st.columns([1, 3])
        with col_back:
            if st.button("← Back"):
                st.session_state.reg_step = 2
                st.rerun()
        with col_sub:
            if st.button("Submit Registration", type="primary", use_container_width=True):
                # Final duplicate check
                phone = rd.get("phone")
                if phone:
                    dups = [w for w in st.session_state.workers.values() if w.get("phone") == phone]
                    if dups:
                        st.error(f"Duplicate found: worker {dups[0]['worker_id']} already uses this phone number.")
                        st.stop()

                # Build and save worker
                existing_ids = set(st.session_state.workers.keys())
                wid = generate_id(existing_ids)

                worker = {
                    **rd,
                    "worker_id":    wid,
                    "police_status": police_status,
                    "police_area":   police_area,
                    "registered_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "flagged":       False,
                    "complaints":    [],
                    "feedbacks":     [],
                }
                # For saved worker, docs = uploaded_docs (files were actually provided)
                worker["docs"] = worker.get("uploaded_docs", worker.get("docs", []))
                worker["trust_score"]  = compute_trust(worker, include_police=True)
                worker["verification"] = build_verification(worker)

                st.session_state.workers[wid] = worker
                st.session_state.last_registered = wid
                st.session_state.reg_step = 4
                st.rerun()

    # ══════════════════════════════════════════════════════════════════════════
    # STEP 4 — Success
    # ══════════════════════════════════════════════════════════════════════════
    elif step == 4:
        wid = st.session_state.last_registered
        w   = st.session_state.workers.get(wid, {})
        ts  = w.get("trust_score", 0)
        tc_col = {"green": "#2d8a4e", "orange": "#f59e0b", "red": "#b91c1c"}[trust_color(ts)]

        pass  # no balloons
        st.success("Registration Successful! Your application has been submitted to the Ministry of Labour & Employment.")

        st.markdown("""<div class="info-box">An SMS confirmation will be sent to your registered phone number. Your application is now under review by the Ministry of Labour & Employment.</div>""", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="worker-id-box">
          <div class="worker-id-label">Your Worker ID</div>
          <div class="worker-id-code">{wid}</div>
          <div style="font-size:12px;opacity:0.75;margin-top:8px">
            Save this ID — you will need it for all future verification and benefit access.
          </div>
        </div>
        """, unsafe_allow_html=True)

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("Trust Score", ts)
        with col_b:
            ver = "Verified" if ts >= 70 else "Partial" if ts >= 40 else "Low"
            st.metric("Verification Status", ver)
        with col_c:
            st.metric("Police Status", w.get("police_status", "Not Verified"))

        st.markdown("**Verification Breakdown:**")
        vdata = w.get("verification", {})
        vcols = st.columns(max(len(vdata), 1))
        for i, (k, v) in enumerate(vdata.items()):
            vcols[i].markdown(f"**{k}**")
            vcols[i].write(v)

        st.markdown("---")
        if st.button("Register Another Worker", use_container_width=True):
            st.session_state.reg_step = 1
            st.session_state.reg_data = {}
            st.session_state.last_registered = None
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — WORKER LOOKUP
# ═══════════════════════════════════════════════════════════════════════════════
with tab_lookup:
    st.markdown("### Worker Lookup")
    st.caption("Employers and agents can verify a registered worker by their Worker ID.")

    col_input, col_btn = st.columns([3, 1])
    with col_input:
        lookup_id = st.text_input(
            "Worker ID",
            placeholder="e.g. DW-4821",
            label_visibility="collapsed"
        ).strip().upper()

    with col_btn:
        do_lookup = st.button("Search", type="primary", use_container_width=True)

    # Only trigger on button click
    if do_lookup:

        if not lookup_id:
            st.warning("Please enter a Worker ID")
        
        else:
            w = st.session_state.workers.get(lookup_id)

            if not w:
                st.markdown(
                    '<div class="warn-box">No worker found with this ID. Please check and try again.</div>',
                    unsafe_allow_html=True
                )

            else:
                # Profile header
                initials = "".join(p[0] for p in w["name"].split())[:2].upper()
                nat_flag = "🇮🇳" if w["nationality"] == "Indian" else "🇳🇵" if w["nationality"] == "Nepal / Bhutan" else ""
                ts = w.get("trust_score", 0)
                state_str = f"· {str(w.get('state'))}" if w.get("state") else ""

                police_badge = '<span class="badge badge-green">Police Verified</span>' if w.get("police_status") == "Verified" else ""
                flag_badge   = '<span class="badge badge-red">Flagged</span>' if w.get("flagged") else ""

                st.markdown(f"""
                <div class="profile-header">
                  <div class="profile-avatar">{initials}</div>
                  <div style="flex:1">
                    <div class="profile-name">{str(w.get('name',''))}</div>
                    <div class="profile-sub">
                      {str(w.get('skill',''))} · {nat_flag} {str(w.get('nationality',''))} {state_str}
                    </div>
                    <div style="margin-top:8px">
                      <span class="badge badge-blue">{w['worker_id']}</span>&nbsp;
                      {police_badge} {flag_badge}
                    </div>
                  </div>
                  <div style="text-align:right">
                    <div style="font-size:11px;opacity:0.75;margin-bottom:2px">Trust Score</div>
                    <div style="font-size:36px;font-weight:700;color:white;line-height:1">{ts}</div>
                  </div>
                </div>
                """, unsafe_allow_html=True)

                # Verification
                st.markdown("**Verification Status:**")
                vcols = st.columns(4)
                for i, (k, v) in enumerate(w.get("verification", {}).items()):
                    vcols[i].markdown(f"**{k}**")
                    vcols[i].write(v)

                st.markdown("---")

                col_info, col_feed = st.columns([1, 1])

                # Worker details
                with col_info:
                    st.markdown("**Worker Details**")
                    details = {
                        "Age": w.get("age"),
                        "Gender": w.get("gender"),
                        "Phone Type": w.get("phone_type"),
                        "Registration Mode": w.get("reg_mode"),
                        "Registered On": w.get("registered_at"),
                        "Police Area": w.get("police_area") or "—",
                    }

                    for k, v in details.items():
                        st.markdown(
                            f"<span style='color:#8899bb;font-size:12px'>{k}</span><br>"
                            f"<span style='font-size:13px;font-weight:500'>{v}</span><br>",
                            unsafe_allow_html=True
                        )

                # Feedback
                with col_feed:
                    st.markdown("**Employer Feedback**")
                    feedbacks = w.get("feedbacks", [])

                    if feedbacks:
                        for fb in feedbacks:
                            stars = "★" * fb["rating"] + "☆" * (5 - fb["rating"])
                            st.markdown(f"{stars} — {fb.get('note', '')}")
                            st.caption(fb.get("created_at", ""))
                    else:
                        st.caption("No feedback yet.")

                    st.markdown("**Add Feedback**")
                    rating = st.select_slider(
                        "Rating",
                        options=[1, 2, 3, 4, 5],
                        format_func=lambda x: "★" * x,
                        key=f"rating_{lookup_id}"
                    )

                    note = st.text_input("Note (optional)", key=f"note_{lookup_id}")

                    if st.button("Submit Feedback", key=f"fb_{lookup_id}"):
                        if "feedbacks" not in st.session_state.workers[lookup_id]:
                            st.session_state.workers[lookup_id]["feedbacks"] = []

                        st.session_state.workers[lookup_id]["feedbacks"].append({
                            "rating": rating,
                            "note": note,
                            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        })

                        st.success("Feedback submitted!")
                        st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — FILE COMPLAINT
# ═══════════════════════════════════════════════════════════════════════════════
with tab_complaint:
    st.markdown("### File a Complaint")
    st.markdown("""
    <div class="info-box">
    Your identity is <strong>fully protected</strong> during the inquiry process.
    All complaints are reviewed by the Ministry of Labour and Employment.
    </div>
    """, unsafe_allow_html=True)

    ctype = st.selectbox("Complaint Type *", [
        "Underpayment / Below Minimum Wage",
        "Workplace Harassment",
        "Physical Abuse",
        "Forced Overtime / No Rest Days",
        "Withheld Salary",
        "Other",
    ])

    c1, c2 = st.columns(2)
    with c1:
        c_worker_id = st.text_input("Worker ID (yours, if you are the worker)", placeholder="e.g. DW-4821")
    with c2:
        c_phone = st.text_input("Contact Phone (optional — for follow-up)", placeholder="Mobile number")

    c_desc = st.text_area("Describe the complaint *",
                          placeholder="Please describe the situation clearly. Include dates and details if possible.",
                          height=140)

    if st.button("Submit Complaint", type="primary", use_container_width=True):
        if not c_desc.strip():
            st.error("Please describe the complaint before submitting.")
        else:
            cid = f"CMP-{len(st.session_state.complaints)+1:04d}"
            st.session_state.complaints.append({
                "id": cid,
                "type": ctype,
                "worker_id": c_worker_id or "Anonymous",
                "phone": c_phone or "Not provided",
                "description": c_desc,
                "status": "Open",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            })
            st.success(f"Complaint filed successfully. Your complaint ID is **{cid}**. "
                       f"You will be contacted if a follow-up is needed.")
