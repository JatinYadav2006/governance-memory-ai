# Governance Memory AI

> **Sankalp Innovation Challenge Finalist** — National AI & Innovation Summit, MNNIT Allahabad 2026

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?style=flat&logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-red?style=flat&logo=streamlit)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat)

An AI-powered civic operations platform that transforms isolated citizen complaints into structured operational intelligence — with semantic clustering, crisis detection, multi-agent response planning, and proof-backed resolution.

---

## 🎥 Demo

[Watch the full platform demo →](https://github.com/JatinYadav2006/governance-memory-ai/blob/main/Demo%20Video.mp4)

---

## 🧠 What Makes This Different

Most civic platforms treat complaints as isolated tickets. Governance Memory AI treats them as signals:

- **Semantic clustering** groups similar complaints by meaning, not keywords
- **Crisis detection** flags emerging service breakdowns before they escalate
- **Governance Memory** surfaces similar resolved cases so solutions aren't reinvented
- **Multi-agent War Room** synthesizes coordinated AI response plans across crisis, operations, policy, and communications perspectives

---

## 🏗 Architecture
Citizen Complaint → AI Prioritization → Semantic Clustering → Crisis Detection

→ Governance Memory → War Room Response Planning → Dispatch

→ Verification → Resolved History

**Stack:**
- Backend: FastAPI + Uvicorn
- Frontend: Streamlit (role-based citizen/admin experience)
- Database: SQLite + SQLAlchemy ORM
- AI/ML: SentenceTransformers (all-MiniLM-L6-v2), scikit-learn, DBSCAN
- NLP: TextBlob, SpeechRecognition
- Data: pandas, numpy

---

## ⚡ Key Features

| Feature | Description |
|---|---|
| Semantic Clustering | Groups complaints by meaning using SentenceTransformers + DBSCAN |
| Crisis Detection | Flags clusters exceeding complaint thresholds (High: 10+, Severe: 30+) |
| Governance Memory | Retrieves similar resolved cases with similarity scores |
| Multi-Agent War Room | Coordinated AI response across crisis, ops, policy, comms perspectives |
| Voice Intake | Multilingual voice complaint filing (English + Indian languages) |
| Department Dispatch | AI-assisted and manual dispatch with SLA tracking |
| Proof Verification | Image-backed work verification before complaint closure |
| Social Pulse | Civic sentiment analysis and narrative risk detection |

---

## 🚀 Quick Start

**1. Clone and install**
```bash
git clone https://github.com/JatinYadav2006/governance-memory-ai
cd governance-memory-ai
pip install -r requirements.txt
```

**2. Start backend**
```bash
uvicorn backend.api.main:app --reload
# Runs at http://127.0.0.1:8000
# Docs at http://127.0.0.1:8000/docs
```

**3. Start frontend**
```bash
streamlit run frontend/app.py
```

**Demo credentials**
Email:    admin@govai.demo

Password: GovAI_Admin#2026!

**Add demo data**
```bash
POST /demo_backfill
```

---

## 📁 Project Structure
governance-memory-ai/

├── backend/

│   ├── ai/

│   ├── api/

│   ├── auth/

│   ├── db/

│   └── services/

├── frontend/

│   ├── app.py

│   ├── public_portal.py

│   ├── admin_dashboard.py

│   └── homepage.py

├── assets/

├── uploads/

└── requirements.txt

---

## 🔌 Core API Endpoints

**Intelligence**
GET  /issue_clusters       # Semantic complaint clusters

GET  /ai_insights          # AI-generated governance insights

GET  /crisis_alerts        # Active crisis flags

GET  /governance_memory    # Similar resolved case retrieval

GET  /war_room?cluster_id= # Multi-agent War Room analysis

**Operations**
POST /submit_issue         # Citizen complaint submission

POST /dispatch_assignment  # Department dispatch

POST /verify_work          # Proof-backed work verification

GET  /sla_overview         # SLA tracking dashboard

---

## 🔮 Roadmap

- [ ] PostgreSQL migration for production scale
- [ ] Live social media API integration
- [ ] Stronger multilingual NLP and translation
- [ ] Production deployment for municipal pilots
- [ ] Enhanced audit trails and approval workflows

---

## 👥 Team

Built by **Jatin Yadav** (Team Lead) and team — Turing Club, MNNIT Allahabad
Finalist — Sankalp Innovation Challenge, National AI & Innovation Summit 2026
