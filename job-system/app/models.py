import json
import uuid
from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.db import SessionLocal, engine
from app.models import Base, Job
from app.redis_client import r
from app.schemas import JobRequest

app = FastAPI(title="Distributed Job System", version="1.0.0")
Base.metadata.create_all(bind=engine)


@app.get("/")
def read_root():
    return {"message": "Job System running"}


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/submit-job")
def submit_job(job: JobRequest, db: Session = Depends(get_db)):
    existing_job = db.query(Job).filter(Job.idempotency_key == job.idempotent_key).first()
    if existing_job:
        return {
            "job_id": existing_job.job_id,
            "job_status": existing_job.status,
            "message": "Job already exists for this idempotency key",
        }

    new_job = Job(
        job_id=str(uuid.uuid4()),
        user_id=job.user_id,
        status="CREATED",
        payload=json.dumps(job.payload, sort_keys=True),
        retry_count=0,
        max_retries=settings.max_retries,
        error_message=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        idempotency_key=job.idempotent_key,
    )

    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    r.lpush(settings.redis_queue_name, str(new_job.job_id))

    return {
        "job_id": new_job.job_id,
        "job_status": new_job.status,
    }


@app.get("/job/{job_id}")
def get_job(job_id: str, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job Not Found")

    return {
        "job_id": job.job_id,
        "status": job.status,
        "retry_count": job.retry_count,
        "error_message": job.error_message,
        "updated_at": job.updated_at,
    }


@app.get("/jobs")
def get_all(db: Session = Depends(get_db)):
    jobs = db.query(Job).all()
    return [
        {
            "job_id": job.job_id,
            "status": job.status,
            "retry_count": job.retry_count,
            "user_id": job.user_id,
        }
        for job in jobs
    ]

