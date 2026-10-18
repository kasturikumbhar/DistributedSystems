import time

from app.config import settings
from app.db import SessionLocal
from app.models import Job
from app.redis_client import r


def process_job(job_id: str):
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.job_id == job_id).first()
        if not job:
            return

        if job.status == "SUCCESS":
            return

        job.status = "PROCESSING"
        job.updated_at = time.time()
        db.commit()
        print(f"Processing job: {job.job_id}")
        time.sleep(5)

        job.status = "SUCCESS"
        job.updated_at = time.time()
        db.commit()
        print(f"Completed job: {job.job_id}")
    except Exception as exc:
        job.status = "FAILED"
        job.retry_count += 1
        job.error_message = str(exc)
        if job.retry_count >= job.max_retries:
            job.status = "DEAD"
        else:
            r.lpush(settings.redis_queue_name, str(job.job_id))
        db.commit()
        print(f"Job {job.job_id} failed: {exc}")
    finally:
        db.close()


def run_worker():
    while True:
        job_id = r.rpop(settings.redis_queue_name)
        if not job_id:
            time.sleep(settings.worker_poll_interval_seconds)
            continue

        process_job(str(job_id))


if __name__ == "__main__":
    run_worker()
