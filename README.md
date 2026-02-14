# RIMAS – Retail Intelligence Multi-Agent System

Production-ready scaffold for:
- FastAPI (async)
- PostgreSQL + SQLAlchemy
- MLflow
- LangGraph multi-agent orchestration
- Docker

## Quick Start

```bash
docker compose up --build
```

- API: http://localhost:8000
- MLflow UI: http://localhost:5000

## Local Development

```bash
poetry install
make run_local
```

## Tests

```bash
make test
```
