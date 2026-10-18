import time
from datetime import datetime, timedelta

from app.config import settings
from app.db import SessionLocal
from app.models import Job
from app.redis_client import r


def recover_stuck_jobs():
    db = SessionLocal()
    try:
        stuck_jobs = db.query(Job).filter(
            Job.status == "PROCESSING",
            Job.updated_at < datetime.utcnow() - timedelta(seconds=settings.processing_timeout_seconds),
        ).all()

        for job in stuck_jobs:
            if job.retry_count < job.max_retries:
                job.retry_count += 1
                job.status = "CREATED"
                r.lpush(settings.redis_queue_name, str(job.job_id))
            else:
                job.status = "DEAD"
            db.commit()
    finally:
        db.close()


def run_recovery_worker():
    while True:
        recover_stuck_jobs()
        time.sleep(settings.recovery_sleep_seconds)


if __name__ == "__main__":
    run_recovery_worker()
