.PHONY: up down run_local seed test build

up:
	docker compose up --build -d

down:
	docker compose down

run_local:
	uvicorn src.rimas.api.main:app --reload --host 0.0.0.0 --port 8000

seed:
	PYTHONPATH=src python -m scripts.seed_db

test:
	PYTHONPATH=src pytest tests/ -v
