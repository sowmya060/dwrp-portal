"""
Shared in-memory data store and helpers.
Both app.py and admin.py import from here.
Run with:
    streamlit run app.py      # public portal
    streamlit run admin.py    # govt admin panel  (separate terminal / port)
"""

import random
from datetime import datetime

# ── Police stations lookup ────────────────────────────────────────────────────
POLICE_STATIONS = {
    "Ahmedabad Central":  {"name": "Kagdapith Police Station",      "phone": "079-25321234", "hours": "10am–5pm"},
    "Mumbai (Andheri)":   {"name": "Oshiwara Police Station",       "phone": "022-26364444", "hours": "10am–5pm"},
    "Delhi (Karol Bagh)": {"name": "Karol Bagh Police Station",     "phone": "011-25735141", "hours": "9am–6pm"},
    "Bengaluru (Jayanagar)": {"name": "Jayanagar Police Station",   "phone": "080-22943444", "hours": "10am–5pm"},
    "Chennai (T Nagar)":  {"name": "T Nagar Police Station",        "phone": "044-28150200", "hours": "9am–5pm"},
    "Hyderabad (Banjara Hills)": {"name": "Banjara Hills PS",       "phone": "040-27891234", "hours": "10am–5pm"},
    "Kolkata (Park Street)": {"name": "Park Street Police Station", "phone": "033-22271000", "hours": "9am–6pm"},
    "Pune (Shivajinagar)": {"name": "Shivajinagar Police Station",  "phone": "020-25531000", "hours": "10am–5pm"},
}

STATES = [
    "Andhra Pradesh","Arunachal Pradesh","Assam","Bihar","Chhattisgarh","Delhi",
    "Goa","Gujarat","Haryana","Himachal Pradesh","Jharkhand","Karnataka","Kerala",
    "Madhya Pradesh","Maharashtra","Manipur","Meghalaya","Mizoram","Nagaland",
    "Odisha","Punjab","Rajasthan","Sikkim","Tamil Nadu","Telangana","Tripura",
    "Uttar Pradesh","Uttarakhand","West Bengal","Other",
]

# ── Seed workers ─────────────────────────────────────────────────────────────
SEED_WORKERS = [
    # -------- EXISTING (cleaned: emojis removed) --------
    {
        "worker_id": "DW-4821", "name": "Sunita Devi", "age": 32,
        "gender": "Female", "skill": "Cook",
        "phone": "98XXXXXX12", "phone_type": "Personal (Aadhaar-linked)",
        "nationality": "Indian", "state": "Uttar Pradesh", "country": None,
        "reg_mode": "Self", "employer_aadhaar": None, "agent_id": None,
        "docs": ["Photograph", "Aadhaar Card", "Address Proof", "Bank Details", "Skill Certification"],
        "references": [{"name": "Meera Sharma", "phone": "9812300001"},
                       {"name": "Raj Kumar", "phone": "9812300002"}],
        "police_status": "Verified", "police_area": "Delhi (Karol Bagh)",
        "trust_score": 82,
        "verification": {"Identity": "Verified", "Address": "Verified",
                         "Police": "Verified", "Skill Cert": "Verified"},
        "flagged": False, "complaints": [],
        "registered_at": "2024-11-15 10:30",
    },

    # -------- NEW DATA --------
    {
        "worker_id": "DW-7788", "name": "Kavita Sharma", "age": 29,
        "gender": "Female", "skill": "Maid",
        "phone": "99XXXXXX21", "phone_type": "Personal",
        "nationality": "Indian", "state": "Delhi", "country": None,
        "reg_mode": "Self", "employer_aadhaar": None, "agent_id": None,
        "docs": ["Photograph", "Aadhaar Card", "Address Proof"],
        "references": [{"name": "Ritu Malhotra", "phone": "9822000001"}],
        "police_status": "Verified", "police_area": "Delhi (Rohini)",
        "trust_score": 76,
        "verification": {"Identity": "Verified", "Address": "Verified",
                         "Police": "Verified", "Skill Cert": "Not Added"},
        "flagged": False, "complaints": [],
        "registered_at": "2025-02-12 12:00",
    },

    {
        "worker_id": "DW-8899", "name": "Imran Khan", "age": 40,
        "gender": "Male", "skill": "Driver",
        "phone": "97XXXXXX67", "phone_type": "Personal",
        "nationality": "Indian", "state": "Maharashtra", "country": None,
        "reg_mode": "Employer", "employer_aadhaar": "XXXX-XXXX-1122", "agent_id": None,
        "docs": ["Driving License", "Aadhaar Card"],
        "references": [],
        "police_status": "Pending", "police_area": "Mumbai (Bandra)",
        "trust_score": 68,
        "verification": {"Identity": "Verified", "Address": "Verified",
                         "Police": "Pending", "Skill Cert": "Verified"},
        "flagged": False, "complaints": [],
        "registered_at": "2025-01-20 09:15",
    },

    {
        "worker_id": "DW-9901", "name": "Sanjay Yadav", "age": 34,
        "gender": "Male", "skill": "Electrician",
        "phone": "96XXXXXX45", "phone_type": "Shared",
        "nationality": "Indian", "state": "Bihar", "country": None,
        "reg_mode": "Agent", "employer_aadhaar": None, "agent_id": "AGT-BR-009",
        "docs": ["Photograph", "Address Proof"],
        "references": [],
        "police_status": "Not Verified", "police_area": None,
        "trust_score": 52,
        "verification": {"Identity": "Partial", "Address": "Pending",
                         "Police": "Not Verified", "Skill Cert": "Not Added"},
        "flagged": False, "complaints": [],
        "registered_at": "2025-03-01 08:45",
    },

    {
        "worker_id": "DW-5522", "name": "Lakshmi Nair", "age": 38,
        "gender": "Female", "skill": "Caretaker",
        "phone": "95XXXXXX90", "phone_type": "Personal",
        "nationality": "Indian", "state": "Kerala", "country": None,
        "reg_mode": "Self", "employer_aadhaar": None, "agent_id": None,
        "docs": ["Aadhaar Card", "PAN Card", "Medical Certificate"],
        "references": [{"name": "Anil Nair", "phone": "9847000001"}],
        "police_status": "Verified", "police_area": "Kochi",
        "trust_score": 88,
        "verification": {"Identity": "Verified", "Address": "Verified",
                         "Police": "Verified", "Skill Cert": "Verified"},
        "flagged": False, "complaints": [],
        "registered_at": "2024-12-28 14:20",
    },

    {
        "worker_id": "DW-6633", "name": "Tashi Sherpa", "age": 31,
        "gender": "Male", "skill": "Cook",
        "phone": "93XXXXXX22", "phone_type": "Personal",
        "nationality": "Nepal", "state": None, "country": "Nepal",
        "reg_mode": "Employer", "employer_aadhaar": "XXXX-XXXX-3344", "agent_id": None,
        "docs": ["Citizenship Card"],
        "references": [],
        "police_status": "Pending", "police_area": "Delhi",
        "trust_score": 60,
        "verification": {"Identity": "Verified", "Address": "Pending",
                         "Police": "Pending", "Skill Cert": "Not Added"},
        "flagged": False, "complaints": [],
        "registered_at": "2025-02-18 11:10",
    },

    {
        "worker_id": "DW-7744", "name": "Pooja Kumari", "age": 26,
        "gender": "Female", "skill": "Cleaner",
        "phone": None, "phone_type": "No Phone",
        "nationality": "Indian", "state": "Jharkhand", "country": None,
        "reg_mode": "Agent", "employer_aadhaar": None, "agent_id": "AGT-JH-002",
        "docs": ["Photograph"],
        "references": [],
        "police_status": "Not Verified", "police_area": None,
        "trust_score": 35,
        "verification": {"Identity": "Partial", "Address": "Not Added",
                         "Police": "Not Verified", "Skill Cert": "Not Added"},
        "flagged": False, "complaints": [],
        "registered_at": "2025-03-10 10:00",
    },

    {
        "worker_id": "DW-8855", "name": "Rahul Verma", "age": 30,
        "gender": "Male", "skill": "Plumber",
        "phone": "92XXXXXX78", "phone_type": "Personal",
        "nationality": "Indian", "state": "Rajasthan", "country": None,
        "reg_mode": "Self", "employer_aadhaar": None, "agent_id": None,
        "docs": ["Aadhaar Card", "Skill Certification"],
        "references": [{"name": "Deepak Singh", "phone": "9828000001"}],
        "police_status": "Verified", "police_area": "Jaipur",
        "trust_score": 79,
        "verification": {"Identity": "Verified", "Address": "Verified",
                         "Police": "Verified", "Skill Cert": "Verified"},
        "flagged": False, "complaints": [],
        "registered_at": "2024-11-05 16:30",
    },

    {
        "worker_id": "DW-9966", "name": "Abdul Rahman", "age": 42,
        "gender": "Male", "skill": "Driver",
        "phone": "91XXXXXX11", "phone_type": "Personal",
        "nationality": "Bangladesh", "state": None, "country": "Bangladesh",
        "reg_mode": "Employer", "employer_aadhaar": "XXXX-XXXX-5566", "agent_id": None,
        "docs": ["Passport", "Work Permit"],
        "references": [],
        "police_status": "Pending", "police_area": "Kolkata",
        "trust_score": 58,
        "verification": {"Identity": "Verified", "Address": "Verified",
                         "Police": "Pending", "Skill Cert": "Not Added"},
        "flagged": False, "complaints": [],
        "registered_at": "2025-01-30 07:50",
    },
        {
        "worker_id": "DW-1101", "name": "Ramesh Kumar", "age": 45,
        "gender": "Male", "skill": "Watchman",
        "phone": "90XXXXXX10", "phone_type": "Personal",
        "nationality": "Indian", "state": "Haryana", "country": None,
        "reg_mode": "Self", "employer_aadhaar": None, "agent_id": None,
        "docs": ["Aadhaar Card", "Photograph"],
        "references": [],
        "police_status": "Pending", "police_area": "Gurgaon",
        "trust_score": 55,
        "verification": {"Identity": "Verified", "Address": "Pending", "Police": "Pending", "Skill Cert": "Not Added"},
        "flagged": False, "complaints": [],
        "registered_at": "2025-02-01 09:00",
    },

    {
        "worker_id": "DW-1102", "name": "Anjali Gupta", "age": 27,
        "gender": "Female", "skill": "Babysitter",
        "phone": "90XXXXXX11", "phone_type": "Personal",
        "nationality": "Indian", "state": "Delhi", "country": None,
        "reg_mode": "Self",
        "docs": ["Aadhaar Card", "Address Proof", "Photograph", "Skill Certification"],
        "references": [{"name": "Neha Jain", "phone": "9899000011"}],
        "police_status": "Verified", "police_area": "Delhi",
        "trust_score": 85,
        "verification": {"Identity": "Verified", "Address": "Verified", "Police": "Verified", "Skill Cert": "Verified"},
        "flagged": False, "complaints": [],
        "registered_at": "2024-12-10 10:20",
    },

    {
        "worker_id": "DW-1103", "name": "Mukesh Singh", "age": 36,
        "gender": "Male", "skill": "Driver",
        "phone": "90XXXXXX12", "phone_type": "Personal",
        "nationality": "Indian", "state": "Punjab",
        "reg_mode": "Employer", "employer_aadhaar": "XXXX-XXXX-7788",
        "docs": ["Driving License"],
        "references": [],
        "police_status": "Not Verified",
        "trust_score": 50,
        "verification": {"Identity": "Partial", "Address": "Not Added", "Police": "Not Verified", "Skill Cert": "Not Added"},
        "flagged": False, "complaints": [],
        "registered_at": "2025-02-15 11:00",
    },

    {
        "worker_id": "DW-1104", "name": "Farida Begum", "age": 41,
        "gender": "Female", "skill": "Cook",
        "phone": "90XXXXXX13", "phone_type": "Family / Shared",
        "nationality": "Indian", "state": "West Bengal",
        "reg_mode": "Agent", "agent_id": "AGT-WB-101",
        "docs": ["Photograph", "Address Proof"],
        "references": [],
        "police_status": "Pending",
        "trust_score": 48,
        "verification": {"Identity": "Partial", "Address": "Pending", "Police": "Pending", "Skill Cert": "Not Added"},
        "flagged": False, "complaints": [],
        "registered_at": "2025-03-05 08:30",
    },

    {
        "worker_id": "DW-1105", "name": "Suresh Patel", "age": 39,
        "gender": "Male", "skill": "Gardener",
        "phone": "90XXXXXX14", "phone_type": "Personal",
        "nationality": "Indian", "state": "Gujarat",
        "reg_mode": "Self",
        "docs": ["Aadhaar Card", "Address Proof", "Photograph"],
        "references": [{"name": "Kiran Patel", "phone": "9825000011"}],
        "police_status": "Verified",
        "trust_score": 78,
        "verification": {"Identity": "Verified", "Address": "Verified", "Police": "Verified", "Skill Cert": "Not Added"},
        "flagged": False, "complaints": [],
        "registered_at": "2024-12-22 13:15",
    },

    {
        "worker_id": "DW-1106", "name": "Geeta Kumari", "age": 33,
        "gender": "Female", "skill": "Maid",
        "phone": None, "phone_type": "No Phone",
        "nationality": "Indian", "state": "Jharkhand",
        "reg_mode": "Agent", "agent_id": "AGT-JH-009",
        "docs": ["Photograph"],
        "references": [],
        "police_status": "Not Verified",
        "trust_score": 30,
        "verification": {"Identity": "Partial", "Address": "Not Added", "Police": "Not Verified", "Skill Cert": "Not Added"},
        "flagged": False,
        "registered_at": "2025-03-12 09:45",
    },

    {
        "worker_id": "DW-1107", "name": "Rajesh Thapa", "age": 37,
        "gender": "Male", "skill": "Cook",
        "phone": "90XXXXXX15", "phone_type": "Personal",
        "nationality": "Nepal", "country": "Nepal",
        "reg_mode": "Employer",
        "docs": ["Citizenship Card"],
        "references": [],
        "police_status": "Pending",
        "trust_score": 60,
        "verification": {"Identity": "Verified", "Address": "Pending", "Police": "Pending", "Skill Cert": "Not Added"},
        "flagged": False,
        "registered_at": "2025-02-20 10:40",
    },

    {
        "worker_id": "DW-1108", "name": "Maria Dsouza", "age": 35,
        "gender": "Female", "skill": "Caretaker",
        "phone": "90XXXXXX16", "phone_type": "Personal",
        "nationality": "Indian", "state": "Goa",
        "reg_mode": "Self",
        "docs": ["Aadhaar Card", "Medical Certificate", "Photograph"],
        "references": [{"name": "Joseph Dsouza", "phone": "9822000022"}],
        "police_status": "Verified",
        "trust_score": 88,
        "verification": {"Identity": "Verified", "Address": "Verified", "Police": "Verified", "Skill Cert": "Verified"},
        "flagged": False,
        "registered_at": "2024-11-18 15:20",
    },

    {
        "worker_id": "DW-1109", "name": "Ali Hassan", "age": 28,
        "gender": "Male", "skill": "Driver",
        "phone": "90XXXXXX17", "phone_type": "Personal",
        "nationality": "Indian", "state": "Karnataka",
        "reg_mode": "Self",
        "docs": ["Driving License", "Aadhaar Card"],
        "references": [],
        "police_status": "Verified",
        "trust_score": 80,
        "verification": {"Identity": "Verified", "Address": "Verified", "Police": "Verified", "Skill Cert": "Verified"},
        "flagged": False,
        "registered_at": "2024-12-01 09:10",
    },

    {
        "worker_id": "DW-1110", "name": "Nirmala Devi", "age": 50,
        "gender": "Female", "skill": "Cook",
        "phone": "90XXXXXX18", "phone_type": "Family / Shared",
        "nationality": "Indian", "state": "Rajasthan",
        "reg_mode": "Self",
        "docs": ["Aadhaar Card"],
        "references": [],
        "police_status": "Not Verified",
        "trust_score": 45,
        "verification": {"Identity": "Verified", "Address": "Not Added", "Police": "Not Verified", "Skill Cert": "Not Added"},
        "flagged": False,
        "registered_at": "2025-01-10 11:30",
    }
]

# ── Trust score engine ────────────────────────────────────────────────────────
REQUIRED_DOCS = {
    "Indian":         {"Photograph", "Aadhaar Card", "Address Proof"},
    "Nepal / Bhutan": {"Citizenship Card", "Address Proof"},
    "Foreign":        {"Passport", "Visa", "Work Permit", "FRRO Registration", "Police Clearance Certificate"},
}

OPTIONAL_BOOST_DOCS = {
    "Bank Details", "PAN Card", "Ration Card", "Permanent Address Proof",
    "Educational Certificates", "Skill Certification",
    "Indian Aadhaar (if issued)", "Police Clearance (home country)", "Form C",
}


def compute_trust(worker: dict, include_police: bool = True) -> int:
    """
    Compute trust score.
    include_police=False during step 1 & 2 so police bonus is not
    counted until the worker actually reaches the verification step.
    Docs only count when they appear in uploaded_docs (files actually uploaded),
    not just checked. Pass uploaded_docs in worker dict for step-2 live preview.
    """
    score = 0

    if worker.get("name", "").strip():   score += 2
    if worker.get("age"):                score += 2
    if worker.get("gender"):             score += 2
    if worker.get("skill", "").strip():  score += 2

    phone_type = worker.get("phone_type", "")
    if phone_type not in ("No Phone", "", None): score += 5

    nat = worker.get("nationality", "")
    if nat == "Indian":           score += 10
    elif nat == "Nepal / Bhutan": score += 8
    else : score += 7
    uploaded = set(worker.get("uploaded_docs", worker.get("docs", [])))
    req = REQUIRED_DOCS.get(nat, set())
    for d in uploaded:
        if d in req:                   score += 8
        elif d in OPTIONAL_BOOST_DOCS: score += 4

    refs = [r for r in worker.get("references", []) if r.get("name") and r.get("phone")]
    score += min(len(refs), 2) * 3

    if include_police:
        ps = worker.get("police_status", "Not Verified")
        if ps == "Verified": score += 25
        elif ps == "Pending": score += 5

    return min(score, 100)


def trust_color(score: int) -> str:
    if score >= 70: return "green"
    if score >= 40: return "orange"
    return "red"


def trust_label(score: int) -> str:
    if score >= 80: return "Excellent — qualifies for all benefits"
    if score >= 60: return "Good — add more documents to improve"
    if score >= 40: return "Moderate — key documents missing"
    return "Low — add required documents urgently"


# ── Worker ID generation ──────────────────────────────────────────────────────
def generate_id(existing_ids: set) -> str:
    while True:
        wid = f"DW-{random.randint(1000, 9999)}"
        if wid not in existing_ids:
            return wid


# ── Verification map builder ──────────────────────────────────────────────────
def build_verification(worker: dict) -> dict:
    nat  = worker.get("nationality", "")
    docs = set(worker.get("docs", []))

    # Identity
    if nat == "Indian":
        if "Aadhaar Card" in docs and "Photograph" in docs:
            identity = "Verified"
        elif "Photograph" in docs:
            identity = "Partial"
        else:
            identity = "Not Added"
    elif nat == "Nepal / Bhutan":
        if "Citizenship Card" in docs or "Passport" in docs:
            identity = "Verified"
        elif "Photograph" in docs:
            identity = "Partial"
        else:
            identity = "Not Added"
    else:  # Foreign
        if "Passport" in docs and "Work Permit" in docs:
            identity = "Verified"
        else:
            identity = "Partial"

    address  = "Verified" if "Address Proof" in docs else "— Not Added"
    skill_c  = "Verified" if "Skill Certification" in docs else "— Not Added"

    ps = worker.get("police_status", "Not Verified")
    police   = "Verified" if ps == "Verified" else ("Pending" if ps == "Pending" else "Not Verified")

    return {"Identity": identity, "Address": address, "Police": police, "Skill Cert": skill_c}
