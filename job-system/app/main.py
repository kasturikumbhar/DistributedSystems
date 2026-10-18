from fastapi import FastAPI
from app.db import engine
from app.models import Base , Job
from app.schemas import JobRequest
from fastapi import Depends
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.redis_client import r
from datetime import datetime
import uuid



app=FastAPI()
Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"message":"Job System running"}

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/submit-job")
def submit_job(job:JobRequest,db : Session=Depends(get_db)):

    existing_job= db.query(Job).filter(Job.idempotency_key==job.idempotent_key).first()
    if existing_job:
        print(f"job details from db:{existing_job}")
        return {
            "job_id": existing_job.job_id,
            "job_status": existing_job.status
        }
    else:
        new_job= Job (
            job_id=str(uuid.uuid4()),
            user_id=job.user_id,
            status = "CREATED",
            payload = str(job.payload),
            retry_count = 0,
            max_retries = 3,
            error_message = None,
            created_at = datetime.utcnow(),
            updated_at = datetime.utcnow(),
            idempotency_key = job.idempotent_key
            )
        
        db.add(new_job)
        db.commit()
        db.refresh(new_job)
    r.lpush("job_queue",str(new_job.job_id))
    

    return {
        "job_id":new_job.job_id,
        "job_status":new_job.status 
        }

@app.get('/job/{job_id}')
def get_job(job_id:str,db: Session= Depends(get_db)):
    job=db.query(Job).filter(Job.job_id==job_id).first()
    if job:
        return {
            "status": job.status,
            "retry count": job.retry_count
        }
    else:
        return {"error":"Job Not Found"}
@app.get("/jobs")
def get_all(db:Session=Depends(get_db)):
    jobs=[(jobid[0],jobid[1]) for jobid in db.query(Job.job_id, Job.status).all()]
    print(jobs)
    return jobs

