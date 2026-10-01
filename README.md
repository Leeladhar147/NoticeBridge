# NoticeBridge

A deterministic career transition, notice-period modeling, and hypothetical financing simulation platform.

---

## Financial Simulation Disclaimer

> **IMPORTANT NOTICE:**  
> **NoticeBridge is NOT a lender, bank, NBFC, credit broker, or financial/legal advisory service.**  
> All financial calculations provided by NoticeBridge are **hypothetical simulations** and estimated buyout models.  
> NoticeBridge does **NOT** offer:
> - Actual lending or loan origination
> - Guaranteed financing or credit approval
> - Real money transfers or payment disbursements
> - Guaranteed employer reimbursement
> - Guaranteed legal entitlement to notice buyout or early release
>
> All transition timelines, buyout costs, and repayment estimates are purely educational models derived deterministically from contractual clauses and user-supplied parameters.

---

## Problem

An employee frequently faces a contractual notice period that extends well beyond the mandatory joining deadline of a prospective employer:

- **The Notice Period Mismatch:** In technology and corporate roles (notably across India and similar markets), employment contracts routinely enforce **60- to 90-day notice periods**. Concurrently, hiring companies often require candidate onboarding within **30 days**.
- **The Liquidity Impasse:** To join the new company on time, the candidate must buy out the remaining unserved notice days (e.g. 60 days). For a professional earning ₹60,000/month, the buyout cost exceeds ₹120,000 upfront. Candidates often face severe short-term liquidity constraints.
- **Contractual Ambiguity:** Employees struggle to decipher whether their contract legally permits buyout, whether buyout is calculated on Basic or Gross salary, which monthly divisor applies (30 days vs 26 working days), and whether the new employer\'s assistance covers the gap.

NoticeBridge models the resulting transition scenarios and simulates possible buyout/repayment arrangements deterministically, giving employees transparent, auditable clarity.

---

## Core Capabilities

- **Employment Document Intelligence:** Ingests employment agreements and offer letters (PDF, TXT, Markdown).
- **Notice-Period Extraction:** Identifies contractual notice terms, buyout clauses, and salary bases with exact page citations and textual evidence.
- **Notice-Period Calculation:** Computes calendar days served, leaves adjusted, remaining notice days, and earliest contractual release date.
- **Buyout Calculation:** Deterministically evaluates gross buyout costs across Basic, Gross, or Fixed salary bases and 30-day, 26-working-day, or calendar-month divisors.
- **Joining-Date Calculation:** Models earliest feasible start dates and compares them against employer joining deadlines.
- **Repayment Simulation:** Models hypothetical amortized repayments across variable tenors (e.g. 3, 6, 12 months) with transparent principal, interest, and fee breakdowns.
- **Affordability Analysis:** Evaluates simulated monthly repayments against estimated disposable post-tax income.
- **Scenario Simulation:** Generates reproducible, deterministic transition pathways (full notice served, employer co-pay, employee-funded early buyout, extended handover).
- **Explainable Evidence:** Distinguishes contract-derived, user-provided, and calculated values with complete provenance tracking.
- **User Authentication & Data Isolation:** Salted bcrypt password hashing, JWT bearer tokens, and strict user-scoped database isolation.
- **PostgreSQL Database:** Production relational persistence with SQLAlchemy 2.0 and Alembic schema migrations.
- **Docker & Docker Compose:** Reproducible multi-container orchestration with PostgreSQL, backend, and frontend services.

---

## Architecture

`
React (Vite UI)
       ↓  (REST API / JWT Auth)
FastAPI (Python 3.11 Backend)
       ↓
Deterministic Python Engines
       ↓
PostgreSQL (SQLAlchemy 2.0 + Alembic)
`

### Document Intelligence to Deterministic Calculation Flow:

`
Employment Documents (PDF / TXT / MD)
       ↓
Targeted Chunking & Keyword / Intent RAG
       ↓
AI / Regex Structured Extraction
       ↓
Validation Gatekeeper & Human Confirmation
       ↓
Deterministic Python Calculation Engines
       ↓
Explainable & Auditable Result
`

> **Design Principle:** The AI never computes money, never decides financial eligibility, and never invents numbers. All calculations are 100% deterministic Python mathematics.

---

## Tech Stack

NoticeBridge only lists technologies that are **actually implemented** in this repository:

- **Backend:** Python 3.11, FastAPI, Pydantic v2, Uvicorn
- **Database & ORM:** PostgreSQL 16, SQLAlchemy 2.0 (psycopg 3 driver), Alembic (migrations), SQLite (development fallback)
- **Security:** bcrypt (salted password hashing), PyJWT (HS256 tokens)
- **Document Processing & RAG:** pypdf, custom semantic chunking, keyword & intent-based targeted retrieval
- **Frontend:** React 19, Vite, Vanilla CSS design system, Lucide React
- **Testing:** pytest (58 automated test cases covering engines, RAG retrieval, validation, auth, and database isolation)
- **Containerization:** Docker, Docker Compose

---

## Running Locally

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm
- Docker (optional, for containerized PostgreSQL)

### 1. Database Setup
Start local PostgreSQL via Docker:
`ash
docker run -d --name noticebridge-postgres -e POSTGRES_USER=noticebridge -e POSTGRES_PASSWORD=noticebridge_dev_secret -e POSTGRES_DB=noticebridge -p 5439:5432 postgres:16-alpine
`

### 2. Backend Setup
`ash
# Install dependencies
pip install -r requirements.txt

# Run migrations
cd backend
python -m alembic upgrade head

# Start FastAPI server
python -m uvicorn app.main:app --port 8000 --reload
`
- API Root: http://localhost:8000
- Interactive API Docs (Swagger): http://localhost:8000/docs
- Health Endpoint: http://localhost:8000/api/health

### 3. Frontend Setup
`ash
cd frontend
npm install
npm run dev
`
- Web Application: http://localhost:5173

### 4. Running with Docker Compose
To run all services (PostgreSQL, Backend, Frontend) together:
`ash
docker-compose up --build
`
- Frontend UI: http://localhost:3000
- Backend API Docs: http://localhost:8000/docs

---

## Testing

Run the automated backend test suite:
`ash
python -m pytest -v
`

**Final Test Count:** **58 / 58 passing** (100% pass rate)

Included test suites:
- ackend/tests/test_notice_engine.py — Deterministic notice period, days served, and leave offset math
- ackend/tests/test_buyout_engine.py — Buyout formulas, salary bases (Basic/Gross), and daily divisor modes
- ackend/tests/test_joining_engine.py — Target date feasibility and shortfall tracking
- ackend/tests/test_repayment_engine.py — Amortization formulas, interest, and service fees
- ackend/tests/test_scenario_engine.py — Multi-scenario generation and deterministic recommendations
- ackend/tests/test_document_rag_affordability.py — Targeted clause retrieval, anti-hallucination, validation, and affordability engine
- ackend/tests/test_auth_postgres_isolation.py — Bcrypt hashing, JWT auth, user data isolation, and foreign key cascades
- ackend/tests/test_api_endpoints.py — Full REST API endpoints and health checks

---

## License & Attribution

NoticeBridge is an open-source engineering demonstration built for career transition modeling and financial simulation.
