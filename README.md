# DistributedSystems

Lightweight distributed job processing demo.

This repository contains a small job processing example under the job-system/ directory. The API accepts jobs, stores metadata in a SQLite database (for local development), pushes job IDs onto a Redis list, and background worker processes consume and execute jobs. This repo is intended as a learning/demo project, not production-ready.

How to run (quick):

1. Install dependencies (inside job-system):

```bash
cd job-system
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Start Redis locally:

```bash
redis-server
```

3. Start the API:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

4. Start a worker in another terminal:

```bash
python job-system/app/worker.py
```

5. Start the recovery worker in another terminal:

```bash
python job-system/app/recovery_worker.py
```

Paths of interest: `job-system/app/main.py` (FastAPI app), `job-system/app/worker.py` (worker loop), `job-system/app/recovery_worker.py` (requeue stuck jobs), `job-system/app/models.py` (DB schema).
