# Distributed Systems - Job Processing System

This repository contains a small distributed job-processing example built with Python, FastAPI, SQLAlchemy, and Redis. It demonstrates an asynchronous queue pattern where incoming job submissions are accepted by an HTTP API, placed on a Redis queue, and consumed by background worker processes.

## Architecture

The solution is intentionally simple and is meant to illustrate a job queue workflow rather than a production-grade future-proof system.

- API layer: FastAPI service exposes endpoints to submit, query, and list jobs.
- Persistence: SQLAlchemy + SQLite for local development storage.
- Messaging: Redis acts as the durable task queue.
- Worker processes: background workers pull tasks from Redis, mark them as processing, and update status on completion or failure.
- Recovery worker: detects jobs stuck in PROCESSING state and re-enqueues them or marks them dead.

### High-level flow

1. A client submits a job via `/submit-job`.
2. The API validates the request and stores the job in the database.
3. The job ID is pushed to Redis.
4. One or more workers receive job IDs from the Redis queue.
5. Workers update the status to PROCESSING, execute the task logic, and mark the result as SUCCESS or FAILED.
6. A recovery process rescans stale processing jobs and requeues them if needed.

## Repository layout

```text
DistributedSystems/
├── README.md
├── job-system/
│   ├── .env.example
│   ├── .gitignore
│   ├── requirements.txt
│   └── app/
│       ├── __init__.py
│       ├── config.py
│       ├── db.py
│       ├── main.py
│       ├── models.py
│       ├── redis_client.py
│       ├── recovery_worker.py
│       ├── schemas.py
│       ├── worker.py
│       └── jobdb.db
└── ...
```

## Improvements made

The codebase was refactored to be more maintainable and easier to run locally:

- Fixed import paths so the application can be started reliably as a package.
- Centralized environment configuration with a dedicated settings module.
- Added a `.env.example` file for Redis and database configuration.
- Reworked the worker loop to be clearer and safer for retries and dead-letter handling.
- Improved API responses and status handling.
- Added package-level initialization and dependency manifest for local setup.

## Local setup

From the repository root:

```bash
cd job-system
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Then start Redis locally:

```bash
redis-server
```

Launch the API:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Start a worker in a separate terminal:

```bash
python app/worker.py
```

Start the recovery worker in another terminal:

```bash
python app/recovery_worker.py
```

## API usage

### Submit a job

```bash
curl -X POST "http://localhost:8000/submit-job" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-123",
    "payload": {"task": "email", "to": "example@example.com"},
    "idempotent_key": "task-001"
  }'
```

### Get a single job

```bash
curl "http://localhost:8000/job/{job_id}"
```

### List all jobs

```bash
curl "http://localhost:8000/jobs"
```

## Notes on production readiness

This project is a good learning exercise, but for production use it would need additional architectural improvements such as:

- Replace SQLite with PostgreSQL in production.
- Use a dedicated broker such as RabbitMQ or Kafka for large-scale workloads.
- Add persistence for task payloads separated from application metadata.
- Introduce explicit task execution modules and a consistent job state machine.
- Add metrics, structured logging, tracing, and health checks.
- Run workers behind a process manager like systemd, Supervisor, or Docker Compose.

## License

This project is provided for educational and demonstration purposes.

