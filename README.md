# IntelliICU — Enterprise AI Clinical Decision Support Platform

**AI-Powered Clinical Decision Support, ICU Monitoring, Clinical Copilot, and Hospital Intelligence Platform**

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-Frontend-61dafb?logo=react)](https://reactjs.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-336791?logo=postgresql)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ed?logo=docker)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-purple)](LICENSE)

---

## What is IntelliICU?

IntelliICU is an enterprise-grade AI Clinical Decision Support System (CDSS) that supports clinicians with intelligent patient monitoring, real-time telemetry, AI-assisted clinical decisions, and hospital-wide operational intelligence in one unified platform.

Clinical teams typically face:
- Alert fatigue from disconnected monitoring signals
- Manual correlation of patient vitals across separate systems
- Time-consuming documentation and guideline lookup
- No integrated AI layer to interpret clinical patterns or suggest next steps

IntelliICU brings an AI copilot directly into the clinical workflow, giving clinicians context-aware, evidence-cited support without replacing their judgment.

> **Medical Disclaimer:** IntelliICU is built for educational, research, and portfolio purposes. It is not a certified medical device and is not intended to replace professional clinical judgment.

---

## Architecture

```
                    React + Vite Frontend
                    (Role-aware routing, WebSocket client)
                              |
                    HTTPS REST API + Secure WebSocket
                              |
                       FastAPI Backend
                              |
        +---------------------+---------------------+
        |                     |                     |
  Auth & RBAC          Clinical AI / RAG      Hospital APIs
  (JWT, bcrypt,        (Clinical Copilot,      & Management
  8-role model)         Hospital Assistant)
        |                     |                     |
        +---------------------+---------------------+
                              |
                    PostgreSQL (SQLAlchemy ORM)
```

---

## Features

### Authentication & Security
- JWT-based authentication with bcrypt password hashing (no legacy fallback)
- Role-Based Access Control across 8 roles: SuperAdmin, HospitalAdmin, ICUManager, Doctor, Nurse, LabTechnician, Receptionist, Viewer
- Route-level and API-level permission enforcement
- Startup-time validation against default/missing JWT secrets
- CORS configuration for secure cross-origin requests

### Doctor / ICU Manager Dashboard
- Clinical overview and patient census
- ICU monitoring access
- AI-powered clinical tools
- Real-time patient data
- Hospital workflow integration

### Admin Dashboard
- Platform overview and system statistics
- User and role management
- Operational monitoring
- Administrative controls

### Patient Analysis View
- Dedicated per-patient page reached by selecting any patient from a dashboard list
- Tabbed interface: Overview, Timeline, Evidence, Explainability, Reports, Clinical Copilot
- Explainable AI panel showing feature-level contribution to risk score
- Risk trajectory chart showing trend over time

### Clinical Copilot
- Per-patient AI assistant, accessed as a tab within the patient analysis view
- Differential diagnosis generation with supporting/contradicting evidence
- Composite clinical risk scoring (SOFA, qSOFA, NEWS2, SIRS, APACHE II)
- Medication recommendations with renal-adjusted dosing
- Guideline citations (NICE, WHO, Sepsis-3) via RAG retrieval

### Hospital Assistant
- Standalone hospital-wide AI assistant, independent of per-patient context
- Natural-language triage queries across the full patient census
- Critical patient ranking, active alerts, and AI-generated operational insights

### Live ICU Monitoring
- Real-time patient and ICU visualization over WebSocket
- Vital sign tracking with continuous updates
- Clinical alert system with escalation logic

### Telemetry Monitoring
- Continuous physiological data visualization: heart rate, blood pressure, SpO2, respiratory rate, temperature
- Multi-patient trend view with deterioration scoring

### User Management
- Create, view, and manage platform users
- Role and department assignment
- Account status management

---

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Frontend | React + Vite | Component-based UI |
| Backend | FastAPI + Python | REST API + WebSocket server |
| Database | PostgreSQL | Persistent relational storage |
| ORM | SQLAlchemy | Database abstraction layer |
| Auth | JWT + bcrypt | Secure authentication |
| Vector store | ChromaDB | Guideline document retrieval |
| Embeddings | sentence-transformers | RAG embedding generation |
| LLM providers | OpenAI / Gemini / Ollama / LM Studio / Mock | Clinical AI inference (pluggable) |
| Real-time | WebSockets | Live telemetry and monitoring |
| Containers | Docker + Docker Compose | Containerized deployment |
| CI | GitHub Actions | Automated build validation |

---

## Live Demo

| Service | URL |
|---------|-----|
| Live Application | [intelli-icu.vercel.app](intelli-icu.vercel.app)|
| Backend API | [ ] |
| API Docs (Swagger) | [ ] |
| GitHub | [github.com/nite208/IntelliICU](https://github.com/nite208/IntelliICU) |

---

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 20+
- npm
- Git
- Docker (optional)
- PostgreSQL (if running locally)

### 1. Clone the repo
```bash
git clone https://github.com/nite208/IntelliICU.git
cd IntelliICU
```

### 2. Configure environment
```bash
cp .env.example .env
```

Key environment variables:
```env
# Database
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=intelliicu
DATABASE_USER=postgres
DATABASE_PASSWORD=your_password

# Auth
AUTH_SECRET_KEY=your_generated_secret_key

# AI Provider (choose one)
AI_PROVIDER=mock
OPENAI_API_KEY=
GEMINI_API_KEY=
```

### 3. Start the backend
```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\Activate.ps1

# Mac/Linux
source .venv/bin/activate

pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

Backend runs at `http://localhost:8000`
Swagger docs at `http://localhost:8000/docs`

### 4. Start the frontend
```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`

### 5. Docker (alternative, runs everything at once)
```bash
docker compose up --build
```

---

## API Endpoints

### Authentication
```
POST /api/auth/login
POST /api/auth/refresh
POST /api/auth/logout
GET  /api/auth/me
```

### RBAC
```
GET  /api/rbac/roles
GET  /api/rbac/users/me/permissions
```

### Clinical
```
GET  /api/patients/{id}
GET  /api/timeline/{patient_id}
POST /api/clinical-copilot/chat
POST /api/clinical-copilot/report
```

### Hospital
```
GET  /api/hospital-assistant/snapshot
GET  /api/hospital-assistant/summary
GET  /api/hospital-assistant/alerts
GET  /api/hospital-assistant/critical
GET  /api/hospital-assistant/insights
POST /api/hospital-assistant/chat
```

### Admin
```
GET  /api/users
POST /api/users
PUT  /api/users/{id}
GET  /api/departments
```

---

## Screenshots

### Login
[ ]

### Admin Dashboard
[ ]

### Doctor Dashboard
[ ]

### Patient Analysis — Clinical Copilot Tab
[ ]

### Hospital Assistant
[ ]

### Live Monitoring
[ ]

### Telemetry Monitor
[ ]

### User Management
[ ]

---

## Project Structure

```
IntelliICU/
|
├── .github/
│   ├── ISSUE_TEMPLATE/
│   └── workflows/
|
├── backend/
│   └── app/
│       ├── main.py
│       ├── api/
│       ├── services/
│       ├── database/
│       ├── ai/
│       └── websocket/
|
├── frontend/
│   └── src/
│       ├── pages/
│       │   ├── PatientProfile/
│       │   ├── HospitalAssistant/
│       │   └── ...
│       ├── components/
│       │   ├── clinicalCopilot/
│       │   ├── hospitalAssistant/
│       │   ├── patientProfile/
│       │   └── dashboardV2/
│       ├── context/
│       └── services/
|
├── docker-compose.yml
├── .env.example
├── CONTRIBUTING.md
└── README.md
```

---

## Core Platform Modules

| Module | Description |
|--------|-------------|
| Authentication | JWT-based auth with 8-role RBAC |
| Doctor Dashboard | Clinical interface for healthcare professionals |
| Admin Dashboard | Administrative platform management |
| Patient Analysis | Per-patient tabbed view with vitals, timeline, evidence, explainability, reports, and Copilot |
| Clinical Copilot | Per-patient AI-assisted clinical reasoning |
| Hospital Assistant | Hospital-wide AI operations assistant |
| Live Monitoring | Real-time ICU patient monitoring |
| Telemetry Monitor | Physiological telemetry visualization |
| User Management | User and role administration |
| REST API | Frontend-backend communication |
| WebSockets | Real-time telemetry streams |
| PostgreSQL | Persistent clinical data storage |

---

## CI/CD Pipeline

GitHub Actions validates every push:
- Backend dependency installation
- Python application compile check
- Frontend dependency installation
- Vite production build validation

```bash
pytest
cd frontend && npm run build
```

---

## Medical Disclaimer

IntelliICU is built for educational, research, demonstration, and portfolio purposes.

- Not a certified medical device
- Not intended for direct clinical diagnosis
- Does not replace qualified healthcare professionals
- Should not be the sole basis for medical decisions

All AI-generated recommendations should be treated as decision-support information only. Clinical decisions must always be made by qualified professionals using appropriate judgment.

---

## Security

- Never commit `.env` files or production credentials
- Never expose database passwords or JWT secrets
- Always validate incoming data
- For production healthcare use, additional regulatory, compliance, and clinical governance requirements apply

---

## License

MIT License, see `LICENSE` file for details.

---

## Developer

**Nitesh Kumawat**
- Computer Engineering (Honours in Data Science), ISBM College of Engineering, Pune, 2026
- Oracle Certified Generative AI Professional
- Google Student Ambassador, AI/Gemini
- [LinkedIn](https://linkedin.com/in/nitesh-kumawat-185356289)
- [GitHub](https://github.com/nite208)
- niteshkumawat2331@gmail.com

---

> ⭐ If IntelliICU is useful or interesting to you, give it a star — it helps others discover the project and supports continued development.

---

<p align="center">
  <strong>IntelliICU — Building the future of AI-powered Clinical Decision Support</strong>
</p>
