````markdown
# Governance Memory AI

Governance Memory AI is an **AI-assisted civic operations platform** that helps governments move from **complaint intake** to **clustered intelligence**, **crisis awareness**, **response planning**, **verification**, and **institutional memory**.

Instead of treating public complaints as isolated tickets, the platform groups similar complaints, detects emerging service pressure, recommends actions, surfaces similar resolved cases, and tracks closure with proof-backed verification.

---

## Problem Statement

In many cities, citizen complaints are collected but not transformed into actionable operational intelligence. Teams often struggle with:

- duplicated complaints across channels
- delayed recognition of service breakdowns
- weak linkage between complaints and field action
- poor visibility into whether issues were actually resolved
- repeated reinvention of solutions for similar civic problems

Governance Memory AI addresses this by turning complaints into a structured command workflow.

---

## What the Platform Does

The system supports a full civic-response loop:

**Citizen Complaint -> AI Prioritization -> Semantic Clustering -> Crisis Detection -> Governance Memory -> War Room Response Planning -> Dispatch -> Verification -> Resolved History**

---

## Key Features

### 1. Unified Access Flow
A single access screen routes users based on credentials:

- **Citizen accounts** open the Citizen Portal
- **Admin accounts** open the Admin Dashboard

### 2. Citizen Portal
Citizens can:

- create an account
- log in
- submit complaints with:
  - title
  - description
  - location
  - urgency
  - optional image evidence
- use **voice complaint filing**
- view:
  - active complaints
  - resolved history
  - local transparency

### 3. Multilingual Voice Complaint Intake
The platform supports voice-based complaint entry for English and multiple Indian languages.

The voice flow can intelligently draft:

- issue title
- issue description
- location
- urgency

This makes reporting easier for users who may not want to type long complaints manually.

### 4. Issue Prioritization
Each complaint receives a **priority score** based on:

- urgency
- issue category
- recurrence of similar complaints
- risk terms in the complaint text

The prioritization logic is designed to avoid naive keyword spam inflating the score.

### 5. Semantic Issue Clustering
Similar complaints are grouped into clusters using:

- `sentence-transformers`
- model: `all-MiniLM-L6-v2`
- cosine similarity
- `DBSCAN`

This allows the platform to group issues by **meaning**, not just exact keywords.

Example:
- “garbage outside IIT gate”
- “trash near IIT entrance”

can be clustered together.

### 6. AI Governance Insights
For each cluster, the platform generates governance-oriented insights such as:

- what the cluster likely represents
- why it matters operationally
- what it may indicate about local service pressure

### 7. Crisis Detection
The platform flags clusters that cross configured complaint thresholds.

Current logic:
- more than `10` linked complaints -> **High**
- more than `30` linked complaints -> **Severe**

This powers the **Crisis Monitor** inside the admin workflow.

### 8. Governance Memory
The platform compares active clusters with **past resolved issues** and returns the most similar historical case, including:

- similar case title
- location
- action taken
- similarity score

This gives the system a form of **institutional memory**.

### 9. AI Multi-Agent Emergency War Room
This is the flagship feature of the platform.

For a selected cluster, the system simulates a coordinated AI response room that combines perspectives like:

- crisis assessment
- operations planning
- policy response
- trust impact
- public communication
- historical memory

The result is a decision-support layer for administrators.

### 10. Social Pulse Intelligence
The admin dashboard includes a **Social Pulse** layer that analyzes a curated/seeded civic social feed for:

- public sentiment
- emerging local issue buzz
- potential misinformation or narrative risk

> **Note:** The current version uses **seeded social feed data** and is not connected to live X/Facebook APIs.

### 11. Department Dispatch
The system supports both AI-assisted and manual dispatch workflows.

Admins can assign:

- department
- team
- officer
- dispatch status
- notes

This connects cluster intelligence to actual operational ownership.

### 12. SLA and Response Tracking
The platform tracks response performance through an SLA layer.

**SLA** stands for **Service Level Agreement**.

It helps admins monitor:

- active issues
- on-track issues
- overdue issues
- average open age
- assigned department/officer
- response stage

### 13. Work Verification and Resolved History
When work is completed, admins can upload:

- proof image
- verification location / verified by
- action taken

Cluster-level verification resolves all linked issues together and moves them from:

- **Active Complaints**
to
- **Resolved History**

This also feeds governance memory for future cases.

### 14. Safe Demo Data Backfill
The system includes a demo backfill workflow that can **add richer showcase data without resetting existing data**.

This helps demonstrate:

- clusters
- crisis alerts
- resolved history
- dispatch
- trust movement
- analytics

---

## Admin Dashboard Workspaces

The Admin Dashboard is organized as a civic command center with multiple workspaces.

### Operational Performance
Shows:

- total issues
- active clusters
- crisis alerts
- public trust score
- impact metrics
- zone performance
- dispatch / SLA analytics

### Command Center
Includes:

- issue category distribution
- urgency signals
- emerging trends
- crisis monitor

### Social Pulse
Includes:

- sentiment split
- emerging social issue buzz
- narrative / misinformation watch
- recent tracked posts

### Cluster Intelligence
Includes:

- cluster review console
- cluster confidence and evidence terms
- AI insights
- policy recommendations
- governance memory matches
- War Room analysis

### Operations Desk
Includes:

- public update generator
- dispatch assignment form
- cluster verification workflow
- active / resolved complaint records
- verification records

### Policy Management
Supports policy document upload and lookup workflows.

---

## System Architecture

### Frontend
- **Streamlit**
- role-based citizen/admin experience
- unified access shell
- command-center style admin dashboard

### Backend
- **FastAPI**
- modular services for analytics, clustering, verification, trust, dispatch, and memory

### Database
- **SQLite**
- **SQLAlchemy ORM**

### AI / NLP Layer
- `sentence-transformers`
- `scikit-learn`
- `scipy`
- `TextBlob`
- `SpeechRecognition`

### Data / Utility Layer
- `pandas`
- `numpy`
- `requests`
- `pypdf`

---

## Core Workflow

### Citizen Flow
1. Citizen logs in or creates an account
2. Citizen files a complaint by text or voice
3. Complaint is stored in SQLite
4. System assigns a priority score
5. Complaint becomes part of the active issue pool

### Intelligence Flow
1. Issues are clustered semantically
2. Insights and policy suggestions are generated
3. Crisis thresholds are evaluated
4. Governance memory retrieves similar resolved cases
5. Social pulse adds public sentiment context
6. War Room synthesizes a response plan

### Operations Flow
1. Admin reviews cluster intelligence
2. Admin assigns department / team / officer
3. Admin tracks SLA and response status
4. Admin uploads verification when work is completed
5. Issues move to resolved history
6. Resolved cases become future governance memory

---

## Tech Stack

- **Backend:** FastAPI, Uvicorn
- **Frontend:** Streamlit
- **Database:** SQLite, SQLAlchemy
- **AI / ML:** SentenceTransformers, scikit-learn, scipy
- **NLP / Text:** TextBlob, SpeechRecognition
- **Data Handling:** pandas, numpy
- **Utilities:** requests, python-multipart, pydantic, pypdf

---

## Project Structure

```text
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
├── requirements.txt
└── README.md
```

---

## Installation

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd governance-memory-ai
```

### 2. Install dependencies

```bash
python -m pip install -r requirements.txt
```

---

## Running the Project

### Start the backend

```bash
python -m uvicorn backend.api.main:app --reload
```

Backend runs at:

```text
http://127.0.0.1:8000
```

FastAPI docs:

```text
http://127.0.0.1:8000/docs
```

### Start the frontend

```bash
streamlit run frontend/app.py
```

---

## Demo Admin Credentials

```text
Email: admin@govai.demo
Password: GovAI_Admin#2026!
```

---

## Demo Data Backfill

To enrich the current database with additional showcase data **without resetting existing records**, run:

```text
POST /demo_backfill
```

You can trigger it from the FastAPI docs page or with a request tool such as:

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/demo_backfill -Method Post
```

This adds more:

- active complaints
- resolved cases
- verification records
- dispatch examples

---

## API Highlights

Some important endpoints in the project include:

### Authentication
- `POST /auth/signup`
- `POST /auth/login`
- `POST /auth/admin_login`

### Issues and Analytics
- `POST /submit_issue`
- `GET /issues`
- `GET /issues/history`
- `GET /analytics`
- `GET /issue_trends`
- `GET /issue_clusters`
- `GET /ai_insights`
- `GET /crisis_alerts`
- `GET /policy_recommendations`
- `GET /governance_memory`
- `GET /war_room?cluster_id=<id>`

### Operations
- `GET /department_assignments`
- `POST /dispatch_assignment`
- `GET /dispatch_assignments`
- `GET /sla_overview`
- `GET /zone_performance`
- `GET /impact_metrics`
- `POST /verify_work`
- `GET /verifications`

### Social / Transparency
- `GET /social_pulse`
- `GET /citizen_transparency`

### Meta
- `GET /health`
- `POST /demo_backfill`

---

## Important Notes

### Social Pulse
The current Social Pulse feature uses **seeded social feed data**, not live social media APIs.

### Trust Score
The trust score is a **platform-derived heuristic**, based on service pressure and resolution behavior. It is not a formal public-opinion survey score.

### Crisis Alerts
Crisis alerts are currently **threshold-based** and intended as early-warning support, not predictive certainty.

### Voice Input
Voice complaint support depends on the speech-recognition pipeline and works best when the complaint clearly mentions the issue and location.

---

## Why This Project Stands Out

Governance Memory AI is more than a complaint portal. It is a prototype of an **AI-powered civic operations system** that combines:

- semantic complaint understanding
- governance memory
- crisis monitoring
- operational dispatch
- social pulse awareness
- proof-backed closure

This makes it useful not only for hackathon demonstration, but also as a strong foundation for real-world civic operations tooling.

---

## Future Improvements

Potential next steps include:

- live social media integration
- stronger authentication and role/session management
- PostgreSQL or production-grade database migration
- better multilingual NLP and translation support
- model-assisted structured extraction from voice
- richer audit trails and approval workflows
- production deployment for municipal pilots

---

## Team

**Jatin Yadav**  
**Turing Club**
````
