# Domestic Worker Registration Portal

## Setup

```bash
pip install -r requirements.txt
```

## Run

**Public portal** (workers, employers, lookup):
```bash
streamlit run app.py
# Opens at http://localhost:8501
```

**Government admin panel** (separate terminal):
```bash
streamlit run admin.py --server.port 8502
# Opens at http://localhost:8502
```

## File Structure

```
dwrp_streamlit/
├── app.py          # Public portal — Home, Register, Lookup, Complaint
├── admin.py        # Govt admin panel — Dashboard, Verify, Complaints
├── data.py         # Shared in-memory store, trust engine, seed data
└── requirements.txt
```

## Notes
- Data is **in-memory only** — restarting either app resets to seed data.
- Both apps share session_state independently (they run as separate Streamlit processes).
- For a real deployment, replace the in-memory dicts in `data.py` with a database (SQLite or PostgreSQL).
