# RIMAS – Retail Intelligence Multi-Agent System

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Version](https://img.shields.io/badge/version-v0.2.0--alpha.2-orange.svg)

> End-to-end retail planning system combining ML-ready infrastructure, multi-agent orchestration and auditable decision workflows.

## 📌 Overview

**RIMAS (Retail Intelligence Multi-Agent System)** is a production-oriented backend system designed to:

- Generate inventory and marketing plans for retail stores.
- Orchestrate multiple AI agents to analyze business context.
- Persist decisions and full audit trails.
- Enable human-in-the-loop approval workflows.
- Be MLOps-ready (MLflow integrated, PostgreSQL backend).

This project demonstrates:

- Async FastAPI backend
- Multi-agent orchestration architecture
- Event-based audit logging
- Dockerized infrastructure
- MLflow tracking backend
- Clean REST contract design

## 🏗 Architecture
```
Client
↓
FastAPI REST API
↓
Orchestration Layer (Multi-Agent Workflow)
↓
Persistence Layer (PostgreSQL)
↓
Audit Events (plan_events)
```

## 🧱 Services


| Service      | Purpose |
|-------------|----------|
| API (FastAPI) | REST contract & orchestration entry point |
| PostgreSQL  | Persistent storage for plans & audit events |
| MLflow      | MLOps tracking backend (future model integration ready) |

## 🚀 Running the System

### 1️⃣ Start Infrastructure

```bash
docker compose up --build -d
```

Verify services:

```bash
docker compose ps
```

Health check:

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{"status":"healthy","service":"rimas"}
```

### 2️⃣ Seed Database

```bash
docker compose exec api python scripts/seed_db.py
```

Expected output:

```
Database seeded
```

### 🔁 End-to-End Workflow

#### 🟢 Create a Plan

Request:

```bash
curl -X POST http://localhost:8000/plans/ \
  -H "Content-Type: application/json" \
  -d '{
    "store_id": 1,
    "horizon_days": 14,
    "constraints": {
      "lead_time_days": 3,
      "budget_limit": 200000,
      "max_discount": 0.15
    },
    "items": [
      {"item_id": 1001, "current_stock": 120},
      {"item_id": 1002, "current_stock": 30}
    ]
  }'
```

Response Example:

```json
{
  "plan_id": "UUID",
  "status": "created",
  "recommendations": [
    {
      "item_id": 1002,
      "recommended_order_qty": 20,
      "recommended_discount": 0.1,
      "confidence": 0.85,
      "rationale": "Stub: stock=30, horizon=14d"
    }
  ],
  "metadata": {
    "model_version": null,
    "generated_at": "...",
    "trace_id": "..."
  }
}
```

#### 🟢 Approve Plan (Human-in-the-Loop)

```bash
curl -X POST http://localhost:8000/plans/{plan_id}/approve
```

Response:

```json
{
  "plan_id": "...",
  "status": "approved",
  ...
}
```

#### 🔍 Verify in Database

```bash
docker compose exec postgres psql -U rimas -d rimas
```

Check plans:

```sql
SELECT id, status FROM plans;
```

Check audit events:

```sql
SELECT event_type, created_at
FROM plan_events
WHERE plan_id='YOUR_PLAN_ID'
ORDER BY created_at DESC;
```

Example event flow:

```
data_analysis
inventory_analysis
marketing_analysis
supervisor_decision
final_decision
approved
```

## 🧠 Multi-Agent Workflow (Current Stub Architecture)

| Agent | Responsibility |
|-------|---------------|
| Data Analysis Agent | Identifies demand trends |
| Inventory Agent | Evaluates stock risk & reorder strategy |
| Marketing Agent | Evaluates promotion potential |
| Supervisor Agent | Consolidates outputs & produces final decision |

All agent outputs are:

- Stored in `agent_outputs`
- Logged individually in `plan_events`
- Consolidated into `final_decision`

This ensures full traceability of every decision.

## 🗄 Database Model

### plans
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Plan identifier |
| request_payload | JSON | Original client request |
| agent_outputs | JSON | All agent intermediate outputs |
| final_decision | JSON | Consolidated output |
| status | string | created / approved / rejected |
| created_at | timestamp | Creation time |
| updated_at | timestamp | Last update |

### plan_events
Audit log table.

| Column | Description |
|--------|-------------|
| plan_id | Foreign key to plans |
| event_type | Agent or lifecycle event |
| payload | JSON payload |
| created_at | Timestamp |

Enables:

- Full auditability
- Event reconstruction
- Compliance-ready logging
- Debug traceability

## 📘 REST Contract

### CreatePlanRequest
```json
{
  "store_id": int,
  "horizon_days": int,
  "constraints": {
    "lead_time_days": int,
    "budget_limit": float,
    "max_discount": float
  },
  "items": [
    {
      "item_id": int,
      "current_stock": int
    }
  ]
}
```

### PlanResponse
```json
{
  "plan_id": string,
  "status": string,
  "recommendations": [
    {
      "item_id": int,
      "recommended_order_qty": int,
      "recommended_discount": float,
      "confidence": float,
      "rationale": string
    }
  ],
  "metadata": {
    "model_version": string | null,
    "generated_at": datetime,
    "trace_id": string
  }
}
```

## 📊 Concepts & Domain Dictionary

- **Plan**: A planning request for a store over a defined time horizon.
- **Horizon**: Future time window considered for planning.
- **Constraints**: Operational limits (lead time, budget limit, maximum discount allowed).
- **Recommendation**: Structured actionable output for a SKU.
- **Trace ID**: Unique identifier for workflow traceability.
- **Agent Output**: Intermediate reasoning result from a specific agent.

## 🔬 MLOps Readiness

MLflow is integrated with PostgreSQL backend.

Future roadmap:

- Model training pipeline
- Versioned model registry
- Online scoring integration
- Model version injection into metadata

## 🛠 Tech Stack

| Layer | Technology |
|-------|------------|
| API | FastAPI (async) |
| ORM | SQLAlchemy Async |
| Validation | Pydantic v2 |
| DB | PostgreSQL |
| MLOps | MLflow |
| Infra | Docker + Docker Compose |
| Testing | Pytest |

## 🧪 Run Tests

```bash
docker compose exec api pytest -q
```

## 📌 Current Status

Tag: `v0.2.0-alpha.2`

✔ Infrastructure stable
✔ REST contract verified
✔ Multi-agent workflow implemented
✔ Audit trail verified
✔ Human approval flow working

## 🧩 Design Decisions

- Async SQLAlchemy is used to ensure non-blocking DB operations.
- Event-based audit log enables traceability and reproducibility.
- Explicit orchestration layer separates business workflow from transport layer.
- MLflow is integrated at infrastructure level to support future model versioning.
- Human-in-the-loop approval ensures operational control over automated decisions.

## 🚧 Next Steps

- Replace stub agents with real ML models
- Connect MLflow model registry
- Add authentication layer
- Add metrics & monitoring
- Introduce background task processing
